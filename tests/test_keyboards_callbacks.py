import unittest

from keyboards import admin_list_item_keyboard, admin_list_view_keyboard


def _row_callback_data(markup, row: int, col: int) -> str:
    return markup.inline_keyboard[row][col].callback_data


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
            "admin_view_photo:123:face:pending:5:brief",
        )
        self.assertEqual(
            _row_callback_data(markup, 4, 0),
            "admin_card:123:full:pending:5",
        )

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

    def test_view_keyboard_full_mode_preserves_photo_mode(self):
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
            "admin_view_photo:777:face:reviewed:1:full",
        )
        self.assertEqual(
            _row_callback_data(markup, 3, 0),
            "admin_card:777:brief:reviewed:1",
        )


if __name__ == "__main__":
    unittest.main()
