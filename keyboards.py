import os

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from texts import t, field_title

SITE_URL = (os.getenv("SITE_URL") or "https://streamflowagency.com").strip().rstrip("/")

# ================= MAIN MENU =================

def main_menu(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "menu_be_model"), callback_data="apply")],
        [InlineKeyboardButton(text=t(lang, "menu_website"), url=SITE_URL)],
        [InlineKeyboardButton(text=t(lang, "menu_portfolio"), callback_data="portfolio")],
        [InlineKeyboardButton(text=t(lang, "menu_about"), callback_data="about")],
        [InlineKeyboardButton(text=t(lang, "menu_contact"), callback_data="contact")],
        [InlineKeyboardButton(text=t(lang, "menu_channel"), url="https://t.me/+uuVr5gJFwoJjYmRi")],
        [InlineKeyboardButton(text=t(lang, "menu_lang"), callback_data="language_menu")],
    ])

# ================= UNIVERSAL =================

def back_to_menu(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "menu_home"), callback_data="main_menu")]
    ])

# ================= FORM =================

def form_keyboard(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="form_back")],
        [InlineKeyboardButton(text=t(lang, "menu_home"), callback_data="main_menu")]
    ])

# ================= PREVIEW =================

def preview_keyboard(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(lang, "btn_edit_data"), callback_data="preview_edit"),
            InlineKeyboardButton(text=t(lang, "btn_edit_photo"), callback_data="preview_edit_photo")
        ],
        [
            InlineKeyboardButton(text=t(lang, "btn_send"), callback_data="preview_confirm")
        ],
        [
            InlineKeyboardButton(text=t(lang, "menu_home"), callback_data="main_menu")
        ]
    ])

# ================= PREVIEW EDIT FIELDS =================

def preview_edit_menu(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=field_title("name", lang), callback_data="edit:name")],
        [InlineKeyboardButton(text=field_title("city", lang), callback_data="edit:city")],
        [InlineKeyboardButton(text=field_title("phone", lang), callback_data="edit:phone")],
        [InlineKeyboardButton(text=field_title("age", lang), callback_data="edit:age")],
        [InlineKeyboardButton(text=field_title("living", lang), callback_data="edit:living")],
        [InlineKeyboardButton(text=field_title("devices", lang), callback_data="edit:devices")],
        [InlineKeyboardButton(text=field_title("device_model", lang), callback_data="edit:device_model")],
        [InlineKeyboardButton(text=field_title("work_time", lang), callback_data="edit:work_time")],
        [InlineKeyboardButton(text=field_title("headphones", lang), callback_data="edit:headphones")],
        [InlineKeyboardButton(text=field_title("telegram", lang), callback_data="edit:telegram")],
        [InlineKeyboardButton(text=field_title("experience", lang), callback_data="edit:experience")],
        [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="preview_back")]
    ])

# ================= PREVIEW EDIT PHOTO =================

def preview_edit_photo_menu(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "photo_face_label"), callback_data="edit_photo:face")],
        [InlineKeyboardButton(text=t(lang, "photo_full_label"), callback_data="edit_photo:full")],
        [InlineKeyboardButton(text=t(lang, "btn_back_to_preview"), callback_data="preview_back")]
    ])

# ================= ABOUT =================

def about_menu(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "about_menu_work"), callback_data="about_work")],
        [InlineKeyboardButton(text=t(lang, "about_menu_platforms"), callback_data="about_platforms")],
        [InlineKeyboardButton(text=t(lang, "about_menu_income"), callback_data="about_income")],
        [InlineKeyboardButton(text=t(lang, "menu_home"), callback_data="main_menu")],
    ])

# ================= PORTFOLIO =================

def portfolio_menu(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "portfolio_menu_reviews"), callback_data="portfolio_reviews")],
        [InlineKeyboardButton(text=t(lang, "portfolio_menu_videos"), callback_data="portfolio_videos")],
        [InlineKeyboardButton(text=t(lang, "portfolio_menu_pdf"), callback_data="portfolio_pdf")],
        [InlineKeyboardButton(text=t(lang, "menu_home"), callback_data="main_menu")],
    ])

# ================= APPLY / CONTINUE =================

def reapply_keyboard(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_apply_again"), callback_data="apply_restart")],
        [InlineKeyboardButton(text=t(lang, "menu_home"), callback_data="main_menu")]
    ])

def continue_form_keyboard(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_continue"), callback_data="form_continue")],
        [InlineKeyboardButton(text=t(lang, "btn_restart"), callback_data="form_restart")],
        [InlineKeyboardButton(text=t(lang, "menu_home"), callback_data="main_menu")]
    ])

# ================= ADMIN =================

def admin_decision(user_id: int, contact_url: str | None = None):
    contact = contact_url or f"tg://user?id={user_id}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Принять",
                callback_data=f"admin_accept:{user_id}"
            ),
            InlineKeyboardButton(
                text="❌ Отклонить",
                callback_data=f"admin_reject:{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="💬 Написать кандидату",
                url=contact
            )
        ]
    ])

def admin_pending_keyboard(user_id: int, contact_url: str | None = None):
    contact = contact_url or f"tg://user?id={user_id}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🟡 На рассмотрении",
                callback_data=f"admin_status:{user_id}:pending"
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ Принять",
                callback_data=f"admin_accept:{user_id}"
            ),
            InlineKeyboardButton(
                text="❌ Отклонить",
                callback_data=f"admin_reject:{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="💬 Написать кандидату",
                url=contact
            )
        ]
    ])

def admin_accepted_keyboard(user_id: int, contact_url: str | None = None):
    contact = contact_url or f"tg://user?id={user_id}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Принято",
                callback_data=f"admin_status:{user_id}:accepted"
            )
        ],
        [
            InlineKeyboardButton(
                text="💬 Написать кандидату",
                url=contact
            )
        ]
    ])

def admin_rejected_keyboard(user_id: int, contact_url: str | None = None):
    contact = contact_url or f"tg://user?id={user_id}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="❌ Отклонено",
                callback_data=f"admin_status:{user_id}:rejected"
            )
        ],
        [
            InlineKeyboardButton(
                text="💬 Написать кандидату",
                url=contact
            )
        ]
    ])
def cancel_keyboard(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="edit_cancel")]
    ])


def language_keyboard(current_lang: str = "ru", include_home: bool = True):
    def lang_label(code: str, title: str) -> str:
        return f"✅ {title}" if code == current_lang else title

    rows = [
        [
            InlineKeyboardButton(text=lang_label("ru", "Русский"), callback_data="set_lang:ru"),
            InlineKeyboardButton(text=lang_label("en", "English"), callback_data="set_lang:en"),
        ],
        [
            InlineKeyboardButton(text=lang_label("pt", "Português"), callback_data="set_lang:pt"),
            InlineKeyboardButton(text=lang_label("es", "Español"), callback_data="set_lang:es"),
        ],
    ]
    if include_home:
        rows.append([InlineKeyboardButton(text=t(current_lang, "menu_home"), callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def reject_templates_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🕊 Сейчас не актуально", callback_data="reject_tpl:1")],
        [InlineKeyboardButton(text="🧩 Не совпали условия", callback_data="reject_tpl:2")],
        [InlineKeyboardButton(text="🕐 Вернёмся позже", callback_data="reject_tpl:3")],
        [InlineKeyboardButton(text="✍️ Своя причина", callback_data="reject_tpl:custom")],
        [InlineKeyboardButton(text="⬅️ В админ-меню", callback_data="admin_menu:refresh")],
    ])

def reject_reason_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ В админ-меню", callback_data="admin_menu:refresh")]
    ])

def confirm_reset_db_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚠️ Да, обнулить", callback_data="admin_reset_db:confirm"),
            InlineKeyboardButton(text="Отмена", callback_data="admin_reset_db:cancel")
        ]
    ])

def admin_menu_keyboard(counts: dict | None = None):
    pending = counts.get("pending", 0) if counts else 0
    accepted = counts.get("accepted", 0) if counts else 0
    rejected = counts.get("rejected", 0) if counts else 0
    total = counts.get("total", pending + accepted + rejected) if counts else 0
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"⏳ Ожидают подтверждения!! Просмотреть ({pending})",
                callback_data="admin_menu:pending"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"✅ Принятые ({accepted})",
                callback_data="admin_menu:accepted"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"❌ Отклонённые ({rejected})",
                callback_data="admin_menu:rejected"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"📚 Все заявки ({total})",
                callback_data="admin_menu:all"
            )
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_menu:stats"),
            InlineKeyboardButton(text="📁 Excel", callback_data="admin_menu:excel")
        ],
        [
            InlineKeyboardButton(text="🧹 Архивировать старые", callback_data="admin_menu:archive")
        ],
        [
            InlineKeyboardButton(text="⚠️ Сбросить базу", callback_data="admin_menu:reset"),
            InlineKeyboardButton(text="🔄 Обновить меню", callback_data="admin_menu:refresh")
        ]
    ])

def admin_list_nav_keyboard(filter_key: str, offset: int, total: int, limit: int):
    buttons = []
    prev_offset = offset - limit
    next_offset = offset + limit
    nav_row = []
    if prev_offset >= 0:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️ Предыдущая",
                callback_data=f"admin_list:{filter_key}:{prev_offset}"
            )
        )
    if next_offset < total:
        nav_row.append(
            InlineKeyboardButton(
                text="Следующая ➡️",
                callback_data=f"admin_list:{filter_key}:{next_offset}"
            )
        )
    if nav_row:
        buttons.append(nav_row)
    buttons.append([
        InlineKeyboardButton(text="⬅️ В админ-меню", callback_data="admin_menu:refresh")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_list_item_keyboard(user_id: int, status: str, contact_url: str | None = None):
    contact = contact_url or f"tg://user?id={user_id}"
    rows = []
    if status == "pending":
        rows.append([
            InlineKeyboardButton(text="✅ Принять", callback_data=f"admin_accept:{user_id}:view"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject:{user_id}:view"),
        ])
    elif status == "accepted":
        rows.append([
            InlineKeyboardButton(text="✅ Принято", callback_data=f"admin_status:{user_id}:accepted")
        ])
    elif status == "rejected":
        rows.append([
            InlineKeyboardButton(text="❌ Отклонено", callback_data=f"admin_status:{user_id}:rejected")
        ])
    rows.append([
        InlineKeyboardButton(text="📷 Фото", callback_data=f"admin_photos:{user_id}")
    ])
    rows.append([
        InlineKeyboardButton(text="💬 Написать кандидату", url=contact)
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def admin_list_view_keyboard(
    user_id: int,
    status: str,
    filter_key: str,
    offset: int,
    total: int,
    limit: int,
    contact_url: str | None = None
):
    contact = contact_url or f"tg://user?id={user_id}"
    rows = []
    if status == "pending":
        rows.append([
            InlineKeyboardButton(text="✅ Принять", callback_data=f"admin_accept:{user_id}:view"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject:{user_id}:view"),
        ])
    elif status == "accepted":
        rows.append([
            InlineKeyboardButton(text="✅ Принято", callback_data=f"admin_status:{user_id}:accepted")
        ])
    elif status == "rejected":
        rows.append([
            InlineKeyboardButton(text="❌ Отклонено", callback_data=f"admin_status:{user_id}:rejected")
        ])

    rows.append([
        InlineKeyboardButton(text="📷 Анфас", callback_data=f"admin_view_photo:{user_id}:face:{filter_key}:{offset}"),
        InlineKeyboardButton(text="🧍 В полный рост", callback_data=f"admin_view_photo:{user_id}:full:{filter_key}:{offset}")
    ])
    rows.append([
        InlineKeyboardButton(text="💬 Написать кандидату", url=contact)
    ])

    prev_offset = offset - limit
    next_offset = offset + limit
    nav_row = []
    if prev_offset >= 0:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️ Предыдущая",
                callback_data=f"admin_list:{filter_key}:{prev_offset}"
            )
        )
    if next_offset < total:
        nav_row.append(
            InlineKeyboardButton(
                text="Следующая ➡️",
                callback_data=f"admin_list:{filter_key}:{next_offset}"
            )
        )
    if nav_row:
        rows.append(nav_row)

    rows.append([
        InlineKeyboardButton(text="⬅️ В админ-меню", callback_data="admin_menu:refresh")
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)
