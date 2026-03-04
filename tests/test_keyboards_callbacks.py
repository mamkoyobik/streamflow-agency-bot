import unittest

from keyboards import (
    admin_list_item_keyboard,
    admin_list_view_keyboard,
    admin_menu_keyboard,
    admin_project_menu_keyboard,
)


def _row_callback_data(markup, row: int, col: int) -> str:
    return markup.inline_keyboard[row][col].callback_data


def _all_buttons(markup):
    for row in markup.inline_keyboard:
        for button in row:
            yield button


class AdminKeyboardCallbacksTests(unittest.TestCase):
    def test_pending_item_keyboard_has_plain_accept_reject_callbacks(self):
        markup = admin_list_item_keyboard(user_id=123, status="pending")
        self.assertEqual(_row_callback_data(markup, 0, 0), "admin_accept:123")
        self.assertEqual(_row_callback_data(markup, 0, 1), "admin_reject:123")

    def test_pending_view_keyboard_keeps_filter_and_offset(self):
        markup = admin_list_view_keyboard(
            user_id=123,
            status="pending",
            filter_key="pending",
            offset=5,
            total=10,
            limit=1,
        )
        self.assertEqual(_row_callback_data(markup, 0, 0), "admin_accept:123:view:pending:5")
        self.assertEqual(_row_callback_data(markup, 0, 1), "admin_reject:123:view:pending:5")
        self.assertEqual(_row_callback_data(markup, 1, 0), "admin_request_info:123:view:pending:5")
        self.assertEqual(
            _row_callback_data(markup, 2, 0),
            "admin_view_photo:123:face:pending:5",
        )

    def test_pending_view_keyboard_can_disable_request_info(self):
        markup = admin_list_view_keyboard(
            user_id=123,
            status="pending",
            filter_key="stage_full",
            offset=0,
            total=1,
            limit=1,
            allow_request_info=False,
        )
        callbacks = [
            button.callback_data
            for row in markup.inline_keyboard
            for button in row
            if button.callback_data
        ]
        self.assertFalse(any(value.startswith("admin_request_info:") for value in callbacks))

    def test_accepted_keyboards_have_send_model_action(self):
        item_markup = admin_list_item_keyboard(user_id=321, status="accepted")
        self.assertEqual(_row_callback_data(item_markup, 1, 0), "admin_send_model:321")

        view_markup = admin_list_view_keyboard(
            user_id=321,
            status="accepted",
            filter_key="accepted",
            offset=2,
            total=5,
            limit=1,
        )
        self.assertEqual(_row_callback_data(view_markup, 1, 0), "admin_send_model:321:view:accepted:2")

    def test_view_keyboard_full_mode_keeps_photo_callbacks(self):
        markup = admin_list_view_keyboard(
            user_id=777,
            status="rejected",
            filter_key="reviewed",
            offset=1,
            total=3,
            limit=1,
            show_full=True,
        )
        self.assertEqual(
            _row_callback_data(markup, 1, 0),
            "admin_view_photo:777:face:reviewed:1",
        )

    def test_admin_menu_has_project_selection(self):
        markup = admin_menu_keyboard({"pending": 1, "accepted": 0, "rejected": 0, "total": 1}, {"quick": 1, "full": 0})
        callbacks = [
            button.callback_data
            for row in markup.inline_keyboard
            for button in row
            if button.callback_data
        ]
        self.assertIn("admin_menu:panel_sf", callbacks)
        self.assertIn("admin_menu:panel_st", callbacks)

    def test_project_menu_has_scoped_filters(self):
        markup = admin_project_menu_keyboard(
            "sf",
            {
                "pending": 1,
                "total": 2,
                "accepted": 1,
                "rejected": 0,
                "reviewed": 1,
                "stage_quick": 1,
                "stage_full": 1,
            },
        )
        callbacks = [
            button.callback_data
            for row in markup.inline_keyboard
            for button in row
            if button.callback_data
        ]
        self.assertIn("admin_menu:f:sfp", callbacks)
        self.assertIn("admin_menu:f:sf", callbacks)

    def test_view_keyboard_has_compact_counter_button(self):
        markup = admin_list_view_keyboard(
            user_id=456,
            status="pending",
            filter_key="all",
            offset=5,
            total=46,
            limit=1,
        )
        buttons = list(_all_buttons(markup))
        counter = next((btn for btn in buttons if btn.callback_data == "admin_noop"), None)
        self.assertIsNotNone(counter)
        self.assertEqual(counter.text, "6/46")

    def test_project_scoped_callbacks_fit_telegram_limit(self):
        project_markup = admin_project_menu_keyboard("st")
        project_callbacks = [
            button.callback_data
            for row in project_markup.inline_keyboard
            for button in row
            if button.callback_data
        ]
        self.assertTrue(all(len(value) <= 64 for value in project_callbacks))

        view_markup = admin_list_view_keyboard(
            user_id=2147483647,
            status="pending",
            filter_key="stp",
            offset=9999,
            total=10000,
            limit=1,
        )
        view_callbacks = [
            button.callback_data
            for row in view_markup.inline_keyboard
            for button in row
            if button.callback_data
        ]
        self.assertTrue(all(len(value) <= 64 for value in view_callbacks))


if __name__ == "__main__":
    unittest.main()
