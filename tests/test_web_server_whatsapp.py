import unittest

import web_server
from database import set_setting


class WebServerWhatsAppTests(unittest.TestCase):
    def tearDown(self):
        for phone in ("+10000000001", "+10000000002"):
            key = web_server._wa_flow_key(phone)
            if key:
                set_setting(key, None)

    def test_menu_response_site_is_compact(self):
        text = web_server._wa_menu_response("en", "site", step="menu")
        self.assertIn("https://", text)
        self.assertNotIn("Main menu", text)
        self.assertNotIn("Choose an action below", text)

    def test_parse_menu_alias_for_menu(self):
        self.assertEqual(web_server._parse_wa_menu_choice("menu"), "menu")
        self.assertEqual(web_server._parse_wa_menu_choice("\u043c\u0435\u043d\u044e"), "menu")

    def test_interactive_menu_uses_body_override(self):
        phone = "+10000000001"
        web_server._save_wa_flow(
            phone,
            {"mode": "quick", "step": "menu", "lang": "en", "data": {}},
        )
        captured: dict = {}

        original_flag = web_server.INFOBIP_INTERACTIVE_ENABLED
        original_buttons = web_server.infobip_send_whatsapp_interactive_buttons
        original_list = web_server.infobip_send_whatsapp_interactive_list
        try:
            web_server.INFOBIP_INTERACTIVE_ENABLED = True

            def fake_buttons(to_phone, body_text, buttons, **kwargs):
                captured["to"] = to_phone
                captured["body"] = body_text
                captured["buttons"] = buttons
                captured["kwargs"] = kwargs
                return True

            web_server.infobip_send_whatsapp_interactive_buttons = fake_buttons
            web_server.infobip_send_whatsapp_interactive_list = lambda *_args, **_kwargs: False

            ok = web_server.send_wa_interactive_controls(phone, body_override="https://example.com")
            self.assertTrue(ok)
            self.assertEqual(captured.get("to"), phone)
            self.assertEqual(captured.get("body"), "https://example.com")
            self.assertTrue(captured.get("buttons"))
        finally:
            web_server.INFOBIP_INTERACTIVE_ENABLED = original_flag
            web_server.infobip_send_whatsapp_interactive_buttons = original_buttons
            web_server.infobip_send_whatsapp_interactive_list = original_list

    def test_menu_action_returns_compact_content_and_keeps_menu_step(self):
        phone = "+10000000002"
        web_server._save_wa_flow(
            phone,
            {"mode": "quick", "step": "menu", "lang": "en", "data": {}},
        )
        handled, reply = web_server.handle_whatsapp_application_message(
            {
                "from": phone,
                "type": "INTERACTIVE",
                "text": "menu_site",
                "media_url": "",
            }
        )
        self.assertTrue(handled)
        self.assertIsInstance(reply, str)
        self.assertIn("https://", reply)
        self.assertNotIn("Main menu", reply)
        flow = web_server._load_wa_flow(phone)
        self.assertEqual(flow.get("step"), "menu")

    def test_manager_link_uses_whatsapp_number(self):
        original = web_server.WA_MANAGER_PHONE
        try:
            web_server.WA_MANAGER_PHONE = "+380998074928"
            self.assertEqual(web_server._wa_manager_link(), "https://wa.me/380998074928")
        finally:
            web_server.WA_MANAGER_PHONE = original

    def test_yes_no_parser_accepts_button_ids(self):
        self.assertEqual(web_server._parse_wa_yes_no_choice("yn_yes", "en"), "Да")
        self.assertEqual(web_server._parse_wa_yes_no_choice("yn_no", "en"), "Нет")

    def test_whatsapp_link_has_no_stage2_key(self):
        original_sender = web_server.INFOBIP_WHATSAPP_SENDER
        try:
            web_server.INFOBIP_WHATSAPP_SENDER = "447860089369"
            link = web_server.build_whatsapp_stage2_link("abcdef123456", "en")
            self.assertEqual(link, "https://wa.me/447860089369")
            self.assertNotIn("text=", link)
        finally:
            web_server.INFOBIP_WHATSAPP_SENDER = original_sender

    def test_start_after_done_returns_menu(self):
        phone = "+10000000002"
        web_server._save_wa_flow(
            phone,
            {"mode": "site_stage2", "step": "done", "lang": "en", "data": {}},
        )
        handled, reply = web_server.handle_whatsapp_application_message(
            {
                "from": phone,
                "type": "TEXT",
                "text": "start",
                "media_url": "",
            }
        )
        self.assertTrue(handled)
        self.assertEqual(reply, web_server._wa_menu_text_for_step("en", "menu"))
        flow = web_server._load_wa_flow(phone)
        self.assertEqual(flow.get("step"), "menu")

    def test_interactive_living_uses_yes_no_buttons(self):
        phone = "+10000000002"
        web_server._save_wa_flow(
            phone,
            {"mode": "quick", "step": "living", "lang": "en", "data": {}},
        )
        captured: dict = {}
        original_flag = web_server.INFOBIP_INTERACTIVE_ENABLED
        original_buttons = web_server.infobip_send_whatsapp_interactive_buttons
        try:
            web_server.INFOBIP_INTERACTIVE_ENABLED = True

            def fake_buttons(to_phone, body_text, buttons, **kwargs):
                captured["to"] = to_phone
                captured["body"] = body_text
                captured["buttons"] = buttons
                captured["kwargs"] = kwargs
                return True

            web_server.infobip_send_whatsapp_interactive_buttons = fake_buttons
            ok = web_server.send_wa_interactive_controls(phone)
            self.assertTrue(ok)
            self.assertEqual(captured.get("to"), phone)
            self.assertIn("private room", captured.get("body", "").lower())
            button_ids = [item.get("id") for item in captured.get("buttons", [])]
            self.assertIn("yn_yes", button_ids)
            self.assertIn("yn_no", button_ids)
        finally:
            web_server.INFOBIP_INTERACTIVE_ENABLED = original_flag
            web_server.infobip_send_whatsapp_interactive_buttons = original_buttons

    def test_portfolio_menu_transition(self):
        phone = "+10000000002"
        web_server._save_wa_flow(
            phone,
            {"mode": "quick", "step": "menu", "lang": "en", "data": {}},
        )
        handled, reply = web_server.handle_whatsapp_application_message(
            {
                "from": phone,
                "type": "INTERACTIVE",
                "text": "menu_portfolio",
                "media_url": "",
            }
        )
        self.assertTrue(handled)
        self.assertIn("portfolio", (reply or "").lower())
        flow = web_server._load_wa_flow(phone)
        self.assertEqual(flow.get("step"), "portfolio_menu")

    def test_portfolio_cases_open_gallery(self):
        phone = "+10000000002"
        web_server._save_wa_flow(
            phone,
            {"mode": "quick", "step": "portfolio_menu", "lang": "en", "data": {}},
        )
        handled, reply = web_server.handle_whatsapp_application_message(
            {
                "from": phone,
                "type": "INTERACTIVE",
                "text": "menu_portfolio_cases",
                "media_url": "",
            }
        )
        self.assertTrue(handled)
        self.assertIn("/assets/portfolio/", reply or "")
        flow = web_server._load_wa_flow(phone)
        self.assertEqual(flow.get("step"), "portfolio_view")
        payload = flow.get("data") if isinstance(flow.get("data"), dict) else {}
        self.assertEqual(payload.get("portfolio_kind"), "cases")

    def test_interactive_portfolio_view_has_nav_and_media_header(self):
        phone = "+10000000002"
        web_server._save_wa_flow(
            phone,
            {
                "mode": "quick",
                "step": "portfolio_view",
                "lang": "en",
                "data": {"portfolio_kind": "cases", "portfolio_index": 0},
            },
        )
        captured: dict = {}
        original_flag = web_server.INFOBIP_INTERACTIVE_ENABLED
        original_buttons = web_server.infobip_send_whatsapp_interactive_buttons
        try:
            web_server.INFOBIP_INTERACTIVE_ENABLED = True

            def fake_buttons(to_phone, body_text, buttons, **kwargs):
                captured["to"] = to_phone
                captured["body"] = body_text
                captured["buttons"] = buttons
                captured["kwargs"] = kwargs
                return True

            web_server.infobip_send_whatsapp_interactive_buttons = fake_buttons
            ok = web_server.send_wa_interactive_controls(phone)
            self.assertTrue(ok)
            self.assertEqual(captured.get("to"), phone)
            self.assertIn("/assets/portfolio/", captured.get("body", ""))
            button_ids = [item.get("id") for item in captured.get("buttons", [])]
            self.assertIn("portfolio_back", button_ids)
            self.assertIn("header_media_url", captured.get("kwargs", {}))
        finally:
            web_server.INFOBIP_INTERACTIVE_ENABLED = original_flag
            web_server.infobip_send_whatsapp_interactive_buttons = original_buttons

    def test_about_menu_shows_section_text(self):
        phone = "+10000000002"
        web_server._save_wa_flow(
            phone,
            {"mode": "quick", "step": "about_menu", "lang": "en", "data": {}},
        )
        handled, reply = web_server.handle_whatsapp_application_message(
            {
                "from": phone,
                "type": "INTERACTIVE",
                "text": "menu_about_work",
                "media_url": "",
            }
        )
        self.assertTrue(handled)
        self.assertIn("remote", (reply or "").lower())
        flow = web_server._load_wa_flow(phone)
        self.assertEqual(flow.get("step"), "about_menu")


if __name__ == "__main__":
    unittest.main()
