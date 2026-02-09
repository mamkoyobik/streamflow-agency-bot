import asyncio
import html
import logging
import os
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
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
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
    get_menu_message_id,
    set_flow_message_id,
    get_flow_message_id,
    set_source,
    get_source,
    get_user_language,
    set_user_language,
    has_user_language,
)
try:
    from excel_export import append_application_row, update_application_status, rebuild_excel_from_db
except Exception:
    append_application_row = None
    update_application_status = None
    rebuild_excel_from_db = None
    logging.getLogger(__name__).warning("Excel export недоступен (нет openpyxl?)")
from utils import edit_or_send
from texts import (
    STATUS_LABELS,
    t,
    normalize_lang,
    form_question,
    field_title,
    status_label,
    support_lines,
    LANGUAGE_NAMES,
)
from time_utils import format_submit_time
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
        exc_name = html.escape(type(exception).__name__)
        exc_text = html.escape(str(exception))[:1200]
        await bot.send_message(
            ADMIN_GROUP_ID,
            "⚠️ <b>Ошибка в боте</b>\n\n"
            f"{exc_name}: {exc_text}"
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
            if dt.year < 1900 or dt.date() > datetime.now().date():
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
    if not value:
        return None
    tokens = re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", value)
    if not tokens:
        tokens = [value]
    yes = {"да", "есть", "имеется", "конечно", "ага", "y", "yes", "ok", "ок", "da", "sim", "si", "sí"}
    no = {"нет", "нету", "неа", "no", "n", "nao", "não"}
    for token in tokens:
        t = token.lower()
        if t in yes:
            return "Да"
        if t in no:
            return "Нет"
    return None


async def safe_call_answer(call: CallbackQuery, text: str | None = None, show_alert: bool = False):
    try:
        if text is None:
            await call.answer()
        else:
            await call.answer(text, show_alert=show_alert)
    except Exception:
        pass

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

def build_ack(user_id: int | None = None) -> str:
    lang = lang_for(user_id) if user_id is not None else "ru"
    lines = support_lines(lang)
    return f"{t(lang, 'ack_text')}\n{random.choice(lines)}"

async def gentle_typing(chat_id: int, duration: float | None = None):
    try:
        await bot.send_chat_action(chat_id, ChatAction.TYPING)
    except Exception:
        return
    await asyncio.sleep(duration or random.uniform(0.4, 0.8))

def build_status_line(status: str | None, lang: str = "ru") -> str | None:
    if not status or status == "new":
        return None
    label = status_label(status, lang)
    if not label:
        return None
    return t(lang, "status_line", status=label)

def build_menu_caption_with_status(
    status: str,
    base_caption: str,
    lang: str = "ru",
    intro: str | None = None,
    tail: str | None = None
) -> str:
    parts = []
    if intro:
        parts.append(intro)
    parts.append(base_caption)
    if tail:
        parts.append(tail)
    status_line = build_status_line(status, lang=lang)
    if status_line:
        parts.append(status_line)
    return "\n\n".join(parts)

PORTFOLIO_COOLDOWN_SECONDS = 10
PORTFOLIO_AUTO_DELETE_SECONDS = 120
PORTFOLIO_VIDEO_LAST: dict[int, datetime] = {}
PORTFOLIO_MEDIA_IDS: dict[int, list[int]] = {}
PORTFOLIO_CLEANUP_TASKS: dict[int, asyncio.Task] = {}
ADMIN_TEMP_MESSAGE_IDS: list[int] = []
CAPTION_LIMIT = 1024
DAILY_STATS_HOUR = 10
DAILY_STATS_MINUTE = 0
ADMIN_ARCHIVE_DAYS = 7
ADMIN_ARCHIVE_CHECK_HOURS = 6
ADMIN_MENU_SETTING_KEY = "admin_menu_message_id"
ADMIN_LIST_LIMIT = 1
ADMIN_NOTIFY_SETTING_KEY = "admin_notify_message_id"
ADMIN_VIEW_SETTING_KEY = "admin_view_message_id"
ADMIN_PHOTOS_SETTING_KEY = "admin_photos_message_ids"
FORCE_LANGUAGE_PICK_ON_START = os.getenv("FORCE_LANGUAGE_PICK_ON_START", "1").strip().lower() in {"1", "true", "yes"}

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

async def delete_user_message(m: Message):
    if m.chat.type != "private":
        return
    try:
        await m.delete()
    except Exception:
        pass

async def try_edit_message(message: Message, text: str, reply_markup=None) -> bool:
    try:
        if message.photo or message.caption is not None:
            await message.edit_caption(caption=text, reply_markup=reply_markup)
        else:
            await message.edit_text(text, reply_markup=reply_markup)
        return True
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            return True
    except TelegramForbiddenError:
        logger.warning("Нет прав на редактирование сообщения пользователя")
    except Exception:
        logger.exception("Не удалось отредактировать сообщение пользователя")
    return False

async def send_status_message(message: Message, status: str | None):
    line = build_status_line(status, lang_for(message.from_user.id))
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

def source_label_for_user(user_id: int) -> str:
    source = get_source(user_id)
    if source == "site":
        return "Сайт"
    if source == "bot":
        return "Бот"
    return "Бот"

def contact_url_for_user(user_id: int, data: dict | None) -> str:
    source = get_source(user_id)
    if source == "site":
        raw = (data or {}).get("telegram", "") or ""
        username = raw.lstrip("@").strip()
        if username:
            return f"https://t.me/{username}"
    return f"tg://user?id={user_id}"

def is_site_source(user_id: int) -> bool:
    return get_source(user_id) == "site"


def lang_for(user_id: int) -> str:
    return get_user_language(user_id)


def tr_user(user_id: int, key: str, **kwargs) -> str:
    return t(lang_for(user_id), key, **kwargs)

def submit_time_label_for_user(user_id: int) -> str:
    app = get_application(user_id) or {}
    raw = app.get("last_apply_at") or app.get("created_at")
    if not raw:
        return "—"
    return _safe_text(format_submit_time(str(raw)))

def _safe_text(value) -> str:
    if value is None:
        return "—"
    text = str(value)
    text = re.sub(r"[\u200b-\u200f\u202a-\u202e\u2060\ufeff\ufffd]", "", text)
    text = re.sub(r"[\x00-\x1F\x7F]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return html.escape(text)

def build_admin_status_text(user_id: int, status: str) -> str:
    data = get_form_data(user_id) or {}
    name = _safe_text(data.get("name", "—"))
    telegram = _safe_text(data.get("telegram", "—"))
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
    submit_time = submit_time_label_for_user(user_id)
    text = (
        f"{header}"
        f"👤 Имя: {_safe_text(data.get('name', '—'))}\n"
        f"📅 Дата рождения: {_safe_text(data.get('age', '—'))}\n"
        f"🌍 Город и страна: {_safe_text(data.get('city', '—'))}\n"
        f"🏠 Помещение без посторонних: {_safe_text(data.get('living', '—'))}\n"
        f"💬 Telegram: {_safe_text(data.get('telegram', '—'))}\n"
        f"🆔 ID: {user_id}\n"
        f"🧭 Источник: {source_label_for_user(user_id)}\n\n"
        f"🕒 Время подачи: {submit_time}\n\n"
        f"Статус: <b>{status_label}</b>"
    )
    if archived:
        text += "\n\n🗂 Архив"
    return text

def build_admin_full_text(data: dict, user_id: int, status: str) -> str:
    status_label = STATUS_LABELS.get(status, status)
    submit_time = submit_time_label_for_user(user_id)
    return (
        "📋 <b>Полная анкета</b>\n\n"
        f"👤 Имя: {_safe_text(data.get('name', '—'))}\n"
        f"📅 Дата рождения: {_safe_text(data.get('age', '—'))}\n"
        f"🌍 Город и страна: {_safe_text(data.get('city', '—'))}\n"
        f"📞 Телефон: {_safe_text(data.get('phone', '—'))}\n"
        f"🏠 Помещение без посторонних: {_safe_text(data.get('living', '—'))}\n"
        f"📱 Устройства: {_safe_text(data.get('devices', '—'))}\n"
        f"📲 Модель: {_safe_text(data.get('device_model', '—'))}\n"
        f"🎧 Наушники: {_safe_text(data.get('headphones', '—'))}\n"
        f"⏱ Время работы: {_safe_text(data.get('work_time', '—'))}\n"
        f"💼 Опыт: {_safe_text(data.get('experience', '—'))}\n"
        f"💬 Telegram: {_safe_text(data.get('telegram', '—'))}\n"
        f"🆔 ID: {user_id}\n"
        f"🧭 Источник: {source_label_for_user(user_id)}\n\n"
        f"🕒 Время подачи: {submit_time}\n\n"
        f"Статус: <b>{status_label}</b>"
    )

def admin_keyboard_for_status(user_id: int, status: str, contact_url: str | None = None):
    if status == "accepted":
        return admin_accepted_keyboard(user_id, contact_url=contact_url)
    if status == "rejected":
        return admin_rejected_keyboard(user_id, contact_url=contact_url)
    return admin_pending_keyboard(user_id, contact_url=contact_url)

async def update_admin_summary_message(user_id: int, status: str) -> bool:
    message_id = get_admin_message_id(user_id)
    if not message_id:
        return False
    data = get_form_data(user_id) or {}
    contact_url = contact_url_for_user(user_id, data)
    try:
        await bot.edit_message_text(
            chat_id=ADMIN_GROUP_ID,
            message_id=message_id,
            text=build_admin_summary(data, user_id, status),
            reply_markup=admin_keyboard_for_status(user_id, status, contact_url=contact_url)
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
    try:
        try:
            counts = get_status_counts()
        except Exception:
            logger.exception("Не удалось получить статистику для админ-меню")
            counts = {"pending": 0, "accepted": 0, "rejected": 0, "total": 0, "new": 0}
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
    except Exception:
        logger.exception("Критическая ошибка ensure_admin_menu_posted")

async def update_admin_menu_message(text: str, reply_markup: InlineKeyboardMarkup):
    try:
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
    except Exception:
        logger.exception("Критическая ошибка update_admin_menu_message")

def _parse_admin_photo_ids(value: str | None) -> list[int]:
    if not value:
        return []
    result = []
    for raw in value.split(","):
        raw = raw.strip()
        if raw.isdigit():
            result.append(int(raw))
    return result

async def clear_admin_notify():
    try:
        stored_id = get_setting(ADMIN_NOTIFY_SETTING_KEY)
        if stored_id and stored_id.isdigit():
            try:
                await bot.delete_message(ADMIN_GROUP_ID, int(stored_id))
            except Exception:
                pass
        set_setting(ADMIN_NOTIFY_SETTING_KEY, None)
    except Exception:
        logger.exception("Ошибка очистки уведомления админа")

async def clear_admin_view_message():
    try:
        stored_id = get_setting(ADMIN_VIEW_SETTING_KEY)
        if stored_id and stored_id.isdigit():
            try:
                await bot.delete_message(ADMIN_GROUP_ID, int(stored_id))
            except Exception:
                pass
        set_setting(ADMIN_VIEW_SETTING_KEY, None)
    except Exception:
        logger.exception("Ошибка очистки карточки просмотра")

async def update_admin_view_message(
    text: str,
    reply_markup: InlineKeyboardMarkup,
    photo_id: str | None
):
    try:
        stored_id = get_setting(ADMIN_VIEW_SETTING_KEY)
    except Exception:
        logger.exception("Не удалось прочитать id карточки просмотра")
        stored_id = None
    if stored_id and stored_id.isdigit():
        msg_id = int(stored_id)
        if photo_id:
            try:
                await bot.edit_message_media(
                    chat_id=ADMIN_GROUP_ID,
                    message_id=msg_id,
                    media=InputMediaPhoto(
                        media=photo_id,
                        caption=text,
                        parse_mode=ParseMode.HTML
                    ),
                    reply_markup=reply_markup
                )
                return
            except Exception:
                try:
                    await bot.delete_message(ADMIN_GROUP_ID, msg_id)
                except Exception:
                    pass
                set_setting(ADMIN_VIEW_SETTING_KEY, None)
        else:
            try:
                await bot.edit_message_text(
                    chat_id=ADMIN_GROUP_ID,
                    message_id=msg_id,
                    text=text,
                    reply_markup=reply_markup
                )
                return
            except Exception:
                try:
                    await bot.delete_message(ADMIN_GROUP_ID, msg_id)
                except Exception:
                    pass
                set_setting(ADMIN_VIEW_SETTING_KEY, None)

    try:
        if photo_id:
            msg = await bot.send_photo(
                ADMIN_GROUP_ID,
                photo_id,
                caption=text,
                reply_markup=reply_markup
            )
        else:
            msg = await bot.send_message(
                ADMIN_GROUP_ID,
                text,
                reply_markup=reply_markup
            )
        set_setting(ADMIN_VIEW_SETTING_KEY, str(msg.message_id))
    except Exception:
        logger.exception("Ошибка отправки сообщения просмотра анкеты")

async def update_admin_photos(user_id: int):
    stored_ids = _parse_admin_photo_ids(get_setting(ADMIN_PHOTOS_SETTING_KEY))
    for msg_id in stored_ids:
        try:
            await bot.delete_message(ADMIN_GROUP_ID, msg_id)
        except Exception:
            pass
    data = get_form_data(user_id) or {}
    face = data.get("photo_face")
    full = data.get("photo_full")
    if not face or not full:
        set_setting(ADMIN_PHOTOS_SETTING_KEY, None)
        return
    try:
        messages = await bot.send_media_group(
            ADMIN_GROUP_ID,
            [
                InputMediaPhoto(media=face),
                InputMediaPhoto(media=full),
            ]
        )
        ids = [m.message_id for m in messages]
        set_setting(ADMIN_PHOTOS_SETTING_KEY, ",".join(str(i) for i in ids))
    except Exception:
        logger.exception("Ошибка отправки фото админу")

async def notify_admin_new_application():
    try:
        counts = get_status_counts()
    except Exception:
        logger.exception("Не удалось получить статистику для уведомления")
        counts = {"pending": 0}
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
    try:
        counts = get_status_counts()
    except Exception:
        logger.exception("Не удалось получить статистику для обновления админ-меню")
        counts = {"pending": 0, "accepted": 0, "rejected": 0, "total": 0, "new": 0}
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
    await safe_call_answer(call)
    try:
        status = None if filter_key == "all" else filter_key
        apps = list_applications(status)
        label = _admin_list_label(filter_key)
        if not apps:
            await update_admin_menu_message(
                f"🤍 {label}: пока пусто ✨",
                admin_menu_keyboard(get_status_counts())
            )
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
        contact_url = contact_url_for_user(user_id, data)
        text = (
            f"🗂 <b>{label}</b>\n\n"
            f"Заявка <b>{offset + 1}</b> из <b>{total}</b>\n"
            f"Страница: <b>{page}/{pages}</b>\n\n"
            f"{build_admin_full_text(data, user_id, item_status)}"
        )
        photo_id = data.get("photo_face") or data.get("photo_full")
        await update_admin_view_message(
            text,
            admin_list_view_keyboard(user_id, item_status, filter_key, offset, total, ADMIN_LIST_LIMIT, contact_url=contact_url),
            photo_id
        )
    except Exception:
        logger.exception("Ошибка отображения списка заявок")
        await update_admin_menu_message(
            "⚠️ Не удалось открыть список заявок. Попробуй ещё раз.",
            admin_menu_keyboard(get_status_counts())
        )

async def send_menu(
    message: Message,
    caption: str | None = None,
    status: str | None = None,
    intro: str | None = None,

    tail: str | None = None
)-> bool:
    lang = lang_for(message.chat.id)
    base_caption = caption or t(lang, "menu_caption")
    await gentle_typing(message.chat.id)
    final_caption = (
        build_menu_caption_with_status(status, base_caption, lang=lang, intro=intro, tail=tail)
        if status
        else base_caption
    )
    return await send_or_edit_user_menu(
        message.chat.id,
        final_caption,
        lang=lang,
    )


async def ensure_language_selected(user_id: int, allow_home_button: bool = False, force_prompt: bool = False) -> bool:
    if has_user_language(user_id) and not force_prompt:
        return True
    current_lang = lang_for(user_id) if has_user_language(user_id) else "ru"
    await send_or_edit_user_text(
        user_id,
        t(current_lang, "language_menu_title"),
        reply_markup=language_keyboard(current_lang, include_home=allow_home_button),
    )
    return False

async def send_or_edit_user_menu(
    user_id: int,
    caption: str,
    lang: str | None = None,
) -> bool:
    locale = normalize_lang(lang or lang_for(user_id))
    message_id = get_menu_message_id(user_id)
    if message_id:
        try:
            await bot.edit_message_caption(
                chat_id=user_id,
                message_id=message_id,
                caption=caption,
                reply_markup=main_menu(locale)
            )
            return True
        except TelegramBadRequest as e:
            text = str(e).lower()
            if "message is not modified" in text:
                return True
            # fall through to send new menu on other edit errors
        except TelegramForbiddenError:
            logger.warning("Нет прав на обновление меню пользователя")
            return False
        except Exception:
            logger.exception("Не удалось обновить меню пользователя")
    if message_id:
        try:
            await bot.delete_message(user_id, message_id)
        except Exception:
            pass
    try:
        msg = await bot.send_photo(
            user_id,
            FSInputFile("media/menu.jpg"),
            caption=caption,
            reply_markup=main_menu(locale)
        )
        set_menu_message_id(user_id, msg.message_id)
        return True
    except TelegramForbiddenError:
        logger.warning("Нет прав на отправку меню пользователю")
        return False
    except Exception:
        logger.exception("Ошибка отправки меню пользователю")
        return False

async def send_or_edit_user_text(
    user_id: int,
    text: str,
    reply_markup=None
) -> bool:
    message_id = get_flow_message_id(user_id)
    if message_id:
        try:
            await bot.edit_message_text(
                chat_id=user_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup
            )
            return True
        except TelegramBadRequest as e:
            err = str(e).lower()
            if "message is not modified" in err:
                return True
            # Message can be deleted/not editable. Fall back to sending a new one.
            logger.warning("edit_message_text failed for user %s: %s", user_id, e)
        except TelegramForbiddenError:
            logger.warning("Нет прав на обновление сообщения пользователя")
            return False
        except Exception:
            logger.exception("Не удалось обновить сообщение пользователя, пробую отправить новое")
    else:
        menu_id = get_menu_message_id(user_id)
        if menu_id and len(text) <= CAPTION_LIMIT:
            try:
                await bot.edit_message_caption(
                    chat_id=user_id,
                    message_id=menu_id,
                    caption=text,
                    reply_markup=reply_markup
                )
                return True
            except TelegramBadRequest as e:
                err = str(e).lower()
                if "message is not modified" in err:
                    return True
                # Menu caption can be missing/not editable. Fall back to sending a new message.
                logger.warning("edit_message_caption failed for user %s: %s", user_id, e)
            except TelegramForbiddenError:
                logger.warning("Нет прав на обновление меню пользователя")
                return False
            except Exception:
                logger.exception("Не удалось обновить меню пользователя, пробую отправить новое сообщение")
    if message_id:
        try:
            await bot.delete_message(user_id, message_id)
        except Exception:
            pass
    try:
        msg = await bot.send_message(
            user_id,
            text,
            reply_markup=reply_markup
        )
        set_flow_message_id(user_id, msg.message_id)
        return True
    except TelegramForbiddenError:
        logger.warning("Нет прав на отправку сообщения пользователю")
        return False
    except Exception:
        logger.exception("Ошибка отправки сообщения пользователю")
        return False

async def clear_user_flow_message(user_id: int):
    message_id = get_flow_message_id(user_id)
    if not message_id:
        return
    try:
        await bot.delete_message(user_id, message_id)
    except Exception:
        pass
    set_flow_message_id(user_id, None)

async def clear_portfolio_media(user_id: int):
    cleanup_task = PORTFOLIO_CLEANUP_TASKS.pop(user_id, None)
    if cleanup_task and not cleanup_task.done():
        cleanup_task.cancel()
    ids = PORTFOLIO_MEDIA_IDS.pop(user_id, [])
    for message_id in ids:
        try:
            await bot.delete_message(user_id, message_id)
        except Exception:
            pass

async def _delayed_portfolio_cleanup(user_id: int, delay_seconds: int):
    try:
        await asyncio.sleep(delay_seconds)
        await clear_portfolio_media(user_id)
    except asyncio.CancelledError:
        pass
    except Exception:
        logger.exception("Ошибка автоочистки портфолио-медиа")

def schedule_portfolio_cleanup(user_id: int):
    old = PORTFOLIO_CLEANUP_TASKS.pop(user_id, None)
    if old and not old.done():
        old.cancel()
    PORTFOLIO_CLEANUP_TASKS[user_id] = asyncio.create_task(
        _delayed_portfolio_cleanup(user_id, PORTFOLIO_AUTO_DELETE_SECONDS)
    )

def track_portfolio_media(user_id: int, message_ids: list[int]):
    if not message_ids:
        return
    PORTFOLIO_MEDIA_IDS.setdefault(user_id, []).extend(message_ids)
    schedule_portfolio_cleanup(user_id)

def track_admin_temp_message(message_id: int | None):
    if not message_id:
        return
    if message_id not in ADMIN_TEMP_MESSAGE_IDS:
        ADMIN_TEMP_MESSAGE_IDS.append(message_id)

async def clear_admin_temp_messages():
    if not ADMIN_TEMP_MESSAGE_IDS:
        return
    ids = ADMIN_TEMP_MESSAGE_IDS.copy()
    ADMIN_TEMP_MESSAGE_IDS.clear()
    for message_id in ids:
        try:
            await bot.delete_message(ADMIN_GROUP_ID, message_id)
        except Exception:
            pass

async def start_application(message: Message, state: FSMContext):
    await state.clear()
    clear_form_data(message.from_user.id)
    await state.set_state(ApplicationStates.name)
    await gentle_typing(message.chat.id)
    lang = lang_for(message.from_user.id)
    question = format_question(
        ApplicationStates.name,
        form_question(ApplicationStates.name, lang),
        user_id=message.from_user.id,
    )
    edited = False
    if message and message.chat.type == "private":
        edited = await try_edit_message(message, question, reply_markup=form_keyboard(lang))
        if edited:
            set_menu_message_id(message.from_user.id, message.message_id)
    if not edited:
        sent = await send_or_edit_user_text(
            message.from_user.id,
            question,
            reply_markup=form_keyboard(lang)
        )
        if not sent:
            await state.clear()
            set_last_state(message.from_user.id, None)
            return False
    set_status(message.from_user.id, "new")
    set_last_state(message.from_user.id, ApplicationStates.name.state)
    return True

async def send_next_question(
    message: Message,
    state: FSMContext,
    next_state: ApplicationStates,
    note: str | None = None
):
    await state.set_state(next_state)
    set_last_state(message.from_user.id, next_state.state)
    await gentle_typing(message.chat.id)
    lang = lang_for(message.from_user.id)
    ack = build_ack(message.from_user.id)
    if note:
        ack = f"{ack}\n{note}"
    next_question = form_question(next_state, lang)
    await send_or_edit_user_text(
        message.from_user.id,
        f"{ack}\n\n{format_question(next_state, next_question, user_id=message.from_user.id)}",
        reply_markup=form_keyboard(lang)
    )

# ================= START =================

@dp.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    try:
        if message.chat.type != "private":
            await message.answer(t("ru", "start_private_only"))
            return
        await state.clear()
        await clear_portfolio_media(message.from_user.id)
        if not await ensure_language_selected(
            message.from_user.id,
            allow_home_button=False,
            force_prompt=FORCE_LANGUAGE_PICK_ON_START,
        ):
            return
        app = get_application(message.from_user.id)
        status = app.get("status") if app else None
        lang = lang_for(message.from_user.id)
        await send_menu(message, caption=t(lang, "menu_caption"), status=status)
        if app and app.get("last_state") in FORM_PROGRESS_STATES and not get_form_data(message.from_user.id):
            set_last_state(message.from_user.id, None)
        if app and app.get("status") in {None, "new"} and app.get("last_state") in FORM_PROGRESS_STATES:
            await send_or_edit_user_text(
                message.from_user.id,
                t(lang, "resume_prompt"),
                reply_markup=continue_form_keyboard(lang)
            )
    except Exception:
        logger.exception("Ошибка в /start")

@dp.callback_query(F.data == "main_menu")
async def main_menu_handler(call: CallbackQuery, state: FSMContext):
    if not call.message or call.message.chat.type != "private":
        await safe_call_answer(call, t("ru", "open_private_prompt"), show_alert=True)
        return
    await safe_call_answer(call)
    await state.clear()
    await clear_portfolio_media(call.from_user.id)
    app = get_application(call.from_user.id)
    status = app.get("status") if app else None
    lang = lang_for(call.from_user.id)
    await send_menu(call.message, caption=t(lang, "menu_caption"), status=status)
    await clear_user_flow_message(call.from_user.id)


@dp.message(F.text == "/language")
async def language_command(message: Message):
    if message.chat.type != "private":
        await message.answer(t("ru", "start_private_only"))
        return
    lang = lang_for(message.from_user.id)
    await send_or_edit_user_text(
        message.from_user.id,
        t(lang, "language_menu_title"),
        reply_markup=language_keyboard(lang),
    )


@dp.callback_query(F.data == "language_menu")
async def language_menu_handler(call: CallbackQuery):
    if not call.message or call.message.chat.type != "private":
        await safe_call_answer(call, t("ru", "open_private_prompt"), show_alert=True)
        return
    lang = lang_for(call.from_user.id)
    await send_or_edit_user_text(
        call.from_user.id,
        t(lang, "language_menu_title"),
        reply_markup=language_keyboard(lang),
    )
    await safe_call_answer(call)


@dp.callback_query(F.data.startswith("set_lang:"))
async def set_language_handler(call: CallbackQuery, state: FSMContext):
    try:
        if not call.message or call.message.chat.type != "private":
            await safe_call_answer(call, t("ru", "open_private_prompt"), show_alert=True)
            return
        await safe_call_answer(call)
        lang_code = call.data.split(":", 1)[1].strip().lower()
        if lang_code not in LANGUAGE_NAMES:
            lang_code = "ru"
        set_user_language(call.from_user.id, lang_code)
        lang = lang_for(call.from_user.id)
        app = get_application(call.from_user.id)
        status = app.get("status") if app else None
        await state.clear()
        await clear_portfolio_media(call.from_user.id)
        intro_text = t(lang, "language_changed", language=LANGUAGE_NAMES.get(lang, lang))
        menu_ok = False
        try:
            menu_ok = await send_menu(
                call.message,
                caption=t(lang, "menu_caption"),
                status=status,
                intro=intro_text,
            )
        except Exception:
            logger.exception("Не удалось обновить меню после смены языка")
        if not menu_ok:
            await send_or_edit_user_text(
                call.from_user.id,
                f"{intro_text}\n\n{t(lang, 'menu_caption')}",
                reply_markup=main_menu(lang),
            )
        await clear_user_flow_message(call.from_user.id)
    except Exception:
        logger.exception("Ошибка выбора языка")
        await safe_call_answer(call, t("ru", "temp_error_retry"), show_alert=True)
# ================= APPLY =================

@dp.callback_query(F.data == "apply")
async def apply(call: CallbackQuery, state: FSMContext):
    try:
        if not call.message or call.message.chat.type != "private":
            await safe_call_answer(call, t("ru", "open_private_prompt"), show_alert=True)
            return
        await safe_call_answer(call)
        lang = lang_for(call.from_user.id)
        logger.info(
            "APPLY_CLICK user_id=%s is_bot=%s chat_id=%s chat_type=%s",
            call.from_user.id,
            call.from_user.is_bot,
            call.message.chat.id,
            call.message.chat.type
        )
        await clear_portfolio_media(call.from_user.id)
        app = get_application(call.from_user.id)
        status = app["status"] if app else None
        logger.info("APPLY_STATUS user_id=%s status=%s", call.from_user.id, status)

        if status in {"pending", "accepted", "rejected"}:
            status_text = {
                "pending": t(lang, "pending_status_text"),
                "accepted": t(lang, "accepted_status_text"),
                "rejected": t(lang, "rejected_status_text")
            }.get(status, t(lang, "pending_status_text"))
            await edit_or_send(
                call,
                f"{status_text}\n\n{t(lang, 'reapply_confirm')}",
                reply_markup=reapply_keyboard(lang)
            )
            return

        if app and is_rate_limited(app.get("last_apply_at")):
            await edit_or_send(
                call,
                t(lang, "rate_limited"),
                reply_markup=main_menu(lang)
            )
            return

        current = await state.get_state()
        last_state = app.get("last_state") if app else None
        if last_state in FORM_PROGRESS_STATES and not get_form_data(call.from_user.id):
            set_last_state(call.from_user.id, None)
            last_state = None
        if (current and current in FORM_PROGRESS_STATES) or (last_state in FORM_PROGRESS_STATES):
            await send_or_edit_user_text(
                call.from_user.id,
                t(lang, "already_started_prompt"),
                reply_markup=continue_form_keyboard(lang)
            )
            return

        started = await start_application(call.message, state)
        if not started:
            await safe_call_answer(call, t(lang, "cannot_send_message"), show_alert=True)
            return
    except Exception:
        logger.exception("Ошибка в apply")
        await safe_call_answer(call, t(lang_for(call.from_user.id), "temp_error_retry"), show_alert=True)

@dp.callback_query(F.data == "apply_restart")
async def apply_restart(call: CallbackQuery, state: FSMContext):
    try:
        if not call.message or call.message.chat.type != "private":
            await safe_call_answer(call, t("ru", "open_private_prompt"), show_alert=True)
            return
        await safe_call_answer(call)
        lang = lang_for(call.from_user.id)
        app = get_application(call.from_user.id)
        if app and is_rate_limited(app.get("last_apply_at")):
            await edit_or_send(
                call,
                t(lang, "rate_limited"),
                reply_markup=main_menu(lang)
            )
            return

        await state.clear()
        started = await start_application(call.message, state)
        if not started:
            await safe_call_answer(call, t(lang, "cannot_send_message"), show_alert=True)
            return
    except Exception:
        logger.exception("Ошибка в apply_restart")
        await safe_call_answer(call, t(lang_for(call.from_user.id), "temp_error_retry"), show_alert=True)

@dp.callback_query(F.data == "form_continue")
async def form_continue(call: CallbackQuery, state: FSMContext):
    try:
        if not call.message or call.message.chat.type != "private":
            await safe_call_answer(call, t("ru", "open_private_prompt"), show_alert=True)
            return
        await safe_call_answer(call)
        lang = lang_for(call.from_user.id)
        current = await state.get_state()
        if not current:
            app = get_application(call.from_user.id)
            last_state = app.get("last_state") if app else None
            if last_state and last_state in FORM_PROGRESS_STATES and not get_form_data(call.from_user.id):
                set_last_state(call.from_user.id, None)
                last_state = None
            if last_state and last_state in FORM_PROGRESS_STATES:
                await state.set_state(last_state)
                await restore_form_data(state, call.from_user.id)
                current = last_state
            else:
                started = await start_application(call.message, state)
                if not started:
                    await safe_call_answer(call, t(lang, "cannot_send_message"), show_alert=True)
                    return
                return

        if current == ApplicationStates.preview.state:
            data = await state.get_data()
            if not REQUIRED_PREVIEW_FIELDS.issubset(data):
                started = await start_application(call.message, state)
                if not started:
                    await safe_call_answer(call, t(lang, "cannot_send_message"), show_alert=True)
                    return
                return
            await show_preview(call.message, state)
            return
        if current == ApplicationStates.edit_value.state:
            data = await state.get_data()
            field = data.get("edit_field")
            if not field:
                await show_preview(call.message, state)
                return
            title = field_title(field, lang_for(call.from_user.id))
            await send_or_edit_user_text(
                call.from_user.id,
                (
                    f"✏️ <b>Редактирование поля:</b>\n\n{title}\n\n👉 Введи новое значение:"
                    if lang == "ru"
                    else (
                        f"✏️ <b>Edit field:</b>\n\n{title}\n\n👉 Enter new value:"
                        if lang == "en"
                        else (
                            f"✏️ <b>Editar campo:</b>\n\n{title}\n\n👉 Digite o novo valor:"
                            if lang == "pt"
                            else f"✏️ <b>Editar campo:</b>\n\n{title}\n\n👉 Escribe el nuevo valor:"
                        )
                    )
                )
            )
            return

        for st in FORM_ORDER:
            if st.state == current:
                lang = lang_for(call.from_user.id)
                await send_or_edit_user_text(
                    call.from_user.id,
                    format_question(st, form_question(st, lang), user_id=call.from_user.id),
                    reply_markup=form_keyboard(lang)
                )
                return

        started = await start_application(call.message, state)
        if not started:
            await safe_call_answer(call, t(lang, "cannot_send_message"), show_alert=True)
            return
    except Exception:
        logger.exception("Ошибка в form_continue")
        await safe_call_answer(call, t(lang_for(call.from_user.id), "temp_error_retry"), show_alert=True)

@dp.callback_query(F.data == "form_restart")
async def form_restart(call: CallbackQuery, state: FSMContext):
    try:
        if not call.message or call.message.chat.type != "private":
            await safe_call_answer(call, t("ru", "open_private_prompt"), show_alert=True)
            return
        await safe_call_answer(call)
        lang = lang_for(call.from_user.id)
        started = await start_application(call.message, state)
        if not started:
            await safe_call_answer(call, t(lang, "cannot_send_message"), show_alert=True)
            return
    except Exception:
        logger.exception("Ошибка в form_restart")
        await safe_call_answer(call, t(lang_for(call.from_user.id), "temp_error_retry"), show_alert=True)

# ================= FORM STEPS =================

@dp.message(StateFilter(ApplicationStates.name), F.text)
async def step_name(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    name = m.text.strip()
    await delete_user_message(m)
    if len(name) < 2:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_name_short"),
            reply_markup=form_keyboard(lang)
        )
        return
    await update_form_field(state, m.from_user.id, name=name)
    await send_next_question(
        m,
        state,
        ApplicationStates.city
    )

@dp.message(StateFilter(ApplicationStates.city), F.text)
async def step_city(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    city = m.text.strip()
    await delete_user_message(m)
    if len(city) < 2:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_city_short"),
            reply_markup=form_keyboard(lang)
        )
        return
    await update_form_field(state, m.from_user.id, city=city)
    await send_next_question(
        m,
        state,
        ApplicationStates.phone
    )

@dp.message(StateFilter(ApplicationStates.phone), F.text)
async def step_phone(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    phone = m.text.strip()
    await delete_user_message(m)
    if not is_valid_phone(phone):
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_phone_invalid"),
            reply_markup=form_keyboard(lang)
        )
        return
    normalized = normalize_phone(phone) or phone
    note = None
    if normalized != phone:
        note = t(lang, "normalized_phone_note", value=normalized)
    await update_form_field(state, m.from_user.id, phone=normalized)
    await send_next_question(
        m,
        state,
        ApplicationStates.age,
        note=note
    )

@dp.message(StateFilter(ApplicationStates.age), F.text)
async def step_age(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    birthdate = m.text.strip()
    await delete_user_message(m)
    if not is_valid_birthdate(birthdate):
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_age_invalid"),
            reply_markup=form_keyboard(lang)
        )
        return
    normalized = normalize_birthdate(birthdate) or birthdate
    note = None
    if normalized != birthdate:
        note = t(lang, "normalized_birthdate_note", value=normalized)
    await update_form_field(
        state,
        m.from_user.id,
        age=normalized
    )
    await send_next_question(
        m,
        state,
        ApplicationStates.living,
        note=note
    )

@dp.message(StateFilter(ApplicationStates.living), F.text)
async def step_living(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    living_raw = m.text.strip()
    await delete_user_message(m)
    normalized = normalize_yes_no(living_raw)
    if not normalized:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_yes_no"),
            reply_markup=form_keyboard(lang)
        )
        return
    note = None
    if normalized != living_raw:
        note = t(lang, "normalized_yes_no_note", value=normalized)
    await update_form_field(state, m.from_user.id, living=normalized)
    await send_next_question(
        m,
        state,
        ApplicationStates.devices,
        note=note
    )

@dp.message(StateFilter(ApplicationStates.devices), F.text)
async def step_devices(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    devices = m.text.strip()
    await delete_user_message(m)
    if len(devices) < 2:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_devices_short"),
            reply_markup=form_keyboard(lang)
        )
        return
    await update_form_field(state, m.from_user.id, devices=devices)
    await send_next_question(
        m,
        state,
        ApplicationStates.device_model
    )

@dp.message(StateFilter(ApplicationStates.device_model), F.text)
async def step_device_model(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    device_model = m.text.strip()
    await delete_user_message(m)
    if len(device_model) < 2:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_device_model_short"),
            reply_markup=form_keyboard(lang)
        )
        return
    await update_form_field(state, m.from_user.id, device_model=device_model)
    await send_next_question(
        m,
        state,
        ApplicationStates.work_time
    )

@dp.message(StateFilter(ApplicationStates.work_time), F.text)
async def step_work_time(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    work_time = m.text.strip()
    await delete_user_message(m)
    if not has_any_digit(work_time):
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_work_time_invalid"),
            reply_markup=form_keyboard(lang)
        )
        return
    await update_form_field(state, m.from_user.id, work_time=work_time)
    await send_next_question(
        m,
        state,
        ApplicationStates.headphones
    )

@dp.message(StateFilter(ApplicationStates.headphones), F.text)
async def step_headphones(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    headphones = m.text.strip()
    await delete_user_message(m)
    if len(headphones) < 2:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_headphones_prompt"),
            reply_markup=form_keyboard(lang)
        )
        return
    await update_form_field(state, m.from_user.id, headphones=headphones)
    await send_next_question(
        m,
        state,
        ApplicationStates.telegram
    )

@dp.message(StateFilter(ApplicationStates.telegram), F.text)
async def step_tg(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    raw = m.text.strip()
    await delete_user_message(m)
    normalized = normalize_telegram(raw)
    if not normalized:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_telegram_invalid"),
            reply_markup=form_keyboard(lang)
        )
        return
    note = None
    if normalized != raw:
        note = t(lang, "normalized_telegram_note", value=normalized)
    await update_form_field(state, m.from_user.id, telegram=normalized)
    await send_next_question(
        m,
        state,
        ApplicationStates.experience,
        note=note
    )

@dp.message(StateFilter(ApplicationStates.experience), F.text)
async def step_exp(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    experience = m.text.strip()
    await delete_user_message(m)
    if len(experience) < 1:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_experience_prompt"),
            reply_markup=form_keyboard(lang)
        )
        return
    await update_form_field(state, m.from_user.id, experience=experience)
    await send_next_question(
        m,
        state,
        ApplicationStates.photo_face
    )

@dp.message(StateFilter(ApplicationStates.photo_face), F.photo)
async def step_face(m: Message, state: FSMContext):
    await update_form_field(state, m.from_user.id, photo_face=m.photo[-1].file_id)
    await delete_user_message(m)
    await send_next_question(
        m,
        state,
        ApplicationStates.photo_full
    )

@dp.message(StateFilter(ApplicationStates.photo_full), F.photo)
async def step_full(m: Message, state: FSMContext):
    await update_form_field(state, m.from_user.id, photo_full=m.photo[-1].file_id)
    await delete_user_message(m)
    await send_or_edit_user_text(m.from_user.id, build_ack(m.from_user.id))
    await show_preview(m, state)

@dp.message(StateFilter(ApplicationStates.photo_face), ~F.photo)
async def reject_non_photo_face(m: Message):
    lang = lang_for(m.from_user.id)
    await delete_user_message(m)
    await send_or_edit_user_text(
        m.from_user.id,
        t(lang, "photo_face_required"),
        reply_markup=form_keyboard(lang)
    )

@dp.message(StateFilter(ApplicationStates.photo_full), ~F.photo)
async def reject_non_photo_full(m: Message):
    lang = lang_for(m.from_user.id)
    await delete_user_message(m)
    await send_or_edit_user_text(
        m.from_user.id,
        t(lang, "photo_full_required"),
        reply_markup=form_keyboard(lang)
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

def format_question(
    state: ApplicationStates,
    question: str,
    user_id: int | None = None,
) -> str:
    step = FORM_STEP_INDEX.get(state)
    if not step:
        return question
    if user_id is not None:
        lang = lang_for(user_id)
        if lang == "en":
            return f"Step {step}/{TOTAL_STEPS}\n\n{question}"
        if lang == "pt":
            return f"Etapa {step}/{TOTAL_STEPS}\n\n{question}"
        if lang == "es":
            return f"Paso {step}/{TOTAL_STEPS}\n\n{question}"
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
)

@dp.message(StateFilter(*TEXT_STATES), ~F.text)
async def reject_non_text(m: Message):
    lang = lang_for(m.from_user.id)
    await delete_user_message(m)
    await send_or_edit_user_text(
        m.from_user.id,
        t(lang, "reject_non_text"),
        reply_markup=form_keyboard(lang)
    )

@dp.message(StateFilter(ApplicationStates.admin_reject_reason), ~F.text)
async def reject_reason_non_text(m: Message, state: FSMContext):
    if m.chat.id != ADMIN_GROUP_ID:
        return
    await update_admin_menu_message(
        "🤍 Пожалуйста, напиши причину отказа текстом.",
        reject_reason_keyboard()
    )

@dp.callback_query(F.data == "form_back")
async def form_back(call: CallbackQuery, state: FSMContext):
    try:
        await safe_call_answer(call)
        current = await state.get_state()

        if current not in FORM_ORDER:
            return

        idx = FORM_ORDER.index(current)

        if idx == 0:
            await safe_call_answer(call, t(lang_for(call.from_user.id), "first_step_notice"))
            return

        prev_state = FORM_ORDER[idx - 1]
        await state.set_state(prev_state)
        set_last_state(call.from_user.id, prev_state.state)

        data = await state.get_data()
        field_key = STATE_TO_FIELD.get(prev_state)
        prev_value = data.get(field_key) if field_key else None

        lang = lang_for(call.from_user.id)
        question = format_question(
            prev_state,
            form_question(prev_state, lang),
            user_id=call.from_user.id,
        )
        if prev_state in {ApplicationStates.photo_face, ApplicationStates.photo_full}:
            question += (
                "\n\nЕсли нужно заменить — пришли новое фото."
                if lang == "ru"
                else (
                    "\n\nIf you want to replace it, send a new photo."
                    if lang == "en"
                    else ("\n\nSe quiser trocar, envie uma nova foto." if lang == "pt" else "\n\nSi quieres reemplazarla, envía una foto nueva.")
                )
            )
        elif prev_value:
            question += (
                f"\n\nТвой прошлый ответ: {prev_value}\nЕсли нужно — отправь новый."
                if lang == "ru"
                else (
                    f"\n\nYour previous answer: {prev_value}\nSend a new one if needed."
                    if lang == "en"
                    else (
                        f"\n\nSua resposta anterior: {prev_value}\nEnvie uma nova se precisar."
                        if lang == "pt"
                        else f"\n\nTu respuesta anterior: {prev_value}\nEnvía una nueva si hace falta."
                    )
                )
            )

        await send_or_edit_user_text(
            call.from_user.id,
            question,
            reply_markup=form_keyboard(lang)
        )
    except Exception:
        logger.exception("Ошибка в form_back")
        await safe_call_answer(call, "Ошибка возврата на предыдущий шаг", show_alert=False)
# ================= MAIN MENU HANDLERS =================

@dp.callback_query(F.data == "about_work")
async def about_work(call: CallbackQuery):
    lang = lang_for(call.from_user.id)
    await clear_portfolio_media(call.from_user.id)
    await edit_or_send(
        call,
        t(lang, "about_work_text"),
        reply_markup=about_menu(lang)
    )


@dp.callback_query(F.data == "about_platforms")
async def about_platforms(call: CallbackQuery):
    lang = lang_for(call.from_user.id)
    await clear_portfolio_media(call.from_user.id)
    await edit_or_send(
        call,
        t(lang, "about_platforms_text"),
        reply_markup=about_menu(lang)
    )


@dp.callback_query(F.data == "about_income")
async def about_income(call: CallbackQuery):
    lang = lang_for(call.from_user.id)
    await clear_portfolio_media(call.from_user.id)
    await edit_or_send(
        call,
        t(lang, "about_income_text"),
        reply_markup=about_menu(lang)
    )

@dp.callback_query(F.data == "portfolio")
async def portfolio(call: CallbackQuery):
    try:
        lang = lang_for(call.from_user.id)
        await clear_portfolio_media(call.from_user.id)
        await edit_or_send(
            call,
            t(lang, "profile_portfolio_title"),
            reply_markup=portfolio_menu(lang)
        )
    except Exception:
        logger.exception("Ошибка в portfolio")
        await safe_call_answer(call, "Не удалось открыть раздел", show_alert=False)

@dp.callback_query(F.data == "about")
async def about(call: CallbackQuery):
    try:
        lang = lang_for(call.from_user.id)
        await clear_portfolio_media(call.from_user.id)
        await edit_or_send(
            call,
            t(lang, "profile_about_title"),
            reply_markup=about_menu(lang)
        )
    except Exception:
        logger.exception("Ошибка в about")
        await safe_call_answer(call, "Не удалось открыть раздел", show_alert=False)

@dp.callback_query(F.data == "contact")
async def contact(call: CallbackQuery):
    try:
        lang = lang_for(call.from_user.id)
        await clear_portfolio_media(call.from_user.id)
        username = ADMIN_USERNAME.lstrip("@")
        await edit_or_send(
            call,
            t(lang, "profile_contact_title", link=f"https://t.me/{username}"),
            reply_markup=main_menu(lang)
        )
    except Exception:
        logger.exception("Ошибка в contact")
        await safe_call_answer(call, "Не удалось открыть раздел", show_alert=False)

@dp.callback_query(F.data == "back")
async def back_handler(call: CallbackQuery, state: FSMContext):
    try:
        if not call.message:
            await safe_call_answer(call, "Не удалось открыть меню", show_alert=False)
            return
        await state.clear()
        await start(call.message, state)
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка в back_handler")
        await safe_call_answer(call, "Ошибка возврата в меню", show_alert=False)

# ================= PREVIEW =================

@dp.callback_query(F.data == "preview_edit")
async def preview_edit(call: CallbackQuery):
    try:
        lang = lang_for(call.from_user.id)
        await edit_or_send(
            call,
            "✏️ <b>Что хочешь исправить?</b>\n\nВыбери пункт:" if lang == "ru" else (
                "✏️ <b>What would you like to edit?</b>\n\nChoose a field:"
                if lang == "en"
                else ("✏️ <b>O que você quer editar?</b>\n\nEscolha um campo:" if lang == "pt" else "✏️ <b>¿Qué quieres editar?</b>\n\nElige un campo:")
            ),
            reply_markup=preview_edit_menu(lang)
        )
    except Exception:
        logger.exception("Ошибка в preview_edit")
        await safe_call_answer(call, "Не удалось открыть редактирование", show_alert=False)

@dp.callback_query(F.data.startswith("edit:"))
async def edit_field(call: CallbackQuery, state: FSMContext):
    try:
        if ":" not in call.data:
            await safe_call_answer(call, "Некорректная команда", show_alert=False)
            return
        field = call.data.split(":", 1)[1]

        await state.update_data(edit_field=field)
        await state.set_state(ApplicationStates.edit_value)
        set_last_state(call.from_user.id, ApplicationStates.edit_value.state)

        lang = lang_for(call.from_user.id)
        title = field_title(field, lang)

        await send_or_edit_user_text(
            call.from_user.id,
            (
                f"✏️ <b>Редактирование поля:</b>\n\n{title}\n\n👉 Введи новое значение:"
                if lang == "ru"
                else (
                    f"✏️ <b>Edit field:</b>\n\n{title}\n\n👉 Enter new value:"
                    if lang == "en"
                    else (
                        f"✏️ <b>Editar campo:</b>\n\n{title}\n\n👉 Digite o novo valor:"
                        if lang == "pt"
                        else f"✏️ <b>Editar campo:</b>\n\n{title}\n\n👉 Escribe el nuevo valor:"
                    )
                )
            )
        )
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка в edit_field")
        await safe_call_answer(call, "Не удалось открыть редактирование", show_alert=False)

@dp.message(StateFilter(ApplicationStates.edit_value), F.text)
async def save_edited_value(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    value = m.text.strip()
    await delete_user_message(m)

    # 🚫 запрет пустых значений
    if not value:
        await send_or_edit_user_text(
            m.from_user.id,
            "🤍 Значение не может быть пустым. Введи ещё раз:" if lang == "ru" else (
                "🤍 Value cannot be empty. Please enter it again:" if lang == "en" else (
                    "🤍 O valor não pode ficar vazio. Digite novamente:" if lang == "pt" else "🤍 El valor no puede estar vacío. Escríbelo nuevamente:"
                )
            )
        )
        return

    data = await state.get_data()
    field = data.get("edit_field")

    if not field:
        await send_or_edit_user_text(m.from_user.id, t(lang, "temp_error_retry"))
        await state.clear()
        return

    # базовая валидация при редактировании
    if field == "name" and len(value) < 2:
        await send_or_edit_user_text(m.from_user.id, t(lang, "field_name_short"))
        return
    if field == "city" and len(value) < 2:
        await send_or_edit_user_text(m.from_user.id, t(lang, "field_city_short"))
        return
    if field == "phone" and not is_valid_phone(value):
        await send_or_edit_user_text(m.from_user.id, t(lang, "field_phone_invalid"))
        return
    if field == "phone":
        value = normalize_phone(value) or value
    if field == "age" and not is_valid_birthdate(value):
        await send_or_edit_user_text(m.from_user.id, t(lang, "field_age_invalid"))
        return
    if field == "age":
        value = normalize_birthdate(value) or value
    if field == "living":
        normalized = normalize_yes_no(value)
        if not normalized:
            await send_or_edit_user_text(m.from_user.id, t(lang, "field_yes_no"))
            return
        value = normalized
    if field == "devices" and len(value) < 2:
        await send_or_edit_user_text(m.from_user.id, t(lang, "field_devices_short"))
        return
    if field == "device_model" and len(value) < 2:
        await send_or_edit_user_text(m.from_user.id, t(lang, "field_device_model_short"))
        return
    if field == "work_time" and not has_any_digit(value):
        await send_or_edit_user_text(m.from_user.id, t(lang, "field_work_time_invalid"))
        return
    if field == "headphones" and len(value) < 2:
        await send_or_edit_user_text(m.from_user.id, t(lang, "field_headphones_prompt"))
        return
    if field == "telegram":
        normalized = normalize_telegram(value)
        if not normalized:
            await send_or_edit_user_text(m.from_user.id, t(lang, "field_telegram_invalid"))
            return
        value = normalized
    if field == "experience" and len(value) < 1:
        await send_or_edit_user_text(m.from_user.id, t(lang, "field_experience_prompt"))
        return

    # сохраняем новое значение
    await update_form_field(state, m.from_user.id, **{field: value})

    # возвращаем предпросмотр
    await show_preview(m, state)


@dp.callback_query(F.data == "preview_edit_photo")
async def preview_edit_photo(call: CallbackQuery):
    try:
        lang = lang_for(call.from_user.id)
        await edit_or_send(
            call,
            "📷 <b>Какое фото хочешь заменить?</b>" if lang == "ru" else (
                "📷 <b>Which photo do you want to replace?</b>"
                if lang == "en"
                else ("📷 <b>Qual foto você quer trocar?</b>" if lang == "pt" else "📷 <b>¿Qué foto quieres reemplazar?</b>")
            ),
            reply_markup=preview_edit_photo_menu(lang)
        )
    except Exception:
        logger.exception("Ошибка в preview_edit_photo")
        await safe_call_answer(call, "Не удалось открыть замену фото", show_alert=False)

@dp.callback_query(F.data.startswith("edit_photo:"))
async def edit_photo(call: CallbackQuery, state: FSMContext):
    try:
        if ":" not in call.data:
            await safe_call_answer(call, "Некорректная команда", show_alert=False)
            return
        photo_type = call.data.split(":", 1)[1]

        await state.update_data(edit_photo=photo_type)

        lang = lang_for(call.from_user.id)
        text = (
            "📷 <b>Замена фото</b>\n\n"
            "Отправь новое фото:\n"
            "• чёткое\n"
            "• без фильтров\n"
            "• хорошее освещение\n\n"
            "⬅️ Если передумала — нажми «Отмена»"
        ) if lang == "ru" else (
            "📷 <b>Photo replacement</b>\n\nSend a new photo.\n⬅️ If you changed your mind, press Cancel."
            if lang == "en"
            else ("📷 <b>Troca de foto</b>\n\nEnvie uma nova foto.\n⬅️ Se mudou de ideia, pressione Cancelar." if lang == "pt" else "📷 <b>Reemplazo de foto</b>\n\nEnvía una foto nueva.\n⬅️ Si cambiaste de idea, pulsa Cancelar.")
        )

        await send_or_edit_user_text(
            call.from_user.id,
            text,
            reply_markup=cancel_keyboard(lang)
        )
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка в edit_photo")
        await safe_call_answer(call, "Не удалось открыть замену фото", show_alert=False)

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

    await delete_user_message(m)
    await state.update_data(edit_photo=None)

    await show_preview(m, state)

@dp.message(StateFilter(ApplicationStates.preview), ~F.photo)
async def reject_text_when_waiting_photo(m: Message, state: FSMContext):
    data = await state.get_data()

    if data.get("edit_photo"):
        lang = lang_for(m.from_user.id)
        await delete_user_message(m)
        await send_or_edit_user_text(
            m.from_user.id,
            "🤍 Сейчас нужно отправить <b>ФОТО</b>, а не текст.\n\n📷 Пришли фотографию или нажми «Отмена»."
            if lang == "ru"
            else (
                "🤍 Please send a <b>PHOTO</b>, not text.\n\n📷 Send a photo or press Cancel."
                if lang == "en"
                else (
                    "🤍 Agora envie uma <b>FOTO</b>, não texto.\n\n📷 Envie uma foto ou pressione Cancelar."
                    if lang == "pt"
                    else "🤍 Ahora debes enviar una <b>FOTO</b>, no texto.\n\n📷 Envía una foto o pulsa Cancelar."
                )
            )
        )

@dp.callback_query(F.data == "preview_back")
async def preview_back(call: CallbackQuery, state: FSMContext):
    try:
        await safe_call_answer(call)
        if not call.message:
            return
        await show_preview(call.message, state)
    except Exception:
        logger.exception("Ошибка в preview_back")
        await safe_call_answer(call, "Не удалось открыть предпросмотр", show_alert=False)

async def show_preview(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    data = await state.get_data()
    await send_or_edit_user_text(m.from_user.id, t(lang, "loading_text"))
    for text in (
        t(lang, "loading_stage_1"),
        t(lang, "loading_stage_2"),
    ):
        await asyncio.sleep(random.uniform(0.4, 0.8))
        await send_or_edit_user_text(m.from_user.id, text)
    await asyncio.sleep(random.uniform(0.3, 0.6))
    status = get_status(m.from_user.id) or "new"
    status_caption = status_label(status, lang)
    text = t(
        lang,
        "preview_title",
        name=data["name"],
        city=data["city"],
        age=data["age"],
        phone=data["phone"],
        living=data["living"],
        devices=data["devices"],
        device_model=data["device_model"],
        headphones=data["headphones"],
        work_time=data["work_time"],
        experience=data["experience"],
        telegram=data["telegram"],
        status=status_caption,
    )
    await state.set_state(ApplicationStates.preview)
    set_last_state(m.from_user.id, ApplicationStates.preview.state)
    await send_or_edit_user_text(m.from_user.id, text, reply_markup=preview_keyboard(lang))

# ================= CONFIRM SEND =================

@dp.callback_query(F.data == "preview_confirm")
async def preview_confirm(call: CallbackQuery, state: FSMContext):
    try:
        lang = lang_for(call.from_user.id)
        await safe_call_answer(call)
        data = await state.get_data()
        user = call.from_user
        app = get_application(user.id)

        if app and is_rate_limited(app.get("last_apply_at")):
            await send_or_edit_user_text(
                call.from_user.id,
                t(lang, "recent_already_sent")
            )
            await safe_call_answer(call)
            return
        if not REQUIRED_PREVIEW_FIELDS.issubset(data):
            await send_or_edit_user_text(
                call.from_user.id,
                t(lang, "application_missing")
            )
            started = await start_application(call.message, state)
            if not started:
                await safe_call_answer(call, t(lang, "cannot_send_message"), show_alert=True)
                return
            await safe_call_answer(call)
            return

        await gentle_typing(call.message.chat.id)

        set_source(user.id, "bot")
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
                t(lang, "menu_caption"),
                lang=lang,
                intro=t(lang, "application_sent")
            )
            await send_or_edit_user_menu(
                call.from_user.id,
                caption,
                lang=lang,
            )
        except Exception:
            logger.exception("Ошибка отправки меню после заявки")
        await clear_user_flow_message(call.from_user.id)
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка в preview_confirm")
        await safe_call_answer(call, t(lang_for(call.from_user.id), "temp_error_retry"), show_alert=True)

@dp.callback_query(F.data == "edit_cancel")
async def edit_cancel(call: CallbackQuery, state: FSMContext):
    try:
        await safe_call_answer(call)
        await state.update_data(edit_field=None, edit_photo=None)
        if not call.message:
            return
        await show_preview(call.message, state)
        lang = lang_for(call.from_user.id)
        await safe_call_answer(call, "Отменено" if lang == "ru" else ("Canceled" if lang == "en" else ("Cancelado" if lang == "pt" else "Cancelado")))
    except Exception:
        logger.exception("Ошибка в edit_cancel")
        await safe_call_answer(call, "Не удалось отменить редактирование", show_alert=False)

# ================= ADMIN =================

@dp.callback_query(F.data.startswith("admin_accept:"))
async def admin_accept(call: CallbackQuery):
    try:
        if not call.message or call.message.chat.id != ADMIN_GROUP_ID:
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        await safe_call_answer(call)
        parts = call.data.split(":")
        uid = int(parts[1])
        view_mode = len(parts) > 2 and parts[2] == "view"
        try:
            user_lang = lang_for(uid)
            caption = build_menu_caption_with_status(
                "accepted",
                t(user_lang, "accept_caption"),
                lang=user_lang,
                tail=t(user_lang, "approved_tail")
            )
            if not is_site_source(uid):
                await send_or_edit_user_menu(uid, caption, lang=user_lang)
                await clear_user_flow_message(uid)
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
        await safe_call_answer(call, "Принято")
    except Exception:
        logger.exception("Ошибка в admin_accept")
        await safe_call_answer(call, "Ошибка при принятии заявки", show_alert=True)

@dp.callback_query(F.data.startswith("admin_reject:"))
async def admin_reject(call: CallbackQuery, state: FSMContext):
    try:
        if not call.message or call.message.chat.id != ADMIN_GROUP_ID:
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        await safe_call_answer(call)
        parts = call.data.split(":")
        uid = int(parts[1])
        view_mode = len(parts) > 2 and parts[2] == "view"
        await state.set_state(ApplicationStates.admin_reject_reason)
        await state.update_data(reject_uid=uid, reject_view=view_mode)
        await update_admin_menu_message(
            "✍️ Укажи причину отказа:\n\n"
            "Можно выбрать готовый вариант или написать свой текст.",
            reject_templates_keyboard()
        )
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка в admin_reject")
        await safe_call_answer(call, "Ошибка при открытии отказа", show_alert=True)

@dp.callback_query(F.data.startswith("reject_tpl:"))
async def reject_template(call: CallbackQuery, state: FSMContext):
    try:
        if not call.message or call.message.chat.id != ADMIN_GROUP_ID:
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        await safe_call_answer(call)
        tpl_code = call.data.split(":", 1)[1]
        data = await state.get_data()
        uid = data.get("reject_uid")
        if not uid:
            await safe_call_answer(call, "🤍 Не вижу кандидата")
            return

        templates = {
            "1": "Сейчас, к сожалению, мы не можем принять заявку.",
            "2": "Сейчас условия не совпали, но спасибо за интерес.",
            "3": "Мы вернёмся к твоей анкете чуть позже. Спасибо за понимание.",
        }

        if tpl_code == "custom":
            await update_admin_menu_message(
                "✍️ Напиши свою причину отказа:",
                reject_reason_keyboard()
            )
            await safe_call_answer(call)
            return

        reason = templates.get(tpl_code)
        if not reason:
            await safe_call_answer(call, "🤍 Шаблон не найден")
            return

        try:
            user_lang = lang_for(uid)
            intro = t(user_lang, "rejected_reason_intro", reason=reason)
            caption = build_menu_caption_with_status(
                "rejected",
                t(user_lang, "menu_caption"),
                lang=user_lang,
                intro=intro
            )
            if not is_site_source(uid):
                await send_or_edit_user_menu(uid, caption, lang=user_lang)
                await clear_user_flow_message(uid)
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
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка в reject_template")
        await safe_call_answer(call, "Ошибка при отклонении", show_alert=True)

@dp.message(StateFilter(ApplicationStates.admin_reject_reason), F.text)
async def reject_reason(m: Message, state: FSMContext):
    try:
        if m.chat.id != ADMIN_GROUP_ID:
            return
        data = await state.get_data()
        uid = data.get("reject_uid")
        if not uid:
            await post_admin_menu()
            await state.clear()
            return

        try:
            user_lang = lang_for(uid)
            intro = t(user_lang, "rejected_reason_intro", reason=m.text)
            caption = build_menu_caption_with_status(
                "rejected",
                t(user_lang, "menu_caption"),
                lang=user_lang,
                intro=intro
            )
            if not is_site_source(uid):
                await send_or_edit_user_menu(uid, caption, lang=user_lang)
                await clear_user_flow_message(uid)
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
        await safe_call_answer(call, f"Статус: {status_label}", show_alert=False)
    except Exception:
        await safe_call_answer(call, "Статус обновлён", show_alert=False)

@dp.callback_query(F.data.startswith("admin_photos:"))
async def admin_photos(call: CallbackQuery):
    try:
        if not call.message:
            await safe_call_answer(call, "Сообщение недоступно", show_alert=False)
            return
        uid = int(call.data.split(":", 1)[1])
        data = get_form_data(uid) or {}
        contact_url = contact_url_for_user(uid, data)
        photo_id = data.get("photo_face") or data.get("photo_full")
        if not photo_id:
            await safe_call_answer(call, "Фото не найдено", show_alert=False)
            return
        status = get_status(uid) or "pending"
        text = build_admin_full_text(data, uid, status)
        await update_admin_view_message(
            text,
            admin_list_view_keyboard(uid, status, "all", 0, 1, ADMIN_LIST_LIMIT, contact_url=contact_url),
            photo_id
        )
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка отправки фото админу")
        await safe_call_answer(call, "Не удалось отправить фото", show_alert=False)

@dp.message(F.text == "/admin", F.chat.id == ADMIN_GROUP_ID)
async def admin_menu(message: Message):
    await clear_admin_temp_messages()
    await ensure_admin_menu_posted()

@dp.callback_query(F.data.startswith("admin_menu:"))
async def admin_menu_action(call: CallbackQuery):
    try:
        if not call.message or call.message.chat.id != ADMIN_GROUP_ID:
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        await safe_call_answer(call)
        await clear_admin_temp_messages()
        action = call.data.split(":", 1)[1]
        if action in {"pending", "accepted", "rejected", "all"}:
            await clear_admin_notify()
            await send_admin_list(call, action, 0)
            return
        if action == "stats":
            await clear_admin_view_message()
            await update_admin_menu_message(
                build_admin_stats_text(),
                admin_menu_keyboard(get_status_counts())
            )
            return
        if action == "excel":
            await clear_admin_view_message()
            if not rebuild_excel_from_db:
                await update_admin_menu_message(
                    "🤍 Экспорт в Excel недоступен. Установи openpyxl.",
                    admin_menu_keyboard(get_status_counts())
                )
                return
            file_path = rebuild_excel_from_db()
            if not file_path:
                await update_admin_menu_message(
                    "🤍 Файл Excel ещё не создан. Отправь хотя бы одну заявку ✨",
                    admin_menu_keyboard(get_status_counts())
                )
                return
            msg = await call.message.answer_document(FSInputFile(str(file_path)))
            track_admin_temp_message(msg.message_id)
            return
        if action == "archive":
            await clear_admin_view_message()
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
            return
        if action == "reset":
            await clear_admin_view_message()
            await update_admin_menu_message(
                "⚠️ Ты уверена, что хочешь полностью обнулить базу и статистику?",
                confirm_reset_db_keyboard()
            )
            return
        if action == "refresh":
            await clear_admin_view_message()
            await post_admin_menu()
            return
        await safe_call_answer(call, "Неизвестная команда", show_alert=False)
    except Exception:
        logger.exception("Ошибка в admin_menu_action")
        await safe_call_answer(call, "Ошибка выполнения команды", show_alert=False)

@dp.callback_query(F.data.startswith("admin_list:"))
async def admin_list_pagination(call: CallbackQuery):
    try:
        _, filter_key, offset_raw = call.data.split(":", 2)
        offset = int(offset_raw)
    except Exception:
        await safe_call_answer(call, "Ошибка пагинации", show_alert=False)
        return
    try:
        await send_admin_list(call, filter_key, offset)
    except Exception:
        logger.exception("Ошибка пагинации списка")
        await safe_call_answer(call, "Не удалось открыть страницу", show_alert=False)

@dp.callback_query(F.data.startswith("admin_view_photo:"))
async def admin_view_photo(call: CallbackQuery):
    try:
        if not call.message:
            await safe_call_answer(call, "Сообщение недоступно", show_alert=False)
            return
        _, uid_raw, photo_type, filter_key, offset_raw = call.data.split(":", 4)
        uid = int(uid_raw)
        offset = int(offset_raw)
        data = get_form_data(uid) or {}
        contact_url = contact_url_for_user(uid, data)
        photo_id = data.get("photo_face") if photo_type == "face" else data.get("photo_full")
        if not photo_id:
            await safe_call_answer(call, "Фото не найдено", show_alert=False)
            return
        status = get_status(uid) or "pending"
        label = _admin_list_label(filter_key)
        total = len(list_applications(None if filter_key == "all" else filter_key))
        if total == 0:
            await safe_call_answer(call)
            return
        page = offset // ADMIN_LIST_LIMIT + 1
        pages = (total + ADMIN_LIST_LIMIT - 1) // ADMIN_LIST_LIMIT
        text = (
            f"🗂 <b>{label}</b>\n\n"
            f"Заявка <b>{offset + 1}</b> из <b>{total}</b>\n"
            f"Страница: <b>{page}/{pages}</b>\n\n"
            f"{build_admin_full_text(data, uid, status)}"
        )
        await update_admin_view_message(
            text,
            admin_list_view_keyboard(uid, status, filter_key, offset, total, ADMIN_LIST_LIMIT, contact_url=contact_url),
            photo_id
        )
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка переключения фото")
        await safe_call_answer(call, "Не удалось показать фото", show_alert=False)

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
    await safe_call_answer(call)

@dp.callback_query(F.data == "admin_reset_db:cancel")
async def admin_reset_db_cancel(call: CallbackQuery):
    await post_admin_menu()
    await safe_call_answer(call, "Отменено")

        
@dp.callback_query(F.data == "portfolio_reviews")
async def portfolio_reviews(call: CallbackQuery):
    try:
        lang = lang_for(call.from_user.id)
        if not call.message:
            await safe_call_answer(call, t(lang, "temp_error_retry"), show_alert=False)
            return
        await clear_portfolio_media(call.from_user.id)
        messages = await call.message.answer_media_group([
            InputMediaPhoto(media=FSInputFile("media/review1.jpg")),
            InputMediaPhoto(media=FSInputFile("media/review2.jpg")),
        ])
        track_portfolio_media(call.from_user.id, [m.message_id for m in messages])
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка в portfolio_reviews")
        await safe_call_answer(call, t(lang_for(call.from_user.id), "portfolio_send_error"), show_alert=False)

@dp.callback_query(F.data == "portfolio_videos")
async def portfolio_streams(call: CallbackQuery):
    try:
        lang = lang_for(call.from_user.id)
        if not call.message:
            await safe_call_answer(call, t(lang, "temp_error_retry"), show_alert=False)
            return
        await clear_portfolio_media(call.from_user.id)
        now = datetime.now(timezone.utc)
        last = PORTFOLIO_VIDEO_LAST.get(call.from_user.id)
        if last and (now - last).total_seconds() < PORTFOLIO_COOLDOWN_SECONDS:
            await safe_call_answer(call, t(lang, "video_cooldown"))
            return
        PORTFOLIO_VIDEO_LAST[call.from_user.id] = now
        messages = await call.message.answer_media_group([
            InputMediaVideo(media=FSInputFile("media/stream1.MP4")),
            InputMediaVideo(media=FSInputFile("media/stream2.MP4")),
        ])
        track_portfolio_media(call.from_user.id, [m.message_id for m in messages])
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка в portfolio_streams")
        await safe_call_answer(call, t(lang_for(call.from_user.id), "video_send_error"), show_alert=False)

@dp.callback_query(F.data == "portfolio_pdf")
async def portfolio_pdf(call: CallbackQuery):
    try:
        lang = lang_for(call.from_user.id)
        if not call.message:
            await safe_call_answer(call, t(lang, "temp_error_retry"), show_alert=False)
            return
        await clear_portfolio_media(call.from_user.id)
        base_dir = Path(__file__).resolve().parent
        candidates = [
            base_dir / "media" / "portfolio.pdf",
            base_dir / "web" / "assets" / "portfolio.pdf",
        ]
        pdf_path = next((p for p in candidates if p.exists()), None)
        if not pdf_path:
            raise FileNotFoundError("portfolio.pdf не найден ни в media, ни в web/assets")
        msg = await call.message.answer_document(
            FSInputFile(str(pdf_path))
        )
        track_portfolio_media(call.from_user.id, [msg.message_id])
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка в portfolio_pdf")
        await safe_call_answer(call, t(lang_for(call.from_user.id), "pdf_send_error"), show_alert=False)

# ================= ADMIN STATS =================

@dp.message(F.text == "/stats", F.chat.id == ADMIN_GROUP_ID)
async def admin_stats(message: Message):
    await clear_admin_temp_messages()
    msg = await message.answer(build_admin_stats_text())
    track_admin_temp_message(msg.message_id)

@dp.message(F.text == "/excel", F.chat.id == ADMIN_GROUP_ID)
async def admin_excel(message: Message):
    await clear_admin_temp_messages()
    if not rebuild_excel_from_db:
        msg = await message.answer("🤍 Экспорт в Excel недоступен. Установи openpyxl.")
        track_admin_temp_message(msg.message_id)
        return
    file_path = rebuild_excel_from_db()
    if not file_path:
        msg = await message.answer("🤍 Файл Excel ещё не создан. Отправь хотя бы одну заявку ✨")
        track_admin_temp_message(msg.message_id)
        return
    msg = await message.answer_document(FSInputFile(str(file_path)))
    track_admin_temp_message(msg.message_id)
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
