from __future__ import annotations

import argparse
from pathlib import Path

from email_validation_core import ValidationResult, read_emails_from_csv, save_results_to_csv, validate_emails_in_batches


def validate_from_csv(file_path: str, check_smtp: bool = False, output_file: str | None = None) -> list[ValidationResult]:
    """Lee un CSV, valida los correos y guarda el resultado."""
    emails = read_emails_from_csv(file_path)
    results = validate_emails_in_batches(emails, check_smtp=check_smtp)

    destination = output_file or str(Path(file_path).with_name(f"{Path(file_path).stem}_resultados.csv"))
    saved_path = save_results_to_csv(results, destination)

    print(f"Resultados guardados en: {saved_path}")
    return results


def manual_input_mode(check_smtp: bool = False) -> list[ValidationResult]:
    """Permite ingresar correos manualmente."""
    emails = []
    print("Ingrese correos electrónicos uno por uno. Escriba 'FIN' para terminar.")
    while True:
        email = input("Correo: ").strip()
        if email.upper() == "FIN":
            break
        emails.append(email)
    return validate_emails_in_batches(emails, check_smtp=check_smtp)


def test_mode(check_smtp: bool = False) -> list[ValidationResult]:
    """Modo de prueba con correos predefinidos."""
    test_emails = ["test@example.com", "invalid-email", "user@domain", "valid.email@service.com"]
    return validate_emails_in_batches(test_emails, check_smtp=check_smtp)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validador de correos desde consola")
    parser.add_argument("--input", help="Ruta del archivo CSV de entrada")
    parser.add_argument("--output", help="Ruta del archivo CSV de salida")
    parser.add_argument("--smtp", action="store_true", help="Activar verificación SMTP")
    parser.add_argument("--test", action="store_true", help="Ejecutar modo de prueba")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.input:
        results = validate_from_csv(args.input, check_smtp=args.smtp, output_file=args.output)
    elif args.test:
        results = test_mode(check_smtp=args.smtp)
    else:
        print("Selecciona el modo de validación:")
        print("1. Entrada manual")
        print("2. Archivo CSV")
        print("3. Modo Test")
        choice = input("Opción: ").strip()

        if choice == "1":
            results = manual_input_mode(check_smtp=args.smtp)
        elif choice == "2":
            file_path = input("Ingrese la ruta del archivo CSV: ").strip()
            results = validate_from_csv(file_path, check_smtp=args.smtp)
        elif choice == "3":
            results = test_mode(check_smtp=args.smtp)
        else:
            print("Opción no válida.")
            return

    print("\nResultados:")
    for result in results:
        print(f"{result.email}: {'valido' if result.is_valid else 'nulo'} ({result.message})")

if __name__ == "__main__":
    main()