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

    def test_reviews_and_streams_are_separate(self):
        review_items = bot.load_portfolio_items("ru", bot.PORTFOLIO_MODE_REVIEWS)
        stream_items = bot.load_portfolio_items("ru", bot.PORTFOLIO_MODE_STREAMS)
        self.assertTrue(review_items)
        self.assertTrue(stream_items)
        self.assertTrue(all(item["kind"] == "photo" for item in review_items))
        self.assertTrue(all(item["kind"] == "video" for item in stream_items))


if __name__ == "__main__":
    unittest.main()
