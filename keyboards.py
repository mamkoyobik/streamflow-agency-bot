from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= MAIN MENU =================

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌸 Стать моделью", callback_data="apply")],
        [InlineKeyboardButton(text="📁 Портфолио моделей", callback_data="portfolio")],
        [InlineKeyboardButton(text="ℹ️ Подробнее о работе", callback_data="about")],
        [InlineKeyboardButton(text="💬 Связь с администратором", callback_data="contact")],
        [InlineKeyboardButton(text="📣 Наш канал", url="https://t.me/+uuVr5gJFwoJjYmRi")],
    ])

# ================= UNIVERSAL =================

def back_to_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")]
    ])

# ================= FORM =================

def form_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="form_back")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")]
    ])

# ================= PREVIEW =================

def preview_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Исправить данные", callback_data="preview_edit"),
            InlineKeyboardButton(text="📷 Исправить фото", callback_data="preview_edit_photo")
        ],
        [
            InlineKeyboardButton(text="✅ Отправить", callback_data="preview_confirm")
        ],
        [
            InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")
        ]
    ])

# ================= PREVIEW EDIT FIELDS =================

def preview_edit_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Имя", callback_data="edit:name")],
        [InlineKeyboardButton(text="🌍 Город и страна", callback_data="edit:city")],
        [InlineKeyboardButton(text="📞 Телефон", callback_data="edit:phone")],
        [InlineKeyboardButton(text="📅 Дата рождения", callback_data="edit:age")],
        [InlineKeyboardButton(text="🏠 Помещение без посторонних", callback_data="edit:living")],
        [InlineKeyboardButton(text="📱 Устройства", callback_data="edit:devices")],
        [InlineKeyboardButton(text="📲 Модель устройства", callback_data="edit:device_model")],
        [InlineKeyboardButton(text="⏱ Время работы", callback_data="edit:work_time")],
        [InlineKeyboardButton(text="🎧 Наушники", callback_data="edit:headphones")],
        [InlineKeyboardButton(text="💬 Telegram", callback_data="edit:telegram")],
        [InlineKeyboardButton(text="💼 Опыт", callback_data="edit:experience")],
        [InlineKeyboardButton(text="⬅ Назад к предпросмотру", callback_data="preview_back")]
    ])

# ================= PREVIEW EDIT PHOTO =================

def preview_edit_photo_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📷 Фото анфас", callback_data="edit_photo:face")],
        [InlineKeyboardButton(text="🧍 Фото в полный рост", callback_data="edit_photo:full")],
        [InlineKeyboardButton(text="⬅ Назад к предпросмотру", callback_data="preview_back")]
    ])

# ================= ABOUT =================

def about_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌷 О формате работы", callback_data="about_work")],
        [InlineKeyboardButton(text="💻 Площадки", callback_data="about_platforms")],
        [InlineKeyboardButton(text="💰 Доход и выплаты", callback_data="about_income")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")],
    ])

# ================= PORTFOLIO =================

def portfolio_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤍 Отзывы моделей", callback_data="portfolio_reviews")],
        [InlineKeyboardButton(text="🎥 Примеры стримов", callback_data="portfolio_videos")],
        [InlineKeyboardButton(text="📄 PDF портфолио", callback_data="portfolio_pdf")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")],
    ])

# ================= APPLY / CONTINUE =================

def reapply_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Заполнить заново", callback_data="apply_restart")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")]
    ])

def continue_form_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Продолжить", callback_data="form_continue")],
        [InlineKeyboardButton(text="🔄 Начать сначала", callback_data="form_restart")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")]
    ])

# ================= ADMIN =================

def admin_decision(user_id: int):
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
                url=f"tg://user?id={user_id}"
            )
        ]
    ])

def admin_pending_keyboard(user_id: int):
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
                url=f"tg://user?id={user_id}"
            )
        ]
    ])

def admin_accepted_keyboard(user_id: int):
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
                url=f"tg://user?id={user_id}"
            )
        ]
    ])

def admin_rejected_keyboard(user_id: int):
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
                url=f"tg://user?id={user_id}"
            )
        ]
    ])
def cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Отмена", callback_data="edit_cancel")]
    ])

def reject_templates_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🕊 Сейчас не актуально", callback_data="reject_tpl:1")],
        [InlineKeyboardButton(text="🧩 Не совпали условия", callback_data="reject_tpl:2")],
        [InlineKeyboardButton(text="🕐 Вернёмся позже", callback_data="reject_tpl:3")],
        [InlineKeyboardButton(text="✍️ Своя причина", callback_data="reject_tpl:custom")],
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

def admin_list_item_keyboard(user_id: int, status: str):
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
        InlineKeyboardButton(text="💬 Написать кандидату", url=f"tg://user?id={user_id}")
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def admin_list_view_keyboard(
    user_id: int,
    status: str,
    filter_key: str,
    offset: int,
    total: int,
    limit: int
):
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
        InlineKeyboardButton(text="💬 Написать кандидату", url=f"tg://user?id={user_id}")
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
