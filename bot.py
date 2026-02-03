import asyncio
import logging
import random
import re
import traceback
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, FSInputFile,
    InputMediaPhoto, InputMediaVideo,
    ChatJoinRequest, InlineKeyboardMarkup
)
try:
    from aiogram.client.default import DefaultBotProperties
except Exception:
    DefaultBotProperties = None
from aiogram.enums import ParseMode, ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import StateFilter

from config import BOT_TOKEN, ADMIN_GROUP_ID, ADMIN_USERNAME, CHANNEL_ID
from states import ApplicationStates
from keyboards import *
from database import (
    set_status,
    get_status,
    get_application,
    set_last_state,
    set_last_apply_at,
    set_form_data,
    get_form_data,
    clear_form_data,
    cleanup_old_form_data,
    get_status_counts,
    set_admin_message_id,
    get_admin_message_id,
    get_admin_messages_for_archive,
    reset_all_data,
    get_setting,
    set_setting,
    list_applications,
    set_menu_message_id,
    get_menu_message_id
)
try:
    from excel_export import append_application_row, update_application_status
except Exception:
    append_application_row = None
    update_application_status = None
    logging.getLogger(__name__).exception("Excel export недоступен (нет openpyxl?)")
from utils import edit_or_send
from texts import (
    MENU_CAPTION,
    ACCEPT_CAPTION,
    ACK_TEXT,
    SUPPORT_LINES,
    LOADING_TEXT,
    STATUS_LABELS,
    FORM_QUESTIONS,
    FIELD_TITLES
)
from pathlib import Path

# ================= LOGGING =================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("bot_errors.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ================= BOT =================

if DefaultBotProperties:
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
else:
    bot = Bot(
        token=BOT_TOKEN,
        parse_mode=ParseMode.HTML
    )

dp = Dispatcher(storage=MemoryStorage())

# ================= GLOBAL ERROR HANDLER =================

from aiogram.types import ErrorEvent

@dp.error()
async def global_error_handler(event: ErrorEvent):
    exception = event.exception

    logger.error("🔥 GLOBAL ERROR")
    logger.error(
        "".join(
            traceback.format_exception(
                type(exception),
                exception,
                exception.__traceback__
            )
        )
    )
    try:
        await bot.send_message(
            ADMIN_GROUP_ID,
            "⚠️ <b>Ошибка в боте</b>\n\n"
            f"{type(exception).__name__}: {exception}"
        )
    except Exception:
        pass
    return True

# ================= JOIN REQUEST =================

@dp.chat_join_request(F.chat.id == CHANNEL_ID)
async def on_join_request(req: ChatJoinRequest):
    try:
        await bot.approve_chat_join_request(CHANNEL_ID, req.from_user.id)
        await bot.send_message(
            req.from_user.id,
            "🤍 Ты подала заявку в закрытый канал\n\nНажми /start ✨"
        )
    except Exception:
        logger.exception("Ошибка в on_join_request")

# ================= HELPERS =================

def is_valid_phone(text: str) -> bool:
    normalized = normalize_phone(text)
    if not normalized:
        return False
    digits = re.sub(r"\D", "", normalized)
    return 10 <= len(digits) <= 15

def normalize_birthdate(text: str) -> str | None:
    value = text.strip()
    for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(value, fmt)
            if dt.year < 1900:
                return None
            return dt.strftime("%d.%m.%Y")
        except ValueError:
            continue
    return None

def is_valid_birthdate(text: str) -> bool:
    return normalize_birthdate(text) is not None

def has_any_digit(text: str) -> bool:
    return any(ch.isdigit() for ch in text)

def normalize_phone(text: str) -> str | None:
    value = re.sub(r"[()\s\-]+", "", text.strip())
    if not value:
        return None
    if value.startswith("+"):
        digits = value[1:]
        if not digits.isdigit():
            return None
        return f"+{digits}"
    if value.isdigit():
        return value
    return None

def normalize_yes_no(text: str) -> str | None:
    value = text.strip().lower()
    yes = {"да", "есть", "имеется", "конечно", "ага", "y", "yes"}
    no = {"нет", "не", "нету", "no", "n"}
    if value in yes:
        return "Да"
    if value in no:
        return "Нет"
    return None

def normalize_telegram(text: str) -> str | None:
    value = text.strip()
    if value.startswith("https://t.me/"):
        value = value.split("/")[-1]
    elif value.startswith("http://t.me/"):
        value = value.split("/")[-1]
    elif value.startswith("t.me/"):
        value = value.split("/", 1)[1]

    if value.startswith("@"):
        value = value[1:]

    if re.fullmatch(r"[A-Za-z0-9_]{5,32}", value):
        return f"@{value}"
    return None

def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None

def is_rate_limited(last_apply_at: str | None, hours: int = 24) -> bool:
    last_dt = _parse_ts(last_apply_at)
    if not last_dt:
        return False
    now = datetime.now(timezone.utc)
    return now - last_dt < timedelta(hours=hours)

FORM_DATA_FIELDS = {
    "name",
    "city",
    "phone",
    "age",
    "living",
    "devices",
    "device_model",
    "work_time",
    "headphones",
    "telegram",
    "experience",
    "photo_face",
    "photo_full",
}
REQUIRED_PREVIEW_FIELDS = set(FORM_DATA_FIELDS)

STATE_TO_FIELD = {
    ApplicationStates.name: "name",
    ApplicationStates.city: "city",
    ApplicationStates.phone: "phone",
    ApplicationStates.age: "age",
    ApplicationStates.living: "living",
    ApplicationStates.devices: "devices",
    ApplicationStates.device_model: "device_model",
    ApplicationStates.work_time: "work_time",
    ApplicationStates.headphones: "headphones",
    ApplicationStates.telegram: "telegram",
    ApplicationStates.experience: "experience",
    ApplicationStates.photo_face: "photo_face",
    ApplicationStates.photo_full: "photo_full",
}

def build_ack() -> str:
    return f"{ACK_TEXT}\n{random.choice(SUPPORT_LINES)}"

async def gentle_typing(chat_id: int, duration: float | None = None):
    try:
        await bot.send_chat_action(chat_id, ChatAction.TYPING)
    except Exception:
        return
    await asyncio.sleep(duration or random.uniform(0.4, 0.8))

def build_status_line(status: str | None) -> str | None:
    if not status or status == "new":
        return None
    label = STATUS_LABELS.get(status)
    if not label:
        return None
    return f"Статус заявки: {label}"

def build_menu_caption_with_status(
    status: str,
    base_caption: str,
    intro: str | None = None,
    tail: str | None = None
) -> str:
    parts = []
    if intro:
        parts.append(intro)
    parts.append(base_caption)
    if tail:
        parts.append(tail)
    status_line = build_status_line(status)
    if status_line:
        parts.append(status_line)
    return "\n\n".join(parts)

PORTFOLIO_COOLDOWN_SECONDS = 10
PORTFOLIO_VIDEO_LAST: dict[int, datetime] = {}

DAILY_STATS_HOUR = 10
DAILY_STATS_MINUTE = 0
ADMIN_ARCHIVE_DAYS = 7
ADMIN_ARCHIVE_CHECK_HOURS = 6
ADMIN_MENU_SETTING_KEY = "admin_menu_message_id"
ADMIN_LIST_LIMIT = 1
ADMIN_NOTIFY_SETTING_KEY = "admin_notify_message_id"

def build_admin_menu_text(counts: dict) -> str:
    return (
        "🛠 <b>Админ-меню</b>\n\n"
        f"Ожидают подтверждения: <b>{counts.get('pending', 0)}</b>\n"
        f"Принятые: <b>{counts.get('accepted', 0)}</b>\n"
        f"Отклонённые: <b>{counts.get('rejected', 0)}</b>\n\n"
        "Выбери раздел ниже ✨"
    )

async def persist_form_data(state: FSMContext, user_id: int):
    data = await state.get_data()
    filtered = {k: v for k, v in data.items() if k in FORM_DATA_FIELDS and v is not None}
    if filtered:
        set_form_data(user_id, filtered)

async def update_form_field(state: FSMContext, user_id: int, **kwargs):
    await state.update_data(**kwargs)
    await persist_form_data(state, user_id)

async def restore_form_data(state: FSMContext, user_id: int):
    data = get_form_data(user_id)
    if data:
        await state.update_data(**data)

async def send_status_message(message: Message, status: str | None):
    line = build_status_line(status)
    if line:
        try:
            temp = await message.answer("✨ Проверяю статус…")
            await asyncio.sleep(random.uniform(0.5, 0.9))
            try:
                await temp.edit_text(line)
            except Exception:
                await message.answer(line)
        except Exception:
            await message.answer(line)

def build_admin_status_text(user_id: int, status: str) -> str:
    data = get_form_data(user_id) or {}
    name = data.get("name", "—")
    telegram = data.get("telegram", "—")
    return (
        "📝 <b>Статус обновлён</b>\n\n"
        f"Статус: <b>{status}</b>\n"
        f"👤 Имя: {name}\n"
        f"💬 Telegram: {telegram}\n"
        f"🆔 ID: {user_id}"
    )

def build_admin_summary(
    data: dict,
    user_id: int,
    status: str,
    archived: bool = False,
    is_new: bool = False
) -> str:
    status_label = STATUS_LABELS.get(status, status)
    header = "🔔 <b>Новая анкета — требуется просмотр</b>\n\n" if is_new else "🧾 <b>Кратко по заявке</b>\n\n"
    text = (
        f"{header}"
        f"👤 Имя: {data.get('name', '—')}\n"
        f"📅 Дата рождения: {data.get('age', '—')}\n"
        f"🌍 Город и страна: {data.get('city', '—')}\n"
        f"🏠 Помещение без посторонних: {data.get('living', '—')}\n"
        f"💬 Telegram: {data.get('telegram', '—')}\n"
        f"🆔 ID: {user_id}\n\n"
        f"Статус: <b>{status_label}</b>"
    )
    if archived:
        text += "\n\n🗂 Архив"
    return text

def admin_keyboard_for_status(user_id: int, status: str):
    if status == "accepted":
        return admin_accepted_keyboard(user_id)
    if status == "rejected":
        return admin_rejected_keyboard(user_id)
    return admin_pending_keyboard(user_id)

async def update_admin_summary_message(user_id: int, status: str) -> bool:
    message_id = get_admin_message_id(user_id)
    if not message_id:
        return False
    data = get_form_data(user_id) or {}
    try:
        await bot.edit_message_text(
            chat_id=ADMIN_GROUP_ID,
            message_id=message_id,
            text=build_admin_summary(data, user_id, status),
            reply_markup=admin_keyboard_for_status(user_id, status)
        )
        return True
    except Exception:
        logger.exception("Ошибка обновления админского сообщения")
        return False

def build_admin_stats_text() -> str:
    counts = get_status_counts()
    return (
        "📊 <b>Статистика заявок</b>\n\n"
        f"Всего: <b>{counts['total']}</b>\n"
        f"Новые: {counts['new']}\n"
        f"На рассмотрении: {counts['pending']}\n"
        f"Одобрены: {counts['accepted']}\n"
        f"Отклонены: {counts['rejected']}"
    )

async def daily_stats_task():
    while True:
        now = datetime.now()
        target = now.replace(
            hour=DAILY_STATS_HOUR,
            minute=DAILY_STATS_MINUTE,
            second=0,
            microsecond=0
        )
        if target <= now:
            target += timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())
        try:
            await bot.send_message(ADMIN_GROUP_ID, build_admin_stats_text())
            file_path = Path("applications.xlsx")
            if file_path.exists():
                await bot.send_document(
                    ADMIN_GROUP_ID,
                    FSInputFile(str(file_path))
                )
        except Exception:
            logger.exception("Ошибка отправки ежедневной статистики")

async def archive_admin_messages_once() -> int:
    archived = 0
    rows = get_admin_messages_for_archive(ADMIN_ARCHIVE_DAYS)
    for user_id, message_id in rows:
        data = get_form_data(user_id) or {}
        status = get_status(user_id) or "accepted"
        try:
            await bot.edit_message_text(
                chat_id=ADMIN_GROUP_ID,
                message_id=message_id,
                text=build_admin_summary(data, user_id, status, archived=True),
                reply_markup=None
            )
            set_admin_message_id(user_id, None)
            archived += 1
        except Exception:
            try:
                await bot.edit_message_reply_markup(
                    chat_id=ADMIN_GROUP_ID,
                    message_id=message_id,
                    reply_markup=None
                )
                set_admin_message_id(user_id, None)
                archived += 1
            except Exception:
                logger.exception("Ошибка архивации админского сообщения")
    return archived

async def archive_admin_messages_task():
    while True:
        try:
            await archive_admin_messages_once()
        except Exception:
            logger.exception("Ошибка задачи архивации")
        await asyncio.sleep(ADMIN_ARCHIVE_CHECK_HOURS * 3600)

async def ensure_admin_menu_posted():
    counts = get_status_counts()
    menu_text = build_admin_menu_text(counts)
    stored_id = get_setting(ADMIN_MENU_SETTING_KEY)
    if stored_id:
        try:
            await bot.edit_message_text(
                chat_id=ADMIN_GROUP_ID,
                message_id=int(stored_id),
                text=menu_text,
                reply_markup=admin_menu_keyboard(counts)
            )
            return
        except Exception:
            logger.exception("Не удалось обновить существующее админ-меню")
    try:
        msg = await bot.send_message(
            ADMIN_GROUP_ID,
            menu_text,
            reply_markup=admin_menu_keyboard(counts)
        )
        set_setting(ADMIN_MENU_SETTING_KEY, str(msg.message_id))
    except Exception:
        logger.exception("Ошибка автопостинга админ-меню")

async def update_admin_menu_message(text: str, reply_markup: InlineKeyboardMarkup):
    stored_id = get_setting(ADMIN_MENU_SETTING_KEY)
    if stored_id and stored_id.isdigit():
        try:
            await bot.edit_message_text(
                chat_id=ADMIN_GROUP_ID,
                message_id=int(stored_id),
                text=text,
                reply_markup=reply_markup
            )
            return
        except Exception:
            logger.exception("Не удалось обновить админ-сообщение")
    try:
        msg = await bot.send_message(
            ADMIN_GROUP_ID,
            text,
            reply_markup=reply_markup
        )
        await set_admin_menu_message_id(msg.message_id)
    except Exception:
        logger.exception("Ошибка отправки админ-сообщения")

async def notify_admin_new_application():
    counts = get_status_counts()
    text = (
        "🔔 <b>Новая анкета</b>\n\n"
        f"Ожидают подтверждения: <b>{counts.get('pending', 0)}</b>\n"
        "Открой админ-меню, чтобы просмотреть ✨"
    )
    stored_id = get_setting(ADMIN_NOTIFY_SETTING_KEY)
    if stored_id and stored_id.isdigit():
        try:
            await bot.delete_message(ADMIN_GROUP_ID, int(stored_id))
        except Exception:
            logger.exception("Не удалось удалить старое уведомление")
    try:
        msg = await bot.send_message(ADMIN_GROUP_ID, text)
        set_setting(ADMIN_NOTIFY_SETTING_KEY, str(msg.message_id))
    except Exception:
        logger.exception("Ошибка уведомления о заявке")

async def set_admin_menu_message_id(message_id: int):
    stored_id = get_setting(ADMIN_MENU_SETTING_KEY)
    if stored_id and stored_id.isdigit() and int(stored_id) != message_id:
        try:
            await bot.delete_message(ADMIN_GROUP_ID, int(stored_id))
        except Exception:
            logger.exception("Не удалось удалить старое админ-меню")
    set_setting(ADMIN_MENU_SETTING_KEY, str(message_id))

async def post_admin_menu():
    counts = get_status_counts()
    await update_admin_menu_message(
        build_admin_menu_text(counts),
        admin_menu_keyboard(counts)
    )

def _admin_list_label(filter_key: str | None) -> str:
    return {
        "pending": "Ожидают подтверждения",
        "accepted": "Принятые",
        "rejected": "Отклонённые",
        "all": "Все заявки",
        None: "Все заявки",
    }.get(filter_key, "Все заявки")

async def send_admin_list(
    call: CallbackQuery,
    filter_key: str,
    offset: int = 0
):
    status = None if filter_key == "all" else filter_key
    apps = list_applications(status)
    label = _admin_list_label(filter_key)
    if not apps:
        await update_admin_menu_message(
            f"🤍 {label}: пока пусто ✨",
            admin_menu_keyboard(get_status_counts())
        )
        await call.answer()
        return

    total = len(apps)
    if offset < 0:
        offset = 0
    if offset >= total:
        offset = max(total - 1, 0)
    slice_items = apps[offset: offset + ADMIN_LIST_LIMIT]
    page = offset // ADMIN_LIST_LIMIT + 1
    pages = (total + ADMIN_LIST_LIMIT - 1) // ADMIN_LIST_LIMIT
    current = slice_items[0]
    user_id = current["user_id"]
    item_status = current["status"] or status or "pending"
    data = get_form_data(user_id) or {}
    text = (
        f"🗂 <b>{label}</b>\n\n"
        f"Заявка <b>{offset + 1}</b> из <b>{total}</b>\n"
        f"Страница: <b>{page}/{pages}</b>\n\n"
        f"{build_admin_summary(data, user_id, item_status)}"
    )
    await update_admin_menu_message(
        text,
        admin_list_view_keyboard(user_id, item_status, filter_key, offset, total, ADMIN_LIST_LIMIT)
    )
    await call.answer()

async def send_menu(
    message: Message,
    caption: str = MENU_CAPTION,
    status: str | None = None,
    intro: str | None = None,
    tail: str | None = None
):
    await gentle_typing(message.chat.id)
    final_caption = (
        build_menu_caption_with_status(status, caption, intro, tail)
        if status
        else caption
    )
    await send_or_edit_user_menu(message.from_user.id, final_caption)

async def send_or_edit_user_menu(user_id: int, caption: str):
    message_id = get_menu_message_id(user_id)
    if message_id:
        try:
            await bot.edit_message_caption(
                chat_id=user_id,
                message_id=message_id,
                caption=caption,
                reply_markup=main_menu()
            )
            return
        except Exception:
            logger.exception("Не удалось обновить меню пользователя")
            try:
                await bot.delete_message(user_id, message_id)
            except Exception:
                pass
    try:
        msg = await bot.send_photo(
            user_id,
            FSInputFile("media/menu.jpg"),
            caption=caption,
            reply_markup=main_menu()
        )
        set_menu_message_id(user_id, msg.message_id)
    except Exception:
        logger.exception("Ошибка отправки меню пользователю")

async def start_application(message: Message, state: FSMContext):
    await state.clear()
    clear_form_data(message.from_user.id)
    set_status(message.from_user.id, "new")
    await state.set_state(ApplicationStates.name)
    set_last_state(message.from_user.id, ApplicationStates.name.state)
    await gentle_typing(message.chat.id)
    await message.answer(
        format_question(
            ApplicationStates.name,
            FORM_QUESTIONS[ApplicationStates.name]
        ),
        reply_markup=form_keyboard()
    )

async def send_next_question(
    message: Message,
    state: FSMContext,
    next_state: ApplicationStates,
    question: str,
    note: str | None = None
):
    await state.set_state(next_state)
    set_last_state(message.from_user.id, next_state.state)
    await gentle_typing(message.chat.id)
    ack = build_ack()
    if note:
        ack = f"{ack}\n{note}"
    await message.answer(
        f"{ack}\n\n{format_question(next_state, question)}",
        reply_markup=form_keyboard()
    )

# ================= START =================

@dp.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    try:
        await state.clear()
        app = get_application(message.from_user.id)
        status = app.get("status") if app else None
        await send_menu(message, status=status)
        if app and app.get("status") in {None, "new"} and app.get("last_state") in FORM_PROGRESS_STATES:
            await message.answer(
                "🤍 Похоже, анкета не завершена.\n\n"
                "Хочешь продолжить заполнение?",
                reply_markup=continue_form_keyboard()
            )
    except Exception:
        logger.exception("Ошибка в /start")

@dp.callback_query(F.data == "main_menu")
async def main_menu_handler(call: CallbackQuery, state: FSMContext):
    await state.clear()
    app = get_application(call.from_user.id)
    status = app.get("status") if app else None
    await send_menu(call.message, status=status)
    await call.answer()
# ================= APPLY =================

@dp.callback_query(F.data == "apply")
async def apply(call: CallbackQuery, state: FSMContext):
    try:
        app = get_application(call.from_user.id)
        status = app["status"] if app else None

        if status in {"pending", "accepted", "rejected"}:
            status_text = {
                "pending": "🤍 Твоя заявка сейчас на рассмотрении.",
                "accepted": "🤍 Твоя заявка уже одобрена.",
                "rejected": "🤍 Мы уже отвечали по твоей заявке."
            }.get(status, "🤍 Твоя заявка уже есть в системе.")
            await edit_or_send(
                call,
                f"{status_text}\n\n"
                "Если хочешь заполнить новую — подтверди, пожалуйста:",
                reply_markup=reapply_keyboard()
            )
            return

        if app and is_rate_limited(app.get("last_apply_at")):
            await edit_or_send(
                call,
                "🤍 Спасибо! Сейчас уже есть недавняя заявка.\n\n"
                "Новую можно отправить немного позже ✨",
                reply_markup=main_menu()
            )
            return

        current = await state.get_state()
        last_state = app.get("last_state") if app else None
        if (current and current in FORM_PROGRESS_STATES) or (last_state in FORM_PROGRESS_STATES):
            await call.message.answer(
                "🤍 Похоже, анкета уже начата.\n\n"
                "Продолжим с того места, где остановились?",
                reply_markup=continue_form_keyboard()
            )
            await call.answer()
            return

        await start_application(call.message, state)
        await call.answer()
    except Exception:
        logger.exception("Ошибка в apply")

@dp.callback_query(F.data == "apply_restart")
async def apply_restart(call: CallbackQuery, state: FSMContext):
    app = get_application(call.from_user.id)
    if app and is_rate_limited(app.get("last_apply_at")):
        await edit_or_send(
            call,
            "🤍 Спасибо! Сейчас уже есть недавняя заявка.\n\n"
            "Новую можно отправить немного позже ✨",
            reply_markup=main_menu()
        )
        return

    await state.clear()
    await start_application(call.message, state)
    await call.answer()

@dp.callback_query(F.data == "form_continue")
async def form_continue(call: CallbackQuery, state: FSMContext):
    current = await state.get_state()
    if not current:
        app = get_application(call.from_user.id)
        last_state = app.get("last_state") if app else None
        if last_state and last_state in FORM_PROGRESS_STATES:
            await state.set_state(last_state)
            await restore_form_data(state, call.from_user.id)
            current = last_state
        else:
            await start_application(call.message, state)
            await call.answer()
            return

    if current == ApplicationStates.preview.state:
        data = await state.get_data()
        if not REQUIRED_PREVIEW_FIELDS.issubset(data):
            await start_application(call.message, state)
            await call.answer()
            return
        await show_preview(call.message, state)
        await call.answer()
        return
    if current == ApplicationStates.edit_value.state:
        data = await state.get_data()
        field = data.get("edit_field")
        if not field:
            await show_preview(call.message, state)
            await call.answer()
            return
        title = FIELD_TITLES.get(field, "Поле")
        await call.message.answer(
            f"✏️ <b>Редактирование поля:</b>\n\n"
            f"{title}\n\n"
            f"👉 Введи новое значение:"
        )
        await call.answer()
        return

    for st in FORM_ORDER:
        if st.state == current:
            await call.message.answer(
                format_question(st, FORM_QUESTIONS[st]),
                reply_markup=form_keyboard()
            )
            await call.answer()
            return

    await start_application(call.message, state)
    await call.answer()

@dp.callback_query(F.data == "form_restart")
async def form_restart(call: CallbackQuery, state: FSMContext):
    await start_application(call.message, state)
    await call.answer()

# ================= FORM STEPS =================

@dp.message(StateFilter(ApplicationStates.name), F.text)
async def step_name(m: Message, state: FSMContext):
    name = m.text.strip()
    if len(name) < 2:
        await m.answer(
            "🤍 Имя должно быть чуть длиннее. Напиши, пожалуйста, полностью:",
            reply_markup=form_keyboard()
        )
        return
    await update_form_field(state, m.from_user.id, name=name)
    await send_next_question(
        m,
        state,
        ApplicationStates.city,
        FORM_QUESTIONS[ApplicationStates.city]
    )

@dp.message(StateFilter(ApplicationStates.city), F.text)
async def step_city(m: Message, state: FSMContext):
    city = m.text.strip()
    if len(city) < 2:
        await m.answer(
            "🤍 Подскажи город и страну проживания ещё раз:",
            reply_markup=form_keyboard()
        )
        return
    await update_form_field(state, m.from_user.id, city=city)
    await send_next_question(
        m,
        state,
        ApplicationStates.phone,
        FORM_QUESTIONS[ApplicationStates.phone]
    )

@dp.message(StateFilter(ApplicationStates.phone), F.text)
async def step_phone(m: Message, state: FSMContext):
    phone = m.text.strip()
    if not is_valid_phone(phone):
        await m.answer(
            "🤍 Кажется, номер введён некорректно. Пример: +7 900 000 00 00",
            reply_markup=form_keyboard()
        )
        return
    normalized = normalize_phone(phone) or phone
    note = None
    if normalized != phone:
        note = f"🤍 Сохранила номер как: {normalized}"
    await update_form_field(state, m.from_user.id, phone=normalized)
    await send_next_question(
        m,
        state,
        ApplicationStates.age,
        FORM_QUESTIONS[ApplicationStates.age],
        note=note
    )

@dp.message(StateFilter(ApplicationStates.age), F.text)
async def step_age(m: Message, state: FSMContext):
    birthdate = m.text.strip()
    if not is_valid_birthdate(birthdate):
        await m.answer(
            "🤍 Напиши дату рождения в формате 01.01.2000:",
            reply_markup=form_keyboard()
        )
        return
    normalized = normalize_birthdate(birthdate) or birthdate
    note = None
    if normalized != birthdate:
        note = f"🤍 Сохранила дату как: {normalized}"
    await update_form_field(
        state,
        m.from_user.id,
        age=normalized
    )
    await send_next_question(
        m,
        state,
        ApplicationStates.living,
        FORM_QUESTIONS[ApplicationStates.living],
        note=note
    )

@dp.message(StateFilter(ApplicationStates.living), F.text)
async def step_living(m: Message, state: FSMContext):
    living_raw = m.text.strip()
    normalized = normalize_yes_no(living_raw)
    if not normalized:
        await m.answer(
            "🤍 Ответь, пожалуйста, «да» или «нет»:",
            reply_markup=form_keyboard()
        )
        return
    note = None
    if normalized != living_raw:
        note = f"🤍 Сохранила ответ как: {normalized}"
    await update_form_field(state, m.from_user.id, living=normalized)
    await send_next_question(
        m,
        state,
        ApplicationStates.devices,
        FORM_QUESTIONS[ApplicationStates.devices],
        note=note
    )

@dp.message(StateFilter(ApplicationStates.devices), F.text)
async def step_devices(m: Message, state: FSMContext):
    devices = m.text.strip()
    if len(devices) < 2:
        await m.answer(
            "🤍 Уточни, пожалуйста, какие устройства есть:",
            reply_markup=form_keyboard()
        )
        return
    await update_form_field(state, m.from_user.id, devices=devices)
    await send_next_question(
        m,
        state,
        ApplicationStates.device_model,
        FORM_QUESTIONS[ApplicationStates.device_model]
    )

@dp.message(StateFilter(ApplicationStates.device_model), F.text)
async def step_device_model(m: Message, state: FSMContext):
    device_model = m.text.strip()
    if len(device_model) < 2:
        await m.answer(
            "🤍 Напиши модель устройства, пожалуйста:",
            reply_markup=form_keyboard()
        )
        return
    await update_form_field(state, m.from_user.id, device_model=device_model)
    await send_next_question(
        m,
        state,
        ApplicationStates.work_time,
        FORM_QUESTIONS[ApplicationStates.work_time]
    )

@dp.message(StateFilter(ApplicationStates.work_time), F.text)
async def step_work_time(m: Message, state: FSMContext):
    work_time = m.text.strip()
    if not has_any_digit(work_time):
        await m.answer(
            "🤍 Напиши, пожалуйста, количество часов цифрами (например: 6):",
            reply_markup=form_keyboard()
        )
        return
    await update_form_field(state, m.from_user.id, work_time=work_time)
    await send_next_question(
        m,
        state,
        ApplicationStates.headphones,
        FORM_QUESTIONS[ApplicationStates.headphones]
    )

@dp.message(StateFilter(ApplicationStates.headphones), F.text)
async def step_headphones(m: Message, state: FSMContext):
    headphones = m.text.strip()
    if len(headphones) < 2:
        await m.answer(
            "🤍 Подскажи, пожалуйста, есть ли наушники с микрофоном:",
            reply_markup=form_keyboard()
        )
        return
    await update_form_field(state, m.from_user.id, headphones=headphones)
    await send_next_question(
        m,
        state,
        ApplicationStates.telegram,
        FORM_QUESTIONS[ApplicationStates.telegram]
    )

@dp.message(StateFilter(ApplicationStates.telegram), F.text)
async def step_tg(m: Message, state: FSMContext):
    normalized = normalize_telegram(m.text)
    if not normalized:
        await m.answer(
            "🤍 Укажи, пожалуйста, Telegram в формате @username:",
            reply_markup=form_keyboard()
        )
        return
    note = None
    if normalized != m.text.strip():
        note = f"🤍 Сохранила Telegram как: {normalized}"
    await update_form_field(state, m.from_user.id, telegram=normalized)
    await send_next_question(
        m,
        state,
        ApplicationStates.experience,
        FORM_QUESTIONS[ApplicationStates.experience],
        note=note
    )

@dp.message(StateFilter(ApplicationStates.experience), F.text)
async def step_exp(m: Message, state: FSMContext):
    experience = m.text.strip()
    if len(experience) < 1:
        await m.answer(
            "🤍 Напиши, пожалуйста, есть ли опыт:",
            reply_markup=form_keyboard()
        )
        return
    await update_form_field(state, m.from_user.id, experience=experience)
    await send_next_question(
        m,
        state,
        ApplicationStates.photo_face,
        FORM_QUESTIONS[ApplicationStates.photo_face]
    )

@dp.message(StateFilter(ApplicationStates.photo_face), F.photo)
async def step_face(m: Message, state: FSMContext):
    await update_form_field(state, m.from_user.id, photo_face=m.photo[-1].file_id)
    await send_next_question(
        m,
        state,
        ApplicationStates.photo_full,
        FORM_QUESTIONS[ApplicationStates.photo_full]
    )

@dp.message(StateFilter(ApplicationStates.photo_full), F.photo)
async def step_full(m: Message, state: FSMContext):
    await update_form_field(state, m.from_user.id, photo_full=m.photo[-1].file_id)
    await m.answer(build_ack())
    await show_preview(m, state)

@dp.message(StateFilter(ApplicationStates.photo_face), ~F.photo)
async def reject_non_photo_face(m: Message):
    await m.answer(
        "🤍 Здесь нужно отправить <b>ФОТО АНФАС</b>.\n\n"
        "📷 Пришли фотографию, пожалуйста",
        reply_markup=form_keyboard()
    )

@dp.message(StateFilter(ApplicationStates.photo_full), ~F.photo)
async def reject_non_photo_full(m: Message):
    await m.answer(
        "🤍 Здесь нужно отправить <b>ФОТО В ПОЛНЫЙ РОСТ</b>.\n\n"
        "📷 Пришли фотографию, пожалуйста",
        reply_markup=form_keyboard()
    )
# ================= FORM CONSTANTS =================

FORM_ORDER = [
    ApplicationStates.name,
    ApplicationStates.city,
    ApplicationStates.phone,
    ApplicationStates.age,
    ApplicationStates.living,
    ApplicationStates.devices,
    ApplicationStates.device_model,
    ApplicationStates.work_time,
    ApplicationStates.headphones,
    ApplicationStates.telegram,
    ApplicationStates.experience,
    ApplicationStates.photo_face,
    ApplicationStates.photo_full,
]

TOTAL_STEPS = len(FORM_ORDER)
FORM_STEP_INDEX = {state: idx + 1 for idx, state in enumerate(FORM_ORDER)}

FORM_PROGRESS_STATES = {s.state for s in FORM_ORDER} | {
    ApplicationStates.preview.state,
    ApplicationStates.edit_value.state,
}

def format_question(state: ApplicationStates, question: str) -> str:
    step = FORM_STEP_INDEX.get(state)
    if not step:
        return question
    return f"Шаг {step}/{TOTAL_STEPS}\n\n{question}"

# ================= FORM VALIDATION =================

TEXT_STATES = (
    ApplicationStates.name,
    ApplicationStates.city,
    ApplicationStates.phone,
    ApplicationStates.age,
    ApplicationStates.living,
    ApplicationStates.devices,
    ApplicationStates.device_model,
    ApplicationStates.work_time,
    ApplicationStates.headphones,
    ApplicationStates.telegram,
    ApplicationStates.experience,
    ApplicationStates.edit_value,
    ApplicationStates.admin_reject_reason,
)

@dp.message(StateFilter(*TEXT_STATES), ~F.text)
async def reject_non_text(m: Message):
    await m.answer(
        "🤍 Пожалуйста, отправь ответ текстом.",
        reply_markup=form_keyboard()
    )

@dp.callback_query(F.data == "form_back")
async def form_back(call: CallbackQuery, state: FSMContext):
    current = await state.get_state()

    if current not in FORM_ORDER:
        await call.answer()
        return

    idx = FORM_ORDER.index(current)

    if idx == 0:
        await call.answer("🤍 Это первый пункт анкеты")
        return

    prev_state = FORM_ORDER[idx - 1]
    await state.set_state(prev_state)
    set_last_state(call.from_user.id, prev_state.state)

    data = await state.get_data()
    field_key = STATE_TO_FIELD.get(prev_state)
    prev_value = data.get(field_key) if field_key else None

    question = format_question(prev_state, FORM_QUESTIONS[prev_state])
    if prev_state in {ApplicationStates.photo_face, ApplicationStates.photo_full}:
        question += "\n\nЕсли нужно заменить — пришли новое фото."
    elif prev_value:
        question += f"\n\nТвой прошлый ответ: {prev_value}\nЕсли нужно — отправь новый."

    await call.message.answer(
        question,
        reply_markup=form_keyboard()
    )
    await call.answer()
# ================= MAIN MENU HANDLERS =================

@dp.callback_query(F.data == "about_work")
async def about_work(call: CallbackQuery):
    await edit_or_send(
        call,
        "🌷 <b>О работе в нашем проекте</b>\n\n"
        "Мы предлагаем современную онлайн-работу в формате стриминга.\n"
        "Это не офис и не «работа по расписанию», а гибкий формат, который\n"
        "можно легко встроить в свою жизнь 🤍\n\n"
        "<b>Как всё проходит:</b>\n"
        "• ты работаешь из любой точки мира\n"
        "• находишься в комфортной для себя обстановке\n"
        "• общаешься с аудиторией в дружелюбном формате\n"
        "• создаёшь свой образ и стиль общения\n\n"
        "<b>График:</b>\n"
        "Он гибкий и подбирается индивидуально.\n"
        "Обычно это от 6 часов в день, но всё обсуждается — мы за комфорт,\n"
        "а не за выгорание.\n\n"
        "<b>Стажировка:</b>\n"
        "Перед стартом есть короткий промо-период (2–5 дней).\n"
        "В это время ты:\n"
        "• знакомишься с форматом\n"
        "• получаешь поддержку и подсказки\n"
        "• и — важно — <b>каждый день оплачивается</b>\n\n"
        "Мы сопровождаем тебя на каждом этапе и всегда на связи ✨",
        reply_markup=about_menu()
    )


@dp.callback_query(F.data == "about_platforms")
async def about_platforms(call: CallbackQuery):
    await edit_or_send(
        call,
        "💻 <b>Площадки и формат работы</b>\n\n"
        "Работа проходит на современных онлайн-платформах,\n"
        "где важно качество картинки и стабильная связь.\n\n"
        "Мы заранее уточняем технику — не потому что «строго»,\n"
        "а чтобы ты чувствовала себя уверенно и комфортно в процессе 🌸\n\n"
        "<b>Что обычно подходит:</b>\n"
        "• современные модели смартфонов\n"
        "• либо ноутбук / ПК с камерой\n\n"
        "Если вдруг текущее устройство не идеально подходит —\n"
        "это не проблема.\n"
        "Мы просто подскажем, какие варианты лучше,\n"
        "или ты сможешь вернуться к нам позже 🤍\n\n"
        "Наша цель — чтобы работа приносила удовольствие,\n"
        "а не стресс из-за техники.",
        reply_markup=about_menu()
    )


@dp.callback_query(F.data == "about_income")
async def about_income(call: CallbackQuery):
    await edit_or_send(
        call,
        "💰 <b>Доход и выплаты</b>\n\n"
        "На старте большинство моделей выходят\n"
        "на доход <b>$800–1000 в месяц</b>.\n\n"
        "<b>Что влияет на доход:</b>\n"
        "• твоя активность\n"
        "• умение общаться\n"
        "• регулярность выходов\n"
        "• следование рекомендациям менеджера\n\n"
        "<b>Выплаты:</b>\n"
        "• происходят еженедельно\n"
        "• без задержек\n"
        "• в удобном формате\n\n"
        "<b>Валюта:</b>\n"
        "USD или USDT\n\n"
        "<b>Способ получения:</b>\n"
        "• для РФ — банковская карта\n"
        "• для других стран — криптокошелёк\n\n"
        "Это стабильный формат работы,\n"
        "а не разовые подработки ✨",
        reply_markup=about_menu()
    )

@dp.callback_query(F.data == "portfolio")
async def portfolio(call: CallbackQuery):
    try:
        await edit_or_send(
            call,
            "📁 <b>Портфолио моделей</b>\n\n"
            "Здесь ты можешь посмотреть примеры работы, отзывы и реальные кейсы.",
            reply_markup=portfolio_menu()
        )
    except Exception:
        logger.exception("Ошибка в portfolio")

@dp.callback_query(F.data == "about")
async def about(call: CallbackQuery):
    try:
        await edit_or_send(
            call,
            "ℹ️ <b>Подробнее о работе</b>\n\n"
            "• Удалённый формат\n"
            "• Без 18+\n"
            "• Поддержка 24/7\n"
            "• Обучение с нуля",
            reply_markup=about_menu()
        )
    except Exception:
        logger.exception("Ошибка в about")

@dp.callback_query(F.data == "contact")
async def contact(call: CallbackQuery):
    try:
        await edit_or_send(
            call,
            f"💬 <b>Связь с администратором</b>\n\n"
            f"https://t.me/{ADMIN_USERNAME}",
            reply_markup=main_menu()
        )
    except Exception:
        logger.exception("Ошибка в contact")

@dp.callback_query(F.data == "back")
async def back_handler(call: CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        await start(call.message, state)
        await call.answer()
    except Exception:
        logger.exception("Ошибка в back_handler")

# ================= PREVIEW =================

@dp.callback_query(F.data == "preview_edit")
async def preview_edit(call: CallbackQuery):
    await edit_or_send(
        call,
        "✏️ <b>Что хочешь исправить?</b>\n\nВыбери пункт:",
        reply_markup=preview_edit_menu()
    )

@dp.callback_query(F.data.startswith("edit:"))
async def edit_field(call: CallbackQuery, state: FSMContext):
    field = call.data.split(":")[1]

    await state.update_data(edit_field=field)
    await state.set_state(ApplicationStates.edit_value)
    set_last_state(call.from_user.id, ApplicationStates.edit_value.state)

    title = FIELD_TITLES.get(field, "Поле")

    await call.message.answer(
        f"✏️ <b>Редактирование поля:</b>\n\n"
        f"{title}\n\n"
        f"👉 Введи новое значение:"
    )
    await call.answer()

@dp.message(StateFilter(ApplicationStates.edit_value), F.text)
async def save_edited_value(m: Message, state: FSMContext):
    value = m.text.strip()

    # 🚫 запрет пустых значений
    if not value:
        await m.answer("🤍 Значение не может быть пустым. Введи ещё раз:")
        return

    data = await state.get_data()
    field = data.get("edit_field")

    if not field:
        await m.answer("🤍 Похоже, что-то пошло не так. Попробуй ещё раз.")
        await state.clear()
        return

    # базовая валидация при редактировании
    if field == "name" and len(value) < 2:
        await m.answer("🤍 Имя должно быть чуть длиннее. Напиши ещё раз:")
        return
    if field == "city" and len(value) < 2:
        await m.answer("🤍 Подскажи город и страну ещё раз:")
        return
    if field == "phone" and not is_valid_phone(value):
        await m.answer("🤍 Номер выглядит некорректно. Пример: +7 900 000 00 00")
        return
    if field == "phone":
        value = normalize_phone(value) or value
    if field == "age" and not is_valid_birthdate(value):
        await m.answer("🤍 Напиши дату рождения в формате 01.01.2000:")
        return
    if field == "age":
        value = normalize_birthdate(value) or value
    if field == "living":
        normalized = normalize_yes_no(value)
        if not normalized:
            await m.answer("🤍 Ответь, пожалуйста, «да» или «нет»:")
            return
        value = normalized
    if field == "devices" and len(value) < 2:
        await m.answer("🤍 Уточни, пожалуйста, какие устройства есть:")
        return
    if field == "device_model" and len(value) < 2:
        await m.answer("🤍 Напиши модель устройства, пожалуйста:")
        return
    if field == "work_time" and not has_any_digit(value):
        await m.answer("🤍 Напиши, пожалуйста, количество часов цифрами:")
        return
    if field == "headphones" and len(value) < 2:
        await m.answer("🤍 Подскажи, пожалуйста, есть ли наушники с микрофоном:")
        return
    if field == "telegram":
        normalized = normalize_telegram(value)
        if not normalized:
            await m.answer("🤍 Укажи, пожалуйста, Telegram в формате @username:")
            return
        value = normalized
    if field == "experience" and len(value) < 1:
        await m.answer("🤍 Напиши, пожалуйста, есть ли опыт:")
        return

    # сохраняем новое значение
    await update_form_field(state, m.from_user.id, **{field: value})

    # возвращаем предпросмотр
    await show_preview(m, state)


@dp.callback_query(F.data == "preview_edit_photo")
async def preview_edit_photo(call: CallbackQuery):
    await edit_or_send(
        call,
        "📷 <b>Какое фото хочешь заменить?</b>",
        reply_markup=preview_edit_photo_menu()
    )

@dp.callback_query(F.data.startswith("edit_photo:"))
async def edit_photo(call: CallbackQuery, state: FSMContext):
    photo_type = call.data.split(":")[1]

    await state.update_data(edit_photo=photo_type)

    text = (
        "📷 <b>Замена фото</b>\n\n"
        "Отправь новое фото:\n"
        "• чёткое\n"
        "• без фильтров\n"
        "• хорошее освещение\n\n"
        "⬅️ Если передумала — нажми «Отмена»"
    )

    await call.message.answer(
        text,
        reply_markup=cancel_keyboard()
    )
    await call.answer()

@dp.message(F.photo)
async def receive_edited_photo(m: Message, state: FSMContext):
    data = await state.get_data()

    if "edit_photo" not in data:
        return

    photo_type = data["edit_photo"]

    if photo_type == "face":
        await update_form_field(state, m.from_user.id, photo_face=m.photo[-1].file_id)
    elif photo_type == "full":
        await update_form_field(state, m.from_user.id, photo_full=m.photo[-1].file_id)

    await state.update_data(edit_photo=None)

    await show_preview(m, state)

@dp.message(StateFilter(ApplicationStates.preview), ~F.photo)
async def reject_text_when_waiting_photo(m: Message, state: FSMContext):
    data = await state.get_data()

    if data.get("edit_photo"):
        await m.answer(
            "🤍 Сейчас нужно отправить <b>ФОТО</b>, а не текст.\n\n"
            "📷 Пришли фотографию или нажми «Отмена»."
        )

@dp.callback_query(F.data == "preview_back")
async def preview_back(call: CallbackQuery, state: FSMContext):
    await show_preview(call.message, state)
    await call.answer()

async def show_preview(m: Message, state: FSMContext):
    data = await state.get_data()
    loading_msg = await m.answer(LOADING_TEXT)
    for text in (
        "✨ Проверяю детали...\nЕщё секунду 🌸",
        "🌷 Оформляю карточку...\nПочти готово 🤍",
    ):
        await asyncio.sleep(random.uniform(0.4, 0.8))
        try:
            await loading_msg.edit_text(text)
        except Exception:
            break
    await asyncio.sleep(random.uniform(0.3, 0.6))
    try:
        await loading_msg.delete()
    except Exception:
        pass
    status = get_status(m.from_user.id) or "new"
    status_label = STATUS_LABELS.get(status, "📝 Черновик")
    text = (
        "🌸 <b>АНКЕТА КАНДИДАТА</b> 🌸\n"
        "<i>Проверь, всё ли верно 🤍</i>\n\n"
        "🌷 <b>Личные данные</b>\n"
        f"👤 <b>Имя:</b> {data['name']}\n"
        f"🌍 <b>Город и страна:</b> {data['city']}\n"
        f"📅 <b>Дата рождения:</b> {data['age']}\n"
        f"📞 <b>Телефон:</b> {data['phone']}\n"
        f"🏠 <b>Помещение без посторонних:</b> {data['living']}\n\n"
        "💻 <b>Техника</b>\n"
        f"📱 <b>Устройства:</b> {data['devices']}\n"
        f"📲 <b>Модель:</b> {data['device_model']}\n"
        f"🎧 <b>Наушники:</b> {data['headphones']}\n\n"
        "🕒 <b>График и опыт</b>\n"
        f"⏱ <b>Время работы:</b> {data['work_time']}\n"
        f"💼 <b>Опыт:</b> {data['experience']}\n\n"
        "💬 <b>Контакт</b>\n"
        f"💬 <b>Telegram:</b> {data['telegram']}\n\n"
        "────────\n"
        f"🧾 <b>Статус:</b> {status_label}\n\n"
        "<i>Если нужно, используй кнопки ниже ✨</i>"
    )
    await state.set_state(ApplicationStates.preview)
    set_last_state(m.from_user.id, ApplicationStates.preview.state)
    await m.answer(text, reply_markup=preview_keyboard())

# ================= CONFIRM SEND =================

@dp.callback_query(F.data == "preview_confirm")
async def preview_confirm(call: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        user = call.from_user
        app = get_application(user.id)

        if app and is_rate_limited(app.get("last_apply_at")):
            await call.message.answer(
                "🤍 Похоже, недавно уже была отправлена заявка.\n\n"
                "Немного позже можно будет отправить новую ✨"
            )
            await call.answer()
            return
        if not REQUIRED_PREVIEW_FIELDS.issubset(data):
            await call.message.answer(
                "🤍 Кажется, анкета заполнена не полностью.\n\n"
                "Давай продолжим заполнение ✨"
            )
            await start_application(call.message, state)
            await call.answer()
            return

        await gentle_typing(call.message.chat.id)

        set_status(user.id, "pending")
        set_last_apply_at(user.id)
        if append_application_row:
            try:
                append_application_row(data, user.id, "pending")
            except Exception:
                logger.exception("Ошибка записи в Excel")
        await state.clear()
        try:
            await notify_admin_new_application()
        except Exception:
            logger.exception("Ошибка уведомления админов о новой заявке")
        try:
            await ensure_admin_menu_posted()
        except Exception:
            logger.exception("Ошибка обновления админ-меню после заявки")
        try:
            caption = build_menu_caption_with_status(
                "pending",
                MENU_CAPTION,
                intro="🤍 Спасибо! Анкета отправлена администратору ✨"
            )
            await send_or_edit_user_menu(call.from_user.id, caption)
        except Exception:
            logger.exception("Ошибка отправки меню после заявки")
        await call.answer()
    except Exception:
        logger.exception("Ошибка в preview_confirm")

@dp.callback_query(F.data == "edit_cancel")
async def edit_cancel(call: CallbackQuery, state: FSMContext):
    await state.update_data(edit_field=None, edit_photo=None)
    await show_preview(call.message, state)
    await call.answer("Отменено")

# ================= ADMIN =================

@dp.callback_query(F.data.startswith("admin_accept:"))
async def admin_accept(call: CallbackQuery):
    try:
        if call.message.chat.id != ADMIN_GROUP_ID:
            await call.answer("Недостаточно прав", show_alert=True)
            return
        parts = call.data.split(":")
        uid = int(parts[1])
        view_mode = len(parts) > 2 and parts[2] == "view"
        try:
            caption = build_menu_caption_with_status(
                "accepted",
                ACCEPT_CAPTION,
                tail="🤍 Ожидайте, скоро админ напишет вам для записи на собеседование ✨"
            )
            await send_or_edit_user_menu(uid, caption)
        except Exception:
            logger.exception("Ошибка отправки меню после принятия")
        set_status(uid, "accepted")
        if update_application_status:
            try:
                update_application_status(uid, "accepted")
            except Exception:
                logger.exception("Ошибка обновления статуса в Excel")
        await update_admin_summary_message(uid, "accepted")
        try:
            await post_admin_menu()
        except Exception:
            logger.exception("Ошибка возврата в админ-меню")
        await call.answer("Принято")
    except Exception:
        logger.exception("Ошибка в admin_accept")

@dp.callback_query(F.data.startswith("admin_reject:"))
async def admin_reject(call: CallbackQuery, state: FSMContext):
    try:
        if call.message.chat.id != ADMIN_GROUP_ID:
            await call.answer("Недостаточно прав", show_alert=True)
            return
        parts = call.data.split(":")
        uid = int(parts[1])
        view_mode = len(parts) > 2 and parts[2] == "view"
        await state.set_state(ApplicationStates.admin_reject_reason)
        await state.update_data(reject_uid=uid, reject_view=view_mode)
        await call.message.answer(
            "✍️ Укажи причину отказа:\n\n"
            "Можно выбрать готовый вариант или написать свой текст."
        )
        await call.message.answer(
            "Выбери шаблон отказа:",
            reply_markup=reject_templates_keyboard()
        )
        try:
            await call.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await call.answer()
    except Exception:
        logger.exception("Ошибка в admin_reject")

@dp.callback_query(F.data.startswith("reject_tpl:"))
async def reject_template(call: CallbackQuery, state: FSMContext):
    try:
        if call.message.chat.id != ADMIN_GROUP_ID:
            await call.answer("Недостаточно прав", show_alert=True)
            return
        tpl_code = call.data.split(":", 1)[1]
        data = await state.get_data()
        uid = data.get("reject_uid")
        if not uid:
            await call.answer("🤍 Не вижу кандидата")
            return

        templates = {
            "1": "Сейчас, к сожалению, мы не можем принять заявку.",
            "2": "Сейчас условия не совпали, но спасибо за интерес.",
            "3": "Мы вернёмся к твоей анкете чуть позже. Спасибо за понимание.",
        }

        if tpl_code == "custom":
            await call.message.answer("✍️ Напиши свою причину отказа:")
            await call.answer()
            return

        reason = templates.get(tpl_code)
        if not reason:
            await call.answer("🤍 Шаблон не найден")
            return

        try:
            intro = (
                "🤍 Спасибо за твою заявку!\n\n"
                "К сожалению, сейчас мы не можем принять её.\n\n"
                f"Причина:\n{reason}\n\n"
                "Если появится возможность — мы обязательно напишем ✨"
            )
            caption = build_menu_caption_with_status(
                "rejected",
                MENU_CAPTION,
                intro=intro
            )
            await send_or_edit_user_menu(uid, caption)
        except Exception:
            logger.exception("Ошибка отправки меню после отказа")
        set_status(uid, "rejected")
        if update_application_status:
            try:
                update_application_status(uid, "rejected")
            except Exception:
                logger.exception("Ошибка обновления статуса в Excel")
        await update_admin_summary_message(uid, "rejected")
        try:
            await post_admin_menu()
        except Exception:
            logger.exception("Ошибка возврата в админ-меню")
        await state.clear()
        await call.answer()
    except Exception:
        logger.exception("Ошибка в reject_template")

@dp.message(StateFilter(ApplicationStates.admin_reject_reason), F.text)
async def reject_reason(m: Message, state: FSMContext):
    try:
        data = await state.get_data()
        uid = data["reject_uid"]

        try:
            intro = (
                "🤍 Спасибо за твою заявку!\n\n"
                "К сожалению, сейчас мы не можем принять её.\n\n"
                f"Причина:\n{m.text}\n\n"
                "Если появится возможность — мы обязательно напишем ✨"
            )
            caption = build_menu_caption_with_status(
                "rejected",
                MENU_CAPTION,
                intro=intro
            )
            await send_or_edit_user_menu(uid, caption)
        except Exception:
            logger.exception("Ошибка отправки меню после отказа")
        set_status(uid, "rejected")
        if update_application_status:
            try:
                update_application_status(uid, "rejected")
            except Exception:
                logger.exception("Ошибка обновления статуса в Excel")
        await update_admin_summary_message(uid, "rejected")
        try:
            await post_admin_menu()
        except Exception:
            logger.exception("Ошибка возврата в админ-меню")
        await state.clear()
    except Exception:
        logger.exception("Ошибка в reject_reason")

@dp.callback_query(F.data.startswith("admin_status:"))
async def admin_status(call: CallbackQuery):
    try:
        _, uid, status = call.data.split(":", 2)
        status_label = STATUS_LABELS.get(status, status)
        await call.answer(f"Статус: {status_label}", show_alert=False)
    except Exception:
        await call.answer("Статус обновлён", show_alert=False)

@dp.callback_query(F.data.startswith("admin_photos:"))
async def admin_photos(call: CallbackQuery):
    try:
        uid = int(call.data.split(":", 1)[1])
        data = get_form_data(uid) or {}
        face = data.get("photo_face")
        full = data.get("photo_full")
        if not face or not full:
            await call.answer("Фото не найдено", show_alert=False)
            return
        await call.message.answer_media_group([
            InputMediaPhoto(media=face),
            InputMediaPhoto(media=full),
        ])
        await call.answer()
    except Exception:
        logger.exception("Ошибка отправки фото админу")
        await call.answer("Не удалось отправить фото", show_alert=False)

@dp.message(F.text == "/admin", F.chat.id == ADMIN_GROUP_ID)
async def admin_menu(message: Message):
    await ensure_admin_menu_posted()

@dp.callback_query(F.data.startswith("admin_menu:"))
async def admin_menu_action(call: CallbackQuery):
    if call.message.chat.id != ADMIN_GROUP_ID:
        await call.answer("Недостаточно прав", show_alert=True)
        return
    action = call.data.split(":", 1)[1]
    if action in {"pending", "accepted", "rejected", "all"}:
        await send_admin_list(call, action, 0)
        return
    if action == "stats":
        await update_admin_menu_message(
            build_admin_stats_text(),
            admin_menu_keyboard(get_status_counts())
        )
        await call.answer()
        return
    if action == "excel":
        if not append_application_row:
            await update_admin_menu_message(
                "🤍 Экспорт в Excel недоступен. Установи openpyxl.",
                admin_menu_keyboard(get_status_counts())
            )
            await call.answer()
            return
        file_path = Path("applications.xlsx")
        if not file_path.exists():
            await update_admin_menu_message(
                "🤍 Файл Excel ещё не создан. Отправь хотя бы одну заявку ✨",
                admin_menu_keyboard(get_status_counts())
            )
            await call.answer()
            return
        await call.message.answer_document(FSInputFile(str(file_path)))
        await call.answer()
        return
    if action == "archive":
        try:
            archived = await archive_admin_messages_once()
            if archived:
                await update_admin_menu_message(
                    f"🧹 Архивировано: {archived}",
                    admin_menu_keyboard(get_status_counts())
                )
            else:
                await update_admin_menu_message(
                    "🤍 Пока нет заявок для архивации ✨",
                    admin_menu_keyboard(get_status_counts())
                )
        except Exception:
            logger.exception("Ошибка ручной архивации")
            await update_admin_menu_message(
                "⚠️ Не удалось архивировать сейчас.",
                admin_menu_keyboard(get_status_counts())
            )
        await call.answer()
        return
    if action == "reset":
        await update_admin_menu_message(
            "⚠️ Ты уверена, что хочешь полностью обнулить базу и статистику?",
            confirm_reset_db_keyboard()
        )
        await call.answer()
        return
    if action == "refresh":
        await post_admin_menu()
        await call.answer()
        return
    await call.answer("Неизвестная команда", show_alert=False)

@dp.callback_query(F.data.startswith("admin_list:"))
async def admin_list_pagination(call: CallbackQuery):
    try:
        _, filter_key, offset_raw = call.data.split(":", 2)
        offset = int(offset_raw)
    except Exception:
        await call.answer("Ошибка пагинации", show_alert=False)
        return
    await send_admin_list(call, filter_key, offset)

@dp.message(F.text == "/reset_db", F.chat.id == ADMIN_GROUP_ID)
async def admin_reset_db(message: Message):
    await update_admin_menu_message(
        "⚠️ Ты уверена, что хочешь полностью обнулить базу и статистику?",
        confirm_reset_db_keyboard()
    )

@dp.callback_query(F.data == "admin_reset_db:confirm")
async def admin_reset_db_confirm(call: CallbackQuery):
    try:
        reset_all_data()
        file_path = Path("applications.xlsx")
        if file_path.exists():
            file_path.unlink()
        await update_admin_menu_message(
            "✅ База и статистика полностью обнулены.",
            admin_menu_keyboard(get_status_counts())
        )
    except Exception:
        logger.exception("Ошибка сброса базы")
        await update_admin_menu_message(
            "⚠️ Ошибка при сбросе базы.",
            admin_menu_keyboard(get_status_counts())
        )
    await call.answer()

@dp.callback_query(F.data == "admin_reset_db:cancel")
async def admin_reset_db_cancel(call: CallbackQuery):
    await post_admin_menu()
    await call.answer("Отменено")

        
@dp.callback_query(F.data == "portfolio_reviews")
async def portfolio_reviews(call: CallbackQuery):
    await call.message.answer_media_group([
        InputMediaPhoto(media=FSInputFile("media/review1.jpg")),
        InputMediaPhoto(media=FSInputFile("media/review2.jpg")),
    ])
    await call.answer()

@dp.callback_query(F.data == "portfolio_videos")
async def portfolio_streams(call: CallbackQuery):
    now = datetime.now(timezone.utc)
    last = PORTFOLIO_VIDEO_LAST.get(call.from_user.id)
    if last and (now - last).total_seconds() < PORTFOLIO_COOLDOWN_SECONDS:
        await call.answer("🤍 Видео уже отправлены, посмотри, пожалуйста ✨")
        return
    PORTFOLIO_VIDEO_LAST[call.from_user.id] = now
    await call.message.answer_media_group([
        InputMediaVideo(media=FSInputFile("media/stream1.MP4")),
        InputMediaVideo(media=FSInputFile("media/stream2.MP4")),
    ])
    await call.answer()

@dp.callback_query(F.data == "portfolio_pdf")
async def portfolio_pdf(call: CallbackQuery):
    await call.message.answer_document(
        FSInputFile("media/portfolio.pdf")
    )
    await call.answer()

# ================= ADMIN STATS =================

@dp.message(F.text == "/stats", F.chat.id == ADMIN_GROUP_ID)
async def admin_stats(message: Message):
    await message.answer(build_admin_stats_text())

@dp.message(F.text == "/excel", F.chat.id == ADMIN_GROUP_ID)
async def admin_excel(message: Message):
    if not append_application_row:
        await message.answer("🤍 Экспорт в Excel недоступен. Установи openpyxl.")
        return
    file_path = Path("applications.xlsx")
    if not file_path.exists():
        await message.answer("🤍 Файл Excel ещё не создан. Отправь хотя бы одну заявку ✨")
        return
    await message.answer_document(FSInputFile(str(file_path)))
# ================= RUN =================

async def main():
    logger.info("БОТ ЗАПУЩЕН")
    try:
        cleanup_old_form_data()
    except Exception:
        logger.exception("Ошибка очистки старых данных")
    await ensure_admin_menu_posted()
    asyncio.create_task(daily_stats_task())
    asyncio.create_task(archive_admin_messages_task())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
