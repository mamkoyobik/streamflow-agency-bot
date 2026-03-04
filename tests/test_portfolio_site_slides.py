import unittest
from pathlib import Path

import bot


class PortfolioSiteSlidesTests(unittest.TestCase):
    def test_load_site_portfolio_slides_ru(self):
        items = bot.load_site_portfolio_slide_items("ru")
        self.assertGreaterEqual(len(items), 8)
        first = items[0]
        self.assertEqual(first["kind"], "photo")
        self.assertIn(str(Path("web") / "assets" / "portfolio" / "1.jpg"), str(first["path"]))

    def test_load_site_portfolio_slides_en_localized(self):
        items = bot.load_site_portfolio_slide_items("en")
        self.assertGreaterEqual(len(items), 8)
        first = items[0]
        self.assertIn(
            str(Path("web") / "assets" / "portfolio" / "en" / "1.jpg"),
            str(first["path"]),
        )

    def test_load_portfolio_items_uses_site_mode(self):
        default_items = bot.load_portfolio_items("en", bot.PORTFOLIO_MODE_DEFAULT)
        site_items = bot.load_portfolio_items("en", bot.PORTFOLIO_MODE_SITE_SLIDES)
        self.assertNotEqual(len(default_items), 0)
        self.assertGreaterEqual(len(site_items), 8)


if __name__ == "__main__":
    unittest.main()
