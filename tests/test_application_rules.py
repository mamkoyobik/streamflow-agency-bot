import unittest
from datetime import date

from application_rules import (
    clean_user_text,
    normalize_user_text_input,
    normalize_phone,
    is_valid_phone,
    normalize_birthdate,
    is_valid_birthdate,
    normalize_yes_no,
    normalize_telegram,
)


class ApplicationRulesTests(unittest.TestCase):
    @staticmethod
    def _safe_shift_years(base: date, years: int) -> date:
        target_year = base.year + years
        while True:
            try:
                return base.replace(year=target_year)
            except ValueError:
                # Handles 29 Feb on non-leap years.
                base = base.replace(day=base.day - 1)

    def test_clean_user_text_strips_control_and_spaces(self):
        value = " \u200bПривет\x00   мир \n\t "
        self.assertEqual(clean_user_text(value), "Привет мир")

    def test_normalize_user_text_input_marks_overflow(self):
        cleaned, too_long = normalize_user_text_input("  123456  ", max_len=5)
        self.assertEqual(cleaned, "12345")
        self.assertTrue(too_long)

    def test_phone_normalization_and_validation(self):
        self.assertEqual(normalize_phone("8 (999) 111-22-33"), "+79991112233")
        self.assertEqual(normalize_phone("0044 7307 810222"), "+447307810222")
        self.assertEqual(normalize_phone("+380 (99) 807-49-28"), "+380998074928")
        self.assertEqual(normalize_phone("+351.912.345.678"), "+351912345678")
        self.assertEqual(normalize_phone("+89991112233"), "+89991112233")
        self.assertTrue(is_valid_phone("+447307810222"))
        self.assertTrue(is_valid_phone("+299123456"))
        self.assertFalse(is_valid_phone("123"))
        self.assertFalse(is_valid_phone("+1234567"))
        self.assertFalse(is_valid_phone("12+34"))

    def test_birthdate_normalization(self):
        self.assertEqual(normalize_birthdate("2000-01-31"), "31.01.2000")
        self.assertEqual(normalize_birthdate("31/01/2000"), "31.01.2000")
        self.assertIsNone(normalize_birthdate("31-01-2000"))

    def test_birthdate_18_plus_logic(self):
        today = date.today()
        exact_18 = self._safe_shift_years(today, -18).strftime("%d.%m.%Y")
        almost_18 = self._safe_shift_years(today, -17).strftime("%d.%m.%Y")
        self.assertTrue(is_valid_birthdate(exact_18))
        self.assertFalse(is_valid_birthdate(almost_18))

    def test_yes_no_multilang(self):
        self.assertEqual(normalize_yes_no("sí"), "Да")
        self.assertEqual(normalize_yes_no("sim"), "Да")
        self.assertEqual(normalize_yes_no("não"), "Нет")
        self.assertEqual(normalize_yes_no("No"), "Нет")
        self.assertIsNone(normalize_yes_no("maybe"))

    def test_telegram_normalization(self):
        self.assertEqual(normalize_telegram("@streamflowmanager"), "@streamflowmanager")
        self.assertEqual(normalize_telegram("https://t.me/streamflowmanager"), "@streamflowmanager")
        self.assertEqual(normalize_telegram("telegram.me/streamflowmanager"), "@streamflowmanager")
        self.assertEqual(
            normalize_telegram("https://t.me/streamflowmanager/?start=abc"),
            "@streamflowmanager",
        )
        self.assertEqual(normalize_telegram("HTTPS://T.ME/streamflowmanager"), "@streamflowmanager")
        self.assertIsNone(normalize_telegram("@ab"))


if __name__ == "__main__":
    unittest.main()
