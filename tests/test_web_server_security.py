import unittest
import time

import web_server


class WebServerSecurityTests(unittest.TestCase):
    def _wait_for_admin_refresh_idle(self, timeout: float = 2.0) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            with web_server._ADMIN_REFRESH_LOCK:
                if not web_server._ADMIN_REFRESH_RUNNING:
                    return
            time.sleep(0.01)
        self.fail("admin refresh worker did not become idle in time")

    def test_detect_honeypot_field_empty(self):
        fields = {"name": "Alice", "phone": "+1234567890"}
        self.assertIsNone(web_server.detect_honeypot_field(fields))

    def test_detect_honeypot_field_website(self):
        fields = {"website": "spam.example", "name": "Alice"}
        self.assertEqual(web_server.detect_honeypot_field(fields), "website")

    def test_detect_honeypot_field_company(self):
        fields = {"company": "Spam LLC", "name": "Alice"}
        self.assertEqual(web_server.detect_honeypot_field(fields), "company")

    def test_hash_for_logs_is_stable_and_short(self):
        first = web_server._hash_for_logs("127.0.0.1")
        second = web_server._hash_for_logs("127.0.0.1")
        self.assertEqual(first, second)
        self.assertEqual(len(first), 12)

    def test_schedule_admin_refresh_runs_worker_once(self):
        original_notify = web_server.notify_admin_new_application
        original_update = web_server.update_admin_menu_message
        calls = {"notify": 0, "update": 0}

        def fake_notify():
            calls["notify"] += 1

        def fake_update():
            calls["update"] += 1

        try:
            with web_server._ADMIN_REFRESH_LOCK:
                web_server._ADMIN_REFRESH_RUNNING = False
                web_server._ADMIN_REFRESH_DIRTY = False
            web_server.notify_admin_new_application = fake_notify
            web_server.update_admin_menu_message = fake_update
            web_server.schedule_admin_refresh()
            self._wait_for_admin_refresh_idle()
            self.assertEqual(calls["notify"], 1)
            self.assertEqual(calls["update"], 1)
        finally:
            web_server.notify_admin_new_application = original_notify
            web_server.update_admin_menu_message = original_update
            with web_server._ADMIN_REFRESH_LOCK:
                web_server._ADMIN_REFRESH_RUNNING = False
                web_server._ADMIN_REFRESH_DIRTY = False

    def test_schedule_admin_refresh_coalesces_multiple_calls(self):
        original_notify = web_server.notify_admin_new_application
        original_update = web_server.update_admin_menu_message
        calls = {"notify": 0, "update": 0}
        first_notify_started = False
        first_notify_released = False

        def fake_notify():
            nonlocal first_notify_started
            nonlocal first_notify_released
            calls["notify"] += 1
            if not first_notify_started:
                first_notify_started = True
                while not first_notify_released:
                    time.sleep(0.005)

        def fake_update():
            calls["update"] += 1

        try:
            with web_server._ADMIN_REFRESH_LOCK:
                web_server._ADMIN_REFRESH_RUNNING = False
                web_server._ADMIN_REFRESH_DIRTY = False
            web_server.notify_admin_new_application = fake_notify
            web_server.update_admin_menu_message = fake_update
            web_server.schedule_admin_refresh()

            deadline = time.time() + 1.0
            while not first_notify_started and time.time() < deadline:
                time.sleep(0.005)
            self.assertTrue(first_notify_started)

            for _ in range(5):
                web_server.schedule_admin_refresh()
            first_notify_released = True
            self._wait_for_admin_refresh_idle()

            self.assertEqual(calls["notify"], 2)
            self.assertEqual(calls["update"], 2)
        finally:
            web_server.notify_admin_new_application = original_notify
            web_server.update_admin_menu_message = original_update
            with web_server._ADMIN_REFRESH_LOCK:
                web_server._ADMIN_REFRESH_RUNNING = False
                web_server._ADMIN_REFRESH_DIRTY = False


if __name__ == "__main__":
    unittest.main()
