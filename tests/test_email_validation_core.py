import tempfile
import unittest
from pathlib import Path

from email_validation_core import normalize_email, read_emails_from_csv


class EmailValidationCoreTests(unittest.TestCase):
    def test_normalize_email_strips_whitespace(self):
        self.assertEqual(normalize_email("  user@example.com  "), "user@example.com")

    def test_read_emails_from_csv_skips_header_and_blank_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "emails.csv"
            csv_path.write_text("Email\n user@example.com \n\nadmin@example.com\n", encoding="utf-8")

            emails = read_emails_from_csv(csv_path)

        self.assertEqual(emails, ["user@example.com", "admin@example.com"])


if __name__ == "__main__":
    unittest.main()
