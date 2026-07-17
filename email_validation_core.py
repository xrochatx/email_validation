from __future__ import annotations

import concurrent.futures
import csv
import smtplib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import dns.resolver
from email_validator import EmailNotValidError, validate_email


@dataclass(frozen=True)
class ValidationResult:
    email: str
    is_valid: bool
    message: str


def normalize_email(raw_email: str) -> str:
    return raw_email.strip()


def validate_email_address(email: str) -> ValidationResult:
    """Validate email syntax without checking deliverability."""
    try:
        validate_email(email, check_deliverability=False)
        return ValidationResult(email=email, is_valid=True, message="Sintaxis válida")
    except EmailNotValidError as exc:
        return ValidationResult(email=email, is_valid=False, message=str(exc))


def check_mx_records(email: str, timeout: float = 5.0) -> bool:
    """Check whether the domain publishes MX records."""
    domain = email.split("@")[-1]
    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    resolver.lifetime = timeout

    try:
        records = resolver.resolve(domain, "MX")
        return bool(records)
    except (
        dns.resolver.NoAnswer,
        dns.resolver.NXDOMAIN,
        dns.resolver.NoNameservers,
        dns.resolver.Timeout,
        dns.resolver.LifetimeTimeout,
    ):
        return False


def verify_smtp(email: str, timeout: float = 10.0) -> bool:
    """Attempt a lightweight SMTP RCPT check.

    This can still produce false negatives because many providers reject
    verification probes, so it should be treated as an optional signal.
    """
    domain = email.split("@")[-1]
    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    resolver.lifetime = timeout

    try:
        mx_records = sorted(resolver.resolve(domain, "MX"), key=lambda record: record.preference)
        if not mx_records:
            return False

        mx_host = str(mx_records[0].exchange).rstrip(".")
        with smtplib.SMTP(mx_host, timeout=timeout) as server:
            server.ehlo_or_helo_if_needed()
            server.mail("test@example.com")
            code, _ = server.rcpt(email)
            return code in {250, 251}
    except Exception:
        return False


def validate_email_full(email: str, check_smtp: bool = False) -> ValidationResult:
    """Run syntax, MX and optionally SMTP validation."""
    syntax_result = validate_email_address(email)
    if not syntax_result.is_valid:
        return syntax_result

    if not check_mx_records(email):
        return ValidationResult(email=email, is_valid=False, message="Dominio sin registros MX")

    if check_smtp:
        smtp_ok = verify_smtp(email)
        if smtp_ok:
            return ValidationResult(email=email, is_valid=True, message="SMTP verificado")
        return ValidationResult(email=email, is_valid=False, message="No verificado por SMTP")

    return ValidationResult(email=email, is_valid=True, message="Sintaxis y MX válidos")


def read_emails_from_csv(file_path: str | Path) -> list[str]:
    """Read emails from the first column of a CSV file.

    Empty rows are ignored. A header row is skipped when the first cell looks
    like a label instead of an address.
    """
    emails: list[str] = []
    path = Path(file_path)

    with path.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row:
                continue

            candidate = normalize_email(row[0])
            if not candidate:
                continue

            if not emails and "@" not in candidate and candidate.lower() in {"email", "correo", "mail"}:
                continue

            emails.append(candidate)

    return emails


def validate_emails_in_batches(
    emails: Iterable[str],
    batch_size: int = 1000,
    max_workers: int | None = None,
    check_smtp: bool = False,
) -> list[ValidationResult]:
    """Validate emails in batches using a thread pool."""
    cleaned_emails = [normalize_email(email) for email in emails if normalize_email(email)]
    results: list[ValidationResult] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for index in range(0, len(cleaned_emails), batch_size):
            batch = cleaned_emails[index : index + batch_size]
            results.extend(executor.map(lambda item: validate_email_full(item, check_smtp=check_smtp), batch))

    return results


def save_results_to_csv(results: Iterable[ValidationResult], output_file: str | Path) -> Path:
    """Save validation results to a CSV file and return the path."""
    path = Path(output_file)
    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Email", "Estado", "Mensaje"])
        for result in results:
            writer.writerow([
                result.email,
                "valido" if result.is_valid else "nulo",
                result.message,
            ])

    return path
