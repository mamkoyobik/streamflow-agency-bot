import unittest

import web_server


class WebServerProjectTests(unittest.TestCase):
    def test_normalize_project(self):
        self.assertEqual(web_server.normalize_project("starflow"), web_server.PROJECT_STARFLOW)
        self.assertEqual(web_server.normalize_project("starflow_corp"), web_server.PROJECT_STARFLOW)
        self.assertEqual(web_server.normalize_project("streamflow"), web_server.PROJECT_STREAMFLOW)
        self.assertEqual(web_server.normalize_project("unknown"), web_server.PROJECT_STREAMFLOW)

    def test_email_validation(self):
        self.assertTrue(web_server.is_valid_email("name@example.com"))
        self.assertTrue(web_server.is_valid_email("john+team@domain.co"))
        self.assertFalse(web_server.is_valid_email("bad"))
        self.assertFalse(web_server.is_valid_email("name@domain"))
        self.assertFalse(web_server.is_valid_email("name @domain.com"))

    def test_build_bot_stage2_link_uses_project_username(self):
        original_main = web_server.BOT_USERNAME
        original_star = web_server.STARFLOW_BOT_USERNAME
        try:
            web_server.BOT_USERNAME = "streamflowbot"
            web_server.STARFLOW_BOT_USERNAME = "starflowbot"
            stream_link = web_server.build_bot_stage2_link("abc123", "ru", project=web_server.PROJECT_STREAMFLOW)
            star_link = web_server.build_bot_stage2_link("abc123", "ru", project=web_server.PROJECT_STARFLOW)
            self.assertIn("streamflowbot", stream_link)
            self.assertIn("starflowbot", star_link)
            self.assertTrue(star_link.endswith("?start=s2_abc123_ru"))
        finally:
            web_server.BOT_USERNAME = original_main
            web_server.STARFLOW_BOT_USERNAME = original_star

    def test_infer_project_from_host(self):
        original_site = web_server.SITE_URL
        original_star_site = web_server.STARFLOW_SITE_URL
        try:
            web_server.SITE_URL = "https://streamflowagency.com"
            web_server.STARFLOW_SITE_URL = "https://starflowcorp.com"
            self.assertEqual(
                web_server.infer_project_from_host("starflowcorp.com"),
                web_server.PROJECT_STARFLOW,
            )
            self.assertEqual(
                web_server.infer_project_from_host("www.starflowcorp.com"),
                web_server.PROJECT_STARFLOW,
            )
            self.assertEqual(
                web_server.infer_project_from_host("streamflowagency.com"),
                web_server.PROJECT_STREAMFLOW,
            )
            self.assertEqual(
                web_server.infer_project_from_host("unknown-host.com"),
                web_server.PROJECT_STREAMFLOW,
            )
        finally:
            web_server.SITE_URL = original_site
            web_server.STARFLOW_SITE_URL = original_star_site

    def test_homepage_path_for_host(self):
        original_site = web_server.SITE_URL
        original_star_site = web_server.STARFLOW_SITE_URL
        try:
            web_server.SITE_URL = "https://streamflowagency.com"
            web_server.STARFLOW_SITE_URL = "https://starflowcorp.com"
            self.assertEqual(web_server.homepage_path_for_host("streamflowagency.com"), "/index.html")
            self.assertEqual(web_server.homepage_path_for_host("starflowcorp.com"), "/starflow.html")
            self.assertEqual(web_server.homepage_path_for_host(""), "/index.html")
        finally:
            web_server.SITE_URL = original_site
            web_server.STARFLOW_SITE_URL = original_star_site

    def test_resolve_project_prefers_explicit_param(self):
        original_site = web_server.SITE_URL
        original_star_site = web_server.STARFLOW_SITE_URL
        try:
            web_server.SITE_URL = "https://streamflowagency.com"
            web_server.STARFLOW_SITE_URL = "https://starflowcorp.com"
            self.assertEqual(
                web_server.resolve_project("streamflow", host="starflowcorp.com"),
                web_server.PROJECT_STREAMFLOW,
            )
            self.assertEqual(
                web_server.resolve_project("starflow", host="streamflowagency.com"),
                web_server.PROJECT_STARFLOW,
            )
            self.assertEqual(
                web_server.resolve_project("", host="starflowcorp.com"),
                web_server.PROJECT_STARFLOW,
            )
            self.assertEqual(
                web_server.resolve_project(None, host="unknown-host.com"),
                web_server.PROJECT_STREAMFLOW,
            )
        finally:
            web_server.SITE_URL = original_site
            web_server.STARFLOW_SITE_URL = original_star_site


if __name__ == "__main__":
    unittest.main()
