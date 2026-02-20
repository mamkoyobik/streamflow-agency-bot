import asyncio
import html
import json
import logging
import os
import random
import re
import traceback
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, FSInputFile,
    InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAnimation,
    ChatJoinRequest, InlineKeyboardMarkup, MessageEntity,
    BotCommand, BotCommandScopeDefault, BotCommandScopeChatAdministrators
)
try:
    from aiogram.client.default import DefaultBotProperties
except Exception:
    DefaultBotProperties = None
from aiogram.enums import ParseMode, ChatAction
from aiogram.exceptions import (
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramNetworkError,
    TelegramConflictError,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import StateFilter, Command

from config import (
    BOT_TOKEN,
    ADMIN_GROUP_ID,
    ADMIN_USERNAME,
    CHANNEL_ID,
    CHANNEL_EN_ID,
    CHANNEL_PT_ID,
    CHANNEL_ES_ID,
    CHANNEL_ID_BY_LANG,
    CHANNEL_IDS,
)
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
    list_applications_by_stage,
    get_application_stage_counts,
    get_source_counts,
    set_menu_message_id,
    get_menu_message_id,
    set_flow_message_id,
    get_flow_message_id,
    set_source,
    get_source,
    get_user_language,
    set_user_language,
    has_user_language,
    create_posted_message,
    get_posted_message,
    list_posted_messages,
    count_posted_messages,
    update_posted_message,
    delete_posted_message,
    delete_application,
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

@dp.chat_join_request()
async def on_join_request(req: ChatJoinRequest):
    chat_id = req.chat.id
    try:
        user_id = req.from_user.id
        await bot.approve_chat_join_request(chat_id, user_id)

        channel_lang = "ru"
        for lang_code, configured_chat_id in CHANNEL_ID_BY_LANG.items():
            if configured_chat_id is not None and chat_id == configured_chat_id:
                channel_lang = lang_code
                break
        else:
            title = (req.chat.title or "").strip().lower()
            username = (req.chat.username or "").strip().lower()
            hint = f"{title} {username}"
            if any(token in hint for token in ("english", " eng", "_en", "-en", " en ")):
                channel_lang = "en"
            elif any(token in hint for token in ("portugu", "brazil", "brasil", " pt", "_pt", "-pt")):
                channel_lang = "pt"
            elif any(token in hint for token in ("spanish", "españ", "espan", " latino", " latam", " es", "_es", "-es")):
                channel_lang = "es"

            logger.warning(
                "Join request from unconfigured channel: id=%s title=%r username=%r; inferred_lang=%s",
                chat_id,
                req.chat.title,
                req.chat.username,
                channel_lang,
            )

        had_lang_before = has_user_language(user_id)
        already_in_bot = (
            had_lang_before
            or get_application(user_id) is not None
            or bool(get_menu_message_id(user_id))
            or bool(get_flow_message_id(user_id))
        )
        if not had_lang_before:
            set_user_language(user_id, channel_lang)

        if already_in_bot:
            logger.info(
                "Join request approved without повторного /start prompt: user_id=%s chat_id=%s",
                user_id,
                chat_id,
            )
            return

        invite_by_lang = {
            "en": "🤍 Your request to join the private channel is approved.\n\nPress /start ✨",
            "pt": "🤍 Sua solicitação para entrar no canal privado foi aprovada.\n\nToque em /start ✨",
            "es": "🤍 Tu solicitud para entrar al canal privado fue aprobada.\n\nPulsa /start ✨",
            "ru": "🤍 Ты подала заявку в закрытый канал\n\nНажми /start ✨",
        }
        invite_message = invite_by_lang.get(channel_lang, invite_by_lang["ru"])
        await bot.send_message(
            user_id,
            invite_message
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
    normalized = normalize_birthdate(text)
    if not normalized:
        return False
    try:
        birth_date = datetime.strptime(normalized, "%d.%m.%Y").date()
    except ValueError:
        return False
    today = datetime.now().date()
    age = today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    return age >= 18

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
        if len(digits) == 11 and digits.startswith("8"):
            digits = "7" + digits[1:]
        return f"+{digits}"
    if value.startswith("00"):
        digits = value[2:]
        if not digits.isdigit():
            return None
        if len(digits) == 11 and digits.startswith("8"):
            digits = "7" + digits[1:]
        return f"+{digits}"
    if value.isdigit():
        digits = value
        if len(digits) == 11 and digits.startswith("8"):
            digits = "7" + digits[1:]
        return f"+{digits}"
    return None


PHONE_COUNTRY_BY_CODE = {
    "1": "United States/Canada",
    "7": "Russia/Kazakhstan",
    "20": "Egypt",
    "27": "South Africa",
    "30": "Greece",
    "31": "Netherlands",
    "32": "Belgium",
    "33": "France",
    "34": "Spain",
    "39": "Italy",
    "40": "Romania",
    "44": "United Kingdom",
    "48": "Poland",
    "49": "Germany",
    "51": "Peru",
    "52": "Mexico",
    "53": "Cuba",
    "54": "Argentina",
    "55": "Brazil",
    "56": "Chile",
    "57": "Colombia",
    "58": "Venezuela",
    "60": "Malaysia",
    "61": "Australia",
    "62": "Indonesia",
    "63": "Philippines",
    "64": "New Zealand",
    "65": "Singapore",
    "66": "Thailand",
    "81": "Japan",
    "82": "South Korea",
    "84": "Vietnam",
    "86": "China",
    "90": "Turkey",
    "91": "India",
    "92": "Pakistan",
    "93": "Afghanistan",
    "94": "Sri Lanka",
    "95": "Myanmar",
    "98": "Iran",
    "211": "South Sudan",
    "212": "Morocco",
    "213": "Algeria",
    "216": "Tunisia",
    "218": "Libya",
    "220": "Gambia",
    "221": "Senegal",
    "222": "Mauritania",
    "223": "Mali",
    "224": "Guinea",
    "225": "Ivory Coast",
    "226": "Burkina Faso",
    "227": "Niger",
    "228": "Togo",
    "229": "Benin",
    "230": "Mauritius",
    "231": "Liberia",
    "232": "Sierra Leone",
    "233": "Ghana",
    "234": "Nigeria",
    "235": "Chad",
    "236": "Central African Republic",
    "237": "Cameroon",
    "238": "Cape Verde",
    "239": "Sao Tome and Principe",
    "240": "Equatorial Guinea",
    "241": "Gabon",
    "242": "Congo",
    "243": "DR Congo",
    "244": "Angola",
    "245": "Guinea-Bissau",
    "248": "Seychelles",
    "249": "Sudan",
    "250": "Rwanda",
    "251": "Ethiopia",
    "252": "Somalia",
    "253": "Djibouti",
    "254": "Kenya",
    "255": "Tanzania",
    "256": "Uganda",
    "257": "Burundi",
    "258": "Mozambique",
    "260": "Zambia",
    "261": "Madagascar",
    "262": "Reunion",
    "263": "Zimbabwe",
    "264": "Namibia",
    "265": "Malawi",
    "266": "Lesotho",
    "267": "Botswana",
    "268": "Eswatini",
    "269": "Comoros",
    "290": "Saint Helena",
    "291": "Eritrea",
    "297": "Aruba",
    "298": "Faroe Islands",
    "299": "Greenland",
    "351": "Portugal",
    "352": "Luxembourg",
    "353": "Ireland",
    "354": "Iceland",
    "355": "Albania",
    "356": "Malta",
    "357": "Cyprus",
    "358": "Finland",
    "359": "Bulgaria",
    "370": "Lithuania",
    "371": "Latvia",
    "372": "Estonia",
    "373": "Moldova",
    "374": "Armenia",
    "375": "Belarus",
    "376": "Andorra",
    "377": "Monaco",
    "378": "San Marino",
    "380": "Ukraine",
    "381": "Serbia",
    "382": "Montenegro",
    "383": "Kosovo",
    "385": "Croatia",
    "386": "Slovenia",
    "387": "Bosnia and Herzegovina",
    "389": "North Macedonia",
    "420": "Czech Republic",
    "421": "Slovakia",
    "423": "Liechtenstein",
    "500": "Falkland Islands",
    "501": "Belize",
    "502": "Guatemala",
    "503": "El Salvador",
    "504": "Honduras",
    "505": "Nicaragua",
    "506": "Costa Rica",
    "507": "Panama",
    "508": "Saint Pierre and Miquelon",
    "509": "Haiti",
    "590": "Guadeloupe",
    "591": "Bolivia",
    "592": "Guyana",
    "593": "Ecuador",
    "594": "French Guiana",
    "595": "Paraguay",
    "596": "Martinique",
    "597": "Suriname",
    "598": "Uruguay",
    "599": "Curacao",
    "670": "Timor-Leste",
    "672": "Australian External Territories",
    "673": "Brunei",
    "674": "Nauru",
    "675": "Papua New Guinea",
    "676": "Tonga",
    "677": "Solomon Islands",
    "678": "Vanuatu",
    "679": "Fiji",
    "680": "Palau",
    "681": "Wallis and Futuna",
    "682": "Cook Islands",
    "683": "Niue",
    "685": "Samoa",
    "686": "Kiribati",
    "687": "New Caledonia",
    "688": "Tuvalu",
    "689": "French Polynesia",
    "690": "Tokelau",
    "691": "Micronesia",
    "692": "Marshall Islands",
    "850": "North Korea",
    "852": "Hong Kong",
    "853": "Macau",
    "855": "Cambodia",
    "856": "Laos",
    "880": "Bangladesh",
    "886": "Taiwan",
    "960": "Maldives",
    "961": "Lebanon",
    "962": "Jordan",
    "963": "Syria",
    "964": "Iraq",
    "965": "Kuwait",
    "966": "Saudi Arabia",
    "967": "Yemen",
    "968": "Oman",
    "970": "Palestine",
    "971": "UAE",
    "972": "Israel",
    "973": "Bahrain",
    "974": "Qatar",
    "975": "Bhutan",
    "976": "Mongolia",
    "977": "Nepal",
    "992": "Tajikistan",
    "993": "Turkmenistan",
    "994": "Azerbaijan",
    "995": "Georgia",
    "996": "Kyrgyzstan",
    "998": "Uzbekistan",
}
PHONE_COUNTRY_CODES_SORTED = sorted(PHONE_COUNTRY_BY_CODE.keys(), key=len, reverse=True)


def country_from_phone(phone: str | None) -> str | None:
    normalized = normalize_phone(phone or "")
    if not normalized:
        return None
    digits = re.sub(r"\D", "", normalized)
    if not digits:
        return None
    for code in PHONE_COUNTRY_CODES_SORTED:
        if digits.startswith(code):
            return PHONE_COUNTRY_BY_CODE[code]
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

def extract_start_payload(text: str | None) -> str:
    raw = (text or "").strip()
    if not raw:
        return ""
    parts = raw.split(maxsplit=1)
    if not parts:
        return ""
    if not parts[0].startswith("/start"):
        return ""
    if len(parts) < 2:
        return ""
    return parts[1].strip()

def extract_site_lead_start_data(start_payload: str | None) -> tuple[str | None, str | None]:
    raw = (start_payload or "").strip()
    match = SITE_START_PAYLOAD_RE.fullmatch(raw)
    if not match:
        return None, None
    token = match.group(1)
    lang = (match.group(2) or "").strip().lower()
    if lang not in {"ru", "en", "pt", "es"}:
        lang = None
    return token, lang

def _site_lead_setting_key(token: str) -> str:
    return f"{SITE_LEAD_TOKEN_PREFIX}{token}"

def consume_site_lead_payload(token: str) -> dict | None:
    key = _site_lead_setting_key(token)
    raw = get_setting(key)
    if not raw:
        return None
    try:
        payload = json.loads(raw)
    except Exception:
        set_setting(key, None)
        return None
    if not isinstance(payload, dict):
        set_setting(key, None)
        return None
    expires_at = _parse_ts(str(payload.get("expires_at") or "")) if payload.get("expires_at") else None
    if expires_at and expires_at < datetime.now(timezone.utc):
        set_setting(key, None)
        return None
    data = payload.get("data")
    if not isinstance(data, dict):
        set_setting(key, None)
        return None
    set_setting(key, None)
    return data

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
    "country",
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
    "lang",
    "application_stage",
    "site_lead_token",
}
OPTIONAL_FORM_DATA_FIELDS = {
    "country",
    "lang",
    "devices",
    "headphones",
    "photo_face",
    "photo_full",
    "site_lead_token",
}
REQUIRED_PREVIEW_FIELDS = {
    "name",
    "phone",
    "age",
    "device_model",
    "telegram",
    "city",
    "work_time",
    "experience",
    "living",
}

APPLICATION_STAGE_QUICK = "quick"
APPLICATION_STAGE_FULL = "full"
SITE_LEAD_TOKEN_PREFIX = "site_lead_token:"
SITE_START_PAYLOAD_RE = re.compile(r"^s2_([A-Za-z0-9]{10,128})(?:_([a-z]{2}))?$")

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

def _has_value(data: dict | None, key: str) -> bool:
    if not isinstance(data, dict):
        return False
    value = data.get(key)
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True

def detect_application_stage(data: dict | None) -> str:
    if not isinstance(data, dict):
        return APPLICATION_STAGE_FULL
    stage = str(data.get("application_stage") or "").strip().lower()
    if stage in {APPLICATION_STAGE_QUICK, APPLICATION_STAGE_FULL}:
        return stage
    if all(_has_value(data, field) for field in REQUIRED_PREVIEW_FIELDS):
        return APPLICATION_STAGE_FULL
    return APPLICATION_STAGE_QUICK

def is_quick_application(data: dict | None) -> bool:
    return detect_application_stage(data) == APPLICATION_STAGE_QUICK

def is_site_quick_application(app: dict | None, data: dict | None) -> bool:
    if not isinstance(app, dict):
        return False
    return app.get("source") == "site" and is_quick_application(data)

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

def _get_env_int(name: str, default: int, min_value: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        logger.warning("Некорректное значение %s=%r, использую %s", name, raw, default)
        return default
    return max(min_value, value)

def _get_env_float(name: str, default: float, min_value: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError:
        logger.warning("Некорректное значение %s=%r, использую %s", name, raw, default)
        return default
    return max(min_value, value)

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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_TRANSLATE_MODEL = os.getenv("OPENAI_TRANSLATE_MODEL", "gpt-4o-mini").strip()
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1").strip().rstrip("/")
POLLING_RETRY_BASE_SECONDS = _get_env_int("POLLING_RETRY_BASE_SECONDS", default=5, min_value=3)
POLLING_RETRY_MAX_SECONDS = max(
    POLLING_RETRY_BASE_SECONDS,
    _get_env_int("POLLING_RETRY_MAX_SECONDS", default=90, min_value=POLLING_RETRY_BASE_SECONDS),
)
POLLING_RETRY_JITTER_SECONDS = _get_env_float("POLLING_RETRY_JITTER_SECONDS", default=2.0, min_value=0.0)
POLLING_CONFLICT_SLEEP_SECONDS = max(
    POLLING_RETRY_BASE_SECONDS,
    _get_env_int("POLLING_CONFLICT_SLEEP_SECONDS", default=30, min_value=POLLING_RETRY_BASE_SECONDS),
)
CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
TELEGRAM_CAPTION_LIMIT = 1024
TELEGRAM_TEXT_LIMIT = 4096
POST_LANG_ORDER = ("ru", "en", "pt", "es")
LANG_TITLES = {"ru": "RU", "en": "EN", "pt": "PT", "es": "ES"}
REQUIRED_CROSSPOST_LANGS = ("en", "pt", "es")
LANG_ENV_HINTS = {
    "en": "CHANNEL_EN_ID / CHANNEL_ID_EN / EN_CHANNEL_ID / CHANNEL_ENG_ID / CHANNEL_EN / CHANNEL_ENGLISH_ID",
    "pt": "CHANNEL_PT_ID / CHANNEL_ID_PT / PT_CHANNEL_ID / CHANNEL_BR_ID / CHANNEL_PT / CHANNEL_PORTUGUESE_ID",
    "es": "CHANNEL_ES_ID / CHANNEL_ID_ES / ES_CHANNEL_ID / CHANNEL_SPANISH_ID / CHANNEL_ES / CHANNEL_LATAM_ID",
}
TRANSLATION_STYLE = {
    "en": "natural, conversational English",
    "pt": "natural, conversational Brazilian Portuguese",
    "es": "natural, conversational Latin American Spanish",
}
MEDIA_CONTENT_TYPES = {"photo", "video", "document", "animation"}
GENERIC_MARKER_RE = re.compile(r"\[\[(?:CE\d+|E\d+[SE]|LK\d+)\]\]")
CUSTOM_EMOJI_PLACEHOLDER = "⭐"
ANONYMOUS_ADMIN_BOT_ID = 1087968824
PUBLIC_MANAGER_HANDLE = "@streamflowmanager"
PUBLIC_MANAGER_USERNAME = PUBLIC_MANAGER_HANDLE.lstrip("@")
TRANSLATABLE_ENTITY_TYPES = {
    "bold",
    "italic",
    "underline",
    "strikethrough",
    "spoiler",
    "code",
    "pre",
    "text_link",
    "blockquote",
    "expandable_blockquote",
}
LOCKED_ENTITY_TYPES = {
    "url",
    "mention",
    "hashtag",
    "cashtag",
    "bot_command",
    "email",
    "phone_number",
}
STAGE2_BRIDGE_TEXTS = {
    "ru": {
        "gate": (
            "📣 Перед продолжением зайди в канал Streamflow.\n\n"
            "Как устроена работа:\n"
            "• удалённо, из дома\n"
            "• без 18+ контента\n"
            "• даём понятный старт и сопровождение\n"
            "• отвечаем по графику, выплатам и процессу\n\n"
            "Дальше выбери удобный формат:\n"
            "• быстро пройти всё в боте и подать заявку без переписок\n"
            f"• или написать {PUBLIC_MANAGER_HANDLE} и записаться через него"
        ),
        "step1": (
            "✅ Предзаявка сохранена.\n\n"
            "Ты уже в системе, и мы видим твой контакт.\n"
            "Сейчас коротко покажу, как всё происходит дальше."
        ),
        "step2": (
            "Как всё проходит:\n"
            "• получаешь понятный старт\n"
            "• двигаемся по шагам с поддержкой\n"
            "• выходим на стабильный результат\n\n"
            "Остался обязательный финальный блок (около 2 минут).\n"
            "Без него мы не сможем запустить старт."
        ),
        "autostart": (
            "✅ Отлично, короткая часть заполнена.\n"
            "Сразу переходим к финальному блоку, чтобы запустить старт без задержек."
        ),
        "next": "Что дальше",
        "start": "Продолжить этап 2 (обязательно)",
        "manager": f"💬 Написать {PUBLIC_MANAGER_HANDLE}",
        "menu_recommendation": (
            "✅ Первая часть анкеты принята мгновенно и автоматически.\n\n"
            "Чтобы быстрее понять формат, открой пункты:\n"
            "• 📁 Портфолио моделей\n"
            "• ℹ️ Подробнее о работе\n"
            "• 📣 Наш канал\n\n"
            "После этого нажми «🌸 Стать моделью» и продолжим.\n"
            f"Если останутся вопросы — пиши {PUBLIC_MANAGER_HANDLE}."
        ),
        "channel": "📣 Открыть канал",
        "continue_bot": "✅ Подать заявку через бота",
        "wait_gate": "Выбери один из вариантов ниже 👇",
        "wait": "Нажми кнопку, чтобы продолжить этап 2 👇",
        "expired": "Ссылка из сайта устарела. Нажми «Стать моделью» и заполни короткий этап заново.",
    },
    "en": {
        "gate": (
            "📣 Before continuing, open the Streamflow channel.\n\n"
            "How this work format looks:\n"
            "• fully remote, from home\n"
            "• no 18+ content\n"
            "• clear onboarding and support\n"
            "• transparent schedule, payouts and workflow\n\n"
            "Now choose your path:\n"
            "• complete everything in the bot and submit without extra chats\n"
            f"• or message {PUBLIC_MANAGER_HANDLE} and apply through them"
        ),
        "step1": (
            "✅ Pre-application saved.\n\n"
            "You are already in the system, and we have your contact.\n"
            "Now I’ll quickly explain what happens next."
        ),
        "step2": (
            "How it works:\n"
            "• clear onboarding\n"
            "• step-by-step support\n"
            "• focus on stable results\n\n"
            "One required final block is left (about 2 minutes).\n"
            "Without it, we can’t launch your start."
        ),
        "autostart": (
            "✅ Great, the short part is done.\n"
            "Let’s move straight to the final required block to launch your start faster."
        ),
        "next": "What’s next",
        "start": "Continue Step 2 (required)",
        "manager": f"💬 Message {PUBLIC_MANAGER_HANDLE}",
        "menu_recommendation": (
            "✅ The first part of your application was accepted instantly and automatically.\n\n"
            "To understand the format better, open these sections:\n"
            "• 📁 Model portfolio\n"
            "• ℹ️ About the work\n"
            "• 📣 Our channel\n\n"
            "Then tap “🌸 Become a model” to continue.\n"
            f"If you have questions, message {PUBLIC_MANAGER_HANDLE}."
        ),
        "channel": "📣 Open channel",
        "continue_bot": "✅ Apply through bot",
        "wait_gate": "Choose one option below 👇",
        "wait": "Tap the button to continue Step 2 👇",
        "expired": "Your website link has expired. Tap “Become a model” and submit the short step again.",
    },
    "pt": {
        "gate": (
            "📣 Antes de continuar, abra o canal Streamflow.\n\n"
            "Como funciona o trabalho:\n"
            "• remoto, de casa\n"
            "• sem conteúdo 18+\n"
            "• início claro com suporte\n"
            "• regras transparentes de rotina, pagamento e processo\n\n"
            "Agora escolha o caminho:\n"
            "• concluir tudo no bot e enviar sem perder tempo em chats\n"
            f"• ou falar com {PUBLIC_MANAGER_HANDLE} e se cadastrar por ele"
        ),
        "step1": (
            "✅ Pré-cadastro salvo.\n\n"
            "Você já está no sistema e já temos seu contato.\n"
            "Agora eu te explico rapidamente o próximo passo."
        ),
        "step2": (
            "Como funciona:\n"
            "• início claro\n"
            "• suporte passo a passo\n"
            "• foco em resultado estável\n\n"
            "Falta um bloco final obrigatório (cerca de 2 minutos).\n"
            "Sem isso, não conseguimos iniciar seu começo."
        ),
        "autostart": (
            "✅ Perfeito, a parte curta já está pronta.\n"
            "Vamos direto para o bloco final obrigatório para acelerar seu início."
        ),
        "next": "Próximo passo",
        "start": "Continuar Etapa 2 (obrigatória)",
        "manager": f"💬 Falar com {PUBLIC_MANAGER_HANDLE}",
        "menu_recommendation": (
            "✅ A primeira parte do cadastro foi aceita de forma instantânea e automática.\n\n"
            "Para entender melhor o formato, abra as seções:\n"
            "• 📁 Portfólio de modelos\n"
            "• ℹ️ Sobre o trabalho\n"
            "• 📣 Nosso canal\n\n"
            "Depois toque em “🌸 Tornar-se modelo” para continuar.\n"
            f"Se tiver dúvidas, fale com {PUBLIC_MANAGER_HANDLE}."
        ),
        "channel": "📣 Abrir canal",
        "continue_bot": "✅ Enviar pelo bot",
        "wait_gate": "Escolha uma opção abaixo 👇",
        "wait": "Toque no botão para continuar a Etapa 2 👇",
        "expired": "Seu link do site expirou. Toque em “Become a model” e preencha a etapa curta novamente.",
    },
    "es": {
        "gate": (
            "📣 Antes de continuar, abre el canal de Streamflow.\n\n"
            "Cómo es el trabajo:\n"
            "• remoto, desde casa\n"
            "• sin contenido 18+\n"
            "• inicio claro con acompañamiento\n"
            "• reglas transparentes sobre horario, pagos y proceso\n\n"
            "Ahora elige tu camino:\n"
            "• completar todo en el bot y enviar sin perder tiempo en chats\n"
            f"• o escribir a {PUBLIC_MANAGER_HANDLE} y registrarte por su vía"
        ),
        "step1": (
            "✅ Pre-solicitud guardada.\n\n"
            "Ya estás en el sistema y ya tenemos tu contacto.\n"
            "Ahora te explico rápido el siguiente paso."
        ),
        "step2": (
            "Cómo funciona:\n"
            "• inicio claro\n"
            "• acompañamiento paso a paso\n"
            "• enfoque en resultados estables\n\n"
            "Queda un bloque final obligatorio (unos 2 minutos).\n"
            "Sin eso no podemos activar tu inicio."
        ),
        "autostart": (
            "✅ Perfecto, la parte corta ya está lista.\n"
            "Vamos directo al bloque final obligatorio para activar tu inicio más rápido."
        ),
        "next": "Qué sigue",
        "start": "Continuar Etapa 2 (obligatoria)",
        "manager": f"💬 Escribir a {PUBLIC_MANAGER_HANDLE}",
        "menu_recommendation": (
            "✅ La primera parte de tu solicitud fue aceptada al instante y de forma automática.\n\n"
            "Para conocer mejor el formato, abre estas secciones:\n"
            "• 📁 Portafolio de modelos\n"
            "• ℹ️ Sobre el trabajo\n"
            "• 📣 Nuestro canal\n\n"
            "Después pulsa “🌸 Ser modelo” para continuar.\n"
            f"Si tienes preguntas, escribe a {PUBLIC_MANAGER_HANDLE}."
        ),
        "channel": "📣 Abrir canal",
        "continue_bot": "✅ Enviar por el bot",
        "wait_gate": "Elige una opción abajo 👇",
        "wait": "Pulsa el botón para continuar la Etapa 2 👇",
        "expired": "Tu enlace del sitio venció. Pulsa “Become a model” y completa de nuevo la etapa corta.",
    },
}

def stage2_text(lang: str, key: str) -> str:
    locale = normalize_lang(lang)
    return STAGE2_BRIDGE_TEXTS.get(locale, STAGE2_BRIDGE_TEXTS["ru"]).get(
        key, STAGE2_BRIDGE_TEXTS["ru"][key]
    )

def manager_contact_url() -> str | None:
    manager_username = PUBLIC_MANAGER_USERNAME or ADMIN_USERNAME.lstrip("@").strip()
    if not manager_username:
        return None
    return f"https://t.me/{manager_username}"

def stage2_keyboard_step1(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=stage2_text(lang, "next"), callback_data="stage2_intro_next")],
            [InlineKeyboardButton(text=t(lang, "menu_home"), callback_data="main_menu")],
        ]
    )

def stage2_keyboard_step2(lang: str) -> InlineKeyboardMarkup:
    manager_url = manager_contact_url()
    rows = [
        [InlineKeyboardButton(text=stage2_text(lang, "start"), callback_data="stage2_start")],
    ]
    if manager_url:
        rows.append([InlineKeyboardButton(text=stage2_text(lang, "manager"), url=manager_url)])
    rows.append([InlineKeyboardButton(text=t(lang, "menu_home"), callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def _normalize_telegram_url(value: str | None) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    if raw.startswith("@"):
        return f"https://t.me/{raw.lstrip('@')}"
    if raw.startswith("t.me/") or raw.startswith("telegram.me/"):
        return f"https://{raw}"
    return raw

def _safe_http_url(value: str | None) -> str:
    normalized = _normalize_telegram_url(value)
    if not normalized:
        return ""
    try:
        parsed = urllib.parse.urlparse(normalized)
    except Exception:
        return ""
    if parsed.scheme not in {"http", "https"}:
        return ""
    if not parsed.netloc:
        return ""
    return normalized

def _first_nonempty_env(*names: str) -> str:
    for name in names:
        raw = os.getenv(name, "").strip()
        if raw:
            return raw
    return ""

DEFAULT_CHANNEL_PUBLIC_LINK = "https://t.me/streamflowagency"
CHANNEL_PUBLIC_LINK = _safe_http_url(
    _first_nonempty_env("CHANNEL_LINK", "CHANNEL_PUBLIC_LINK")
    or DEFAULT_CHANNEL_PUBLIC_LINK
) or DEFAULT_CHANNEL_PUBLIC_LINK
CHANNEL_LINK_BY_LANG = {
    "ru": _safe_http_url(
        _first_nonempty_env(
            "CHANNEL_LINK_RU",
            "RU_CHANNEL_LINK",
            "CHANNEL_RU_LINK",
        )
    )
    or CHANNEL_PUBLIC_LINK,
    "en": _safe_http_url(
        _first_nonempty_env(
            "CHANNEL_LINK_EN",
            "EN_CHANNEL_LINK",
            "CHANNEL_EN_LINK",
            "CHANNEL_ENGLISH_LINK",
        )
    )
    or CHANNEL_PUBLIC_LINK,
    "pt": _safe_http_url(
        _first_nonempty_env(
            "CHANNEL_LINK_PT",
            "PT_CHANNEL_LINK",
            "CHANNEL_PT_LINK",
            "CHANNEL_BR_LINK",
            "CHANNEL_PORTUGUESE_LINK",
        )
    )
    or CHANNEL_PUBLIC_LINK,
    "es": _safe_http_url(
        _first_nonempty_env(
            "CHANNEL_LINK_ES",
            "ES_CHANNEL_LINK",
            "CHANNEL_ES_LINK",
            "CHANNEL_SPANISH_LINK",
            "CHANNEL_LATAM_LINK",
        )
    )
    or CHANNEL_PUBLIC_LINK,
}

def stage2_channel_link(lang: str) -> str:
    locale = normalize_lang(lang)
    return CHANNEL_LINK_BY_LANG.get(locale) or CHANNEL_PUBLIC_LINK

def stage2_gate_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=stage2_text(lang, "channel"), url=stage2_channel_link(lang))],
    ]
    manager_url = manager_contact_url()
    if manager_url:
        rows.append([InlineKeyboardButton(text=stage2_text(lang, "manager"), url=manager_url)])
    rows.append([InlineKeyboardButton(text=stage2_text(lang, "continue_bot"), callback_data="stage2_gate_continue")])
    rows.append([InlineKeyboardButton(text=t(lang, "menu_home"), callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
        return value if value > 0 else default
    except Exception:
        return default


OPENAI_HTTP_TIMEOUT_SECONDS = _env_int("OPENAI_HTTP_TIMEOUT_SECONDS", 30)


def active_post_channels() -> dict[str, int]:
    result: dict[str, int] = {}
    for lang in POST_LANG_ORDER:
        chat_id = CHANNEL_ID_BY_LANG.get(lang)
        if isinstance(chat_id, int):
            result[lang] = chat_id
    return result


def missing_crosspost_langs(channels: dict[str, int] | None = None) -> list[str]:
    available = channels or active_post_channels()
    return [lang for lang in REQUIRED_CROSSPOST_LANGS if lang not in available]


async def setup_bot_commands() -> None:
    user_commands = [
        BotCommand(command="start", description="Открыть меню"),
        BotCommand(command="language", description="Сменить язык"),
    ]
    admin_commands = [
        BotCommand(command="admin", description="Открыть админ-меню"),
        BotCommand(command="create_post", description="Создать пост и кросспост"),
        BotCommand(command="crosspost", description="Алиас команды create_post"),
        BotCommand(command="stats", description="Показать статистику"),
        BotCommand(command="excel", description="Выгрузить Excel"),
        BotCommand(command="reset_db", description="Сбросить базу (опасно)"),
    ]
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())
    await bot.set_my_commands(
        admin_commands,
        scope=BotCommandScopeChatAdministrators(chat_id=ADMIN_GROUP_ID),
    )


def extract_post_text(message: Message) -> str:
    return (message.text or message.caption or "").strip()


def extract_post_text_and_entities(message: Message) -> tuple[str, list[MessageEntity]]:
    if message.text is not None:
        return message.text, list(message.entities or [])
    if message.caption is not None:
        return message.caption, list(message.caption_entities or [])
    return "", []


def post_creator_prompt() -> str:
    channels = active_post_channels()
    langs = ", ".join(LANG_TITLES[lang] for lang in POST_LANG_ORDER if lang in channels) or "RU"
    text = (
        "📝 <b>Создание поста</b>\n\n"
        "Отправь один пост <b>на русском</b> (текст или медиа с подписью).\n"
        "Я автоматически переведу и опубликую его в каналы:\n"
        f"{langs}\n\n"
        "Чтобы выйти без публикации, нажми «Отменить»."
    )
    missing_langs = missing_crosspost_langs(channels)
    if missing_langs:
        missing_titles = ", ".join(LANG_TITLES[lang] for lang in missing_langs)
        env_hints = "\n".join(f"{LANG_TITLES[lang]}: {LANG_ENV_HINTS.get(lang, '-')}" for lang in missing_langs)
        text += (
            "\n\n⚠️ <b>Кросспост настроен не полностью</b>\n"
            f"Не хватает каналов: {missing_titles}.\n"
            "Проверь env bot-сервиса:\n"
            f"{env_hints}"
        )
    return text


def _extract_openai_text(payload: dict) -> str:
    choices = payload.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text" and item.get("text"):
                text_parts.append(str(item["text"]))
        return "".join(text_parts).strip()
    return ""


def utf16_length(value: str) -> int:
    return len(value.encode("utf-16-le")) // 2


def utf16_offset_to_index(text: str, utf16_offset: int) -> int:
    if utf16_offset <= 0:
        return 0
    units = 0
    for idx, char in enumerate(text):
        units += utf16_length(char)
        if units >= utf16_offset:
            return idx + 1
    return len(text)


def tokens_intact(text: str, expected_tokens: list[str]) -> bool:
    if not expected_tokens:
        return True
    found_tokens = [match.group(0) for match in GENERIC_MARKER_RE.finditer(text)]
    if found_tokens != expected_tokens:
        return False
    return all(text.count(token) == 1 for token in expected_tokens)


def entity_to_dict(entity: MessageEntity) -> dict:
    try:
        return entity.model_dump(exclude_none=True)
    except Exception:
        try:
            return entity.dict(exclude_none=True)
        except Exception:
            return {}


def entities_to_dicts(entities: list[MessageEntity] | None) -> list[dict]:
    if not entities:
        return []
    payload: list[dict] = []
    for entity in entities:
        data = entity_to_dict(entity)
        if data:
            payload.append(data)
    return payload


def dicts_to_entities(payload: list[dict] | None) -> list[MessageEntity] | None:
    if not payload:
        return None
    result: list[MessageEntity] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        try:
            result.append(MessageEntity(**item))
        except Exception:
            continue
    return result or None


def markerize_entities_for_translation(
    text: str,
    entities: list[MessageEntity] | None,
) -> tuple[str, list[str], list[dict], list[tuple[str, str]], list[tuple[str, str, str]]]:
    if not text:
        return text, [], [], [], []

    rich_specs: list[dict] = []
    replacement_spans: dict[int, tuple[int, str, str]] = {}
    custom_specs: list[tuple[str, str]] = []
    locked_specs: list[tuple[str, str, str]] = []

    for entity in (entities or []):
        entity_type = str(getattr(entity, "type", "") or "")
        start_u16 = int(getattr(entity, "offset", 0))
        end_u16 = start_u16 + int(getattr(entity, "length", 0))
        start = utf16_offset_to_index(text, start_u16)
        end = utf16_offset_to_index(text, end_u16)
        if end <= start:
            continue

        if entity_type == "custom_emoji":
            custom_emoji_id = getattr(entity, "custom_emoji_id", None)
            if not custom_emoji_id:
                continue
            token = f"[[CE{len(custom_specs)}]]"
            custom_specs.append((token, str(custom_emoji_id)))
            current = replacement_spans.get(start)
            if current is None or end > current[0]:
                replacement_spans[start] = (end, token, "custom")
            continue

        if entity_type in LOCKED_ENTITY_TYPES:
            token = f"[[LK{len(locked_specs)}]]"
            locked_specs.append((token, text[start:end], entity_type))
            current = replacement_spans.get(start)
            if current is None or end > current[0]:
                replacement_spans[start] = (end, token, "locked")
            continue

        if entity_type not in TRANSLATABLE_ENTITY_TYPES:
            continue

        spec = {
            "id": len(rich_specs),
            "type": entity_type,
            "start": start,
            "end": end,
        }
        if entity_type == "text_link":
            url = getattr(entity, "url", None)
            if url:
                spec["url"] = str(url)
        if entity_type == "pre":
            language = getattr(entity, "language", None)
            if language:
                spec["language"] = str(language)
        rich_specs.append(spec)

    starts: dict[int, list[dict]] = {}
    ends: dict[int, list[dict]] = {}
    for spec in rich_specs:
        starts.setdefault(int(spec["start"]), []).append(spec)
        ends.setdefault(int(spec["end"]), []).append(spec)

    markerized_parts: list[str] = []
    expected_tokens: list[str] = []
    idx = 0
    text_len = len(text)
    while idx <= text_len:
        ending = ends.get(idx, [])
        if ending:
            for spec in sorted(ending, key=lambda item: (-int(item["start"]), int(item["id"]))):
                token = f"[[E{int(spec['id'])}E]]"
                markerized_parts.append(token)
                expected_tokens.append(token)

        starting = starts.get(idx, [])
        if starting:
            for spec in sorted(starting, key=lambda item: (-int(item["end"]), int(item["id"]))):
                token = f"[[E{int(spec['id'])}S]]"
                markerized_parts.append(token)
                expected_tokens.append(token)

        if idx == text_len:
            break

        replacement = replacement_spans.get(idx)
        if replacement:
            end, token, _kind = replacement
            markerized_parts.append(token)
            expected_tokens.append(token)
            idx = end
            continue

        markerized_parts.append(text[idx])
        idx += 1

    return "".join(markerized_parts), expected_tokens, rich_specs, custom_specs, locked_specs


def restore_entities_from_markers(
    text: str,
    expected_tokens: list[str],
    rich_specs: list[dict],
    custom_specs: list[tuple[str, str]],
    locked_specs: list[tuple[str, str, str]],
) -> tuple[str, list[MessageEntity] | None]:
    if not expected_tokens:
        return text, None
    if not tokens_intact(text, expected_tokens):
        raise RuntimeError("⚠️ Переводчик повредил маркеры форматирования/ссылок. Попробуй отправить пост ещё раз.")

    rich_by_id = {int(spec["id"]): spec for spec in rich_specs}
    token_actions: dict[str, tuple] = {}
    for spec_id in rich_by_id:
        token_actions[f"[[E{spec_id}S]]"] = ("start", spec_id)
        token_actions[f"[[E{spec_id}E]]"] = ("end", spec_id)
    for idx, (token, custom_emoji_id) in enumerate(custom_specs):
        token_actions[token] = ("custom", idx, custom_emoji_id)
    for idx, (token, value, entity_type) in enumerate(locked_specs):
        token_actions[token] = ("locked", idx, value, entity_type)

    open_offsets: dict[int, int] = {}
    result_parts: list[str] = []
    result_entities: list[MessageEntity] = []
    cursor = 0
    utf16_cursor = 0
    for match in GENERIC_MARKER_RE.finditer(text):
        before = text[cursor:match.start()]
        if before:
            result_parts.append(before)
            utf16_cursor += utf16_length(before)

        token = match.group(0)
        action = token_actions.get(token)
        if action is None:
            result_parts.append(token)
            utf16_cursor += utf16_length(token)
            cursor = match.end()
            continue

        if action[0] == "start":
            open_offsets[int(action[1])] = utf16_cursor
        elif action[0] == "end":
            spec_id = int(action[1])
            start_offset = open_offsets.pop(spec_id, None)
            if start_offset is not None:
                length = utf16_cursor - start_offset
                if length > 0:
                    spec = rich_by_id.get(spec_id) or {}
                    kwargs = {
                        "type": str(spec.get("type") or ""),
                        "offset": start_offset,
                        "length": length,
                    }
                    if kwargs["type"] == "text_link" and spec.get("url"):
                        kwargs["url"] = str(spec["url"])
                    if kwargs["type"] == "pre" and spec.get("language"):
                        kwargs["language"] = str(spec["language"])
                    try:
                        result_entities.append(MessageEntity(**kwargs))
                    except Exception:
                        pass
        elif action[0] == "custom":
            custom_emoji_id = str(action[2])
            result_parts.append(CUSTOM_EMOJI_PLACEHOLDER)
            result_entities.append(
                MessageEntity(
                    type="custom_emoji",
                    offset=utf16_cursor,
                    length=utf16_length(CUSTOM_EMOJI_PLACEHOLDER),
                    custom_emoji_id=custom_emoji_id,
                )
            )
            utf16_cursor += utf16_length(CUSTOM_EMOJI_PLACEHOLDER)
        elif action[0] == "locked":
            locked_value = str(action[2])
            locked_type = str(action[3])
            result_parts.append(locked_value)
            length = utf16_length(locked_value)
            if length > 0:
                try:
                    result_entities.append(
                        MessageEntity(
                            type=locked_type,
                            offset=utf16_cursor,
                            length=length,
                        )
                    )
                except Exception:
                    pass
            utf16_cursor += length

        cursor = match.end()

    tail = text[cursor:]
    if tail:
        result_parts.append(tail)

    if open_offsets:
        raise RuntimeError("⚠️ Переводчик повредил маркеры форматирования. Попробуй отправить пост ещё раз.")

    result_text = "".join(result_parts)
    if result_entities:
        result_entities.sort(key=lambda item: (int(getattr(item, "offset", 0)), int(getattr(item, "length", 0))))
    return result_text, (result_entities or None)


def fit_caption_with_entities(text: str, entities: list[MessageEntity] | None) -> tuple[str, list[MessageEntity] | None]:
    if utf16_length(text) <= TELEGRAM_CAPTION_LIMIT:
        return text, entities
    if entities:
        raise RuntimeError("⚠️ Подпись после перевода слишком длинная для Telegram. Укороти исходный пост.")
    return fit_caption(text), None


def fit_text_with_entities(text: str, entities: list[MessageEntity] | None) -> tuple[str, list[MessageEntity] | None]:
    if utf16_length(text) <= TELEGRAM_TEXT_LIMIT:
        return text, entities
    if entities:
        raise RuntimeError("⚠️ Текст после перевода слишком длинный для Telegram. Укороти исходный пост.")
    return text[:TELEGRAM_TEXT_LIMIT], None


def translate_ru_to_lang_sync(ru_text: str, target_lang: str, required_tokens: list[str] | None = None) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("⚠️ Не найден OPENAI_API_KEY. Добавь ключ в .env для авто-перевода.")
    if not OPENAI_TRANSLATE_MODEL:
        raise RuntimeError("⚠️ Не задан OPENAI_TRANSLATE_MODEL в .env.")
    style = TRANSLATION_STYLE.get(target_lang)
    if not style:
        raise RuntimeError(f"⚠️ Неподдерживаемый язык перевода: {target_lang}")

    tokens = list(required_tokens or [])
    token_hint = ""
    if tokens:
        token_hint = (
            " Token markers in formats like [[E0S]], [[E0E]], [[CE0]], [[LK0]] must be preserved exactly, without changes, "
            "without reordering, and each marker must appear exactly once."
        )

    for attempt in range(3):
        system_prompt = (
            f"You translate Russian Telegram posts into {style}. "
            "Keep tone lively and human, preserve structure, line breaks, emojis, hashtags, and CTA. "
            "Do not add explanations or comments. Return only translated text."
            f"{token_hint}"
        )
        user_content = ru_text
        if tokens and attempt > 0:
            user_content = (
                f"{ru_text}\n\n"
                f"STRICT MARKERS (KEEP UNCHANGED): {', '.join(tokens)}"
            )
        payload = {
            "model": OPENAI_TRANSLATE_MODEL,
            "temperature": 0.4 if tokens else 0.6,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        }
        req = urllib.request.Request(
            f"{OPENAI_API_BASE}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=OPENAI_HTTP_TIMEOUT_SECONDS) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                body = exc.read().decode("utf-8")
                parsed = json.loads(body)
                detail = parsed.get("error", {}).get("message") or parsed.get("message") or body[:300]
            except Exception:
                detail = f"HTTP {exc.code}"
            raise RuntimeError(f"⚠️ Ошибка перевода: {detail}") from exc
        except Exception as exc:
            raise RuntimeError("⚠️ Не удалось выполнить перевод. Проверь сеть и настройки API.") from exc

        translated_text = _extract_openai_text(data)
        if not translated_text:
            continue
        if tokens and not tokens_intact(translated_text, tokens):
            continue
        return translated_text

    if tokens:
        raise RuntimeError("⚠️ Переводчик не смог сохранить премиум-эмодзи маркеры. Отправь пост ещё раз.")
    raise RuntimeError("⚠️ Сервис перевода вернул пустой ответ.")


async def translate_ru_to_lang(ru_text: str, target_lang: str, required_tokens: list[str] | None = None) -> str:
    if not ru_text:
        return ""
    return await asyncio.to_thread(translate_ru_to_lang_sync, ru_text, target_lang, required_tokens)


async def translate_ru_to_targets(
    ru_text: str,
    target_langs: list[str],
    required_tokens: list[str] | None = None
) -> dict[str, str]:
    result: dict[str, str] = {}
    if not ru_text or not target_langs:
        return result
    for target_lang in target_langs:
        result[target_lang] = await translate_ru_to_lang(ru_text, target_lang, required_tokens=required_tokens)
    return result


async def is_admin_actor(chat_id: int, user_id: int | None) -> bool:
    if not user_id:
        return False
    try:
        member = await bot.get_chat_member(chat_id, user_id)
    except Exception:
        logger.exception("Не удалось проверить права участника чата")
        return False
    return member.status in {"creator", "administrator"}


def is_anonymous_admin_post(message: Message) -> bool:
    sender_chat = getattr(message, "sender_chat", None)
    return bool(sender_chat and sender_chat.id == message.chat.id)


async def can_manage_admin_group(message: Message) -> bool:
    if message.chat.id != ADMIN_GROUP_ID:
        return False
    if is_anonymous_admin_post(message):
        return True
    if not message.from_user:
        return False
    return await is_admin_actor(message.chat.id, message.from_user.id)


async def can_manage_admin_callback(call: CallbackQuery) -> bool:
    if not call.message or not call.from_user:
        return False
    chat_id = call.message.chat.id
    if chat_id == ADMIN_GROUP_ID and call.from_user.id == ANONYMOUS_ADMIN_BOT_ID:
        return True
    if chat_id == ADMIN_GROUP_ID:
        return await is_admin_actor(ADMIN_GROUP_ID, call.from_user.id)
    # Fallback for cases when admin chat ID was changed but admin still presses buttons in admin group.
    return await is_admin_actor(chat_id, call.from_user.id)


async def sync_anonymous_create_post_state(enabled: bool):
    try:
        anon_ctx = dp.fsm.get_context(
            bot=bot,
            chat_id=ADMIN_GROUP_ID,
            user_id=ANONYMOUS_ADMIN_BOT_ID,
        )
        if enabled:
            await anon_ctx.set_state(ApplicationStates.admin_create_post)
        else:
            await anon_ctx.clear()
    except Exception:
        logger.exception("Не удалось синхронизировать состояние create_post для анонимного админа")


def fit_caption(text: str) -> str:
    if len(text) <= TELEGRAM_CAPTION_LIMIT:
        return text
    return text[: TELEGRAM_CAPTION_LIMIT - 1].rstrip() + "…"


async def send_crosspost_to_channels(
    source_message: Message,
    ru_text: str,
    translated_texts: dict[str, str],
    translated_entities: dict[str, list[MessageEntity] | None] | None = None,
    ru_entities: list[MessageEntity] | None = None,
) -> dict:
    channels = active_post_channels()
    if "ru" not in channels:
        raise ValueError("⚠️ Не задан CHANNEL_ID (русский канал).")

    if source_message.media_group_id:
        raise ValueError("⚠️ Для альбома отправь один пост без media-group.")

    if ru_text:
        required = [lang for lang in channels if lang != "ru"]
        missing = [lang for lang in required if not translated_texts.get(lang)]
        if missing:
            missing_titles = ", ".join(LANG_TITLES.get(lang, lang.upper()) for lang in missing)
            raise RuntimeError(f"⚠️ Не удалось получить перевод для: {missing_titles}")
    if source_message.text and not ru_text:
        raise ValueError("⚠️ Текст поста пустой. Отправь текст заново.")
    entities_map = translated_entities or {}
    posted_message_ids: dict[str, int] = {}
    posted_texts: dict[str, str] = {}
    posted_entities: dict[str, list[MessageEntity] | None] = {}

    content_type = "text"
    if source_message.photo:
        content_type = "photo"
    elif source_message.video:
        content_type = "video"
    elif source_message.document:
        content_type = "document"
    elif source_message.animation:
        content_type = "animation"

    # RU channel gets exact copy to preserve original formatting and premium emoji 1:1.
    ru_copy = await bot.copy_message(
        chat_id=channels["ru"],
        from_chat_id=source_message.chat.id,
        message_id=source_message.message_id,
    )
    posted_message_ids["ru"] = int(getattr(ru_copy, "message_id", 0))
    posted_texts["ru"] = (ru_text or "").strip()
    posted_entities["ru"] = list(ru_entities or [])

    translated_channels = [lang for lang in POST_LANG_ORDER if lang in channels and lang != "ru"]
    if not translated_channels:
        return {
            "content_type": content_type,
            "message_ids": posted_message_ids,
            "texts": posted_texts,
            "entities": posted_entities,
        }

    def text_for_lang(lang: str) -> str:
        return (translated_texts.get(lang) or "").strip()

    async def rollback_posted() -> None:
        for lang, message_id in list(posted_message_ids.items()):
            chat_id = channels.get(lang)
            if not chat_id or not message_id:
                continue
            try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception:
                logger.exception("Не удалось откатить опубликованное сообщение: lang=%s id=%s", lang, message_id)

    current_lang = "ru"
    try:
        if source_message.photo:
            file_id = source_message.photo[-1].file_id
            for lang in translated_channels:
                current_lang = lang
                chat_id = channels[lang]
                text = text_for_lang(lang)
                entities = entities_map.get(lang)
                kwargs = {"chat_id": chat_id, "photo": file_id}
                if text:
                    text, entities = fit_caption_with_entities(text, entities)
                    kwargs["caption"] = text
                    kwargs["parse_mode"] = None
                    if entities:
                        kwargs["caption_entities"] = entities
                sent = await bot.send_photo(**kwargs)
                posted_message_ids[lang] = int(sent.message_id)
                posted_texts[lang] = text or ""
                posted_entities[lang] = entities
        elif source_message.video:
            file_id = source_message.video.file_id
            for lang in translated_channels:
                current_lang = lang
                chat_id = channels[lang]
                text = text_for_lang(lang)
                entities = entities_map.get(lang)
                kwargs = {"chat_id": chat_id, "video": file_id}
                if text:
                    text, entities = fit_caption_with_entities(text, entities)
                    kwargs["caption"] = text
                    kwargs["parse_mode"] = None
                    if entities:
                        kwargs["caption_entities"] = entities
                sent = await bot.send_video(**kwargs)
                posted_message_ids[lang] = int(sent.message_id)
                posted_texts[lang] = text or ""
                posted_entities[lang] = entities
        elif source_message.document:
            file_id = source_message.document.file_id
            for lang in translated_channels:
                current_lang = lang
                chat_id = channels[lang]
                text = text_for_lang(lang)
                entities = entities_map.get(lang)
                kwargs = {"chat_id": chat_id, "document": file_id}
                if text:
                    text, entities = fit_caption_with_entities(text, entities)
                    kwargs["caption"] = text
                    kwargs["parse_mode"] = None
                    if entities:
                        kwargs["caption_entities"] = entities
                sent = await bot.send_document(**kwargs)
                posted_message_ids[lang] = int(sent.message_id)
                posted_texts[lang] = text or ""
                posted_entities[lang] = entities
        elif source_message.animation:
            file_id = source_message.animation.file_id
            for lang in translated_channels:
                current_lang = lang
                chat_id = channels[lang]
                text = text_for_lang(lang)
                entities = entities_map.get(lang)
                kwargs = {"chat_id": chat_id, "animation": file_id}
                if text:
                    text, entities = fit_caption_with_entities(text, entities)
                    kwargs["caption"] = text
                    kwargs["parse_mode"] = None
                    if entities:
                        kwargs["caption_entities"] = entities
                sent = await bot.send_animation(**kwargs)
                posted_message_ids[lang] = int(sent.message_id)
                posted_texts[lang] = text or ""
                posted_entities[lang] = entities
        elif source_message.text:
            for lang in translated_channels:
                current_lang = lang
                chat_id = channels[lang]
                text = text_for_lang(lang)
                if not text:
                    raise RuntimeError(f"Пустой перевод для {LANG_TITLES.get(lang, lang.upper())}.")
                entities = entities_map.get(lang)
                text, entities = fit_text_with_entities(text, entities)
                kwargs = {"chat_id": chat_id, "text": text, "parse_mode": None}
                if entities:
                    kwargs["entities"] = entities
                sent = await bot.send_message(**kwargs)
                posted_message_ids[lang] = int(sent.message_id)
                posted_texts[lang] = text or ""
                posted_entities[lang] = entities
        else:
            raise ValueError("⚠️ Поддерживаются текст, фото, видео, gif и документ.")
    except Exception as exc:
        await rollback_posted()
        lang_title = LANG_TITLES.get(current_lang, current_lang.upper())
        detail = str(exc).strip()
        if detail:
            detail = re.sub(r"\s+", " ", detail)
            if len(detail) > 240:
                detail = f"{detail[:240].rstrip()}..."
            raise RuntimeError(
                f"⚠️ Публикация отменена: ошибка в канале {lang_title}. {detail}"
            ) from exc
        raise RuntimeError(f"⚠️ Публикация отменена: ошибка в канале {lang_title}.") from exc

    return {
        "content_type": content_type,
        "message_ids": posted_message_ids,
        "texts": posted_texts,
        "entities": posted_entities,
    }


def entities_map_to_payload(entities_map: dict[str, list[MessageEntity] | None]) -> dict[str, list[dict]]:
    payload: dict[str, list[dict]] = {}
    for lang, entities in entities_map.items():
        payload[lang] = entities_to_dicts(entities)
    return payload


def entities_map_from_payload(payload: dict | None) -> dict[str, list[MessageEntity] | None]:
    result: dict[str, list[MessageEntity] | None] = {}
    if not isinstance(payload, dict):
        return result
    for lang, raw_entities in payload.items():
        if isinstance(raw_entities, list):
            result[str(lang)] = dicts_to_entities(raw_entities)
        else:
            result[str(lang)] = None
    return result


def content_type_label(content_type: str | None) -> str:
    return {
        "text": "Текст",
        "photo": "Фото",
        "video": "Видео",
        "document": "Документ",
        "animation": "GIF",
    }.get((content_type or "").strip().lower(), content_type or "Неизвестно")


def post_preview_text(item: dict) -> str:
    texts = item.get("texts")
    if isinstance(texts, dict):
        candidate = (
            texts.get("ru")
            or texts.get("en")
            or texts.get("pt")
            or texts.get("es")
            or ""
        )
    else:
        candidate = item.get("source_preview", "") or ""
    candidate = str(candidate)
    compact = " ".join(candidate.split())
    return compact[:300]


def post_full_text(item: dict) -> str:
    texts = item.get("texts")
    if isinstance(texts, dict):
        ru_value = texts.get("ru")
        if ru_value is not None and str(ru_value).strip():
            return str(ru_value)
        for lang in POST_LANG_ORDER:
            value = texts.get(lang)
            if value is not None and str(value).strip():
                return str(value)
    source_preview = item.get("source_preview")
    return str(source_preview or "")


def clip_text_for_telegram(text: str, max_chars: int) -> tuple[str, bool]:
    if max_chars <= 0:
        return "", bool(text)
    if len(text) <= max_chars:
        return text, False
    return text[: max_chars - 1].rstrip() + "…", True


def build_admin_posted_item_text(item: dict, offset: int, total: int) -> str:
    full_text = post_full_text(item) or ""
    safe_full_text = full_text if full_text.strip() else "—"
    created_at = html.escape(str(item.get("created_at") or "—"))
    content = content_type_label(str(item.get("content_type") or ""))
    message_ids = item.get("message_ids", {})
    if not isinstance(message_ids, dict):
        message_ids = {}
    langs = [LANG_TITLES.get(lang, lang.upper()) for lang in POST_LANG_ORDER if message_ids.get(lang)]
    langs_text = ", ".join(langs) if langs else "—"
    base = (
        "📣 <b>Выложенные посты</b>\n\n"
        f"Пост <b>{offset + 1}</b> из <b>{total}</b>\n"
        f"ID: <code>{item.get('id')}</code>\n"
        f"Тип: <b>{html.escape(content)}</b>\n"
        f"Каналы: <b>{html.escape(langs_text)}</b>\n"
        f"Создан: <code>{created_at}</code>"
    )
    header = "\n\n📝 <b>Текст поста (RU):</b>\n"
    reserve = TELEGRAM_TEXT_LIMIT - len(base) - len(header) - 120
    shown_text, was_cut = clip_text_for_telegram(safe_full_text, max(reserve, 256))
    result = f"{base}{header}{html.escape(shown_text)}"
    while len(result) > TELEGRAM_TEXT_LIMIT and shown_text:
        was_cut = True
        overflow = len(result) - TELEGRAM_TEXT_LIMIT
        trim_by = max(16, overflow + 16)
        shown_text = shown_text[:-trim_by].rstrip()
        result = f"{base}{header}{html.escape(shown_text)}"
    if was_cut:
        result += (
            "\n\n⚠️ Текст очень длинный и не помещается целиком в одно сообщение Telegram. "
            "Для полного изменения нажми «Изменить текст»."
        )
        while len(result) > TELEGRAM_TEXT_LIMIT and shown_text:
            shown_text = shown_text[:-32].rstrip()
            result = (
                f"{base}{header}{html.escape(shown_text)}\n\n"
                "⚠️ Текст длиннее лимита Telegram. Для полного изменения нажми «Изменить текст»."
            )
    return result

def build_admin_menu_text(counts: dict, stage_counts: dict | None = None) -> str:
    stage_quick = (stage_counts or {}).get("quick", 0)
    stage_full = (stage_counts or {}).get("full", 0)
    return (
        "🛠 <b>Админ-меню</b>\n\n"
        "Зоны:\n"
        "• Контент: посты\n"
        "• Заявки: статусы и этапы\n"
        "• Аналитика: статистика и Excel\n"
        "• Сервис: архив, обновление, сброс\n\n"
        f"Ожидают подтверждения: <b>{counts.get('pending', 0)}</b>\n"
        f"Принятые: <b>{counts.get('accepted', 0)}</b>\n"
        f"Отклонённые: <b>{counts.get('rejected', 0)}</b>\n\n"
        f"1️⃣ Прошёл первый этап: <b>{stage_quick}</b>\n"
        f"2️⃣ Полностью заполнил заявку: <b>{stage_full}</b>\n\n"
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

def extract_country_from_location(location: str | None) -> str | None:
    raw = (location or "").strip()
    if not raw:
        return None
    raw = re.sub(r"\s+", " ", raw)
    by_brackets = re.search(r"\(([^()]{2,80})\)\s*$", raw)
    if by_brackets:
        candidate = by_brackets.group(1).strip(" .")
        if candidate:
            return candidate
    parts = [
        part.strip(" .")
        for part in re.split(r"\s*(?:,|;|/|\|)\s*|\s+[—–-]\s+", raw)
        if part and part.strip(" .")
    ]
    if len(parts) >= 2:
        return parts[-1]
    return None

def submission_country(data: dict | None) -> str:
    if isinstance(data, dict):
        explicit = str(data.get("country") or "").strip()
        if explicit:
            return explicit
        derived = extract_country_from_location(str(data.get("city") or ""))
        if derived:
            return derived
        by_phone = country_from_phone(str(data.get("phone") or ""))
        if by_phone:
            return by_phone
    return "—"

def submission_lang_for_user(user_id: int, data: dict | None = None) -> str:
    payload = data if isinstance(data, dict) else (get_form_data(user_id) or {})
    payload_lang = normalize_lang((payload.get("lang") if isinstance(payload, dict) else None) or "")
    if payload_lang in LANGUAGE_NAMES:
        return payload_lang
    return lang_for(user_id)

def application_stage_label(data: dict | None) -> str:
    stage = detect_application_stage(data)
    if stage == APPLICATION_STAGE_QUICK:
        return "1/2 Предзаявка (этап 2 не завершён)"
    return "2/2 Полная заявка"

AUTO_REJECT_REASONS = {
    "ru": {
        "1": "Сейчас, к сожалению, мы не можем принять заявку.",
        "2": "Сейчас условия не совпали, но спасибо за интерес.",
        "3": "Мы вернёмся к твоей анкете чуть позже. Спасибо за понимание.",
    },
    "en": {
        "1": "Unfortunately, we can’t accept your application right now.",
        "2": "At the moment, your profile doesn’t match the current requirements, but thank you for your interest.",
        "3": "We’ll return to your application a bit later. Thanks for understanding.",
    },
    "pt": {
        "1": "No momento, infelizmente, não podemos aceitar sua candidatura.",
        "2": "Neste momento, seu perfil não corresponde aos requisitos atuais, mas obrigada pelo interesse.",
        "3": "Vamos retornar à sua candidatura um pouco mais tarde. Obrigada pela compreensão.",
    },
    "es": {
        "1": "Por ahora, lamentablemente, no podemos aceptar tu solicitud.",
        "2": "En este momento, tu perfil no coincide con los requisitos actuales, pero gracias por tu interés.",
        "3": "Volveremos a tu solicitud un poco más adelante. Gracias por la comprensión.",
    },
}

def auto_reject_reason(template_code: str, lang: str) -> str | None:
    locale = normalize_lang(lang)
    templates = AUTO_REJECT_REASONS.get(locale, AUTO_REJECT_REASONS["ru"])
    return templates.get(template_code)

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
        f"🏳️ Страна подачи: {_safe_text(submission_country(data))}\n"
        f"🧩 Этап анкеты: {_safe_text(application_stage_label(data))}\n"
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
        f"🏳️ Страна подачи: {_safe_text(submission_country(data))}\n"
        f"🧩 Этап анкеты: {_safe_text(application_stage_label(data))}\n"
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
    stage_counts = get_application_stage_counts()
    source_counts = get_source_counts()
    reviewed = counts["accepted"] + counts["rejected"]
    total_stage = stage_counts.get("total", 0)

    def pct(part: int, whole: int) -> str:
        if whole <= 0:
            return "0%"
        return f"{(part / whole) * 100:.1f}%"

    return (
        "📊 <b>Статистика заявок</b>\n\n"
        f"Всего: <b>{counts['total']}</b>\n"
        f"Новые: {counts['new']}\n"
        f"На рассмотрении: {counts['pending']}\n"
        f"Одобрены: {counts['accepted']}\n"
        f"Отклонены: {counts['rejected']}\n\n"
        "🧩 <b>Этапы воронки</b>\n"
        f"1️⃣ Только первый этап: {stage_counts.get('quick', 0)}\n"
        f"2️⃣ Полная заявка: {stage_counts.get('full', 0)}\n"
        f"Конверсия в полную заявку: {pct(stage_counts.get('full', 0), total_stage)}\n\n"
        "🧭 <b>Источники</b>\n"
        f"Сайт: {source_counts.get('site', 0)}\n"
        f"Бот: {source_counts.get('bot', 0)}\n"
        f"Не определён: {source_counts.get('unknown', 0)}\n\n"
        "✅ <b>Качество обработки</b>\n"
        f"Аппрув среди обработанных: {pct(counts['accepted'], reviewed)}"
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
            stage_counts = get_application_stage_counts()
        except Exception:
            logger.exception("Не удалось получить статистику для админ-меню")
            counts = {"pending": 0, "accepted": 0, "rejected": 0, "total": 0, "new": 0}
            stage_counts = {"quick": 0, "full": 0, "total": 0}
        menu_text = build_admin_menu_text(counts, stage_counts)
        stored_id = get_setting(ADMIN_MENU_SETTING_KEY)
        if stored_id:
            try:
                await bot.edit_message_text(
                    chat_id=ADMIN_GROUP_ID,
                    message_id=int(stored_id),
                    text=menu_text,
                    reply_markup=admin_menu_keyboard(counts, stage_counts)
                )
                return
            except TelegramBadRequest as exc:
                if _is_not_modified_error(exc):
                    return
                logger.exception("Не удалось обновить существующее админ-меню")
            except Exception:
                logger.exception("Не удалось обновить существующее админ-меню")
        try:
            msg = await bot.send_message(
                ADMIN_GROUP_ID,
                menu_text,
                reply_markup=admin_menu_keyboard(counts, stage_counts)
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
            except TelegramBadRequest as exc:
                if _is_not_modified_error(exc):
                    return
                logger.exception("Не удалось обновить админ-сообщение")
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
        stage_counts = get_application_stage_counts()
    except Exception:
        logger.exception("Не удалось получить статистику для обновления админ-меню")
        counts = {"pending": 0, "accepted": 0, "rejected": 0, "total": 0, "new": 0}
        stage_counts = {"quick": 0, "full": 0, "total": 0}
    await update_admin_menu_message(
        build_admin_menu_text(counts, stage_counts),
        admin_menu_keyboard(counts, stage_counts)
    )

def _admin_list_label(filter_key: str | None) -> str:
    return {
        "pending": "Ожидают подтверждения",
        "accepted": "Принятые",
        "rejected": "Отклонённые",
        "all": "Все заявки",
        "stage_quick": "Прошли только первый этап",
        "stage_full": "Полностью заполненные заявки",
        None: "Все заявки",
    }.get(filter_key, "Все заявки")

async def send_admin_list(
    call: CallbackQuery,
    filter_key: str,
    offset: int = 0
):
    await safe_call_answer(call)
    try:
        status = None if filter_key in {"all", "stage_quick", "stage_full"} else filter_key
        if filter_key == "stage_quick":
            apps = list_applications_by_stage("quick", status=None)
        elif filter_key == "stage_full":
            apps = list_applications_by_stage("full", status=None)
        else:
            apps = list_applications(status)
        label = _admin_list_label(filter_key)
        if not apps:
            counts = get_status_counts()
            stage_counts = get_application_stage_counts()
            await update_admin_menu_message(
                f"🤍 {label}: пока пусто ✨",
                admin_menu_keyboard(counts, stage_counts)
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
        counts = get_status_counts()
        stage_counts = get_application_stage_counts()
        await update_admin_menu_message(
            "⚠️ Не удалось открыть список заявок. Попробуй ещё раз.",
            admin_menu_keyboard(counts, stage_counts)
        )


def _post_message_ids(item: dict | None) -> dict[str, int]:
    payload = (item or {}).get("message_ids", {})
    if not isinstance(payload, dict):
        return {}
    result: dict[str, int] = {}
    for lang, raw_value in payload.items():
        try:
            message_id = int(raw_value)
        except Exception:
            continue
        if message_id > 0:
            result[str(lang)] = message_id
    return result


def _post_texts(item: dict | None) -> dict[str, str]:
    payload = (item or {}).get("texts", {})
    if not isinstance(payload, dict):
        return {}
    result: dict[str, str] = {}
    for lang, value in payload.items():
        if value is None:
            result[str(lang)] = ""
        else:
            result[str(lang)] = str(value)
    return result


def _post_entities(item: dict | None) -> dict[str, list[MessageEntity] | None]:
    return entities_map_from_payload((item or {}).get("entities", {}))


async def show_posted_media_preview(item: dict) -> None:
    content_type = str(item.get("content_type") or "").strip().lower()
    if content_type not in MEDIA_CONTENT_TYPES:
        return
    message_ids = _post_message_ids(item)
    ru_message_id = message_ids.get("ru")
    ru_channel_id = CHANNEL_ID_BY_LANG.get("ru")
    if not isinstance(ru_channel_id, int) or not isinstance(ru_message_id, int) or ru_message_id <= 0:
        return
    try:
        copied = await bot.copy_message(
            chat_id=ADMIN_GROUP_ID,
            from_chat_id=ru_channel_id,
            message_id=ru_message_id,
        )
        track_admin_temp_message(int(getattr(copied, "message_id", 0) or 0))
    except Exception:
        logger.exception("Не удалось показать медиа-превью выложенного поста")


async def show_admin_posted_posts(offset: int = 0) -> tuple[dict | None, int, int]:
    total = count_posted_messages()
    if total <= 0:
        await clear_admin_temp_messages()
        await clear_admin_view_message()
        counts = get_status_counts()
        stage_counts = get_application_stage_counts()
        await update_admin_menu_message(
            "🤍 Выложенных постов пока нет ✨",
            admin_menu_keyboard(counts, stage_counts)
        )
        return None, 0, 0

    if offset < 0:
        offset = 0
    if offset >= total:
        offset = max(total - 1, 0)
    rows = list_posted_messages(limit=1, offset=offset)
    if not rows:
        await clear_admin_temp_messages()
        await clear_admin_view_message()
        counts = get_status_counts()
        stage_counts = get_application_stage_counts()
        await update_admin_menu_message(
            "🤍 Выложенных постов пока нет ✨",
            admin_menu_keyboard(counts, stage_counts)
        )
        return None, 0, 0

    item = rows[0]
    await clear_admin_temp_messages()
    await show_posted_media_preview(item)
    await update_admin_view_message(
        build_admin_posted_item_text(item, offset, total),
        admin_posts_view_keyboard(
            int(item["id"]),
            offset,
            total,
            str(item.get("content_type") or ""),
        ),
        None,
    )
    return item, offset, total


async def delete_post_from_channels(item: dict) -> None:
    message_ids = _post_message_ids(item)
    for lang, message_id in message_ids.items():
        chat_id = CHANNEL_ID_BY_LANG.get(lang)
        if not isinstance(chat_id, int):
            continue
        try:
            await bot.delete_message(chat_id, message_id)
        except Exception:
            logger.exception("Не удалось удалить пост из канала %s (message_id=%s)", lang, message_id)


def _is_not_modified_error(exc: Exception) -> bool:
    return "message is not modified" in str(exc).lower()


async def edit_post_text_in_channels(
    item: dict,
    texts_map: dict[str, str],
    entities_map: dict[str, list[MessageEntity] | None],
) -> tuple[dict[str, str], dict[str, list[MessageEntity] | None]]:
    message_ids = _post_message_ids(item)
    content_type = str(item.get("content_type") or "text").strip().lower()
    current_texts = _post_texts(item)
    current_entities = _post_entities(item)

    final_texts = dict(current_texts)
    final_entities: dict[str, list[MessageEntity] | None] = dict(current_entities)

    for lang, message_id in message_ids.items():
        chat_id = CHANNEL_ID_BY_LANG.get(lang)
        if not isinstance(chat_id, int):
            continue
        text = texts_map.get(lang, current_texts.get(lang, "")) or ""
        entities = entities_map.get(lang, current_entities.get(lang))

        if content_type == "text":
            if not text.strip():
                raise RuntimeError(f"⚠️ Пустой текст для {LANG_TITLES.get(lang, lang.upper())}.")
            text, entities = fit_text_with_entities(text, entities)
            kwargs = {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                "parse_mode": None,
            }
            if entities:
                kwargs["entities"] = entities
            try:
                await bot.edit_message_text(**kwargs)
            except TelegramBadRequest as exc:
                if not _is_not_modified_error(exc):
                    raise
        else:
            if text:
                text, entities = fit_caption_with_entities(text, entities)
            else:
                entities = None
            kwargs = {
                "chat_id": chat_id,
                "message_id": message_id,
                "caption": text or "",
                "parse_mode": None,
            }
            if entities:
                kwargs["caption_entities"] = entities
            try:
                await bot.edit_message_caption(**kwargs)
            except TelegramBadRequest as exc:
                if not _is_not_modified_error(exc):
                    raise

        final_texts[lang] = text
        final_entities[lang] = entities

    return final_texts, final_entities


async def replace_post_media_in_channels(
    item: dict,
    new_file_id: str,
    expected_content_type: str,
) -> tuple[dict[str, str], dict[str, list[MessageEntity] | None]]:
    content_type = str(item.get("content_type") or "").strip().lower()
    normalized_expected = (expected_content_type or "").strip().lower()
    if content_type not in MEDIA_CONTENT_TYPES:
        raise RuntimeError("⚠️ У этого поста нет медиа для замены.")
    if normalized_expected != content_type:
        raise RuntimeError("⚠️ Тип нового медиа не совпадает с типом поста.")

    media_class_map = {
        "photo": InputMediaPhoto,
        "video": InputMediaVideo,
        "document": InputMediaDocument,
        "animation": InputMediaAnimation,
    }
    media_class = media_class_map.get(content_type)
    if media_class is None:
        raise RuntimeError("⚠️ Этот тип медиа пока не поддерживается для замены.")

    message_ids = _post_message_ids(item)
    texts = _post_texts(item)
    entities_map = _post_entities(item)

    final_texts = dict(texts)
    final_entities: dict[str, list[MessageEntity] | None] = dict(entities_map)

    for lang, message_id in message_ids.items():
        chat_id = CHANNEL_ID_BY_LANG.get(lang)
        if not isinstance(chat_id, int):
            continue
        caption = texts.get(lang, "") or ""
        entities = entities_map.get(lang)
        if caption:
            caption, entities = fit_caption_with_entities(caption, entities)
        else:
            entities = None

        media_kwargs = {"media": new_file_id}
        if caption:
            media_kwargs["caption"] = caption
            if entities:
                media_kwargs["caption_entities"] = entities
        media = media_class(**media_kwargs)
        try:
            await bot.edit_message_media(
                chat_id=chat_id,
                message_id=message_id,
                media=media,
            )
        except TelegramBadRequest as exc:
            if not _is_not_modified_error(exc):
                raise
        final_texts[lang] = caption
        final_entities[lang] = entities

    return final_texts, final_entities

async def send_menu(
    message: Message,
    caption: str | None = None,
    status: str | None = None,
    intro: str | None = None,
    tail: str | None = None,
    channel_url: str | None = None,
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
        channel_url=channel_url,
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
    channel_url: str | None = None,
) -> bool:
    locale = normalize_lang(lang or lang_for(user_id))
    resolved_channel_url = _normalize_telegram_url(channel_url) or CHANNEL_PUBLIC_LINK
    message_id = get_menu_message_id(user_id)
    if message_id:
        try:
            await bot.edit_message_caption(
                chat_id=user_id,
                message_id=message_id,
                caption=caption,
                reply_markup=main_menu(locale, channel_url=resolved_channel_url)
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
            reply_markup=main_menu(locale, channel_url=resolved_channel_url)
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

async def start_application(message: Message, state: FSMContext, user_id: int | None = None):
    target_user_id = user_id or message.chat.id
    await state.clear()
    clear_form_data(target_user_id)
    await state.set_state(ApplicationStates.name)
    await gentle_typing(message.chat.id)
    lang = lang_for(target_user_id)
    question = format_question(
        ApplicationStates.name,
        form_question(ApplicationStates.name, lang),
        user_id=target_user_id,
    )
    edited = False
    if message and message.chat.type == "private":
        edited = await try_edit_message(message, question, reply_markup=form_keyboard(lang))
        if edited:
            set_menu_message_id(target_user_id, message.message_id)
    if not edited:
        sent = await send_or_edit_user_text(
            target_user_id,
            question,
            reply_markup=form_keyboard(lang)
        )
        if not sent:
            await state.clear()
            set_last_state(target_user_id, None)
            return False
    set_status(target_user_id, "new")
    set_source(target_user_id, "bot")
    set_last_state(target_user_id, ApplicationStates.name.state)
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

async def enter_stage2_gate(
    user_id: int,
    state: FSMContext,
):
    lang = lang_for(user_id)
    await state.set_state(ApplicationStates.stage2_gate)
    set_last_state(user_id, ApplicationStates.stage2_gate.state)
    await send_or_edit_user_text(
        user_id,
        stage2_text(lang, "gate"),
        reply_markup=stage2_gate_keyboard(lang),
    )

async def enter_stage2_intro(
    user_id: int,
    state: FSMContext,
    note: str | None = None,
    start_from_step2: bool = False,
):
    lang = lang_for(user_id)
    await state.set_state(ApplicationStates.stage2_intro)
    set_last_state(user_id, ApplicationStates.stage2_intro.state)
    if start_from_step2:
        text = stage2_text(lang, "step2")
        await send_or_edit_user_text(
            user_id,
            text,
            reply_markup=stage2_keyboard_step2(lang),
        )
        return

    first = stage2_text(lang, "step1")
    if note:
        first = f"{note}\n\n{first}"
    await send_or_edit_user_text(
        user_id,
        first,
        reply_markup=stage2_keyboard_step1(lang),
    )

async def start_stage2_questions(user_id: int, state: FSMContext, intro: str | None = None):
    lang = lang_for(user_id)
    await state.set_state(ApplicationStates.city)
    set_last_state(user_id, ApplicationStates.city.state)
    question = format_question(
        ApplicationStates.city,
        form_question(ApplicationStates.city, lang),
        user_id=user_id,
    )
    if intro:
        question = f"{intro}\n\n{question}"
    await send_or_edit_user_text(
        user_id,
        question,
        reply_markup=form_keyboard(lang),
    )

async def bootstrap_site_stage2_start(
    message: Message,
    state: FSMContext,
    token: str,
    start_lang: str | None = None,
) -> bool:
    lead = consume_site_lead_payload(token)
    if not lead:
        lang = normalize_lang(start_lang or lang_for(message.from_user.id))
        if start_lang:
            set_user_language(message.from_user.id, lang)
        await send_or_edit_user_text(message.from_user.id, stage2_text(lang, "expired"), reply_markup=main_menu(lang))
        return True

    lang = normalize_lang(str(lead.get("lang") or start_lang or "ru"))
    set_user_language(message.from_user.id, lang)
    await state.clear()
    clear_form_data(message.from_user.id)
    legacy_user_id = lead.get("site_pending_user_id")
    if legacy_user_id is not None:
        try:
            delete_application(int(legacy_user_id))
            try:
                await ensure_admin_menu_posted()
            except Exception:
                logger.exception("Не удалось обновить админ-меню после удаления веб-предзаявки")
        except Exception:
            logger.exception("Не удалось удалить временную веб-заявку")
    payload = {
        "name": str(lead.get("name") or "").strip(),
        "phone": str(lead.get("phone") or "").strip(),
        "age": str(lead.get("age") or "").strip(),
        "device_model": str(lead.get("device_model") or "").strip(),
        "telegram": str(lead.get("telegram") or "").strip(),
        "country": str(lead.get("country") or "").strip() or None,
        "lang": lang,
        "application_stage": APPLICATION_STAGE_QUICK,
        "site_lead_token": token,
    }
    payload = {k: v for k, v in payload.items() if v not in {None, ""}}
    await state.update_data(**payload)
    set_form_data(message.from_user.id, payload)
    set_status(message.from_user.id, "new")
    set_source(message.from_user.id, "site")
    await state.set_state(ApplicationStates.stage2_gate)
    set_last_state(message.from_user.id, ApplicationStates.stage2_gate.state)
    menu_caption = f"{t(lang, 'menu_caption')}\n\n{stage2_text(lang, 'menu_recommendation')}"
    menu_sent = await send_or_edit_user_menu(
        message.from_user.id,
        menu_caption,
        lang=lang,
        channel_url=stage2_channel_link(lang),
    )
    if not menu_sent:
        await send_or_edit_user_text(
            message.from_user.id,
            stage2_text(lang, "menu_recommendation"),
            reply_markup=main_menu(lang, channel_url=stage2_channel_link(lang)),
        )
    await clear_user_flow_message(message.from_user.id)
    return True

# ================= START =================

@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    try:
        if message.chat.type != "private":
            await message.answer(t("ru", "start_private_only"))
            return
        await state.clear()
        await clear_portfolio_media(message.from_user.id)
        start_payload = extract_start_payload(message.text)
        site_token, start_lang = extract_site_lead_start_data(start_payload)
        if start_lang:
            set_user_language(message.from_user.id, start_lang)
        if site_token:
            started = await bootstrap_site_stage2_start(message, state, site_token, start_lang=start_lang)
            if started:
                return
        if not await ensure_language_selected(
            message.from_user.id,
            allow_home_button=False,
            force_prompt=FORCE_LANGUAGE_PICK_ON_START,
        ):
            return
        app = get_application(message.from_user.id)
        data = get_form_data(message.from_user.id) or {}
        status = app.get("status") if app else None
        lang = lang_for(message.from_user.id)
        site_stage2 = is_site_quick_application(app, data)
        await send_menu(
            message,
            caption=t(lang, "menu_caption"),
            status=status,
            channel_url=stage2_channel_link(lang) if site_stage2 else None,
        )
        if app and app.get("last_state") in FORM_PROGRESS_STATES and not get_form_data(message.from_user.id):
            set_last_state(message.from_user.id, None)
        can_resume = (
            app
            and app.get("last_state") in FORM_PROGRESS_STATES
            and (
                app.get("status") in {None, "new"}
                or (app.get("status") == "pending" and is_quick_application(data))
            )
        )
        if can_resume:
            pending_site_quick = app.get("status") == "pending" and is_site_quick_application(app, data)
            resume_text = (
                stage2_text(lang, "gate")
                if pending_site_quick
                else (
                    stage2_text(lang, "step2")
                    if app.get("status") == "pending" and is_quick_application(data)
                    else t(lang, "resume_prompt")
                )
            )
            await send_or_edit_user_text(
                message.from_user.id,
                resume_text,
                reply_markup=continue_form_keyboard(lang)
            )
    except Exception:
        logger.exception("Ошибка в /start")
        try:
            await message.answer(t(lang_for(message.from_user.id), "temp_error_retry"))
        except Exception:
            pass

@dp.callback_query(F.data == "main_menu")
async def main_menu_handler(call: CallbackQuery, state: FSMContext):
    if not call.message or call.message.chat.type != "private":
        await safe_call_answer(call, t("ru", "open_private_prompt"), show_alert=True)
        return
    await safe_call_answer(call)
    await state.clear()
    await clear_portfolio_media(call.from_user.id)
    app = get_application(call.from_user.id)
    data = get_form_data(call.from_user.id) or {}
    status = app.get("status") if app else None
    lang = lang_for(call.from_user.id)
    site_stage2 = is_site_quick_application(app, data)
    await send_menu(
        call.message,
        caption=t(lang, "menu_caption"),
        status=status,
        channel_url=stage2_channel_link(lang) if site_stage2 else None,
    )
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
        data = get_form_data(call.from_user.id) or {}
        status = app.get("status") if app else None
        await state.clear()
        await clear_portfolio_media(call.from_user.id)
        intro_text = t(lang, "language_changed", language=LANGUAGE_NAMES.get(lang, lang))
        site_stage2 = is_site_quick_application(app, data)
        menu_ok = False
        try:
            menu_ok = await send_menu(
                call.message,
                caption=t(lang, "menu_caption"),
                status=status,
                intro=intro_text,
                channel_url=stage2_channel_link(lang) if site_stage2 else None,
            )
        except Exception:
            logger.exception("Не удалось обновить меню после смены языка")
        if not menu_ok:
            await send_or_edit_user_text(
                call.from_user.id,
                f"{intro_text}\n\n{t(lang, 'menu_caption')}",
                reply_markup=main_menu(
                    lang,
                    channel_url=stage2_channel_link(lang) if site_stage2 else None,
                ),
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
        form_data = get_form_data(call.from_user.id) or {}
        pending_quick = status == "pending" and is_quick_application(form_data)
        logger.info("APPLY_STATUS user_id=%s status=%s", call.from_user.id, status)

        if status in {"accepted", "rejected"} or (status == "pending" and not pending_quick):
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

        if pending_quick:
            await state.update_data(**form_data)
            if is_site_quick_application(app, form_data):
                await enter_stage2_gate(call.from_user.id, state)
            else:
                await start_stage2_questions(
                    call.from_user.id,
                    state,
                    intro=stage2_text(lang, "autostart"),
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

        started = await start_application(call.message, state, user_id=call.from_user.id)
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
        started = await start_application(call.message, state, user_id=call.from_user.id)
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
            data = get_form_data(call.from_user.id) or {}
            last_state = app.get("last_state") if app else None
            if last_state and last_state in FORM_PROGRESS_STATES and not get_form_data(call.from_user.id):
                set_last_state(call.from_user.id, None)
                last_state = None
            if last_state and last_state in FORM_PROGRESS_STATES:
                await state.set_state(last_state)
                await restore_form_data(state, call.from_user.id)
                current = last_state
            elif app and app.get("status") == "pending" and is_quick_application(data):
                await state.update_data(**data)
                if is_site_quick_application(app, data):
                    await enter_stage2_gate(call.from_user.id, state)
                else:
                    await start_stage2_questions(
                        call.from_user.id,
                        state,
                        intro=stage2_text(lang, "autostart"),
                    )
                return
            else:
                started = await start_application(call.message, state, user_id=call.from_user.id)
                if not started:
                    await safe_call_answer(call, t(lang, "cannot_send_message"), show_alert=True)
                    return
                return

        if current == ApplicationStates.preview.state:
            data = await state.get_data()
            if not REQUIRED_PREVIEW_FIELDS.issubset(data):
                started = await start_application(call.message, state, user_id=call.from_user.id)
                if not started:
                    await safe_call_answer(call, t(lang, "cannot_send_message"), show_alert=True)
                    return
                return
            await show_preview(call.message, state, user_id=call.from_user.id)
            return
        if current == ApplicationStates.stage2_intro.state:
            await enter_stage2_intro(call.from_user.id, state, start_from_step2=True)
            return
        if current == ApplicationStates.stage2_gate.state:
            await enter_stage2_gate(call.from_user.id, state)
            return
        if current == ApplicationStates.edit_value.state:
            data = await state.get_data()
            field = data.get("edit_field")
            if not field:
                await show_preview(call.message, state, user_id=call.from_user.id)
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

        started = await start_application(call.message, state, user_id=call.from_user.id)
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
        started = await start_application(call.message, state, user_id=call.from_user.id)
        if not started:
            await safe_call_answer(call, t(lang, "cannot_send_message"), show_alert=True)
            return
    except Exception:
        logger.exception("Ошибка в form_restart")
        await safe_call_answer(call, t(lang_for(call.from_user.id), "temp_error_retry"), show_alert=True)

@dp.callback_query(F.data == "stage2_intro_next")
async def stage2_intro_next(call: CallbackQuery, state: FSMContext):
    try:
        if not call.message or call.message.chat.type != "private":
            await safe_call_answer(call, t("ru", "open_private_prompt"), show_alert=True)
            return
        await safe_call_answer(call)
        await enter_stage2_intro(call.from_user.id, state, start_from_step2=True)
    except Exception:
        logger.exception("Ошибка в stage2_intro_next")
        await safe_call_answer(call, t(lang_for(call.from_user.id), "temp_error_retry"), show_alert=True)

@dp.callback_query(F.data == "stage2_gate_continue")
async def stage2_gate_continue(call: CallbackQuery, state: FSMContext):
    try:
        if not call.message or call.message.chat.type != "private":
            await safe_call_answer(call, t("ru", "open_private_prompt"), show_alert=True)
            return
        await safe_call_answer(call)
        await start_stage2_questions(call.from_user.id, state)
    except Exception:
        logger.exception("Ошибка в stage2_gate_continue")
        await safe_call_answer(call, t(lang_for(call.from_user.id), "temp_error_retry"), show_alert=True)

@dp.callback_query(F.data == "stage2_start")
async def stage2_start(call: CallbackQuery, state: FSMContext):
    try:
        if not call.message or call.message.chat.type != "private":
            await safe_call_answer(call, t("ru", "open_private_prompt"), show_alert=True)
            return
        await safe_call_answer(call)
        await start_stage2_questions(call.from_user.id, state)
    except Exception:
        logger.exception("Ошибка в stage2_start")
        await safe_call_answer(call, t(lang_for(call.from_user.id), "temp_error_retry"), show_alert=True)

# ================= FORM STEPS =================

@dp.message(StateFilter(ApplicationStates.stage2_gate))
async def stage2_gate_block_input(message: Message):
    lang = lang_for(message.from_user.id)
    await delete_user_message(message)
    await send_or_edit_user_text(
        message.from_user.id,
        stage2_text(lang, "wait_gate"),
        reply_markup=stage2_gate_keyboard(lang),
    )

@dp.message(StateFilter(ApplicationStates.stage2_intro))
async def stage2_intro_block_input(message: Message):
    lang = lang_for(message.from_user.id)
    await delete_user_message(message)
    await send_or_edit_user_text(
        message.from_user.id,
        stage2_text(lang, "wait"),
        reply_markup=stage2_keyboard_step2(lang),
    )

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
        ApplicationStates.phone
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
    await update_form_field(
        state,
        m.from_user.id,
        city=city,
        country=extract_country_from_location(city)
    )
    await send_next_question(
        m,
        state,
        ApplicationStates.work_time
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
    current_data = await state.get_data()
    payload = {"phone": normalized}
    country_guess = country_from_phone(normalized)
    if country_guess and not str(current_data.get("country") or "").strip():
        payload["country"] = country_guess
    await update_form_field(state, m.from_user.id, **payload)
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
        ApplicationStates.device_model,
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
        ApplicationStates.photo_face,
        note=note,
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
        ApplicationStates.telegram
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
        ApplicationStates.experience
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
    await update_form_field(
        state,
        m.from_user.id,
        telegram=normalized,
        application_stage=APPLICATION_STAGE_QUICK
    )
    if is_site_source(m.from_user.id):
        await enter_stage2_gate(m.from_user.id, state)
        return
    intro = stage2_text(lang, "autostart")
    if note:
        intro = f"{note}\n\n{intro}"
    await start_stage2_questions(m.from_user.id, state, intro=intro)

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
        ApplicationStates.living
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
    ApplicationStates.phone,
    ApplicationStates.age,
    ApplicationStates.device_model,
    ApplicationStates.telegram,
    ApplicationStates.city,
    ApplicationStates.work_time,
    ApplicationStates.experience,
    ApplicationStates.living,
    ApplicationStates.photo_face,
    ApplicationStates.photo_full,
]

TOTAL_STEPS = len(FORM_ORDER)
FORM_STEP_INDEX = {state: idx + 1 for idx, state in enumerate(FORM_ORDER)}

FORM_PROGRESS_STATES = {s.state for s in FORM_ORDER} | {
    ApplicationStates.stage2_gate.state,
    ApplicationStates.stage2_intro.state,
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
        username = PUBLIC_MANAGER_USERNAME
        await edit_or_send(
            call,
            t(
                lang,
                "profile_contact_title",
                link=f"https://t.me/{username}",
            ),
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
    if field == "city":
        await update_form_field(
            state,
            m.from_user.id,
            city=value,
            country=extract_country_from_location(value)
        )
    else:
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

@dp.message(StateFilter(ApplicationStates.preview), F.photo)
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
        await show_preview(call.message, state, user_id=call.from_user.id)
    except Exception:
        logger.exception("Ошибка в preview_back")
        await safe_call_answer(call, "Не удалось открыть предпросмотр", show_alert=False)

async def show_preview(m: Message, state: FSMContext, user_id: int | None = None):
    target_user_id = user_id or m.chat.id
    lang = lang_for(target_user_id)
    data = await state.get_data()
    await send_or_edit_user_text(target_user_id, t(lang, "loading_text"))
    for text in (
        t(lang, "loading_stage_1"),
        t(lang, "loading_stage_2"),
    ):
        await asyncio.sleep(random.uniform(0.4, 0.8))
        await send_or_edit_user_text(target_user_id, text)
    await asyncio.sleep(random.uniform(0.3, 0.6))
    status = get_status(target_user_id) or "new"
    status_caption = status_label(status, lang)
    text = t(
        lang,
        "preview_title",
        name=_safe_text(data.get("name", "—")),
        city=_safe_text(data.get("city", "—")),
        age=_safe_text(data.get("age", "—")),
        phone=_safe_text(data.get("phone", "—")),
        living=_safe_text(data.get("living", "—")),
        devices=_safe_text(data.get("devices", "—")),
        device_model=_safe_text(data.get("device_model", "—")),
        headphones=_safe_text(data.get("headphones", "—")),
        work_time=_safe_text(data.get("work_time", "—")),
        experience=_safe_text(data.get("experience", "—")),
        telegram=_safe_text(data.get("telegram", "—")),
        status=status_caption,
    )
    await state.set_state(ApplicationStates.preview)
    set_last_state(target_user_id, ApplicationStates.preview.state)
    await send_or_edit_user_text(target_user_id, text, reply_markup=preview_keyboard(lang))

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
            started = await start_application(call.message, state, user_id=call.from_user.id)
            if not started:
                await safe_call_answer(call, t(lang, "cannot_send_message"), show_alert=True)
                return
            await safe_call_answer(call)
            return

        await update_form_field(
            state,
            user.id,
            lang=normalize_lang(lang),
            country=(
                data.get("country")
                or extract_country_from_location(data.get("city"))
                or country_from_phone(data.get("phone"))
            ),
            application_stage=APPLICATION_STAGE_FULL,
        )
        data = await state.get_data()

        await gentle_typing(call.message.chat.id)

        current_source = get_source(user.id)
        set_source(user.id, "site" if current_source == "site" else "bot")
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
        await show_preview(call.message, state, user_id=call.from_user.id)
        lang = lang_for(call.from_user.id)
        await safe_call_answer(call, "Отменено" if lang == "ru" else ("Canceled" if lang == "en" else ("Cancelado" if lang == "pt" else "Cancelado")))
    except Exception:
        logger.exception("Ошибка в edit_cancel")
        await safe_call_answer(call, "Не удалось отменить редактирование", show_alert=False)

# ================= ADMIN =================

@dp.callback_query(StateFilter("*"), F.data.startswith("admin_accept:"))
async def admin_accept(call: CallbackQuery):
    try:
        if not await can_manage_admin_callback(call):
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

@dp.callback_query(StateFilter("*"), F.data.startswith("admin_reject:"))
async def admin_reject(call: CallbackQuery, state: FSMContext):
    try:
        if not await can_manage_admin_callback(call):
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

@dp.callback_query(StateFilter("*"), F.data.startswith("reject_tpl:"))
async def reject_template(call: CallbackQuery, state: FSMContext):
    try:
        if not await can_manage_admin_callback(call):
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        await safe_call_answer(call)
        tpl_code = call.data.split(":", 1)[1]
        state_data = await state.get_data()
        uid = state_data.get("reject_uid")
        if not uid:
            await safe_call_answer(call, "🤍 Не вижу кандидата")
            return
        form_data = get_form_data(uid) or {}
        user_lang = submission_lang_for_user(uid, form_data)

        if tpl_code == "custom":
            await update_admin_menu_message(
                "✍️ Напиши свою причину отказа:",
                reject_reason_keyboard()
            )
            await safe_call_answer(call)
            return

        reason = auto_reject_reason(tpl_code, user_lang)
        if not reason:
            await safe_call_answer(call, "🤍 Шаблон не найден")
            return

        try:
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
            form_data = get_form_data(uid) or {}
            user_lang = submission_lang_for_user(uid, form_data)
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

async def open_create_post_mode(state: FSMContext):
    await state.set_state(ApplicationStates.admin_create_post)
    await sync_anonymous_create_post_state(enabled=True)
    await clear_admin_view_message()
    await update_admin_menu_message(
        post_creator_prompt(),
        admin_create_post_keyboard()
    )


@dp.message(Command("create_post"), F.chat.id == ADMIN_GROUP_ID)
@dp.message(Command("crosspost"), F.chat.id == ADMIN_GROUP_ID)
async def admin_create_post_command(message: Message, state: FSMContext):
    if not await can_manage_admin_group(message):
        await message.answer("Недостаточно прав")
        return
    await open_create_post_mode(state)
    await message.answer("📝 Режим создания поста включен. Отправь пост на русском (если в группе включена анонимность — тоже сработает).")


@dp.message(StateFilter(ApplicationStates.admin_create_post), F.chat.id == ADMIN_GROUP_ID)
async def admin_create_post_submit(message: Message, state: FSMContext):
    if message.from_user and message.from_user.is_bot and not is_anonymous_admin_post(message):
        return
    if not await can_manage_admin_group(message):
        await message.answer("⚠️ Для публикации нужны права администратора этой группы.")
        return
    if message.text and message.text.strip().startswith("/"):
        await message.answer("⚠️ Сейчас включён режим публикации. Отправь пост или нажми «Отменить».")
        return
    if message.media_group_id:
        await message.answer("⚠️ Альбомы не поддерживаются. Отправь один пост (одно сообщение).")
        return
    if not any([message.text, message.photo, message.video, message.document, message.animation]):
        await message.answer("⚠️ Поддерживаются: текст, фото, видео, gif или документ.")
        return

    ru_text, ru_entities = extract_post_text_and_entities(message)
    if ru_text and not CYRILLIC_RE.search(ru_text):
        await message.answer("⚠️ Текст поста должен быть на русском, чтобы перевести его автоматически.")
        return

    try:
        channels = active_post_channels()
        missing_langs = missing_crosspost_langs(channels)
        if missing_langs:
            missing_titles = ", ".join(LANG_TITLES[lang] for lang in missing_langs)
            env_hints = "\n".join(f"{LANG_TITLES[lang]}: {LANG_ENV_HINTS.get(lang, '-')}" for lang in missing_langs)
            raise RuntimeError(
                "⚠️ Публикация остановлена: кросспост не полностью настроен.\n"
                f"Отсутствуют каналы: {missing_titles}.\n"
                "Проверь переменные окружения bot-сервиса:\n"
                f"{env_hints}"
            )
        target_langs = [lang for lang in POST_LANG_ORDER if lang in channels and lang != "ru"]
        translated_texts: dict[str, str] = {}
        translated_entities: dict[str, list[MessageEntity] | None] = {}
        if ru_text:
            marked_text, required_tokens, rich_specs, custom_specs, locked_specs = markerize_entities_for_translation(
                ru_text,
                ru_entities,
            )
            translated_marked = await translate_ru_to_targets(
                marked_text,
                target_langs,
                required_tokens=required_tokens,
            )
            for lang in target_langs:
                translated_marked_text = translated_marked.get(lang, "")
                restored_text, restored_entities = restore_entities_from_markers(
                    translated_marked_text,
                    required_tokens,
                    rich_specs,
                    custom_specs,
                    locked_specs,
                )
                translated_texts[lang] = restored_text
                translated_entities[lang] = restored_entities
        posted = await send_crosspost_to_channels(
            message,
            ru_text,
            translated_texts,
            translated_entities=translated_entities,
            ru_entities=ru_entities,
        )
        try:
            create_posted_message(
                content_type=str(posted.get("content_type") or "text"),
                source_chat_id=message.chat.id,
                source_message_id=message.message_id,
                message_ids=posted.get("message_ids", {}),
                texts=posted.get("texts", {}),
                entities=entities_map_to_payload(posted.get("entities", {})),
            )
        except Exception:
            logger.exception("Не удалось сохранить информацию о выложенном посте")

        try:
            await message.delete()
        except Exception:
            pass

        await state.clear()
        await sync_anonymous_create_post_state(enabled=False)
        posted_langs = posted.get("message_ids", {})
        langs = ", ".join(
            LANG_TITLES[lang] for lang in POST_LANG_ORDER if lang in posted_langs
        ) or "RU"
        counts = get_status_counts()
        stage_counts = get_application_stage_counts()
        await update_admin_menu_message(
            f"✅ Пост опубликован в каналы: {langs}",
            admin_menu_keyboard(counts, stage_counts)
        )
    except ValueError as exc:
        await message.answer(str(exc))
    except RuntimeError as exc:
        await message.answer(str(exc))
    except Exception:
        logger.exception("Ошибка публикации в режиме create_post")
        await message.answer("⚠️ Не удалось опубликовать пост. Попробуй ещё раз.")

@dp.message(F.text == "/admin", F.chat.id == ADMIN_GROUP_ID)
async def admin_menu(message: Message, state: FSMContext):
    await state.clear()
    await sync_anonymous_create_post_state(enabled=False)
    await clear_admin_temp_messages()
    await ensure_admin_menu_posted()

@dp.callback_query(F.data == "admin_post:cancel")
async def admin_create_post_cancel(call: CallbackQuery, state: FSMContext):
    try:
        if not call.message or call.message.chat.id != ADMIN_GROUP_ID:
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        await state.clear()
        await sync_anonymous_create_post_state(enabled=False)
        await post_admin_menu()
        await safe_call_answer(call, "Отменено")
    except Exception:
        logger.exception("Ошибка отмены режима создания поста")
        await safe_call_answer(call, "Не удалось отменить", show_alert=False)

@dp.callback_query(StateFilter("*"), F.data.startswith("admin_menu:"))
async def admin_menu_action(call: CallbackQuery, state: FSMContext):
    try:
        if not call.message or call.message.chat.id != ADMIN_GROUP_ID:
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        if not await can_manage_admin_callback(call):
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        await safe_call_answer(call)
        await clear_admin_temp_messages()
        action = call.data.split(":", 1)[1]
        if action != "create_post":
            current_state = await state.get_state()
            if current_state in {
                ApplicationStates.admin_create_post.state,
                ApplicationStates.admin_edit_post_text.state,
                ApplicationStates.admin_edit_post_photo.state,
            }:
                await state.clear()
                if current_state == ApplicationStates.admin_create_post.state:
                    await sync_anonymous_create_post_state(enabled=False)
        if action in {"home", "refresh"}:
            await clear_admin_view_message()
            await post_admin_menu()
            return
        if action == "cat_content":
            await clear_admin_view_message()
            await update_admin_menu_message(
                "🗂 <b>Контент</b>\n\nПубликация и управление постами.",
                admin_menu_content_keyboard()
            )
            return
        if action == "cat_apps":
            await clear_admin_view_message()
            counts = get_status_counts()
            stage_counts = get_application_stage_counts()
            await update_admin_menu_message(
                "📥 <b>Заявки</b>\n\nФильтры по статусам и этапам воронки.",
                admin_menu_applications_keyboard(counts, stage_counts)
            )
            return
        if action == "cat_analytics":
            await clear_admin_view_message()
            await update_admin_menu_message(
                "📊 <b>Аналитика</b>\n\nСтатистика и выгрузка Excel.",
                admin_menu_analytics_keyboard()
            )
            return
        if action == "cat_service":
            await clear_admin_view_message()
            await update_admin_menu_message(
                "⚙️ <b>Сервис</b>\n\nОбслуживание меню и базы.",
                admin_menu_service_keyboard()
            )
            return
        if action == "create_post":
            await open_create_post_mode(state)
            return
        if action == "posts":
            await clear_admin_view_message()
            await show_admin_posted_posts(0)
            return
        if action in {"pending", "accepted", "rejected", "all", "stage_quick", "stage_full"}:
            await clear_admin_notify()
            await send_admin_list(call, action, 0)
            return
        if action == "stats":
            await clear_admin_view_message()
            counts = get_status_counts()
            stage_counts = get_application_stage_counts()
            await update_admin_menu_message(
                build_admin_stats_text(),
                admin_menu_keyboard(counts, stage_counts)
            )
            return
        if action == "excel":
            await clear_admin_view_message()
            counts = get_status_counts()
            stage_counts = get_application_stage_counts()
            if not rebuild_excel_from_db:
                await update_admin_menu_message(
                    "🤍 Экспорт в Excel недоступен. Установи openpyxl.",
                    admin_menu_keyboard(counts, stage_counts)
                )
                return
            file_path = rebuild_excel_from_db()
            if not file_path:
                await update_admin_menu_message(
                    "🤍 Файл Excel ещё не создан. Отправь хотя бы одну заявку ✨",
                    admin_menu_keyboard(counts, stage_counts)
                )
                return
            msg = await call.message.answer_document(FSInputFile(str(file_path)))
            track_admin_temp_message(msg.message_id)
            return
        if action == "archive":
            await clear_admin_view_message()
            try:
                archived = await archive_admin_messages_once()
                counts = get_status_counts()
                stage_counts = get_application_stage_counts()
                if archived:
                    await update_admin_menu_message(
                        f"🧹 Архивировано: {archived}",
                        admin_menu_keyboard(counts, stage_counts)
                    )
                else:
                    await update_admin_menu_message(
                        "🤍 Пока нет заявок для архивации ✨",
                        admin_menu_keyboard(counts, stage_counts)
                    )
            except Exception:
                logger.exception("Ошибка ручной архивации")
                counts = get_status_counts()
                stage_counts = get_application_stage_counts()
                await update_admin_menu_message(
                    "⚠️ Не удалось архивировать сейчас.",
                    admin_menu_keyboard(counts, stage_counts)
                )
            return
        if action == "reset":
            await clear_admin_view_message()
            await update_admin_menu_message(
                "⚠️ Ты уверена, что хочешь полностью обнулить базу и статистику?",
                confirm_reset_db_keyboard()
            )
            return
        await safe_call_answer(call, "Неизвестная команда", show_alert=False)
    except Exception:
        logger.exception("Ошибка в admin_menu_action")
        await safe_call_answer(call, "Ошибка выполнения команды", show_alert=False)

@dp.callback_query(StateFilter("*"), F.data.startswith("admin_list:"))
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

@dp.callback_query(StateFilter("*"), F.data.startswith("admin_view_photo:"))
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
        if filter_key == "stage_quick":
            total = len(list_applications_by_stage("quick"))
        elif filter_key == "stage_full":
            total = len(list_applications_by_stage("full"))
        else:
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

@dp.callback_query(F.data.startswith("admin_posts:"))
async def admin_posts_pagination(call: CallbackQuery):
    try:
        if not call.message or call.message.chat.id != ADMIN_GROUP_ID:
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        _, offset_raw = call.data.split(":", 1)
        offset = int(offset_raw)
        await show_admin_posted_posts(offset)
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка открытия выложенных постов")
        await safe_call_answer(call, "Не удалось открыть посты", show_alert=False)


@dp.callback_query(F.data.startswith("admin_post_delete:"))
async def admin_post_delete(call: CallbackQuery):
    try:
        if not call.message or call.message.chat.id != ADMIN_GROUP_ID:
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        _, post_id_raw, offset_raw = call.data.split(":", 2)
        post_id = int(post_id_raw)
        offset = int(offset_raw)
        item = get_posted_message(post_id)
        if not item:
            await safe_call_answer(call, "Пост не найден", show_alert=False)
            await show_admin_posted_posts(offset)
            return
        await delete_post_from_channels(item)
        delete_posted_message(post_id)
        _, _, total = await show_admin_posted_posts(offset)
        if total == 0:
            await post_admin_menu()
        await safe_call_answer(call, "Удалено")
    except Exception:
        logger.exception("Ошибка удаления выложенного поста")
        await safe_call_answer(call, "Не удалось удалить пост", show_alert=False)


@dp.callback_query(F.data.startswith("admin_post_edit_text:"))
async def admin_post_edit_text(call: CallbackQuery, state: FSMContext):
    try:
        if not call.message or call.message.chat.id != ADMIN_GROUP_ID:
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        _, post_id_raw, offset_raw = call.data.split(":", 2)
        post_id = int(post_id_raw)
        offset = int(offset_raw)
        item = get_posted_message(post_id)
        if not item:
            await safe_call_answer(call, "Пост не найден", show_alert=False)
            await show_admin_posted_posts(offset)
            return
        current_ru = post_full_text(item)
        prompt_base = (
            "✏️ Отправь новый текст поста на русском.\n\n"
            "Форматирование, ссылки и премиум-эмодзи будут сохранены.\n"
            "Я обновлю текст во всех каналах автоматически.\n\n"
            "<b>Текущий текст RU:</b>\n"
        )
        reserve = TELEGRAM_TEXT_LIMIT - len(prompt_base) - 120
        shown_ru, was_cut = clip_text_for_telegram(current_ru or "—", max(reserve, 256))
        prompt = f"{prompt_base}{html.escape(shown_ru or '—')}"
        while len(prompt) > TELEGRAM_TEXT_LIMIT and shown_ru:
            shown_ru = shown_ru[:-32].rstrip()
            was_cut = True
            prompt = f"{prompt_base}{html.escape(shown_ru or '—')}"
        if was_cut:
            prompt += "\n\n⚠️ Текущий текст очень длинный, показана часть."
        await state.set_state(ApplicationStates.admin_edit_post_text)
        await state.update_data(post_id=post_id, posts_offset=offset)
        await update_admin_view_message(
            prompt,
            admin_posts_edit_keyboard(post_id, offset),
            None,
        )
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка входа в режим редактирования текста поста")
        await safe_call_answer(call, "Не удалось открыть редактирование", show_alert=False)


def post_media_type_name(content_type: str) -> str:
    normalized = (content_type or "").strip().lower()
    return {
        "photo": "фото",
        "video": "видео",
        "document": "файл",
        "animation": "GIF",
    }.get(normalized, "медиа")


def post_media_replace_prompt(content_type: str) -> str:
    normalized = (content_type or "").strip().lower()
    if normalized == "photo":
        return "🖼 Отправь новое фото одним сообщением.\n\nПодписи на всех языках сохранятся, заменится только изображение."
    if normalized == "video":
        return "🎬 Отправь новое видео одним сообщением.\n\nПодписи на всех языках сохранятся, заменится только видео."
    if normalized == "document":
        return "📄 Отправь новый файл одним сообщением.\n\nПодписи на всех языках сохранятся, заменится только файл."
    if normalized == "animation":
        return "🎞 Отправь новую GIF одним сообщением.\n\nПодписи на всех языках сохранятся, заменится только GIF."
    return "🖼 Отправь новое медиа одним сообщением."


def extract_media_file_id_for_post(message: Message, content_type: str) -> str | None:
    normalized = (content_type or "").strip().lower()
    if normalized == "photo" and message.photo:
        return message.photo[-1].file_id
    if normalized == "video" and message.video:
        return message.video.file_id
    if normalized == "document" and message.document:
        return message.document.file_id
    if normalized == "animation" and message.animation:
        return message.animation.file_id
    return None


@dp.callback_query(F.data.startswith("admin_post_edit_photo:"))
async def admin_post_edit_photo(call: CallbackQuery, state: FSMContext):
    try:
        if not call.message or call.message.chat.id != ADMIN_GROUP_ID:
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        _, post_id_raw, offset_raw = call.data.split(":", 2)
        post_id = int(post_id_raw)
        offset = int(offset_raw)
        item = get_posted_message(post_id)
        if not item:
            await safe_call_answer(call, "Пост не найден", show_alert=False)
            await show_admin_posted_posts(offset)
            return
        content_type = str(item.get("content_type") or "").strip().lower()
        if content_type not in MEDIA_CONTENT_TYPES:
            await safe_call_answer(call, "У этого поста нет медиа для замены", show_alert=True)
            return
        await state.set_state(ApplicationStates.admin_edit_post_photo)
        await state.update_data(post_id=post_id, posts_offset=offset, post_media_type=content_type)
        await update_admin_view_message(
            post_media_replace_prompt(content_type),
            admin_posts_edit_keyboard(post_id, offset),
            None,
        )
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка входа в режим редактирования медиа поста")
        await safe_call_answer(call, "Не удалось открыть замену медиа", show_alert=False)


@dp.callback_query(F.data.startswith("admin_post_edit_cancel:"))
async def admin_post_edit_cancel(call: CallbackQuery, state: FSMContext):
    try:
        if not call.message or call.message.chat.id != ADMIN_GROUP_ID:
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        _, post_id_raw, offset_raw = call.data.split(":", 2)
        _ = int(post_id_raw)
        offset = int(offset_raw)
        await state.clear()
        await show_admin_posted_posts(offset)
        await safe_call_answer(call, "Отменено")
    except Exception:
        logger.exception("Ошибка отмены редактирования поста")
        await safe_call_answer(call, "Не удалось отменить", show_alert=False)


@dp.message(StateFilter(ApplicationStates.admin_edit_post_text), F.chat.id == ADMIN_GROUP_ID)
async def admin_post_edit_text_submit(message: Message, state: FSMContext):
    try:
        if not await can_manage_admin_group(message):
            await message.answer("⚠️ Для редактирования нужны права администратора этой группы.")
            return
        if not message.text:
            await message.answer("⚠️ Отправь текст поста (не фото и не файл).")
            return
        ru_text, ru_entities = extract_post_text_and_entities(message)
        if not ru_text.strip():
            await message.answer("⚠️ Текст пустой. Отправь текст заново.")
            return
        if not CYRILLIC_RE.search(ru_text):
            await message.answer("⚠️ Текст должен быть на русском, чтобы сделать автоперевод.")
            return

        data = await state.get_data()
        post_id = int(data.get("post_id", 0))
        offset = int(data.get("posts_offset", 0))
        item = get_posted_message(post_id)
        if not item:
            await message.answer("⚠️ Пост не найден.")
            await state.clear()
            await show_admin_posted_posts(offset)
            return

        message_ids = _post_message_ids(item)
        target_langs = [lang for lang in POST_LANG_ORDER if lang in message_ids and lang != "ru"]
        translated_texts: dict[str, str] = {}
        translated_entities: dict[str, list[MessageEntity] | None] = {}

        marked_text, required_tokens, rich_specs, custom_specs, locked_specs = markerize_entities_for_translation(
            ru_text,
            ru_entities,
        )
        translated_marked = await translate_ru_to_targets(
            marked_text,
            target_langs,
            required_tokens=required_tokens,
        )
        for lang in target_langs:
            translated_marked_text = translated_marked.get(lang, "")
            restored_text, restored_entities = restore_entities_from_markers(
                translated_marked_text,
                required_tokens,
                rich_specs,
                custom_specs,
                locked_specs,
            )
            translated_texts[lang] = restored_text
            translated_entities[lang] = restored_entities

        texts_map = {"ru": ru_text, **translated_texts}
        entities_map = {"ru": ru_entities, **translated_entities}
        final_texts, final_entities = await edit_post_text_in_channels(item, texts_map, entities_map)
        update_posted_message(
            post_id,
            texts=final_texts,
            entities=entities_map_to_payload(final_entities),
        )
        await state.clear()
        await show_admin_posted_posts(offset)
        try:
            await message.delete()
        except Exception:
            pass
    except RuntimeError as exc:
        await message.answer(str(exc))
    except Exception:
        logger.exception("Ошибка редактирования текста выложенного поста")
        await message.answer("⚠️ Не удалось обновить текст поста.")


@dp.message(StateFilter(ApplicationStates.admin_edit_post_photo), F.chat.id == ADMIN_GROUP_ID)
async def admin_post_edit_photo_submit(message: Message, state: FSMContext):
    try:
        if not await can_manage_admin_group(message):
            await message.answer("⚠️ Для редактирования нужны права администратора этой группы.")
            return
        data = await state.get_data()
        post_id = int(data.get("post_id", 0))
        offset = int(data.get("posts_offset", 0))
        item = get_posted_message(post_id)
        if not item:
            await message.answer("⚠️ Пост не найден.")
            await state.clear()
            await show_admin_posted_posts(offset)
            return

        content_type = str(item.get("content_type") or "").strip().lower()
        expected_type = str(data.get("post_media_type") or content_type).strip().lower()
        new_file_id = extract_media_file_id_for_post(message, expected_type)
        if not new_file_id:
            media_name = post_media_type_name(expected_type)
            await message.answer(f"⚠️ Отправь именно {media_name} одним сообщением.")
            return

        final_texts, final_entities = await replace_post_media_in_channels(
            item,
            new_file_id,
            expected_type,
        )
        update_posted_message(
            post_id,
            texts=final_texts,
            entities=entities_map_to_payload(final_entities),
        )
        await state.clear()
        await show_admin_posted_posts(offset)
        try:
            await message.delete()
        except Exception:
            pass
    except RuntimeError as exc:
        await message.answer(str(exc))
    except Exception:
        logger.exception("Ошибка замены фото у выложенного поста")
        await message.answer("⚠️ Не удалось заменить фото.")

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
        counts = get_status_counts()
        stage_counts = get_application_stage_counts()
        await update_admin_menu_message(
            "✅ База и статистика полностью обнулены.",
            admin_menu_keyboard(counts, stage_counts)
        )
    except Exception:
        logger.exception("Ошибка сброса базы")
        counts = get_status_counts()
        stage_counts = get_application_stage_counts()
        await update_admin_menu_message(
            "⚠️ Ошибка при сбросе базы.",
            admin_menu_keyboard(counts, stage_counts)
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
        await setup_bot_commands()
    except Exception:
        logger.exception("Не удалось зарегистрировать команды бота")
    channels = active_post_channels()
    logger.info("Кросспост каналы: %s", ", ".join(f"{lang}:{chat_id}" for lang, chat_id in channels.items()))
    missing_langs = missing_crosspost_langs(channels)
    if missing_langs:
        logger.warning("Не настроены каналы кросспоста: %s", ", ".join(missing_langs))
    try:
        cleanup_old_form_data()
    except Exception:
        logger.exception("Ошибка очистки старых данных")
    await ensure_admin_menu_posted()
    tasks = [
        asyncio.create_task(daily_stats_task(), name="daily_stats_task"),
        asyncio.create_task(archive_admin_messages_task(), name="archive_admin_messages_task"),
    ]
    try:
        try:
            await bot.delete_webhook(drop_pending_updates=False)
        except Exception:
            logger.exception("Не удалось удалить webhook перед polling")
        await run_polling_forever()
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await bot.session.close()


async def run_polling_forever():
    retry_delay = float(POLLING_RETRY_BASE_SECONDS)
    while True:
        started_at = datetime.now(timezone.utc)
        reason = "stopped"
        try:
            logger.info("Запуск polling...")
            await dp.start_polling(bot)
            logger.warning("Polling остановлен без исключения")
        except asyncio.CancelledError:
            logger.info("Polling отменён, завершаю процесс")
            raise
        except TelegramConflictError:
            reason = "conflict"
            logger.exception("Конфликт getUpdates: запущено больше одного экземпляра бота")
        except TelegramNetworkError:
            reason = "network"
            logger.exception("Сетевая ошибка Telegram API")
        except Exception:
            reason = "error"
            logger.exception("Необработанная ошибка polling")

        uptime = (datetime.now(timezone.utc) - started_at).total_seconds()
        if reason == "conflict":
            retry_delay = float(POLLING_CONFLICT_SLEEP_SECONDS)
        elif uptime >= 180:
            retry_delay = float(POLLING_RETRY_BASE_SECONDS)
        else:
            retry_delay = min(retry_delay * 2, float(POLLING_RETRY_MAX_SECONDS))

        sleep_for = retry_delay + (random.random() * POLLING_RETRY_JITTER_SECONDS)
        logger.info(
            "Перезапуск polling через %.1f сек (причина=%s, uptime=%.1f сек)",
            sleep_for,
            reason,
            uptime,
        )
        await asyncio.sleep(sleep_for)

if __name__ == "__main__":
    asyncio.run(main())
