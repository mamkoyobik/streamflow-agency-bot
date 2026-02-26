import unittest
from email.message import Message

import web_server


class _DummyHandler:
    def __init__(self, headers: dict[str, str] | None = None, path: str = "/api/infobip/webhook"):
        message = Message()
        base_headers = {"Host": "streamflowagency.com"}
        if headers:
            base_headers.update(headers)
        for key, value in base_headers.items():
            message[key] = value
        self.headers = message
        self.path = path

    def _request_host(self) -> str:
        return web_server.Handler._request_host(self)

    def _request_origin_host(self) -> str:
        return web_server.Handler._request_origin_host(self)


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
            web_server.STARFLOW_SITE_URL = "https://starflowinc.com"
            self.assertEqual(
                web_server.infer_project_from_host("starflowinc.com"),
                web_server.PROJECT_STARFLOW,
            )
            self.assertEqual(
                web_server.infer_project_from_host("www.starflowinc.com"),
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
            web_server.STARFLOW_SITE_URL = "https://starflowinc.com"
            self.assertEqual(web_server.homepage_path_for_host("streamflowagency.com"), "/index.html")
            self.assertEqual(web_server.homepage_path_for_host("starflowinc.com"), "/starflow.html")
            self.assertEqual(web_server.homepage_path_for_host(""), "/index.html")
        finally:
            web_server.SITE_URL = original_site
            web_server.STARFLOW_SITE_URL = original_star_site

    def test_resolve_project_prefers_explicit_param(self):
        original_site = web_server.SITE_URL
        original_star_site = web_server.STARFLOW_SITE_URL
        try:
            web_server.SITE_URL = "https://streamflowagency.com"
            web_server.STARFLOW_SITE_URL = "https://starflowinc.com"
            self.assertEqual(
                web_server.resolve_project("streamflow", host="starflowinc.com"),
                web_server.PROJECT_STREAMFLOW,
            )
            self.assertEqual(
                web_server.resolve_project("starflow", host="streamflowagency.com"),
                web_server.PROJECT_STARFLOW,
            )
            self.assertEqual(
                web_server.resolve_project("", host="starflowinc.com"),
                web_server.PROJECT_STARFLOW,
            )
            self.assertEqual(
                web_server.resolve_project(None, host="unknown-host.com"),
                web_server.PROJECT_STREAMFLOW,
            )
        finally:
            web_server.SITE_URL = original_site
            web_server.STARFLOW_SITE_URL = original_star_site

    def test_request_host_from_headers_prefers_public_host(self):
        original_site = web_server.SITE_URL
        original_star_site = web_server.STARFLOW_SITE_URL
        try:
            web_server.SITE_URL = "https://streamflowagency.com"
            web_server.STARFLOW_SITE_URL = "https://starflowinc.com"
            host = web_server.request_host_from_headers(
                "starflowinc.com",
                "tqmax4l.up.railway.app",
            )
            self.assertEqual(host, "starflowinc.com")
        finally:
            web_server.SITE_URL = original_site
            web_server.STARFLOW_SITE_URL = original_star_site

    def test_internal_proxy_host_detection(self):
        self.assertTrue(web_server.is_internal_proxy_host("internal.railway.internal"))
        self.assertTrue(web_server.is_internal_proxy_host("tqmax4l.up.railway.app"))
        self.assertFalse(web_server.is_internal_proxy_host("streamflowagency.com"))

    def test_extract_authorization_secret(self):
        self.assertEqual(web_server._extract_authorization_secret("Bearer abc123"), "abc123")
        self.assertEqual(web_server._extract_authorization_secret("Token qwerty"), "qwerty")
        self.assertEqual(web_server._extract_authorization_secret("raw-secret"), "raw-secret")

    def test_infobip_webhook_secret_candidates_collect_header_and_query(self):
        handler = _DummyHandler(
            headers={
                "X-Webhook-Secret": "header-secret",
                "Authorization": "Bearer auth-secret",
            },
            path="/api/infobip/webhook?secret=query-secret",
        )
        candidates = web_server._infobip_webhook_secret_candidates(handler)
        self.assertIn("header-secret", candidates)
        self.assertIn("auth-secret", candidates)
        self.assertIn("query-secret", candidates)

    def test_is_infobip_webhook_authorized_true_when_secret_matches(self):
        original = web_server.INFOBIP_WEBHOOK_SECRET
        try:
            web_server.INFOBIP_WEBHOOK_SECRET = "expected-secret"
            handler = _DummyHandler(headers={"X-Infobip-Secret": "expected-secret"})
            self.assertTrue(web_server._is_infobip_webhook_authorized(handler))
        finally:
            web_server.INFOBIP_WEBHOOK_SECRET = original

    def test_is_infobip_webhook_authorized_false_when_secret_missing(self):
        original = web_server.INFOBIP_WEBHOOK_SECRET
        try:
            web_server.INFOBIP_WEBHOOK_SECRET = ""
            handler = _DummyHandler(headers={"X-Infobip-Secret": "expected-secret"})
            self.assertFalse(web_server._is_infobip_webhook_authorized(handler))
        finally:
            web_server.INFOBIP_WEBHOOK_SECRET = original

    def test_allowed_site_origin_accepts_public_hosts(self):
        original_site = web_server.SITE_URL
        original_star_site = web_server.STARFLOW_SITE_URL
        try:
            web_server.SITE_URL = "https://streamflowagency.com"
            web_server.STARFLOW_SITE_URL = "https://starflowinc.com"
            handler = _DummyHandler(headers={"Origin": "https://streamflowagency.com"})
            self.assertTrue(web_server.Handler._is_allowed_site_origin(handler))
        finally:
            web_server.SITE_URL = original_site
            web_server.STARFLOW_SITE_URL = original_star_site

    def test_allowed_site_origin_rejects_foreign_host(self):
        original_site = web_server.SITE_URL
        original_star_site = web_server.STARFLOW_SITE_URL
        try:
            web_server.SITE_URL = "https://streamflowagency.com"
            web_server.STARFLOW_SITE_URL = "https://starflowinc.com"
            handler = _DummyHandler(headers={"Origin": "https://evil.example"})
            self.assertFalse(web_server.Handler._is_allowed_site_origin(handler))
        finally:
            web_server.SITE_URL = original_site
            web_server.STARFLOW_SITE_URL = original_star_site


if __name__ == "__main__":
    unittest.main()
