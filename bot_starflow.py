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

# Starflow bot uses isolated project identity while sharing the same DB/admin stream.
os.environ.setdefault("PROJECT_KEY", "starflow_corp")
if (os.getenv("STARFLOW_BOT_TOKEN") or "").strip():
    os.environ["BOT_TOKEN"] = (os.getenv("STARFLOW_BOT_TOKEN") or "").strip()
if (os.getenv("STARFLOW_BOT_USERNAME") or "").strip():
    os.environ["BOT_USERNAME"] = (os.getenv("STARFLOW_BOT_USERNAME") or "").strip()
if (os.getenv("STARFLOW_CHANNEL_LINK") or "").strip():
    os.environ["CHANNEL_LINK"] = (os.getenv("STARFLOW_CHANNEL_LINK") or "").strip()
if (os.getenv("STARFLOW_SITE_URL") or "").strip():
    os.environ["SITE_URL"] = (os.getenv("STARFLOW_SITE_URL") or "").strip()
if (os.getenv("STARFLOW_ADMIN_GROUP_ID") or "").strip():
    os.environ["ADMIN_GROUP_ID"] = (os.getenv("STARFLOW_ADMIN_GROUP_ID") or "").strip()

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, FSInputFile,
    InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAnimation,
    ChatJoinRequest, InlineKeyboardMarkup, MessageEntity,
    BotCommand, BotCommandScopeDefault, BotCommandScopeChatAdministrators,
    BufferedInputFile,
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
import keyboards as shared_keyboards
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
from texts_starflow import (
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
from application_rules import (
    FORM_NAME_MAX_LEN as SHARED_FORM_NAME_MAX_LEN,
    FORM_CITY_MAX_LEN as SHARED_FORM_CITY_MAX_LEN,
    FORM_PHONE_MAX_LEN as SHARED_FORM_PHONE_MAX_LEN,
    FORM_AGE_MAX_LEN as SHARED_FORM_AGE_MAX_LEN,
    FORM_DEVICE_MODEL_MAX_LEN as SHARED_FORM_DEVICE_MODEL_MAX_LEN,
    FORM_WORK_TIME_MAX_LEN as SHARED_FORM_WORK_TIME_MAX_LEN,
    FORM_TELEGRAM_MAX_LEN as SHARED_FORM_TELEGRAM_MAX_LEN,
    FORM_EXPERIENCE_MAX_LEN as SHARED_FORM_EXPERIENCE_MAX_LEN,
    FORM_YES_NO_MAX_LEN as SHARED_FORM_YES_NO_MAX_LEN,
    FORM_DEVICES_MAX_LEN as SHARED_FORM_DEVICES_MAX_LEN,
    normalize_user_text_input as normalize_user_text_input_shared,
    normalize_phone as normalize_phone_shared,
    is_valid_phone as is_valid_phone_shared,
    normalize_birthdate as normalize_birthdate_shared,
    is_valid_birthdate as is_valid_birthdate_shared,
    has_any_digit as has_any_digit_shared,
    normalize_yes_no as normalize_yes_no_shared,
    normalize_telegram as normalize_telegram_shared,
)

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
STARFLOW_ENABLE_ADMIN_JOBS = (
    (os.getenv("STARFLOW_ENABLE_ADMIN_JOBS") or "").strip().lower() in {"1", "true", "yes", "on"}
)

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
        admin_chat_id = current_admin_chat_id()
        await bot.send_message(
            admin_chat_id,
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

        channel_lang = STARFLOW_DEFAULT_LANG
        for lang_code, configured_chat_id in CHANNEL_ID_BY_LANG.items():
            if lang_code not in STARFLOW_USER_LANGS:
                continue
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

        had_lang_before = has_lang_for(user_id)
        already_in_bot = (
            had_lang_before
            or get_application(user_id) is not None
            or bool(get_menu_message_id(user_id))
            or bool(get_flow_message_id(user_id))
        )
        if not had_lang_before:
            set_lang_for(user_id, channel_lang)

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
        invite_message = invite_by_lang.get(channel_lang, invite_by_lang[STARFLOW_DEFAULT_LANG])
        await bot.send_message(
            user_id,
            invite_message
        )
    except Exception:
        logger.exception("Ошибка в on_join_request")

# ================= HELPERS =================

def is_valid_phone(text: str) -> bool:
    return is_valid_phone_shared(text)

def normalize_birthdate(text: str) -> str | None:
    return normalize_birthdate_shared(text)

def is_valid_birthdate(text: str) -> bool:
    return is_valid_birthdate_shared(text)

def has_any_digit(text: str) -> bool:
    return has_any_digit_shared(text)

def normalize_phone(text: str) -> str | None:
    return normalize_phone_shared(text)


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

YES_NO_BY_LANG = {
    "ru": {"yes": "Да", "no": "Нет"},
    "en": {"yes": "Yes", "no": "No"},
    "pt": {"yes": "Sim", "no": "Não"},
    "es": {"yes": "Sí", "no": "No"},
}


def localize_yes_no_value(value: str | None, lang: str | None) -> str | None:
    if value is None:
        return None
    raw = str(value).strip().lower()
    if raw in {"да", "yes", "sim", "sí", "si"}:
        key = "yes"
    elif raw in {"нет", "no", "não", "nao"}:
        key = "no"
    else:
        return value
    locale = normalize_lang(lang)
    return YES_NO_BY_LANG.get(locale, YES_NO_BY_LANG["en"]).get(key, value)


def normalize_yes_no(text: str, lang: str | None = None) -> str | None:
    normalized = normalize_yes_no_shared(text)
    if not normalized:
        return None
    return localize_yes_no_value(normalized, lang)


async def safe_call_answer(call: CallbackQuery, text: str | None = None, show_alert: bool = False):
    try:
        if text is None:
            await call.answer()
        else:
            await call.answer(text, show_alert=show_alert)
    except Exception:
        pass


def current_admin_chat_id() -> int:
    raw = get_setting(ADMIN_CHAT_ID_SETTING_KEY)
    if raw and str(raw).lstrip("-").isdigit():
        return int(raw)
    return int(ADMIN_GROUP_ID)


def bind_admin_chat_id(chat_id: int | None) -> None:
    if not chat_id:
        return
    chat_id = int(chat_id)
    current = current_admin_chat_id()
    if chat_id == current:
        return
    set_setting(ADMIN_CHAT_ID_SETTING_KEY, str(chat_id))
    # Message ids are chat-scoped; reset to avoid editing stale messages in another chat.
    set_setting(ADMIN_MENU_SETTING_KEY, None)
    set_setting(ADMIN_NOTIFY_SETTING_KEY, None)
    set_setting(ADMIN_VIEW_SETTING_KEY, None)
    set_setting(ADMIN_PHOTOS_SETTING_KEY, None)
    logger.warning("Admin chat rebound from %s to %s", current, chat_id)


def is_admin_chat(chat_id: int | None) -> bool:
    if chat_id is None:
        return False
    try:
        cid = int(chat_id)
    except Exception:
        return False
    return cid in {int(ADMIN_GROUP_ID), int(current_admin_chat_id())}


def normalize_telegram(text: str) -> str | None:
    return normalize_telegram_shared(text)


def is_valid_email(text: str) -> bool:
    raw = (text or "").strip()
    if not raw or len(raw) > FORM_EMAIL_MAX_LEN:
        return False
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]{2,}", raw, flags=re.IGNORECASE) is not None

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
    if lang not in STARFLOW_USER_LANGS:
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
    "email",
    "living",
    "devices",
    "work_time",
    "telegram",
    "experience",
    "lang",
    "project",
    "application_stage",
    "site_lead_token",
}
OPTIONAL_FORM_DATA_FIELDS = {
    "country",
    "email",
    "lang",
    "project",
    "site_lead_token",
}
REQUIRED_PREVIEW_FIELDS = {
    "name",
    "phone",
    "age",
    "email",
    "devices",
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
    ApplicationStates.headphones: "email",
    ApplicationStates.living: "living",
    ApplicationStates.devices: "devices",
    ApplicationStates.work_time: "work_time",
    ApplicationStates.telegram: "telegram",
    ApplicationStates.experience: "experience",
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
    source = normalize_source_value(app.get("source"), data if isinstance(data, dict) else None)
    return source in {SOURCE_SITE_TG, SOURCE_SITE_WHATSAPP} and is_quick_application(data)

def build_ack(user_id: int | None = None) -> str:
    lang = lang_for(user_id) if user_id is not None else STARFLOW_DEFAULT_LANG
    lines = support_lines(lang)
    return f"{t(lang, 'ack_text')}\n{random.choice(lines)}"

async def gentle_typing(chat_id: int, duration: float | None = None):
    try:
        await bot.send_chat_action(chat_id, ChatAction.TYPING)
    except Exception:
        return
    await asyncio.sleep(duration or random.uniform(0.4, 0.8))

def build_status_line(status: str | None, lang: str = "en") -> str | None:
    if not status or status == "new":
        return None
    label = status_label(status, lang)
    if not label:
        return None
    return t(lang, "status_line", status=label)

def build_menu_caption_with_status(
    status: str,
    base_caption: str,
    lang: str = "en",
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

PORTFOLIO_AUTO_DELETE_SECONDS = 120
PORTFOLIO_VIDEO_AUTONEXT_SECONDS = _get_env_int("PORTFOLIO_VIDEO_AUTONEXT_SECONDS", default=18, min_value=5)
AUTO_REQUEST_INFO_DELAY_MINUTES = _get_env_int("AUTO_REQUEST_INFO_DELAY_MINUTES", default=45, min_value=5)
AUTO_REQUEST_INFO_CHECK_SECONDS = _get_env_int("AUTO_REQUEST_INFO_CHECK_SECONDS", default=120, min_value=30)
AUTO_REQUEST_INFO_FLAG_KEY = "auto_info_requested_at"
PORTFOLIO_MEDIA_IDS: dict[int, list[int]] = {}
PORTFOLIO_CLEANUP_TASKS: dict[int, asyncio.Task] = {}
PORTFOLIO_AUTONEXT_TASKS: dict[int, asyncio.Task] = {}
PORTFOLIO_PLAYER_SPECS = (
    {
        "kind": "photo",
        "file": "media/review1.jpg",
        "title": {"ru": "Отзывы партнёров", "en": "Partner reviews", "pt": "Avaliações de parceiros", "es": "Reseñas de partners"},
    },
    {
        "kind": "photo",
        "file": "media/review2.jpg",
        "title": {"ru": "Отзывы партнёров", "en": "Partner reviews", "pt": "Avaliações de parceiros", "es": "Reseñas de partners"},
    },
    {
        "kind": "video",
        "file": "media/stream1.MP4",
        "title": {"ru": "Примеры стримов", "en": "Stream examples", "pt": "Exemplos de streams", "es": "Ejemplos de streams"},
        "autonext_seconds": PORTFOLIO_VIDEO_AUTONEXT_SECONDS,
    },
    {
        "kind": "video",
        "file": "media/stream2.MP4",
        "title": {"ru": "Примеры стримов", "en": "Stream examples", "pt": "Exemplos de streams", "es": "Ejemplos de streams"},
        "autonext_seconds": PORTFOLIO_VIDEO_AUTONEXT_SECONDS,
    },
)
ADMIN_TEMP_MESSAGE_IDS: list[int] = []
CAPTION_LIMIT = 1024
FORM_NAME_MAX_LEN = SHARED_FORM_NAME_MAX_LEN
FORM_CITY_MAX_LEN = SHARED_FORM_CITY_MAX_LEN
FORM_PHONE_MAX_LEN = SHARED_FORM_PHONE_MAX_LEN
FORM_AGE_MAX_LEN = SHARED_FORM_AGE_MAX_LEN
FORM_DEVICE_MODEL_MAX_LEN = SHARED_FORM_DEVICE_MODEL_MAX_LEN
FORM_WORK_TIME_MAX_LEN = SHARED_FORM_WORK_TIME_MAX_LEN
FORM_TELEGRAM_MAX_LEN = SHARED_FORM_TELEGRAM_MAX_LEN
FORM_EXPERIENCE_MAX_LEN = SHARED_FORM_EXPERIENCE_MAX_LEN
FORM_YES_NO_MAX_LEN = SHARED_FORM_YES_NO_MAX_LEN
FORM_DEVICES_MAX_LEN = SHARED_FORM_DEVICES_MAX_LEN
FORM_EMAIL_MAX_LEN = 160
DAILY_STATS_HOUR = 10
DAILY_STATS_MINUTE = 0
ADMIN_ARCHIVE_DAYS = 7
ADMIN_ARCHIVE_CHECK_HOURS = 6
ADMIN_CHAT_ID_SETTING_KEY = "admin_chat_id"
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
PUBLIC_MANAGER_HANDLE = (os.getenv("STARFLOW_PUBLIC_MANAGER_HANDLE") or "@starflowmanager").strip()
PUBLIC_MANAGER_USERNAME = PUBLIC_MANAGER_HANDLE.lstrip("@")
STARFLOW_DEFAULT_LANG = "en"
STARFLOW_USER_LANGS = ("en", "pt", "es")

# Rebind shared keyboards to Starflow translations.
shared_keyboards.t = t
shared_keyboards.field_title = field_title


def preview_keyboard(lang: str = STARFLOW_DEFAULT_LANG):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_edit_data"), callback_data="preview_edit")],
            [InlineKeyboardButton(text=t(lang, "btn_send"), callback_data="preview_confirm")],
            [InlineKeyboardButton(text=t(lang, "menu_home"), callback_data="main_menu")],
        ]
    )


def preview_edit_menu(lang: str = STARFLOW_DEFAULT_LANG):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=field_title("name", lang), callback_data="edit:name")],
            [InlineKeyboardButton(text=field_title("phone", lang), callback_data="edit:phone")],
            [InlineKeyboardButton(text=field_title("age", lang), callback_data="edit:age")],
            [InlineKeyboardButton(text=field_title("email", lang), callback_data="edit:email")],
            [InlineKeyboardButton(text=field_title("telegram", lang), callback_data="edit:telegram")],
            [InlineKeyboardButton(text=field_title("city", lang), callback_data="edit:city")],
            [InlineKeyboardButton(text=field_title("work_time", lang), callback_data="edit:work_time")],
            [InlineKeyboardButton(text=field_title("experience", lang), callback_data="edit:experience")],
            [InlineKeyboardButton(text=field_title("living", lang), callback_data="edit:living")],
            [InlineKeyboardButton(text=field_title("devices", lang), callback_data="edit:devices")],
            [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="preview_back")],
        ]
    )


def portfolio_menu(lang: str = STARFLOW_DEFAULT_LANG):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "portfolio_menu_reviews"), callback_data="portfolio_reviews")],
            [InlineKeyboardButton(text=t(lang, "portfolio_menu_videos"), callback_data="portfolio_videos")],
            [InlineKeyboardButton(text=t(lang, "portfolio_menu_pdf"), callback_data="portfolio_pdf")],
            [InlineKeyboardButton(text=t(lang, "menu_home"), callback_data="main_menu")],
        ]
    )


def language_keyboard(current_lang: str = STARFLOW_DEFAULT_LANG, include_home: bool = True):
    def lang_label(code: str, title: str) -> str:
        return f"✅ {title}" if code == current_lang else title

    rows = [[
        InlineKeyboardButton(text=lang_label("en", "English"), callback_data="set_lang:en"),
        InlineKeyboardButton(text=lang_label("pt", "Português"), callback_data="set_lang:pt"),
        InlineKeyboardButton(text=lang_label("es", "Español"), callback_data="set_lang:es"),
    ]]
    if include_home:
        rows.append([InlineKeyboardButton(text=t(current_lang, "menu_home"), callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_accepted_keyboard(user_id: int, contact_url: str | None = None):
    contact = contact_url or f"tg://user?id={user_id}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Принято", callback_data=f"admin_status:{user_id}:accepted")],
            [InlineKeyboardButton(text="📨 Отправить сообщение партнёру", callback_data=f"admin_send_model:{user_id}")],
            [InlineKeyboardButton(text="💬 Написать кандидату", url=contact)],
        ]
    )


def _parse_admin_allowed_ids() -> set[int]:
    raw_values = [
        os.getenv("ADMIN_USER_ID", ""),
        os.getenv("ADMIN_USER_IDS", ""),
        os.getenv("ADMIN_ID", ""),
    ]
    result: set[int] = set()
    for raw in raw_values:
        for part in str(raw or "").replace(";", ",").split(","):
            value = part.strip()
            if not value:
                continue
            if value.lstrip("-").isdigit():
                result.add(int(value))
    return result


ADMIN_ALLOWED_USER_IDS = _parse_admin_allowed_ids()
ADMIN_ALLOWED_USERNAME = ADMIN_USERNAME.lstrip("@").strip().lower()
ADMIN_ALLOWED_USERNAMES = {
    item
    for item in {
        ADMIN_ALLOWED_USERNAME,
        PUBLIC_MANAGER_USERNAME.strip().lower(),
    }
    if item
}
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
            "📣 Перед продолжением подпишись на канал Starflow.\n\n"
            "Как работает партнёрка:\n"
            "• ты привлекаешь кандидатов на собеседования\n"
            "• источник трафика любой\n"
            "• CPA $20-40 за успешное собеседование\n"
            "• выплаты каждое воскресенье в USDT\n\n"
            "Дальше выбери формат:\n"
            "• пройти всё в боте\n"
            "• или написать менеджеру"
        ),
        "step1": (
            "✅ Предзаявка сохранена.\n\n"
            "Ты уже в системе, контакт получен.\n"
            "Сейчас коротко покажу следующий шаг."
        ),
        "step2": (
            "Что дальше:\n"
            "• заполняешь финальный блок\n"
            "• фиксируем твой профиль партнёра\n"
            "• даём доступ к CRM и материалам\n\n"
            "Остался обязательный блок (около 2 минут)."
        ),
        "autostart": (
            "✅ Отлично, короткая часть заполнена.\n"
            "Переходим к финальному блоку, чтобы запустить партнёрский старт."
        ),
        "next": "Что дальше",
        "start": "Продолжить этап 2 (обязательно)",
        "manager": "💬 Связь с менеджером",
        "menu_recommendation": (
            "✅ Первая часть анкеты принята мгновенно и автоматически.\n\n"
            "Чтобы быстрее понять формат, открой пункты:\n"
            "• 📁 Материалы партнёра\n"
            "• ℹ️ Об оффере\n"
            "• 📣 Наш канал\n\n"
            "После этого нажми «🤝 Стать партнёром» и продолжим.\n"
            "Если останутся вопросы — пиши менеджеру."
        ),
        "channel": "📣 Открыть канал",
        "continue_bot": "✅ Подать заявку через бота",
        "wait_gate": "Выбери один из вариантов ниже 👇",
        "wait": "Нажми кнопку, чтобы продолжить этап 2 👇",
        "expired": "Ссылка из сайта устарела. Нажми «Стать партнёром» и заполни короткий этап заново.",
    },
    "en": {
        "gate": (
            "📣 Before continuing, open the Starflow channel.\n\n"
            "How the partner offer works:\n"
            "• you bring candidates to interviews\n"
            "• any traffic source is allowed\n"
            "• CPA $20-40 per successful interview\n"
            "• payouts every Sunday in USDT\n\n"
            "Now choose your path:\n"
            "• complete everything in the bot\n"
            "• or message the manager"
        ),
        "step1": (
            "✅ Pre-application saved.\n\n"
            "You are already in the system and we have your contact.\n"
            "Now I will quickly explain the next step."
        ),
        "step2": (
            "What happens next:\n"
            "• complete the final block\n"
            "• we lock your partner profile\n"
            "• we give you CRM and materials\n\n"
            "One required final block is left (about 2 minutes)."
        ),
        "autostart": (
            "✅ Great, the short part is done.\n"
            "Let’s move to the final required block to launch your partner flow."
        ),
        "next": "What’s next",
        "start": "Continue Step 2 (required)",
        "manager": "💬 Contact manager",
        "menu_recommendation": (
            "✅ The first part of your application was accepted instantly and automatically.\n\n"
            "To understand the format better, open these sections:\n"
            "• 📁 Partner materials\n"
            "• ℹ️ About the offer\n"
            "• 📣 Our channel\n\n"
            "Then tap “🤝 Become a partner” to continue.\n"
            "If you have questions, message the manager."
        ),
        "channel": "📣 Open channel",
        "continue_bot": "✅ Apply through bot",
        "wait_gate": "Choose one option below 👇",
        "wait": "Tap the button to continue Step 2 👇",
        "expired": "Your website link has expired. Tap “Become a partner” and submit the short step again.",
    },
    "pt": {
        "gate": (
            "📣 Antes de continuar, abra o canal Starflow.\n\n"
            "Como funciona a parceria:\n"
            "• você traz candidatos para entrevistas\n"
            "• qualquer fonte de tráfego é válida\n"
            "• CPA de $20-40 por entrevista concluída\n"
            "• pagamentos todo domingo em USDT\n\n"
            "Agora escolha o caminho:\n"
            "• concluir tudo no bot\n"
            "• ou falar com o gerente"
        ),
        "step1": (
            "✅ Pré-cadastro salvo.\n\n"
            "Você já está no sistema e já temos seu contato.\n"
            "Agora explico rapidamente o próximo passo."
        ),
        "step2": (
            "Próximos passos:\n"
            "• preencher o bloco final\n"
            "• confirmar seu perfil de parceiro\n"
            "• liberar CRM e materiais\n\n"
            "Falta um bloco final obrigatório (cerca de 2 minutos)."
        ),
        "autostart": (
            "✅ Perfeito, a parte curta já está pronta.\n"
            "Vamos para o bloco final obrigatório para iniciar seu fluxo de parceria."
        ),
        "next": "Próximo passo",
        "start": "Continuar Etapa 2 (obrigatória)",
        "manager": "💬 Contato com gerente",
        "menu_recommendation": (
            "✅ A primeira parte do cadastro foi aceita de forma instantânea e automática.\n\n"
            "Para entender melhor o formato, abra as seções:\n"
            "• 📁 Materiais do parceiro\n"
            "• ℹ️ Sobre a oferta\n"
            "• 📣 Nosso canal\n\n"
            "Depois toque em “🤝 Tornar-se parceiro” para continuar.\n"
            "Se tiver dúvidas, fale com o gerente."
        ),
        "channel": "📣 Abrir canal",
        "continue_bot": "✅ Enviar pelo bot",
        "wait_gate": "Escolha uma opção abaixo 👇",
        "wait": "Toque no botão para continuar a Etapa 2 👇",
        "expired": "Seu link do site expirou. Toque em “Tornar-se parceiro” e preencha a etapa curta novamente.",
    },
    "es": {
        "gate": (
            "📣 Antes de continuar, abre el canal de Starflow.\n\n"
            "Cómo funciona la alianza:\n"
            "• traes candidatos a entrevistas\n"
            "• cualquier fuente de tráfico es válida\n"
            "• CPA de $20-40 por entrevista exitosa\n"
            "• pagos cada domingo en USDT\n\n"
            "Ahora elige tu camino:\n"
            "• completar todo en el bot\n"
            "• o escribir al manager"
        ),
        "step1": (
            "✅ Pre-solicitud guardada.\n\n"
            "Ya estás en el sistema y ya tenemos tu contacto.\n"
            "Ahora te explico rápido el siguiente paso."
        ),
        "step2": (
            "Siguiente paso:\n"
            "• completar el bloque final\n"
            "• fijar tu perfil de partner\n"
            "• entregar CRM y materiales\n\n"
            "Queda un bloque final obligatorio (unos 2 minutos)."
        ),
        "autostart": (
            "✅ Perfecto, la parte corta ya está lista.\n"
            "Vamos directo al bloque final obligatorio para activar tu flujo de partner."
        ),
        "next": "Qué sigue",
        "start": "Continuar Etapa 2 (obligatoria)",
        "manager": "💬 Contacto con manager",
        "menu_recommendation": (
            "✅ La primera parte de tu solicitud fue aceptada al instante y de forma automática.\n\n"
            "Para conocer mejor el formato, abre estas secciones:\n"
            "• 📁 Materiales del partner\n"
            "• ℹ️ Sobre la oferta\n"
            "• 📣 Nuestro canal\n\n"
            "Después pulsa “🤝 Ser partner” para continuar.\n"
            "Si tienes preguntas, escribe al manager."
        ),
        "channel": "📣 Abrir canal",
        "continue_bot": "✅ Enviar por el bot",
        "wait_gate": "Elige una opción abajo 👇",
        "wait": "Pulsa el botón para continuar la Etapa 2 👇",
        "expired": "Tu enlace del sitio venció. Pulsa “Ser partner” y completa de nuevo la etapa corta.",
    },
}

def stage2_text(lang: str, key: str) -> str:
    locale = normalize_lang(lang)
    return STAGE2_BRIDGE_TEXTS.get(locale, STAGE2_BRIDGE_TEXTS[STARFLOW_DEFAULT_LANG]).get(
        key, STAGE2_BRIDGE_TEXTS[STARFLOW_DEFAULT_LANG][key]
    )


def auto_request_info_text(lang: str) -> str:
    locale = normalize_lang(lang)
    mapping = {
        "ru": (
            "📝 Заявка пока на рассмотрении.\n\n"
            "Чтобы ускорить решение, дополни анкету до конца — это занимает около 2 минут.\n"
            "Все данные конфиденциальны."
        ),
        "en": (
            "📝 Your application is still under review.\n\n"
            "To speed up the decision, please complete the full form — it takes about 2 minutes.\n"
            "All data is confidential."
        ),
        "pt": (
            "📝 Sua candidatura ainda está em análise.\n\n"
            "Para acelerar a decisão, complete o formulário até o fim — leva cerca de 2 minutos.\n"
            "Todos os dados são confidenciais."
        ),
        "es": (
            "📝 Tu solicitud sigue en revisión.\n\n"
            "Para acelerar la decisión, completa el formulario hasta el final — tarda unos 2 minutos.\n"
            "Todos los datos son confidenciales."
        ),
    }
    return mapping.get(locale, mapping[STARFLOW_DEFAULT_LANG])

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

DEFAULT_CHANNEL_PUBLIC_LINK = (os.getenv("STARFLOW_CHANNEL_LINK") or "https://t.me/starflowcorp").strip()
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
    admin_scope_ids: list[int] = [int(ADMIN_GROUP_ID)]
    active_admin_chat_id = int(current_admin_chat_id())
    if active_admin_chat_id not in admin_scope_ids:
        admin_scope_ids.append(active_admin_chat_id)
    for chat_id in admin_scope_ids:
        await bot.set_my_commands(
            admin_commands,
            scope=BotCommandScopeChatAdministrators(chat_id=chat_id),
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


async def is_group_member(chat_id: int, user_id: int | None) -> bool:
    if not user_id:
        return False
    try:
        member = await bot.get_chat_member(chat_id, user_id)
    except Exception:
        logger.exception("Не удалось проверить членство в чате")
        return False
    return member.status not in {"left", "kicked"}


def stage2_required_channel_id(lang: str) -> int | None:
    chat_id = CHANNEL_ID_BY_LANG.get(normalize_lang(lang))
    return chat_id if isinstance(chat_id, int) else None


async def can_continue_stage2_gate(user_id: int, lang: str) -> bool:
    chat_id = stage2_required_channel_id(lang)
    if chat_id is None:
        return True
    return await is_group_member(chat_id, user_id)


def is_anonymous_admin_post(message: Message) -> bool:
    sender_chat = getattr(message, "sender_chat", None)
    return bool(sender_chat and sender_chat.id == message.chat.id)


async def can_manage_admin_group(message: Message) -> bool:
    if not message or not message.chat:
        return False
    if message.chat.type not in {"group", "supergroup"}:
        return False
    chat_id = int(message.chat.id)
    if is_anonymous_admin_post(message) and is_admin_chat(chat_id):
        return True
    if not message.from_user:
        return False
    if message.from_user.id == ANONYMOUS_ADMIN_BOT_ID:
        bind_admin_chat_id(chat_id)
        return True
    if message.from_user.id in ADMIN_ALLOWED_USER_IDS:
        bind_admin_chat_id(chat_id)
        return True
    username = (message.from_user.username or "").strip().lower()
    if username in ADMIN_ALLOWED_USERNAMES:
        bind_admin_chat_id(chat_id)
        return True
    if not is_admin_chat(chat_id):
        return False
    if await is_admin_actor(chat_id, message.from_user.id):
        return True
    return await is_group_member(chat_id, message.from_user.id)


async def can_manage_admin_callback(call: CallbackQuery) -> bool:
    if not call.message or not call.from_user:
        return False
    if call.message.chat.type not in {"group", "supergroup"}:
        return False
    chat_id = int(call.message.chat.id)
    if call.from_user.id == ANONYMOUS_ADMIN_BOT_ID:
        bind_admin_chat_id(chat_id)
        return True
    if call.from_user.id in ADMIN_ALLOWED_USER_IDS:
        bind_admin_chat_id(chat_id)
        return True
    username = (call.from_user.username or "").strip().lower()
    if username in ADMIN_ALLOWED_USERNAMES:
        bind_admin_chat_id(chat_id)
        return True
    if is_admin_chat(chat_id):
        if await is_admin_actor(chat_id, call.from_user.id):
            return True
        return await is_group_member(chat_id, call.from_user.id)
    return False


async def sync_anonymous_create_post_state(enabled: bool):
    try:
        admin_chat_id = current_admin_chat_id()
        anon_ctx = dp.fsm.get_context(
            bot=bot,
            chat_id=admin_chat_id,
            user_id=ANONYMOUS_ADMIN_BOT_ID,
        )
        if enabled:
            await anon_ctx.set_state(ApplicationStates.admin_create_post)
        else:
            await anon_ctx.clear()
    except Exception:
        logger.exception("Не удалось синхронизировать состояние create_post для анонимного админа")


async def sync_anonymous_admin_state(
    chat_id: int | None,
    target_state: ApplicationStates | str | None,
    data: dict | None = None,
):
    try:
        target_chat_id = int(chat_id or current_admin_chat_id())
        anon_ctx = dp.fsm.get_context(
            bot=bot,
            chat_id=target_chat_id,
            user_id=ANONYMOUS_ADMIN_BOT_ID,
        )
        if not target_state:
            await anon_ctx.clear()
            return
        await anon_ctx.set_state(target_state)
        if data is not None:
            await anon_ctx.set_data(dict(data))
    except Exception:
        logger.exception("Не удалось синхронизировать состояние админ-флоу для анонимного админа")


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
    pending = counts.get("pending", 0)
    accepted = counts.get("accepted", 0)
    rejected = counts.get("rejected", 0)
    reviewed = accepted + rejected
    total = counts.get("total", pending + reviewed)
    return (
        "🛠 <b>Админ-панель</b>\n\n"
        "Быстрые разделы:\n"
        "• 🆕 Новые\n"
        "• 1️⃣ Управление проектом Streamflow Agency\n"
        "• 2️⃣ Управление проектом Starflow Inc.\n"
        "• 1️⃣ Этап 1\n"
        "• 2️⃣ Этап 2\n"
        "• ✅ Решённые\n"
        "• 📝 Создать пост\n"
        "• 📣 Выложенные посты\n\n"
        f"Ожидают: <b>{pending}</b>\n"
        f"Решённые: <b>{reviewed}</b>\n"
        f"Этап 1: <b>{stage_quick}</b>\n"
        f"Этап 2: <b>{stage_full}</b>\n"
        f"Всего: <b>{total}</b>"
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

SOURCE_SITE_TG = "site_tg"
SOURCE_SITE_WHATSAPP = "site_whatsapp"
SOURCE_TELEGRAM_BOT = "telegram_bot"
SOURCE_WHATSAPP_BOT = "whatsapp_bot"
SOURCE_UNKNOWN = "unknown"
PROJECT_STREAMFLOW = "streamflow_agency"
PROJECT_STARFLOW = "starflow_corp"
PROJECT_LABELS = {
    PROJECT_STREAMFLOW: "Streamflow Agency",
    PROJECT_STARFLOW: "Starflow Inc.",
}


def normalize_project_value(value: str | None) -> str:
    raw = str(value or "").strip().lower()
    if raw in {PROJECT_STARFLOW, "starflow", "starflow_corp"}:
        return PROJECT_STARFLOW
    return PROJECT_STREAMFLOW


BOT_PROJECT_KEY = normalize_project_value(os.getenv("PROJECT_KEY", PROJECT_STREAMFLOW))


def project_label(value: str | None) -> str:
    return PROJECT_LABELS.get(normalize_project_value(value), PROJECT_LABELS[PROJECT_STREAMFLOW])


def normalize_source_value(source: str | None, data: dict | None = None) -> str:
    raw = str(source or "").strip().lower()
    preferred = str((data or {}).get("preferred_contact") or "").strip().lower()
    if raw in {SOURCE_SITE_TG, "site_telegram", "site+telegram", "site+tgbot"}:
        return SOURCE_SITE_TG
    if raw in {SOURCE_SITE_WHATSAPP, "site_wa", "site+whatsapp", "site+wa"}:
        return SOURCE_SITE_WHATSAPP
    if raw in {SOURCE_TELEGRAM_BOT, "tg_bot", "bot"}:
        return SOURCE_TELEGRAM_BOT
    if raw in {SOURCE_WHATSAPP_BOT, "wa_bot", "whatsapp"}:
        return SOURCE_WHATSAPP_BOT
    if raw == "site":
        return SOURCE_SITE_WHATSAPP if preferred == "whatsapp" else SOURCE_SITE_TG
    return SOURCE_UNKNOWN


def source_label_for_user(user_id: int) -> str:
    payload = get_form_data(user_id) or {}
    source = normalize_source_value(get_source(user_id), payload)
    labels = {
        SOURCE_SITE_TG: "Сайт + Telegram бот",
        SOURCE_SITE_WHATSAPP: "Сайт + WhatsApp",
        SOURCE_TELEGRAM_BOT: "Telegram бот",
        SOURCE_WHATSAPP_BOT: "WhatsApp бот",
        SOURCE_UNKNOWN: "Не определён",
    }
    return labels.get(source, labels[SOURCE_UNKNOWN])


def project_key_from_data(data: dict | None) -> str:
    payload = data if isinstance(data, dict) else {}
    return normalize_project_value(str(payload.get("project") or PROJECT_STREAMFLOW))


def project_label_for_user(user_id: int, data: dict | None = None) -> str:
    payload = data if isinstance(data, dict) else get_form_data(user_id) or {}
    return project_label(payload.get("project"))


def _whatsapp_contact_url(data: dict | None) -> str | None:
    payload = data or {}
    candidates = [
        payload.get("whatsapp"),
        payload.get("wa_phone"),
        payload.get("phone"),
    ]
    telegram_value = str(payload.get("telegram") or "").strip()
    if telegram_value.lower().startswith("wa:"):
        candidates.append(telegram_value.split(":", 1)[1])
    for candidate in candidates:
        normalized = normalize_phone(str(candidate or ""))
        if not normalized:
            continue
        digits = "".join(ch for ch in normalized if ch.isdigit())
        if len(digits) >= 8:
            return f"https://wa.me/{digits}"
    return None


def contact_url_for_user(user_id: int, data: dict | None) -> str:
    payload = data or {}
    source = normalize_source_value(get_source(user_id), payload)
    if source in {SOURCE_SITE_WHATSAPP, SOURCE_WHATSAPP_BOT}:
        wa_url = _whatsapp_contact_url(payload)
        if wa_url:
            return wa_url
    raw = str(payload.get("telegram") or "").strip()
    if raw and not raw.lower().startswith("wa:"):
        username = raw.lstrip("@").strip()
        if username:
            return f"https://t.me/{username}"
    if user_id > 0:
        return f"tg://user?id={user_id}"
    wa_url = _whatsapp_contact_url(payload)
    if wa_url:
        return wa_url
    fallback_username = PUBLIC_MANAGER_HANDLE.lstrip("@").strip()
    if fallback_username:
        return f"https://t.me/{fallback_username}"
    return "https://t.me"


def is_site_source(user_id: int) -> bool:
    payload = get_form_data(user_id) or {}
    return normalize_source_value(get_source(user_id), payload) in {SOURCE_SITE_TG, SOURCE_SITE_WHATSAPP}


def lang_for(user_id: int) -> str:
    try:
        return normalize_lang(get_user_language(user_id))
    except Exception:
        logger.exception("Не удалось получить язык пользователя user_id=%s, fallback=%s", user_id, STARFLOW_DEFAULT_LANG)
        return STARFLOW_DEFAULT_LANG


def has_lang_for(user_id: int) -> bool:
    try:
        return has_user_language(user_id)
    except Exception:
        logger.exception("Не удалось проверить язык пользователя user_id=%s", user_id)
        return False


def set_lang_for(user_id: int, language: str) -> None:
    language = normalize_lang(language)
    if language not in LANGUAGE_NAMES:
        language = STARFLOW_DEFAULT_LANG
    try:
        set_user_language(user_id, language)
    except Exception:
        logger.exception(
            "Не удалось сохранить язык пользователя user_id=%s language=%s",
            user_id,
            language,
        )


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


def normalize_user_text_input(value: str | None, max_len: int) -> tuple[str, bool]:
    return normalize_user_text_input_shared(value, max_len)

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
        f"📚 Готов учиться по материалам: {_safe_text(data.get('living', '—'))}\n"
        f"📣 Источники трафика: {_safe_text(data.get('devices', '—'))}\n"
        f"💬 Telegram: {_safe_text(data.get('telegram', '—'))}\n"
        f"📧 Email: {_safe_text(data.get('email', '—'))}\n"
        f"🏷 Проект: {project_label_for_user(user_id, data)}\n"
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
        "📋 <b>Полная заявка партнёра</b>\n\n"
        f"👤 Имя: {_safe_text(data.get('name', '—'))}\n"
        f"📅 Дата рождения: {_safe_text(data.get('age', '—'))}\n"
        f"🌍 Город и страна: {_safe_text(data.get('city', '—'))}\n"
        f"🏳️ Страна подачи: {_safe_text(submission_country(data))}\n"
        f"🧩 Этап анкеты: {_safe_text(application_stage_label(data))}\n"
        f"📞 Телефон: {_safe_text(data.get('phone', '—'))}\n"
        f"📧 Email: {_safe_text(data.get('email', '—'))}\n"
        f"💬 Telegram: {_safe_text(data.get('telegram', '—'))}\n"
        f"📚 Готов учиться по материалам: {_safe_text(data.get('living', '—'))}\n"
        f"📣 Источники трафика: {_safe_text(data.get('devices', '—'))}\n"
        f"⏱ Время работы: {_safe_text(data.get('work_time', '—'))}\n"
        f"💼 Опыт: {_safe_text(data.get('experience', '—'))}\n"
        f"🏷 Проект: {project_label_for_user(user_id, data)}\n"
        f"🆔 ID: {user_id}\n"
        f"🧭 Источник: {source_label_for_user(user_id)}\n\n"
        f"🕒 Время подачи: {submit_time}\n\n"
        f"Статус: <b>{status_label}</b>"
    )


def build_admin_brief_text(data: dict, user_id: int, status: str) -> str:
    status_label = STATUS_LABELS.get(status, status)
    submit_time = submit_time_label_for_user(user_id)
    telegram = _safe_text(data.get("telegram", "—"))
    email = _safe_text(data.get("email", "—"))
    phone = _safe_text(data.get("phone", "—"))
    primary_contact = telegram if telegram != "—" else phone
    return (
        "📌 <b>Краткая карточка</b>\n\n"
        f"👤 Имя: {_safe_text(data.get('name', '—'))}\n"
        f"📅 Дата рождения: {_safe_text(data.get('age', '—'))}\n"
        f"🏳️ Страна подачи: {_safe_text(submission_country(data))}\n"
        f"🧩 Этап анкеты: {_safe_text(application_stage_label(data))}\n"
        f"☎️ Контакт: {primary_contact}\n"
        f"📧 Email: {email}\n"
        f"🏷 Проект: {project_label_for_user(user_id, data)}\n"
        f"🆔 ID: {user_id}\n"
        f"🧭 Источник: {source_label_for_user(user_id)}\n"
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
    admin_chat_id = current_admin_chat_id()
    try:
        await bot.edit_message_text(
            chat_id=admin_chat_id,
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
        f"Сайт + Telegram бот: {source_counts.get(SOURCE_SITE_TG, 0)}\n"
        f"Сайт + WhatsApp: {source_counts.get(SOURCE_SITE_WHATSAPP, 0)}\n"
        f"Telegram бот: {source_counts.get(SOURCE_TELEGRAM_BOT, 0)}\n"
        f"WhatsApp бот: {source_counts.get(SOURCE_WHATSAPP_BOT, 0)}\n"
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
            admin_chat_id = current_admin_chat_id()
            await bot.send_message(admin_chat_id, build_admin_stats_text())
            file_path = Path("applications.xlsx")
            if file_path.exists():
                await bot.send_document(
                    admin_chat_id,
                    FSInputFile(str(file_path))
                )
        except Exception:
            logger.exception("Ошибка отправки ежедневной статистики")

async def archive_admin_messages_once() -> int:
    archived = 0
    rows = get_admin_messages_for_archive(ADMIN_ARCHIVE_DAYS)
    admin_chat_id = current_admin_chat_id()
    for user_id, message_id in rows:
        data = get_form_data(user_id) or {}
        status = get_status(user_id) or "accepted"
        try:
            await bot.edit_message_text(
                chat_id=admin_chat_id,
                message_id=message_id,
                text=build_admin_summary(data, user_id, status, archived=True),
                reply_markup=None
            )
            set_admin_message_id(user_id, None)
            archived += 1
        except Exception:
            try:
                await bot.edit_message_reply_markup(
                    chat_id=admin_chat_id,
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


def _application_time_from_row(app_row: dict | None) -> datetime | None:
    if not isinstance(app_row, dict):
        return None
    raw = (
        app_row.get("updated_at")
        or app_row.get("last_apply_at")
        or app_row.get("created_at")
    )
    dt = _parse_ts(str(raw or ""))
    if not dt:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


async def auto_request_info_task():
    delay = timedelta(minutes=AUTO_REQUEST_INFO_DELAY_MINUTES)
    while True:
        try:
            pending_apps = list_applications("pending")
            now = datetime.now(timezone.utc)
            for app_row in pending_apps:
                try:
                    user_id = int(app_row.get("user_id") or 0)
                except Exception:
                    continue
                if user_id <= 0:
                    continue
                data = get_form_data(user_id) or {}
                if detect_application_stage(data) != APPLICATION_STAGE_QUICK:
                    continue
                if str(data.get(AUTO_REQUEST_INFO_FLAG_KEY) or "").strip():
                    continue
                created_at = _application_time_from_row(app_row)
                if not created_at:
                    app_meta = get_application(user_id) or {}
                    created_at = _application_time_from_row(app_meta)
                if not created_at or now - created_at < delay:
                    continue

                user_lang = submission_lang_for_user(user_id, data)
                app_meta = get_application(user_id) or {}
                source = normalize_source_value(app_meta.get("source"), data)
                channel_url = stage2_channel_link(user_lang) if source in {SOURCE_SITE_TG, SOURCE_SITE_WHATSAPP} else None
                try:
                    await send_or_edit_user_text(
                        user_id,
                        auto_request_info_text(user_lang),
                        reply_markup=main_menu(user_lang, channel_url=channel_url),
                    )
                    data[AUTO_REQUEST_INFO_FLAG_KEY] = datetime.now(timezone.utc).isoformat()
                    set_form_data(user_id, data)
                    logger.info("AUTO_REQUEST_INFO_SENT user_id=%s", user_id)
                except TelegramForbiddenError:
                    data[AUTO_REQUEST_INFO_FLAG_KEY] = datetime.now(timezone.utc).isoformat()
                    set_form_data(user_id, data)
                    logger.warning("AUTO_REQUEST_INFO_FORBIDDEN user_id=%s", user_id)
                except Exception:
                    logger.exception("Ошибка авто-запроса уточнения для user_id=%s", user_id)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Ошибка фоновой задачи auto_request_info_task")
        await asyncio.sleep(AUTO_REQUEST_INFO_CHECK_SECONDS)

async def ensure_admin_menu_posted():
    try:
        admin_chat_id = current_admin_chat_id()
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
                    chat_id=admin_chat_id,
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
                admin_chat_id,
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
        admin_chat_id = current_admin_chat_id()
        stored_id = get_setting(ADMIN_MENU_SETTING_KEY)
        if stored_id and stored_id.isdigit():
            try:
                await bot.edit_message_text(
                    chat_id=admin_chat_id,
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
                admin_chat_id,
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
        admin_chat_id = current_admin_chat_id()
        stored_id = get_setting(ADMIN_NOTIFY_SETTING_KEY)
        if stored_id and stored_id.isdigit():
            try:
                await bot.delete_message(admin_chat_id, int(stored_id))
            except Exception:
                pass
        set_setting(ADMIN_NOTIFY_SETTING_KEY, None)
    except Exception:
        logger.exception("Ошибка очистки уведомления админа")

async def clear_admin_view_message():
    try:
        admin_chat_id = current_admin_chat_id()
        stored_id = get_setting(ADMIN_VIEW_SETTING_KEY)
        if stored_id and stored_id.isdigit():
            try:
                await bot.delete_message(admin_chat_id, int(stored_id))
            except Exception:
                pass
        set_setting(ADMIN_VIEW_SETTING_KEY, None)
    except Exception:
        logger.exception("Ошибка очистки карточки просмотра")


def _is_http_url(value: str | None) -> bool:
    raw = (value or "").strip().lower()
    return raw.startswith("http://") or raw.startswith("https://")


def _photo_caption_fallback(text: str) -> str:
    plain = re.sub(r"<[^>]+>", "", text or "")
    plain = html.unescape(plain).strip()
    if not plain:
        plain = "Анкета кандидата"
    if len(plain) > 1024:
        plain = plain[:1021] + "..."
    return plain


async def _resolve_remote_photo_file_id(url: str) -> str | None:
    raw_url = (url or "").strip()
    if not _is_http_url(raw_url):
        return None
    admin_chat_id = current_admin_chat_id()
    try:
        msg = await bot.send_photo(admin_chat_id, raw_url)
        file_id = msg.photo[-1].file_id if getattr(msg, "photo", None) else None
        try:
            await bot.delete_message(admin_chat_id, msg.message_id)
        except Exception:
            pass
        if file_id:
            return str(file_id)
    except Exception:
        pass

    headers = {"Accept": "*/*"}
    infobip_key = (os.getenv("INFOBIP_API_KEY", "") or "").strip()
    if infobip_key and "infobip" in raw_url.lower():
        headers["Authorization"] = f"App {infobip_key}"
    try:
        req = urllib.request.Request(raw_url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = resp.read()
            if not payload:
                return None
            content_type = (resp.headers.get("Content-Type", "") or "").split(";", 1)[0].strip().lower()
            filename = "candidate_photo.jpg"
            if content_type == "image/png":
                filename = "candidate_photo.png"
            elif content_type == "image/webp":
                filename = "candidate_photo.webp"
        msg = await bot.send_photo(admin_chat_id, BufferedInputFile(payload, filename))
        file_id = msg.photo[-1].file_id if getattr(msg, "photo", None) else None
        try:
            await bot.delete_message(admin_chat_id, msg.message_id)
        except Exception:
            pass
        if file_id:
            return str(file_id)
    except Exception:
        return None
    return None


async def _ensure_admin_photo_ref(user_id: int, data: dict, field_key: str) -> str | None:
    raw_ref = str(data.get(field_key) or "").strip()
    if not raw_ref:
        return None
    if not _is_http_url(raw_ref):
        return raw_ref
    resolved = await _resolve_remote_photo_file_id(raw_ref)
    if not resolved:
        logger.warning("Failed to resolve remote photo for user_id=%s field=%s", user_id, field_key)
        return None
    data[field_key] = resolved
    try:
        set_form_data(user_id, data)
    except Exception:
        logger.exception("Не удалось сохранить Telegram file_id фото для user_id=%s", user_id)
    return resolved


async def _preferred_admin_photo(user_id: int, data: dict) -> str | None:
    face = await _ensure_admin_photo_ref(user_id, data, "photo_face")
    if face:
        return face
    return await _ensure_admin_photo_ref(user_id, data, "photo_full")


async def update_admin_view_message(
    text: str,
    reply_markup: InlineKeyboardMarkup,
    photo_id: str | None
):
    admin_chat_id = current_admin_chat_id()
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
                    chat_id=admin_chat_id,
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
                    await bot.edit_message_media(
                        chat_id=admin_chat_id,
                        message_id=msg_id,
                        media=InputMediaPhoto(
                            media=photo_id,
                            caption=_photo_caption_fallback(text),
                        ),
                        reply_markup=reply_markup
                    )
                    return
                except Exception:
                    try:
                        await bot.edit_message_caption(
                            chat_id=admin_chat_id,
                            message_id=msg_id,
                            caption=_photo_caption_fallback(text),
                            reply_markup=reply_markup,
                        )
                        return
                    except Exception:
                        try:
                            await bot.edit_message_text(
                                chat_id=admin_chat_id,
                                message_id=msg_id,
                                text=text,
                                reply_markup=reply_markup,
                            )
                            return
                        except Exception:
                            pass
                    try:
                        await bot.delete_message(admin_chat_id, msg_id)
                    except Exception:
                        pass
                    set_setting(ADMIN_VIEW_SETTING_KEY, None)
        else:
            try:
                await bot.edit_message_text(
                    chat_id=admin_chat_id,
                    message_id=msg_id,
                    text=text,
                    reply_markup=reply_markup
                )
                return
            except Exception:
                try:
                    await bot.delete_message(admin_chat_id, msg_id)
                except Exception:
                    pass
                set_setting(ADMIN_VIEW_SETTING_KEY, None)

    try:
        if photo_id:
            try:
                msg = await bot.send_photo(
                    admin_chat_id,
                    photo_id,
                    caption=text,
                    reply_markup=reply_markup
                )
            except Exception:
                try:
                    msg = await bot.send_photo(
                        admin_chat_id,
                        photo_id,
                        caption=_photo_caption_fallback(text),
                        reply_markup=reply_markup
                    )
                except Exception:
                    msg = await bot.send_message(
                        admin_chat_id,
                        text,
                        reply_markup=reply_markup
                    )
        else:
            msg = await bot.send_message(
                admin_chat_id,
                text,
                reply_markup=reply_markup
            )
        set_setting(ADMIN_VIEW_SETTING_KEY, str(msg.message_id))
    except Exception:
        logger.exception("Ошибка отправки сообщения просмотра анкеты")

async def update_admin_photos(user_id: int):
    admin_chat_id = current_admin_chat_id()
    stored_ids = _parse_admin_photo_ids(get_setting(ADMIN_PHOTOS_SETTING_KEY))
    for msg_id in stored_ids:
        try:
            await bot.delete_message(admin_chat_id, msg_id)
        except Exception:
            pass
    data = get_form_data(user_id) or {}
    face = await _ensure_admin_photo_ref(user_id, data, "photo_face")
    full = await _ensure_admin_photo_ref(user_id, data, "photo_full")
    if not face or not full:
        set_setting(ADMIN_PHOTOS_SETTING_KEY, None)
        return
    try:
        messages = await bot.send_media_group(
            admin_chat_id,
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
    admin_chat_id = current_admin_chat_id()
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
            await bot.delete_message(admin_chat_id, int(stored_id))
        except Exception:
            logger.exception("Не удалось удалить старое уведомление")
    try:
        msg = await bot.send_message(admin_chat_id, text)
        set_setting(ADMIN_NOTIFY_SETTING_KEY, str(msg.message_id))
    except Exception:
        logger.exception("Ошибка уведомления о заявке")

async def set_admin_menu_message_id(message_id: int):
    admin_chat_id = current_admin_chat_id()
    stored_id = get_setting(ADMIN_MENU_SETTING_KEY)
    if stored_id and stored_id.isdigit() and int(stored_id) != message_id:
        try:
            await bot.delete_message(admin_chat_id, int(stored_id))
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
        "reviewed": "Решённые",
        "accepted": "Принятые",
        "rejected": "Отклонённые",
        "all": "Все заявки",
        "stage_quick": "Прошли только первый этап",
        "stage_full": "Полностью заполненные заявки",
        "src_site": "Источник: сайт",
        "src_bot": "Источник: боты",
        "src_unknown": "Источник: не определён",
        "project_streamflow": "Проект: Streamflow Agency",
        "project_starflow": "Проект: Starflow Inc.",
        None: "Все заявки",
    }.get(filter_key, "Все заявки")

def _list_apps_by_filter(filter_key: str) -> list[dict]:
    status = None if filter_key in {
        "all",
        "reviewed",
        "stage_quick",
        "stage_full",
        "src_site",
        "src_bot",
        "src_unknown",
        "project_streamflow",
        "project_starflow",
    } else filter_key
    if filter_key == "stage_quick":
        return list_applications_by_stage("quick", status=None)
    if filter_key == "stage_full":
        return list_applications_by_stage("full", status=None)
    apps = list_applications(status)
    if filter_key == "reviewed":
        return [a for a in apps if a.get("status") in {"accepted", "rejected"}]
    if filter_key in {"src_site", "src_bot", "src_unknown"}:
        expected = {"src_site": "site", "src_bot": "bot", "src_unknown": "unknown"}[filter_key]
        filtered: list[dict] = []
        for app in apps:
            uid = int(app.get("user_id") or 0)
            payload = get_form_data(uid) or {}
            source = normalize_source_value(get_source(uid), payload)
            if source in {SOURCE_SITE_TG, SOURCE_SITE_WHATSAPP}:
                source_key = "site"
            elif source in {SOURCE_TELEGRAM_BOT, SOURCE_WHATSAPP_BOT}:
                source_key = "bot"
            else:
                source_key = "unknown"
            if source_key == expected:
                filtered.append(app)
        return filtered
    if filter_key in {"project_streamflow", "project_starflow"}:
        expected_project = PROJECT_STREAMFLOW if filter_key == "project_streamflow" else PROJECT_STARFLOW
        filtered: list[dict] = []
        for app in apps:
            uid = int(app.get("user_id") or 0)
            payload = get_form_data(uid) or {}
            if project_key_from_data(payload) == expected_project:
                filtered.append(app)
        return filtered
    return apps


def _apps_total_for_filter(filter_key: str) -> int:
    try:
        return len(_list_apps_by_filter(filter_key))
    except Exception:
        logger.exception("Ошибка подсчёта заявок для фильтра %s", filter_key)
        return 0


def _build_admin_list_header(
    label: str,
    offset: int,
    total: int,
) -> str:
    page = offset // ADMIN_LIST_LIMIT + 1
    pages = (total + ADMIN_LIST_LIMIT - 1) // ADMIN_LIST_LIMIT
    return (
        f"🗂 <b>{label}</b>\n\n"
        f"Заявка <b>{offset + 1}</b> из <b>{total}</b>\n"
        f"Страница: <b>{page}/{pages}</b>\n\n"
    )


async def _render_admin_list_message(
    filter_key: str,
    offset: int,
    user_id: int,
    item_status: str,
    total: int,
    show_full: bool | None = None,
):
    data = get_form_data(user_id) or {}
    is_full_stage = detect_application_stage(data) == APPLICATION_STAGE_FULL
    effective_show_full = True
    allow_request_info = not is_full_stage
    contact_url = contact_url_for_user(user_id, data)
    label = _admin_list_label(filter_key)
    header = _build_admin_list_header(label, offset, total)
    body = build_admin_full_text(data, user_id, item_status)
    photo_id = await _preferred_admin_photo(user_id, data)
    await update_admin_view_message(
        f"{header}{body}",
        admin_list_view_keyboard(
            user_id,
            item_status,
            filter_key,
            offset,
            total,
            ADMIN_LIST_LIMIT,
            contact_url=contact_url,
            show_full=effective_show_full,
            allow_request_info=allow_request_info,
        ),
        photo_id,
    )


async def send_admin_list(
    call: CallbackQuery,
    filter_key: str,
    offset: int = 0,
    preferred_user_id: int | None = None,
    show_full: bool | None = None,
):
    await safe_call_answer(call)
    try:
        apps = _list_apps_by_filter(filter_key)
        label = _admin_list_label(filter_key)
        if not apps:
            await clear_admin_view_message()
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
        if preferred_user_id is not None:
            for idx, app in enumerate(apps):
                if int(app.get("user_id") or 0) == int(preferred_user_id):
                    offset = idx
                    break
        slice_items = apps[offset: offset + ADMIN_LIST_LIMIT]
        current = slice_items[0]
        user_id = current["user_id"]
        item_status = (current.get("status") or "pending").strip().lower()
        if item_status not in {"pending", "accepted", "rejected"}:
            item_status = "pending"
        await _render_admin_list_message(
            filter_key=filter_key,
            offset=offset,
            user_id=user_id,
            item_status=item_status,
            total=total,
            show_full=show_full,
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
        admin_chat_id = current_admin_chat_id()
        copied = await bot.copy_message(
            chat_id=admin_chat_id,
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
    if has_lang_for(user_id) and not force_prompt:
        return True
    current_lang = lang_for(user_id) if has_lang_for(user_id) else STARFLOW_DEFAULT_LANG
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

async def send_or_edit_user_preview(
    user_id: int,
    media: str | FSInputFile,
    caption: str,
    reply_markup=None,
) -> bool:
    message_id = get_flow_message_id(user_id)
    safe_caption = fit_caption(caption)
    if message_id:
        try:
            await bot.edit_message_media(
                chat_id=user_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=media,
                    caption=safe_caption,
                    parse_mode=ParseMode.HTML,
                ),
                reply_markup=reply_markup,
            )
            return True
        except TelegramBadRequest as e:
            err = str(e).lower()
            if "message is not modified" in err:
                try:
                    await bot.edit_message_reply_markup(
                        chat_id=user_id,
                        message_id=message_id,
                        reply_markup=reply_markup,
                    )
                except Exception:
                    pass
                return True
            logger.warning("edit_message_media failed for user %s: %s", user_id, e)
        except TelegramForbiddenError:
            logger.warning("Нет прав на обновление preview сообщения пользователя")
            return False
        except Exception:
            logger.exception("Не удалось обновить preview сообщения пользователя")

    if message_id:
        try:
            await bot.delete_message(user_id, message_id)
        except Exception:
            pass

    try:
        msg = await bot.send_photo(
            user_id,
            photo=media,
            caption=safe_caption,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )
        set_flow_message_id(user_id, msg.message_id)
        return True
    except TelegramForbiddenError:
        logger.warning("Нет прав на отправку preview сообщения пользователю")
        return False
    except Exception:
        logger.exception("Ошибка отправки preview сообщения пользователю")
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

async def clear_user_menu_message(user_id: int):
    message_id = get_menu_message_id(user_id)
    if not message_id:
        return
    try:
        await bot.delete_message(user_id, message_id)
    except Exception:
        pass
    set_menu_message_id(user_id, None)

async def clear_portfolio_media(user_id: int):
    auto_task = PORTFOLIO_AUTONEXT_TASKS.pop(user_id, None)
    if auto_task and not auto_task.done() and auto_task is not asyncio.current_task():
        auto_task.cancel()
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
    admin_chat_id = current_admin_chat_id()
    ids = ADMIN_TEMP_MESSAGE_IDS.copy()
    ADMIN_TEMP_MESSAGE_IDS.clear()
    for message_id in ids:
        try:
            await bot.delete_message(admin_chat_id, message_id)
        except Exception:
            pass


async def delete_message_silent(message: Message | None):
    if not message:
        return
    try:
        await message.delete()
    except Exception:
        pass


def cancel_portfolio_autonext(user_id: int):
    task = PORTFOLIO_AUTONEXT_TASKS.pop(user_id, None)
    if task and not task.done() and task is not asyncio.current_task():
        task.cancel()


def portfolio_slide_dots(index: int, total: int) -> str:
    if total <= 1:
        return ""
    return " ".join("●" if i == index else "○" for i in range(total))


def _portfolio_player_text(lang: str, key: str) -> str:
    locale = normalize_lang(lang)
    values = {
        "ru": {
            "hint": "Листай карточки кнопками ниже ⬇️",
            "prev": "⬅️ Назад",
            "next": "Вперёд ➡️",
            "photos": "🖼 Фото",
            "videos": "🎬 Видео",
            "empty": "⚠️ Портфолио пока недоступно.",
        },
        "en": {
            "hint": "Use the buttons below to browse ⬇️",
            "prev": "⬅️ Back",
            "next": "Next ➡️",
            "photos": "🖼 Photos",
            "videos": "🎬 Videos",
            "empty": "⚠️ Portfolio is not available right now.",
        },
        "pt": {
            "hint": "Use os botões abaixo para navegar ⬇️",
            "prev": "⬅️ Voltar",
            "next": "Avançar ➡️",
            "photos": "🖼 Fotos",
            "videos": "🎬 Vídeos",
            "empty": "⚠️ Portfólio indisponível no momento.",
        },
        "es": {
            "hint": "Usa los botones de abajo para navegar ⬇️",
            "prev": "⬅️ Atrás",
            "next": "Siguiente ➡️",
            "photos": "🖼 Fotos",
            "videos": "🎬 Videos",
            "empty": "⚠️ El portafolio no está disponible ahora.",
        },
    }
    return values.get(locale, values[STARFLOW_DEFAULT_LANG]).get(key, values[STARFLOW_DEFAULT_LANG][key])


def load_portfolio_player_items() -> list[dict]:
    base_dir = Path(__file__).resolve().parent
    items: list[dict] = []
    for spec in PORTFOLIO_PLAYER_SPECS:
        file_path = base_dir / str(spec.get("file") or "")
        if not file_path.exists():
            continue
        raw_autonext = spec.get("autonext_seconds")
        try:
            autonext_seconds = max(0, int(raw_autonext or 0))
        except Exception:
            autonext_seconds = 0
        items.append(
            {
                "kind": str(spec.get("kind") or "photo"),
                "path": file_path,
                "title": dict(spec.get("title") or {}),
                "autonext_seconds": autonext_seconds,
            }
        )
    return items


def portfolio_start_index(items: list[dict], kind: str | None = None) -> int:
    if not items:
        return 0
    normalized = (kind or "").strip().lower()
    if normalized not in {"photo", "video"}:
        return 0
    for idx, item in enumerate(items):
        if str(item.get("kind") or "").strip().lower() == normalized:
            return idx
    return 0


def portfolio_player_caption(lang: str, item: dict, index: int, total: int) -> str:
    locale = normalize_lang(lang)
    titles = item.get("title") or {}
    title = str(titles.get(locale) or titles.get(STARFLOW_DEFAULT_LANG) or "Portfolio")
    dots = portfolio_slide_dots(index, total)
    dots_line = f"\n{dots}" if dots else ""
    return f"📁 <b>{html.escape(title)}</b>\n{index + 1}/{total}{dots_line}\n\n{_portfolio_player_text(locale, 'hint')}"


def _next_portfolio_index(index: int, total: int) -> int | None:
    candidate = index + 1
    if candidate >= total:
        return None
    return candidate


async def _portfolio_video_autonext_worker(user_id: int, next_index: int, delay_seconds: int):
    try:
        await asyncio.sleep(delay_seconds)
        ids = PORTFOLIO_MEDIA_IDS.get(user_id) or []
        if not ids:
            return
        await show_portfolio_player(
            user_id,
            lang_for(user_id),
            next_index,
            source_message_id=int(ids[0]),
            skip_autonext_cancel=True,
        )
    except asyncio.CancelledError:
        pass
    except Exception:
        logger.exception("Ошибка автоперехода портфолио")
    finally:
        current = PORTFOLIO_AUTONEXT_TASKS.get(user_id)
        if current is asyncio.current_task():
            PORTFOLIO_AUTONEXT_TASKS.pop(user_id, None)


def schedule_portfolio_autonext(user_id: int, next_index: int | None, delay_seconds: int):
    cancel_portfolio_autonext(user_id)
    if next_index is None or delay_seconds <= 0:
        return
    PORTFOLIO_AUTONEXT_TASKS[user_id] = asyncio.create_task(
        _portfolio_video_autonext_worker(user_id, next_index, delay_seconds)
    )


def portfolio_player_keyboard(lang: str, index: int, total: int, has_photos: bool, has_videos: bool):
    locale = normalize_lang(lang)
    rows: list[list[InlineKeyboardButton]] = []
    if total > 1:
        rows.append(
            [
                InlineKeyboardButton(
                    text=_portfolio_player_text(locale, "prev"),
                    callback_data=f"portfolio_nav:{max(index - 1, 0)}",
                ),
                InlineKeyboardButton(
                    text=_portfolio_player_text(locale, "next"),
                    callback_data=f"portfolio_nav:{min(index + 1, total - 1)}",
                ),
            ]
        )
    jump_row: list[InlineKeyboardButton] = []
    if has_photos:
        jump_row.append(InlineKeyboardButton(text=_portfolio_player_text(locale, "photos"), callback_data="portfolio_jump:photo"))
    if has_videos:
        jump_row.append(InlineKeyboardButton(text=_portfolio_player_text(locale, "videos"), callback_data="portfolio_jump:video"))
    if jump_row:
        rows.append(jump_row)
    rows.append([InlineKeyboardButton(text=t(locale, "btn_back"), callback_data="portfolio")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def show_portfolio_player(
    user_id: int,
    lang: str,
    index: int,
    source_message: Message | None = None,
    source_message_id: int | None = None,
    skip_autonext_cancel: bool = False,
):
    if not skip_autonext_cancel:
        cancel_portfolio_autonext(user_id)
    items = load_portfolio_player_items()
    if not items:
        await send_or_edit_user_text(
            user_id,
            _portfolio_player_text(lang, "empty"),
            reply_markup=portfolio_menu(lang),
        )
        return
    if index < 0:
        index = 0
    if index >= len(items):
        index = len(items) - 1
    item = items[index]
    total = len(items)
    has_photos = any(str(x.get("kind") or "").lower() == "photo" for x in items)
    has_videos = any(str(x.get("kind") or "").lower() == "video" for x in items)
    caption = portfolio_player_caption(lang, item, index, total)
    reply_markup = portfolio_player_keyboard(lang, index, total, has_photos, has_videos)

    kind = str(item.get("kind") or "").strip().lower()
    media_path = str(item.get("path"))
    media_obj = (
        InputMediaVideo(media=FSInputFile(media_path), caption=caption)
        if kind == "video"
        else InputMediaPhoto(media=FSInputFile(media_path), caption=caption)
    )
    next_index = _next_portfolio_index(index, total)
    auto_delay = int(item.get("autonext_seconds") or 0)

    target_message_id = source_message.message_id if source_message else source_message_id
    if target_message_id:
        try:
            await bot.edit_message_media(
                chat_id=user_id,
                message_id=target_message_id,
                media=media_obj,
                reply_markup=reply_markup,
            )
            PORTFOLIO_MEDIA_IDS[user_id] = [target_message_id]
            schedule_portfolio_cleanup(user_id)
            if kind == "video":
                schedule_portfolio_autonext(user_id, next_index, auto_delay)
            return
        except TelegramBadRequest as exc:
            if _is_not_modified_error(exc):
                try:
                    await bot.edit_message_reply_markup(
                        chat_id=user_id,
                        message_id=target_message_id,
                        reply_markup=reply_markup,
                    )
                    PORTFOLIO_MEDIA_IDS[user_id] = [target_message_id]
                    schedule_portfolio_cleanup(user_id)
                    if kind == "video":
                        schedule_portfolio_autonext(user_id, next_index, auto_delay)
                    return
                except Exception:
                    pass
        except Exception:
            pass

    await clear_portfolio_media(user_id)
    if kind == "video":
        sent = await bot.send_video(
            chat_id=user_id,
            video=FSInputFile(media_path),
            caption=caption,
            reply_markup=reply_markup,
        )
    else:
        sent = await bot.send_photo(
            chat_id=user_id,
            photo=FSInputFile(media_path),
            caption=caption,
            reply_markup=reply_markup,
        )
    PORTFOLIO_MEDIA_IDS[user_id] = [sent.message_id]
    schedule_portfolio_cleanup(user_id)
    if kind == "video":
        schedule_portfolio_autonext(user_id, next_index, auto_delay)

async def start_application(message: Message, state: FSMContext, user_id: int | None = None):
    target_user_id = user_id or message.chat.id
    await state.clear()
    clear_form_data(target_user_id)
    await state.set_state(ApplicationStates.name)
    await gentle_typing(message.chat.id)
    lang = lang_for(target_user_id)
    await state.update_data(project=BOT_PROJECT_KEY, lang=lang)
    set_form_data(target_user_id, {"project": BOT_PROJECT_KEY, "lang": lang})
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
    set_source(target_user_id, SOURCE_TELEGRAM_BOT)
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
            set_lang_for(message.from_user.id, lang)
        sent = await send_or_edit_user_text(
            message.from_user.id,
            stage2_text(lang, "expired"),
            reply_markup=main_menu(lang),
        )
        if not sent:
            try:
                await message.answer(stage2_text(lang, "expired"))
            except Exception:
                logger.exception("Не удалось отправить fallback-сообщение об истечении site-токена")
        return True

    lang = normalize_lang(str(lead.get("lang") or start_lang or STARFLOW_DEFAULT_LANG))
    set_lang_for(message.from_user.id, lang)
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
        "email": str(lead.get("email") or "").strip(),
        "telegram": str(lead.get("telegram") or "").strip(),
        "whatsapp": str(lead.get("whatsapp") or "").strip(),
        "country": str(lead.get("country") or "").strip() or None,
        "lang": lang,
        "project": normalize_project_value(str(lead.get("project") or BOT_PROJECT_KEY)),
        "application_stage": APPLICATION_STAGE_QUICK,
        "site_lead_token": token,
    }
    if not payload.get("telegram") and payload.get("whatsapp"):
        digits = "".join(ch for ch in str(payload.get("whatsapp") or "") if ch.isdigit())
        if digits:
            payload["telegram"] = f"wa:{digits}"
    payload = {k: v for k, v in payload.items() if v not in {None, ""}}
    await state.update_data(**payload)
    set_form_data(message.from_user.id, payload)
    set_status(message.from_user.id, "new")
    preferred_contact = str(lead.get("preferred_contact") or "").strip().lower()
    set_source(message.from_user.id, SOURCE_SITE_WHATSAPP if preferred_contact == "whatsapp" else SOURCE_SITE_TG)
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
            await message.answer(t(STARFLOW_DEFAULT_LANG, "start_private_only"))
            return
        await delete_user_message(message)
        logger.info(
            "START_CMD user_id=%s text=%r",
            message.from_user.id if message.from_user else None,
            (message.text or "")[:200],
        )
        await state.clear()
        await clear_portfolio_media(message.from_user.id)
        await clear_user_flow_message(message.from_user.id)
        start_payload = extract_start_payload(message.text)
        site_token, start_lang = extract_site_lead_start_data(start_payload)
        if start_lang:
            set_lang_for(message.from_user.id, start_lang)
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
        menu_ok = await send_menu(
            message,
            caption=t(lang, "menu_caption"),
            status=status,
            channel_url=stage2_channel_link(lang) if site_stage2 else None,
        )
        if not menu_ok:
            logger.warning("START_CMD menu send failed, using fallback text menu user_id=%s", message.from_user.id)
            fallback_sent = await send_or_edit_user_text(
                message.from_user.id,
                t(lang, "menu_caption"),
                reply_markup=main_menu(
                    lang,
                    channel_url=stage2_channel_link(lang) if site_stage2 else None,
                ),
            )
            if not fallback_sent:
                await message.answer(t(lang, "menu_caption"))
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
            started_site_quick = app.get("status") in {None, "new"} and is_site_quick_application(app, data)
            resume_text = (
                stage2_text(lang, "gate")
                if pending_site_quick
                else (
                    t(lang, "already_started_site_prompt")
                    if started_site_quick
                    else (
                        stage2_text(lang, "step2")
                        if app.get("status") == "pending" and is_quick_application(data)
                        else t(lang, "resume_prompt")
                    )
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
            await message.answer(t(STARFLOW_DEFAULT_LANG, "temp_error_retry"))
        except Exception:
            pass


@dp.message(F.text.regexp(r"(?i)^\s*(?:start|старт)\s*$"))
async def start_text_alias(message: Message, state: FSMContext):
    if message.chat.type != "private":
        return
    await start(message, state)


@dp.callback_query(F.data == "main_menu")
async def main_menu_handler(call: CallbackQuery, state: FSMContext):
    if not call.message or call.message.chat.type != "private":
        await safe_call_answer(call, t(STARFLOW_DEFAULT_LANG, "open_private_prompt"), show_alert=True)
        return
    await safe_call_answer(call)
    await state.clear()
    await clear_portfolio_media(call.from_user.id)
    app = get_application(call.from_user.id)
    data = get_form_data(call.from_user.id) or {}
    status = app.get("status") if app else None
    lang = lang_for(call.from_user.id)
    site_stage2 = is_site_quick_application(app, data)
    menu_ok = await send_menu(
        call.message,
        caption=t(lang, "menu_caption"),
        status=status,
        channel_url=stage2_channel_link(lang) if site_stage2 else None,
    )
    if not menu_ok:
        logger.warning("MAIN_MENU menu send failed, using fallback text menu user_id=%s", call.from_user.id)
        await send_or_edit_user_text(
            call.from_user.id,
            t(lang, "menu_caption"),
            reply_markup=main_menu(
                lang,
                channel_url=stage2_channel_link(lang) if site_stage2 else None,
            ),
        )
    await clear_user_flow_message(call.from_user.id)


@dp.message(F.text == "/language")
async def language_command(message: Message):
    if message.chat.type != "private":
        await message.answer(t(STARFLOW_DEFAULT_LANG, "start_private_only"))
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
        await safe_call_answer(call, t(STARFLOW_DEFAULT_LANG, "open_private_prompt"), show_alert=True)
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
            await safe_call_answer(call, t(STARFLOW_DEFAULT_LANG, "open_private_prompt"), show_alert=True)
            return
        await safe_call_answer(call)
        lang_code = call.data.split(":", 1)[1].strip().lower()
        if lang_code not in LANGUAGE_NAMES:
            lang_code = STARFLOW_DEFAULT_LANG
        set_lang_for(call.from_user.id, lang_code)
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
        await safe_call_answer(call, t(STARFLOW_DEFAULT_LANG, "temp_error_retry"), show_alert=True)
        
# ================= APPLY =================

@dp.callback_query(F.data == "apply")
async def apply(call: CallbackQuery, state: FSMContext):
    try:
        if not call.message or call.message.chat.type != "private":
            await safe_call_answer(call, t(STARFLOW_DEFAULT_LANG, "open_private_prompt"), show_alert=True)
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
            resume_prompt = (
                t(lang, "already_started_site_prompt")
                if is_site_quick_application(app, form_data)
                else t(lang, "already_started_prompt")
            )
            await send_or_edit_user_text(
                call.from_user.id,
                resume_prompt,
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
            await safe_call_answer(call, t(STARFLOW_DEFAULT_LANG, "open_private_prompt"), show_alert=True)
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
            await safe_call_answer(call, t(STARFLOW_DEFAULT_LANG, "open_private_prompt"), show_alert=True)
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
            await safe_call_answer(call, t(STARFLOW_DEFAULT_LANG, "open_private_prompt"), show_alert=True)
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
            await safe_call_answer(call, t(STARFLOW_DEFAULT_LANG, "open_private_prompt"), show_alert=True)
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
            await safe_call_answer(call, t(STARFLOW_DEFAULT_LANG, "open_private_prompt"), show_alert=True)
            return
        lang = lang_for(call.from_user.id)
        if not await can_continue_stage2_gate(call.from_user.id, lang):
            await safe_call_answer(call, stage2_text(lang, "wait_gate"), show_alert=True)
            await send_or_edit_user_text(
                call.from_user.id,
                stage2_text(lang, "gate"),
                reply_markup=stage2_gate_keyboard(lang),
            )
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
            await safe_call_answer(call, t(STARFLOW_DEFAULT_LANG, "open_private_prompt"), show_alert=True)
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
    name, too_long = normalize_user_text_input(m.text, FORM_NAME_MAX_LEN)
    await delete_user_message(m)
    if too_long:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_too_long", max=FORM_NAME_MAX_LEN),
            reply_markup=form_keyboard(lang),
        )
        return
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
    city, too_long = normalize_user_text_input(m.text, FORM_CITY_MAX_LEN)
    await delete_user_message(m)
    if too_long:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_too_long", max=FORM_CITY_MAX_LEN),
            reply_markup=form_keyboard(lang),
        )
        return
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
    phone, too_long = normalize_user_text_input(m.text, FORM_PHONE_MAX_LEN)
    await delete_user_message(m)
    if too_long:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_too_long", max=FORM_PHONE_MAX_LEN),
            reply_markup=form_keyboard(lang),
        )
        return
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
    birthdate, too_long = normalize_user_text_input(m.text, FORM_AGE_MAX_LEN)
    await delete_user_message(m)
    if too_long:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_too_long", max=FORM_AGE_MAX_LEN),
            reply_markup=form_keyboard(lang),
        )
        return
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
        ApplicationStates.headphones,
        note=note
    )

@dp.message(StateFilter(ApplicationStates.living), F.text)
async def step_living(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    living_raw, too_long = normalize_user_text_input(m.text, FORM_YES_NO_MAX_LEN)
    await delete_user_message(m)
    if too_long:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_too_long", max=FORM_YES_NO_MAX_LEN),
            reply_markup=form_keyboard(lang),
        )
        return
    normalized = normalize_yes_no(living_raw, lang=lang)
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
        note=note,
    )

@dp.message(StateFilter(ApplicationStates.devices), F.text)
async def step_devices(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    devices, too_long = normalize_user_text_input(m.text, FORM_DEVICES_MAX_LEN)
    await delete_user_message(m)
    if too_long:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_too_long", max=FORM_DEVICES_MAX_LEN),
            reply_markup=form_keyboard(lang),
        )
        return
    if len(devices) < 2:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_devices_short"),
            reply_markup=form_keyboard(lang)
        )
        return
    await update_form_field(state, m.from_user.id, devices=devices)
    await send_or_edit_user_text(m.from_user.id, build_ack(m.from_user.id))
    await show_preview(m, state)

@dp.message(StateFilter(ApplicationStates.device_model), F.text)
async def step_device_model(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    value, too_long = normalize_user_text_input(m.text, FORM_DEVICE_MODEL_MAX_LEN)
    await delete_user_message(m)
    if too_long:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_too_long", max=FORM_DEVICE_MODEL_MAX_LEN),
            reply_markup=form_keyboard(lang),
        )
        return
    # Legacy compatibility: old users may return to deprecated state.
    if len(value) >= 2:
        await update_form_field(state, m.from_user.id, devices=value)
    await send_next_question(
        m,
        state,
        ApplicationStates.headphones
    )

@dp.message(StateFilter(ApplicationStates.work_time), F.text)
async def step_work_time(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    work_time, too_long = normalize_user_text_input(m.text, FORM_WORK_TIME_MAX_LEN)
    await delete_user_message(m)
    if too_long:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_too_long", max=FORM_WORK_TIME_MAX_LEN),
            reply_markup=form_keyboard(lang),
        )
        return
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
    email, too_long = normalize_user_text_input(m.text, FORM_EMAIL_MAX_LEN)
    await delete_user_message(m)
    if too_long:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_too_long", max=FORM_EMAIL_MAX_LEN),
            reply_markup=form_keyboard(lang),
        )
        return
    if not is_valid_email(email):
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_email_invalid"),
            reply_markup=form_keyboard(lang)
        )
        return
    await update_form_field(state, m.from_user.id, email=email.strip().lower())
    await send_next_question(
        m,
        state,
        ApplicationStates.telegram
    )

@dp.message(StateFilter(ApplicationStates.telegram), F.text)
async def step_tg(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    raw, too_long = normalize_user_text_input(m.text, FORM_TELEGRAM_MAX_LEN)
    await delete_user_message(m)
    if too_long:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_too_long", max=FORM_TELEGRAM_MAX_LEN),
            reply_markup=form_keyboard(lang),
        )
        return
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
    experience, too_long = normalize_user_text_input(m.text, FORM_EXPERIENCE_MAX_LEN)
    await delete_user_message(m)
    if too_long:
        await send_or_edit_user_text(
            m.from_user.id,
            t(lang, "field_too_long", max=FORM_EXPERIENCE_MAX_LEN),
            reply_markup=form_keyboard(lang),
        )
        return
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
    lang = lang_for(m.from_user.id)
    await delete_user_message(m)
    await send_or_edit_user_text(
        m.from_user.id,
        t(lang, "photo_step_removed"),
        reply_markup=form_keyboard(lang)
    )
    await send_next_question(
        m,
        state,
        ApplicationStates.devices
    )

@dp.message(StateFilter(ApplicationStates.photo_full), F.photo)
async def step_full(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    await delete_user_message(m)
    await send_or_edit_user_text(m.from_user.id, t(lang, "photo_step_removed"))
    await show_preview(m, state)

@dp.message(StateFilter(ApplicationStates.photo_face), ~F.photo)
async def reject_non_photo_face(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    await delete_user_message(m)
    await send_next_question(m, state, ApplicationStates.devices, note=t(lang, "photo_step_removed"))

@dp.message(StateFilter(ApplicationStates.photo_full), ~F.photo)
async def reject_non_photo_full(m: Message, state: FSMContext):
    lang = lang_for(m.from_user.id)
    await delete_user_message(m)
    await send_or_edit_user_text(m.from_user.id, t(lang, "photo_step_removed"))
    await show_preview(m, state)
# ================= FORM CONSTANTS =================

FORM_ORDER = [
    ApplicationStates.name,
    ApplicationStates.phone,
    ApplicationStates.age,
    ApplicationStates.headphones,
    ApplicationStates.telegram,
    ApplicationStates.city,
    ApplicationStates.work_time,
    ApplicationStates.experience,
    ApplicationStates.living,
    ApplicationStates.devices,
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
    ApplicationStates.headphones,
    ApplicationStates.living,
    ApplicationStates.devices,
    ApplicationStates.device_model,
    ApplicationStates.work_time,
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
    if not await can_manage_admin_group(m):
        await delete_message_silent(m)
        return
    data = await state.get_data()
    uid = int(data.get("reject_uid") or 0)
    view_mode = bool(data.get("reject_view"))
    view_filter = str(data.get("reject_filter") or "all")
    view_offset = int(data.get("reject_offset") or 0)
    await delete_message_silent(m)
    if uid > 0 and view_mode:
        form_data = get_form_data(uid) or {}
        photo_id = await _preferred_admin_photo(uid, form_data)
        await update_admin_view_message(
            "🤍 Пожалуйста, напиши причину отказа текстом.",
            reject_reason_keyboard(),
            photo_id,
        )
    else:
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
    await safe_call_answer(call)
    await clear_portfolio_media(call.from_user.id)
    await send_or_edit_user_text(
        call.from_user.id,
        t(lang, "about_work_text"),
        reply_markup=about_menu(lang)
    )


@dp.callback_query(F.data == "about_platforms")
async def about_platforms(call: CallbackQuery):
    lang = lang_for(call.from_user.id)
    await safe_call_answer(call)
    await clear_portfolio_media(call.from_user.id)
    await send_or_edit_user_text(
        call.from_user.id,
        t(lang, "about_platforms_text"),
        reply_markup=about_menu(lang)
    )


@dp.callback_query(F.data == "about_income")
async def about_income(call: CallbackQuery):
    lang = lang_for(call.from_user.id)
    await safe_call_answer(call)
    await clear_portfolio_media(call.from_user.id)
    await send_or_edit_user_text(
        call.from_user.id,
        t(lang, "about_income_text"),
        reply_markup=about_menu(lang)
    )

@dp.callback_query(F.data == "portfolio")
async def portfolio(call: CallbackQuery):
    try:
        lang = lang_for(call.from_user.id)
        await safe_call_answer(call)
        await clear_portfolio_media(call.from_user.id)
        await send_or_edit_user_text(
            call.from_user.id,
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
        await safe_call_answer(call)
        await clear_portfolio_media(call.from_user.id)
        await send_or_edit_user_text(
            call.from_user.id,
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
        await safe_call_answer(call)
        await clear_portfolio_media(call.from_user.id)
        username = PUBLIC_MANAGER_USERNAME
        link_titles = {
            "ru": "Открыть чат с менеджером",
            "en": "Open manager chat",
            "pt": "Abrir chat com o gerente",
            "es": "Abrir chat con manager",
        }
        manager_link = f"https://t.me/{username}"
        manager_link_html = f'<a href="{manager_link}">{link_titles.get(lang, link_titles["ru"])}</a>'
        await send_or_edit_user_text(
            call.from_user.id,
            t(
                lang,
                "profile_contact_title",
                link=manager_link_html,
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
    if field == "email":
        if not is_valid_email(value):
            await send_or_edit_user_text(m.from_user.id, t(lang, "field_email_invalid"))
            return
        value = value.strip().lower()
    if field == "living":
        normalized = normalize_yes_no(value, lang=lang)
        if not normalized:
            await send_or_edit_user_text(m.from_user.id, t(lang, "field_yes_no"))
            return
        value = normalized
    if field == "devices" and len(value) < 2:
        await send_or_edit_user_text(m.from_user.id, t(lang, "field_devices_short"))
        return
    if field == "work_time" and not has_any_digit(value):
        await send_or_edit_user_text(m.from_user.id, t(lang, "field_work_time_invalid"))
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
        await safe_call_answer(call, t(lang, "photo_edit_disabled"), show_alert=False)
    except Exception:
        logger.exception("Ошибка в preview_edit_photo")
        await safe_call_answer(call, "Не удалось открыть замену фото", show_alert=False)

@dp.callback_query(F.data.startswith("edit_photo:"))
async def edit_photo(call: CallbackQuery, state: FSMContext):
    try:
        lang = lang_for(call.from_user.id)
        await state.update_data(edit_photo=None)
        await safe_call_answer(call, t(lang, "photo_edit_disabled"), show_alert=False)
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

def _merge_preview_payload(user_id: int, state_data: dict | None) -> dict:
    merged: dict = {}
    saved = get_form_data(user_id) or {}
    if isinstance(saved, dict):
        merged.update(saved)
    if isinstance(state_data, dict):
        for key, value in state_data.items():
            if value is not None:
                merged[key] = value
    return merged

@dp.callback_query(StateFilter(ApplicationStates.preview), F.data.startswith("preview_photo:"))
async def preview_photo(call: CallbackQuery, state: FSMContext):
    try:
        lang = lang_for(call.from_user.id)
        await state.update_data(preview_photo_mode=None, edit_photo=None)
        await safe_call_answer(call, t(lang, "photo_edit_disabled"), show_alert=False)
    except Exception:
        logger.exception("Ошибка в preview_photo")
        lang = lang_for(call.from_user.id)
        fail_text = (
            "Не удалось открыть фото. Попробуй ещё раз."
            if lang == "ru"
            else (
                "Couldn't open the photo. Please try again."
                if lang == "en"
                else (
                    "Nao foi possivel abrir a foto. Tente novamente."
                    if lang == "pt"
                    else "No se pudo abrir la foto. Intentalo de nuevo."
                )
            )
        )
        await safe_call_answer(call, fail_text, show_alert=False)

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

async def show_preview(
    m: Message,
    state: FSMContext,
    user_id: int | None = None,
    show_loading: bool = True,
):
    target_user_id = user_id or m.chat.id
    lang = lang_for(target_user_id)
    data = _merge_preview_payload(target_user_id, await state.get_data())
    if show_loading:
        await clear_user_menu_message(target_user_id)
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
        email=_safe_text(data.get("email", "—")),
        living=_safe_text(data.get("living", "—")),
        devices=_safe_text(data.get("devices", "—")),
        work_time=_safe_text(data.get("work_time", "—")),
        experience=_safe_text(data.get("experience", "—")),
        telegram=_safe_text(data.get("telegram", "—")),
        status=status_caption,
    )
    await state.update_data(preview_photo_mode=None, edit_photo=None)
    await state.set_state(ApplicationStates.preview)
    set_last_state(target_user_id, ApplicationStates.preview.state)
    await send_or_edit_user_text(
        target_user_id,
        text,
        reply_markup=preview_keyboard(lang),
    )

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
            project=normalize_project_value(str((data or {}).get("project") or BOT_PROJECT_KEY)),
            country=(
                data.get("country")
                or extract_country_from_location(data.get("city"))
                or country_from_phone(data.get("phone"))
            ),
            application_stage=APPLICATION_STAGE_FULL,
        )
        data = await state.get_data()

        await gentle_typing(call.message.chat.id)

        current_source = normalize_source_value(get_source(user.id), data)
        preferred = str((data or {}).get("preferred_contact") or "").strip().lower()
        if current_source == SOURCE_UNKNOWN:
            if preferred == "whatsapp":
                resolved_source = SOURCE_SITE_WHATSAPP
            elif preferred == "telegram":
                resolved_source = SOURCE_SITE_TG
            else:
                resolved_source = SOURCE_TELEGRAM_BOT
        elif current_source == SOURCE_SITE_TG and preferred == "whatsapp":
            resolved_source = SOURCE_SITE_WHATSAPP
        else:
            resolved_source = current_source
        set_source(user.id, resolved_source)
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
        parts = call.data.split(":")
        try:
            uid = int(parts[1])
        except Exception:
            await safe_call_answer(call, "Некорректный ID заявки", show_alert=True)
            return
        view_mode = len(parts) > 2 and parts[2] == "view"
        view_filter: str | None = None
        view_offset = 0
        if view_mode and len(parts) > 4:
            view_filter = parts[3]
            try:
                view_offset = max(int(parts[4]), 0)
            except Exception:
                view_offset = 0

        set_status(uid, "accepted")
        if update_application_status:
            try:
                update_application_status(uid, "accepted")
            except Exception:
                logger.exception("Ошибка обновления статуса в Excel")

        try:
            if uid > 0:
                form_data = get_form_data(uid) or {}
                user_lang = submission_lang_for_user(uid, form_data)
                app = get_application(uid)
                site_stage2 = is_site_quick_application(app, form_data)
                channel_url = stage2_channel_link(user_lang) if site_stage2 else None
            else:
                form_data = {}
                user_lang = STARFLOW_DEFAULT_LANG
                channel_url = None
            caption = build_menu_caption_with_status(
                "accepted",
                t(user_lang, "accept_caption"),
                lang=user_lang,
                tail=t(user_lang, "approved_tail")
            )
            if uid > 0:
                await send_or_edit_user_menu(uid, caption, lang=user_lang, channel_url=channel_url)
                await clear_user_flow_message(uid)
        except Exception:
            logger.exception("Ошибка отправки меню после принятия")
        await update_admin_summary_message(uid, "accepted")
        try:
            await post_admin_menu()
        except Exception:
            logger.exception("Ошибка возврата в админ-меню")
        if view_mode:
            try:
                if view_filter:
                    await send_admin_list(call, view_filter, view_offset)
                else:
                    data = get_form_data(uid) or {}
                    contact_url = contact_url_for_user(uid, data)
                    photo_id = await _preferred_admin_photo(uid, data)
                    await update_admin_view_message(
                        build_admin_full_text(data, uid, "accepted"),
                        admin_list_item_keyboard(uid, "accepted", contact_url=contact_url),
                        photo_id,
                    )
            except Exception:
                logger.exception("Ошибка обновления карточки после принятия")
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
        parts = call.data.split(":")
        try:
            uid = int(parts[1])
        except Exception:
            await safe_call_answer(call, "Некорректный ID заявки", show_alert=True)
            return
        view_mode = len(parts) > 2 and parts[2] == "view"
        view_filter = parts[3] if view_mode and len(parts) > 4 else None
        view_offset = 0
        if view_mode and len(parts) > 4:
            try:
                view_offset = max(int(parts[4]), 0)
            except Exception:
                view_offset = 0
        flow_payload = {
            "reject_uid": uid,
            "reject_view": view_mode,
            "reject_filter": view_filter or "all",
            "reject_offset": view_offset,
        }
        await state.set_state(ApplicationStates.admin_reject_reason)
        await state.update_data(**flow_payload)
        await sync_anonymous_admin_state(
            chat_id=call.message.chat.id if call.message else None,
            target_state=ApplicationStates.admin_reject_reason,
            data=flow_payload,
        )

        prompt = (
            "✍️ <b>Отклонение заявки</b>\n\n"
            "Выбери готовую причину или нажми «Своя причина» и напиши текст вручную."
        )
        if view_mode:
            form_data = get_form_data(uid) or {}
            photo_id = await _preferred_admin_photo(uid, form_data)
            await update_admin_view_message(
                prompt,
                reject_templates_keyboard(uid, view_filter or "all", view_offset),
                photo_id,
            )
        else:
            await update_admin_menu_message(
                prompt,
                reject_templates_keyboard(uid, view_filter or "all", view_offset),
            )
        await safe_call_answer(call, "Выбери причину отказа", show_alert=True)
    except Exception:
        logger.exception("Ошибка в admin_reject")
        await safe_call_answer(call, "Ошибка при открытии отказа", show_alert=True)

@dp.callback_query(StateFilter("*"), F.data.startswith("reject_tpl:"))
async def reject_template(call: CallbackQuery, state: FSMContext):
    try:
        if not await can_manage_admin_callback(call):
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        parts = call.data.split(":")
        tpl_code = parts[1] if len(parts) > 1 else ""
        uid_from_callback: int | None = None
        filter_from_callback: str | None = None
        offset_from_callback: int | None = None
        if len(parts) > 2:
            try:
                uid_from_callback = int(parts[2])
            except Exception:
                uid_from_callback = None
        if len(parts) > 3:
            filter_from_callback = str(parts[3] or "").strip() or None
        if len(parts) > 4:
            try:
                offset_from_callback = max(int(parts[4]), 0)
            except Exception:
                offset_from_callback = 0

        state_data = await state.get_data()
        uid = uid_from_callback or state_data.get("reject_uid")
        if not uid:
            await safe_call_answer(call, "🤍 Не вижу кандидата")
            return
        view_mode = bool(state_data.get("reject_view")) or (uid_from_callback is not None)
        view_filter = filter_from_callback or str(state_data.get("reject_filter") or "all")
        view_offset = offset_from_callback if offset_from_callback is not None else int(state_data.get("reject_offset") or 0)

        await state.update_data(
            reject_uid=uid,
            reject_view=view_mode,
            reject_filter=view_filter,
            reject_offset=view_offset,
        )
        await sync_anonymous_admin_state(
            chat_id=call.message.chat.id if call.message else None,
            target_state=ApplicationStates.admin_reject_reason,
            data=await state.get_data(),
        )

        form_data = get_form_data(uid) or {}
        user_lang = submission_lang_for_user(uid, form_data)

        if tpl_code == "custom":
            if view_mode:
                photo_id = await _preferred_admin_photo(uid, form_data)
                await update_admin_view_message(
                    "✍️ <b>Своя причина отказа</b>\n\nНапиши текст следующим сообщением в чат админки.",
                    reject_reason_keyboard(),
                    photo_id,
                )
            else:
                await update_admin_menu_message(
                    "✍️ Напиши свою причину отказа:",
                    reject_reason_keyboard()
                )
            await safe_call_answer(call, "Введи свой текст отказа", show_alert=True)
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
            if uid > 0:
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
            if view_mode and view_filter:
                await send_admin_list(
                    call,
                    view_filter,
                    view_offset,
                )
            elif view_mode:
                data = get_form_data(uid) or {}
                contact_url = contact_url_for_user(uid, data)
                photo_id = await _preferred_admin_photo(uid, data)
                await update_admin_view_message(
                    build_admin_full_text(data, uid, "rejected"),
                    admin_list_item_keyboard(uid, "rejected", contact_url=contact_url),
                    photo_id,
                )
        except Exception:
            logger.exception("Ошибка обновления карточки после отклонения")
        try:
            await post_admin_menu()
        except Exception:
            logger.exception("Ошибка возврата в админ-меню")
        await state.clear()
        await sync_anonymous_admin_state(
            chat_id=call.message.chat.id if call.message else None,
            target_state=None,
        )
        await safe_call_answer(call, "Заявка отклонена")
    except Exception:
        logger.exception("Ошибка в reject_template")
        await safe_call_answer(call, "Ошибка при отклонении", show_alert=True)

@dp.message(StateFilter(ApplicationStates.admin_reject_reason), F.text)
async def reject_reason(m: Message, state: FSMContext):
    try:
        if not await can_manage_admin_group(m):
            await delete_message_silent(m)
            return
        await delete_message_silent(m)
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
            if uid > 0:
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
            if bool(data.get("reject_view")) and data.get("reject_filter"):
                filter_key = str(data.get("reject_filter") or "all")
                offset = int(data.get("reject_offset") or 0)
                total = _apps_total_for_filter(filter_key)
                if total > 0:
                    if offset < 0:
                        offset = 0
                    if offset >= total:
                        offset = total - 1
                    await _render_admin_list_message(
                        filter_key=filter_key,
                        offset=offset,
                        user_id=uid,
                        item_status="rejected",
                        total=total,
                    )
            elif bool(data.get("reject_view")):
                form_data = get_form_data(uid) or {}
                contact_url = contact_url_for_user(uid, form_data)
                photo_id = await _preferred_admin_photo(uid, form_data)
                await update_admin_view_message(
                    build_admin_full_text(form_data, uid, "rejected"),
                    admin_list_item_keyboard(uid, "rejected", contact_url=contact_url),
                    photo_id,
                )
        except Exception:
            logger.exception("Ошибка обновления карточки после отклонения")
        try:
            await post_admin_menu()
        except Exception:
            logger.exception("Ошибка возврата в админ-меню")
        await state.clear()
        await sync_anonymous_admin_state(
            chat_id=m.chat.id if m.chat else None,
            target_state=None,
        )
    except Exception:
        logger.exception("Ошибка в reject_reason")


@dp.callback_query(StateFilter("*"), F.data.startswith("admin_send_model:"))
async def admin_send_model(call: CallbackQuery, state: FSMContext):
    try:
        if not await can_manage_admin_callback(call):
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        parts = call.data.split(":")
        try:
            uid = int(parts[1])
        except Exception:
            await safe_call_answer(call, "Некорректный ID заявки", show_alert=True)
            return
        if uid <= 0:
            await safe_call_answer(call, "Для этого источника отправка недоступна", show_alert=True)
            return
        if (get_status(uid) or "pending") != "accepted":
            await safe_call_answer(call, "Сначала прими заявку", show_alert=True)
            return

        view_mode = len(parts) > 2 and parts[2] == "view"
        view_filter = parts[3] if view_mode and len(parts) > 4 else None
        view_offset = 0
        if view_mode and len(parts) > 4:
            try:
                view_offset = max(int(parts[4]), 0)
            except Exception:
                view_offset = 0

        form_data = get_form_data(uid) or {}
        candidate_name = str(form_data.get("name") or f"ID {uid}")

        flow_payload = {
            "send_model_uid": uid,
            "send_model_view": view_mode,
            "send_model_filter": view_filter,
            "send_model_offset": view_offset,
        }
        await state.set_state(ApplicationStates.admin_send_model_message)
        await state.update_data(**flow_payload)
        await sync_anonymous_admin_state(
            call.message.chat.id if call.message else None,
            ApplicationStates.admin_send_model_message,
            flow_payload,
        )
        await update_admin_view_message(
            "📨 <b>Отправка сообщения партнёру</b>\n\n"
            f"Кандидат: <b>{html.escape(candidate_name)}</b>\n\n"
            "Отправь одним сообщением уникальный текст для этого партнёра.\n"
            "Можно вставить Zoom-ссылку.\n\n"
            "Сообщение уйдёт в личку пользователю от бота.",
            admin_send_model_keyboard(),
            None,
        )
    except Exception:
        logger.exception("Ошибка в admin_send_model")
        await safe_call_answer(call, "Не удалось открыть отправку сообщения", show_alert=True)


@dp.callback_query(StateFilter(ApplicationStates.admin_send_model_message), F.data == "admin_send_model_cancel")
async def admin_send_model_cancel(call: CallbackQuery, state: FSMContext):
    try:
        if not await can_manage_admin_callback(call):
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        await state.clear()
        await sync_anonymous_admin_state(call.message.chat.id if call.message else None, None)
        await post_admin_menu()
        await safe_call_answer(call, "Отменено")
    except Exception:
        logger.exception("Ошибка в admin_send_model_cancel")
        await safe_call_answer(call, "Не удалось отменить", show_alert=False)


@dp.message(StateFilter(ApplicationStates.admin_send_model_message), ~F.text)
async def admin_send_model_non_text(message: Message):
    if not await can_manage_admin_group(message):
        await delete_message_silent(message)
        return
    await delete_message_silent(message)
    await update_admin_view_message(
        "⚠️ Отправь текстовым сообщением.\n\nМожно вставить ссылку Zoom.",
        admin_send_model_keyboard(),
        None,
    )


@dp.message(StateFilter(ApplicationStates.admin_send_model_message), F.text)
async def admin_send_model_message(message: Message, state: FSMContext):
    try:
        if not await can_manage_admin_group(message):
            await delete_message_silent(message)
            return
        if message.text and message.text.strip().startswith("/"):
            await delete_message_silent(message)
            await update_admin_menu_message(
                "⚠️ Отправь именно текст для партнёра, а не команду.\n\nМожно вставить Zoom-ссылку.",
                admin_send_model_keyboard(),
            )
            return

        data = await state.get_data()
        uid_raw = data.get("send_model_uid")
        try:
            uid = int(uid_raw)
        except Exception:
            uid = 0
        if uid <= 0:
            await state.clear()
            await sync_anonymous_admin_state(message.chat.id, None)
            await delete_message_silent(message)
            await post_admin_menu()
            return

        if (get_status(uid) or "pending") != "accepted":
            await state.clear()
            await sync_anonymous_admin_state(message.chat.id, None)
            await delete_message_silent(message)
            counts = get_status_counts()
            stage_counts = get_application_stage_counts()
            await update_admin_menu_message(
                "⚠️ Заявка больше не в статусе «Принято». Сначала проверь статус.",
                admin_menu_keyboard(counts, stage_counts),
            )
            return

        await bot.copy_message(
            chat_id=uid,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
        )
        form_data = get_form_data(uid) or {}
        form_data[AUTO_REQUEST_INFO_FLAG_KEY] = datetime.now(timezone.utc).isoformat()
        set_form_data(uid, form_data)
        await delete_message_silent(message)
        await state.clear()
        await sync_anonymous_admin_state(message.chat.id, None)
        counts = get_status_counts()
        stage_counts = get_application_stage_counts()
        await update_admin_menu_message(
            f"✅ Сообщение отправлено партнёру (ID: {uid}).",
            admin_menu_keyboard(counts, stage_counts),
        )
    except TelegramForbiddenError:
        data = await state.get_data()
        uid_raw = data.get("send_model_uid")
        logger.warning(
            "Пользователь %s заблокировал бота или не открыл диалог",
            uid_raw if uid_raw is not None else "unknown",
        )
        await update_admin_view_message(
            "⚠️ Не удалось доставить сообщение.\n"
            "Пользователь не открыл чат с ботом или заблокировал бота.",
            admin_send_model_keyboard(),
            None,
        )
    except Exception:
        logger.exception("Ошибка в admin_send_model_message")
        await update_admin_view_message(
            "⚠️ Ошибка отправки. Попробуй отправить текст ещё раз.",
            admin_send_model_keyboard(),
            None,
        )


@dp.callback_query(StateFilter("*"), F.data.startswith("admin_request_info:"))
async def admin_request_info(call: CallbackQuery):
    try:
        if not await can_manage_admin_callback(call):
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        parts = call.data.split(":")
        try:
            uid = int(parts[1])
        except Exception:
            await safe_call_answer(call, "Некорректный ID заявки", show_alert=True)
            return
        if uid <= 0:
            await safe_call_answer(call, "Для этого источника отправка недоступна", show_alert=True)
            return
        if (get_status(uid) or "pending") != "pending":
            await safe_call_answer(call, "Запрос уточнения доступен только для новых заявок", show_alert=True)
            return

        view_mode = len(parts) > 2 and parts[2] == "view"
        view_filter = parts[3] if view_mode and len(parts) > 4 else None
        view_offset = 0
        if view_mode and len(parts) > 4:
            try:
                view_offset = max(int(parts[4]), 0)
            except Exception:
                view_offset = 0

        form_data = get_form_data(uid) or {}
        if detect_application_stage(form_data) == APPLICATION_STAGE_FULL:
            await safe_call_answer(call, "Для полной анкеты уточнение не требуется", show_alert=True)
            return
        candidate_name = str(form_data.get("name") or f"ID {uid}")
        user_lang = submission_lang_for_user(uid, form_data)
        locale = normalize_lang(user_lang)
        continue_line = {
            "ru": "Нажми «Продолжить» ниже, чтобы дозаполнить анкету и перейти к старту работы.",
            "en": "Tap “Continue” below to complete your form and move to work start.",
            "pt": "Toque em “Continuar” abaixo para completar o cadastro e iniciar o trabalho.",
            "es": "Pulsa “Continuar” abajo para completar tu solicitud y pasar al inicio del trabajo.",
        }.get(locale, "Нажми «Продолжить» ниже, чтобы дозаполнить анкету и перейти к старту работы.")
        message_text = f"{auto_request_info_text(user_lang)}\n\n{continue_line}"

        await send_or_edit_user_text(
            uid,
            message_text,
            reply_markup=continue_form_keyboard(user_lang),
        )

        form_data[AUTO_REQUEST_INFO_FLAG_KEY] = datetime.now(timezone.utc).isoformat()
        set_form_data(uid, form_data)

        if view_mode and view_filter:
            await send_admin_list(call, view_filter, view_offset, preferred_user_id=uid)
        else:
            counts = get_status_counts()
            stage_counts = get_application_stage_counts()
            await update_admin_menu_message(
                f"✅ Запрос уточнения отправлен кандидату (ID: {uid}, имя: {html.escape(candidate_name)}).",
                admin_menu_keyboard(counts, stage_counts),
            )
        await safe_call_answer(call, "Запрос уточнения отправлен", show_alert=True)
    except TelegramForbiddenError:
        await update_admin_menu_message(
            "⚠️ Не удалось доставить запрос уточнения.\n"
            "Пользователь не открыл чат с ботом или заблокировал бота.",
            admin_menu_keyboard(get_status_counts(), get_application_stage_counts()),
        )
        await safe_call_answer(call, "Сообщение не доставлено", show_alert=True)
    except Exception:
        logger.exception("Ошибка в admin_request_info")
        await safe_call_answer(call, "Не удалось открыть запрос уточнения", show_alert=True)


@dp.callback_query(StateFilter(ApplicationStates.admin_request_info_message), F.data == "admin_request_info_cancel")
async def admin_request_info_cancel(call: CallbackQuery, state: FSMContext):
    try:
        if not await can_manage_admin_callback(call):
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        await state.clear()
        await post_admin_menu()
        await safe_call_answer(call, "Отменено")
    except Exception:
        logger.exception("Ошибка в admin_request_info_cancel")
        await safe_call_answer(call, "Не удалось отменить", show_alert=False)


@dp.message(StateFilter(ApplicationStates.admin_request_info_message), ~F.text)
async def admin_request_info_non_text(message: Message):
    if not await can_manage_admin_group(message):
        await delete_message_silent(message)
        return
    await delete_message_silent(message)
    await update_admin_menu_message(
        "⚠️ Отправь текстовым сообщением, что нужно уточнить.",
        admin_request_info_keyboard(),
    )


@dp.message(StateFilter(ApplicationStates.admin_request_info_message), F.text)
async def admin_request_info_message(message: Message, state: FSMContext):
    try:
        if not await can_manage_admin_group(message):
            await delete_message_silent(message)
            return
        if message.text and message.text.strip().startswith("/"):
            await delete_message_silent(message)
            await update_admin_menu_message(
                "⚠️ Отправь именно текст для кандидата, а не команду.",
                admin_request_info_keyboard(),
            )
            return

        data = await state.get_data()
        uid_raw = data.get("request_info_uid")
        try:
            uid = int(uid_raw)
        except Exception:
            uid = 0
        if uid <= 0:
            await state.clear()
            await delete_message_silent(message)
            await post_admin_menu()
            return

        await bot.copy_message(
            chat_id=uid,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
        )
        await delete_message_silent(message)
        await state.clear()
        counts = get_status_counts()
        stage_counts = get_application_stage_counts()
        await update_admin_menu_message(
            f"✅ Запрос уточнения отправлен кандидату (ID: {uid}).",
            admin_menu_keyboard(counts, stage_counts),
        )
    except TelegramForbiddenError:
        await update_admin_menu_message(
            "⚠️ Не удалось доставить сообщение.\n"
            "Пользователь не открыл чат с ботом или заблокировал бота.",
            admin_request_info_keyboard(),
        )
    except Exception:
        logger.exception("Ошибка в admin_request_info_message")
        await update_admin_menu_message(
            "⚠️ Ошибка отправки. Попробуй ещё раз.",
            admin_request_info_keyboard(),
        )


@dp.callback_query(StateFilter("*"), F.data.startswith("admin_card:"))
async def admin_card_toggle(call: CallbackQuery):
    try:
        if not await can_manage_admin_callback(call):
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        _, uid_raw, mode, filter_key, offset_raw = call.data.split(":", 4)
        uid = int(uid_raw)
        offset = int(offset_raw)
        show_full = True
        await send_admin_list(
            call,
            filter_key=filter_key,
            offset=offset,
            preferred_user_id=uid,
            show_full=show_full,
        )
    except Exception:
        logger.exception("Ошибка в admin_card_toggle")
        await safe_call_answer(call, "Не удалось обновить карточку", show_alert=False)


@dp.callback_query(F.data.startswith("admin_status:"))
async def admin_status(call: CallbackQuery):
    try:
        if not await can_manage_admin_callback(call):
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        _, uid, status = call.data.split(":", 2)
        status_label = STATUS_LABELS.get(status, status)
        await safe_call_answer(call, f"Статус: {status_label}", show_alert=False)
    except Exception:
        await safe_call_answer(call, "Статус обновлён", show_alert=False)

@dp.callback_query(F.data.startswith("admin_photos:"))
async def admin_photos(call: CallbackQuery):
    try:
        if not await can_manage_admin_callback(call):
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        if not call.message:
            await safe_call_answer(call, "Сообщение недоступно", show_alert=False)
            return
        uid = int(call.data.split(":", 1)[1])
        data = get_form_data(uid) or {}
        is_full_stage = detect_application_stage(data) == APPLICATION_STAGE_FULL
        contact_url = contact_url_for_user(uid, data)
        photo_id = await _preferred_admin_photo(uid, data)
        if not photo_id:
            await safe_call_answer(call, "Фото не найдено", show_alert=False)
            return
        status = get_status(uid) or "pending"
        text = build_admin_full_text(data, uid, status)
        await update_admin_view_message(
            text,
            admin_list_view_keyboard(
                uid,
                status,
                "all",
                0,
                1,
                ADMIN_LIST_LIMIT,
                contact_url=contact_url,
                show_full=True,
                allow_request_info=not is_full_stage,
            ),
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
    await show_admin_create_post_prompt()


async def show_admin_create_post_prompt(notice: str | None = None):
    prompt = post_creator_prompt()
    if notice:
        prompt = f"{notice}\n\n{prompt}"
    await update_admin_menu_message(prompt, admin_create_post_keyboard())


@dp.message(Command("create_post"))
@dp.message(Command("crosspost"))
async def admin_create_post_command(message: Message, state: FSMContext):
    if not await can_manage_admin_group(message):
        await delete_message_silent(message)
        return
    await open_create_post_mode(state)
    await delete_message_silent(message)


@dp.message(StateFilter(ApplicationStates.admin_create_post))
async def admin_create_post_submit(message: Message, state: FSMContext):
    if message.from_user and message.from_user.is_bot and not is_anonymous_admin_post(message):
        return
    if not await can_manage_admin_group(message):
        await delete_message_silent(message)
        return
    if message.text and message.text.strip().startswith("/"):
        await delete_message_silent(message)
        await show_admin_create_post_prompt("⚠️ Сейчас включён режим публикации. Отправь пост или нажми «Отменить».")
        return
    if message.media_group_id:
        await delete_message_silent(message)
        await show_admin_create_post_prompt("⚠️ Альбомы не поддерживаются. Отправь один пост (одно сообщение).")
        return
    if not any([message.text, message.photo, message.video, message.document, message.animation]):
        await delete_message_silent(message)
        await show_admin_create_post_prompt("⚠️ Поддерживаются: текст, фото, видео, gif или документ.")
        return

    ru_text, ru_entities = extract_post_text_and_entities(message)
    if ru_text and not CYRILLIC_RE.search(ru_text):
        await delete_message_silent(message)
        await show_admin_create_post_prompt("⚠️ Текст поста должен быть на русском, чтобы перевести его автоматически.")
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
        await delete_message_silent(message)
        await show_admin_create_post_prompt(str(exc))
    except RuntimeError as exc:
        await delete_message_silent(message)
        await show_admin_create_post_prompt(str(exc))
    except Exception:
        logger.exception("Ошибка публикации в режиме create_post")
        await delete_message_silent(message)
        await show_admin_create_post_prompt("⚠️ Не удалось опубликовать пост. Попробуй ещё раз.")

@dp.message(F.text == "/admin")
async def admin_menu(message: Message, state: FSMContext):
    if not await can_manage_admin_group(message):
        await delete_message_silent(message)
        return
    await state.clear()
    await sync_anonymous_create_post_state(enabled=False)
    await clear_admin_temp_messages()
    await ensure_admin_menu_posted()
    await delete_message_silent(message)

@dp.callback_query(F.data == "admin_post:cancel")
async def admin_create_post_cancel(call: CallbackQuery, state: FSMContext):
    try:
        if not await can_manage_admin_callback(call):
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
                ApplicationStates.admin_send_model_message.state,
                ApplicationStates.admin_request_info_message.state,
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
        if action == "sources":
            await clear_admin_view_message()
            await update_admin_menu_message(
                "🌐 <b>Фильтр по источнику</b>\n\nБыстрый просмотр заявок из сайта или бота.",
                admin_menu_sources_keyboard()
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
        if action in {
            "pending",
            "reviewed",
            "accepted",
            "rejected",
            "all",
            "stage_quick",
            "stage_full",
            "src_site",
            "src_bot",
            "src_unknown",
            "project_streamflow",
            "project_starflow",
        }:
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
    if not await can_manage_admin_callback(call):
        await safe_call_answer(call, "Недостаточно прав", show_alert=True)
        return
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
        if not await can_manage_admin_callback(call):
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
        if not call.message:
            await safe_call_answer(call, "Сообщение недоступно", show_alert=False)
            return
        parts = call.data.split(":")
        if len(parts) < 5:
            await safe_call_answer(call, "Некорректные данные фото", show_alert=False)
            return
        uid = int(parts[1])
        photo_type = parts[2]
        filter_key = parts[3]
        offset = int(parts[4])
        data = get_form_data(uid) or {}
        is_full_stage = detect_application_stage(data) == APPLICATION_STAGE_FULL
        # Always show full card in admin list.
        show_full = True
        contact_url = contact_url_for_user(uid, data)
        photo_key = "photo_face" if photo_type == "face" else "photo_full"
        photo_id = await _ensure_admin_photo_ref(uid, data, photo_key)
        if not photo_id:
            await safe_call_answer(call, "Фото не найдено", show_alert=False)
            return
        status = get_status(uid) or "pending"
        label = _admin_list_label(filter_key)
        total = _apps_total_for_filter(filter_key)
        if total == 0:
            await safe_call_answer(call)
            return
        if offset < 0:
            offset = 0
        if offset >= total:
            offset = total - 1
        page = offset // ADMIN_LIST_LIMIT + 1
        pages = (total + ADMIN_LIST_LIMIT - 1) // ADMIN_LIST_LIMIT
        body = build_admin_full_text(data, uid, status)
        text = (
            f"🗂 <b>{label}</b>\n\n"
            f"Заявка <b>{offset + 1}</b> из <b>{total}</b>\n"
            f"Страница: <b>{page}/{pages}</b>\n\n"
            f"{body}"
        )
        await update_admin_view_message(
            text,
            admin_list_view_keyboard(
                uid,
                status,
                filter_key,
                offset,
                total,
                ADMIN_LIST_LIMIT,
                contact_url=contact_url,
                show_full=show_full,
                allow_request_info=not is_full_stage,
            ),
            photo_id
        )
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка переключения фото")
        await safe_call_answer(call, "Не удалось показать фото", show_alert=False)

@dp.callback_query(F.data.startswith("admin_posts:"))
async def admin_posts_pagination(call: CallbackQuery):
    try:
        if not await can_manage_admin_callback(call):
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
        if not await can_manage_admin_callback(call):
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
        if not await can_manage_admin_callback(call):
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
        if not await can_manage_admin_callback(call):
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
        if not await can_manage_admin_callback(call):
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


@dp.message(StateFilter(ApplicationStates.admin_edit_post_text))
async def admin_post_edit_text_submit(message: Message, state: FSMContext):
    state_data = await state.get_data()
    post_id = int(state_data.get("post_id", 0) or 0)
    offset = int(state_data.get("posts_offset", 0) or 0)
    async def show_notice(text: str):
        if post_id:
            await update_admin_view_message(
                text,
                admin_posts_edit_keyboard(post_id, offset),
                None,
            )
        else:
            counts = get_status_counts()
            stage_counts = get_application_stage_counts()
            await update_admin_menu_message(text, admin_menu_keyboard(counts, stage_counts))
    try:
        if not await can_manage_admin_group(message):
            await delete_message_silent(message)
            return
        if not message.text:
            await show_notice("⚠️ Отправь текст поста (не фото и не файл).")
            return
        ru_text, ru_entities = extract_post_text_and_entities(message)
        if not ru_text.strip():
            await show_notice("⚠️ Текст пустой. Отправь текст заново.")
            return
        if not CYRILLIC_RE.search(ru_text):
            await show_notice("⚠️ Текст должен быть на русском, чтобы сделать автоперевод.")
            return

        item = get_posted_message(post_id)
        if not item:
            await show_notice("⚠️ Пост не найден.")
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
    except RuntimeError as exc:
        await show_notice(str(exc))
    except Exception:
        logger.exception("Ошибка редактирования текста выложенного поста")
        await show_notice("⚠️ Не удалось обновить текст поста.")
    finally:
        await delete_message_silent(message)


@dp.message(StateFilter(ApplicationStates.admin_edit_post_photo))
async def admin_post_edit_photo_submit(message: Message, state: FSMContext):
    state_data = await state.get_data()
    post_id = int(state_data.get("post_id", 0) or 0)
    offset = int(state_data.get("posts_offset", 0) or 0)
    async def show_notice(text: str):
        if post_id:
            await update_admin_view_message(
                text,
                admin_posts_edit_keyboard(post_id, offset),
                None,
            )
        else:
            counts = get_status_counts()
            stage_counts = get_application_stage_counts()
            await update_admin_menu_message(text, admin_menu_keyboard(counts, stage_counts))
    try:
        if not await can_manage_admin_group(message):
            await delete_message_silent(message)
            return
        item = get_posted_message(post_id)
        if not item:
            await show_notice("⚠️ Пост не найден.")
            await state.clear()
            await show_admin_posted_posts(offset)
            return

        content_type = str(item.get("content_type") or "").strip().lower()
        expected_type = str(state_data.get("post_media_type") or content_type).strip().lower()
        new_file_id = extract_media_file_id_for_post(message, expected_type)
        if not new_file_id:
            media_name = post_media_type_name(expected_type)
            await show_notice(f"⚠️ Отправь именно {media_name} одним сообщением.")
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
    except RuntimeError as exc:
        await show_notice(str(exc))
    except Exception:
        logger.exception("Ошибка замены фото у выложенного поста")
        await show_notice("⚠️ Не удалось заменить фото.")
    finally:
        await delete_message_silent(message)

@dp.message(F.text == "/reset_db")
async def admin_reset_db(message: Message):
    if not await can_manage_admin_group(message):
        await delete_message_silent(message)
        return
    await update_admin_menu_message(
        "⚠️ Ты уверена, что хочешь полностью обнулить базу и статистику?",
        confirm_reset_db_keyboard()
    )
    await delete_message_silent(message)

@dp.callback_query(F.data == "admin_reset_db:confirm")
async def admin_reset_db_confirm(call: CallbackQuery):
    try:
        if not await can_manage_admin_callback(call):
            await safe_call_answer(call, "Недостаточно прав", show_alert=True)
            return
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
    if not await can_manage_admin_callback(call):
        await safe_call_answer(call, "Недостаточно прав", show_alert=True)
        return
    await post_admin_menu()
    await safe_call_answer(call, "Отменено")

        
@dp.callback_query(F.data == "portfolio_reviews")
async def portfolio_reviews(call: CallbackQuery):
    try:
        lang = lang_for(call.from_user.id)
        await clear_portfolio_media(call.from_user.id)
        await send_or_edit_user_text(
            call.from_user.id,
            t(lang, "portfolio_faq_text"),
            reply_markup=portfolio_menu(lang),
        )
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка в portfolio_reviews")
        await safe_call_answer(call, t(lang_for(call.from_user.id), "portfolio_send_error"), show_alert=False)

@dp.callback_query(F.data == "portfolio_videos")
async def portfolio_streams(call: CallbackQuery):
    try:
        lang = lang_for(call.from_user.id)
        await clear_portfolio_media(call.from_user.id)
        await send_or_edit_user_text(
            call.from_user.id,
            t(lang, "portfolio_script_text"),
            reply_markup=portfolio_menu(lang),
        )
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка в portfolio_streams")
        await safe_call_answer(call, t(lang_for(call.from_user.id), "portfolio_send_error"), show_alert=False)


@dp.callback_query(F.data.startswith("portfolio_nav:"))
async def portfolio_nav(call: CallbackQuery):
    try:
        lang = lang_for(call.from_user.id)
        await safe_call_answer(call, t(lang, "portfolio_nav_disabled"), show_alert=False)
    except Exception:
        logger.exception("Ошибка навигации портфолио")
        await safe_call_answer(call, t(lang_for(call.from_user.id), "portfolio_send_error"), show_alert=False)


@dp.callback_query(F.data.startswith("portfolio_jump:"))
async def portfolio_jump(call: CallbackQuery):
    try:
        lang = lang_for(call.from_user.id)
        await safe_call_answer(call, t(lang, "portfolio_nav_disabled"), show_alert=False)
    except Exception:
        logger.exception("Ошибка переключения секции портфолио")
        await safe_call_answer(call, t(lang_for(call.from_user.id), "portfolio_send_error"), show_alert=False)

@dp.callback_query(F.data == "portfolio_pdf")
async def portfolio_pdf(call: CallbackQuery):
    try:
        lang = lang_for(call.from_user.id)
        await clear_portfolio_media(call.from_user.id)
        await send_or_edit_user_text(
            call.from_user.id,
            t(lang, "portfolio_materials_text"),
            reply_markup=portfolio_menu(lang),
        )
        await safe_call_answer(call)
    except Exception:
        logger.exception("Ошибка в portfolio_pdf")
        await safe_call_answer(call, t(lang_for(call.from_user.id), "portfolio_send_error"), show_alert=False)

# ================= ADMIN STATS =================

@dp.message(F.text == "/stats")
async def admin_stats(message: Message):
    if not await can_manage_admin_group(message):
        await delete_message_silent(message)
        return
    await clear_admin_temp_messages()
    counts = get_status_counts()
    stage_counts = get_application_stage_counts()
    await update_admin_menu_message(
        build_admin_stats_text(),
        admin_menu_keyboard(counts, stage_counts),
    )
    await delete_message_silent(message)

@dp.message(F.text == "/excel")
async def admin_excel(message: Message):
    if not await can_manage_admin_group(message):
        await delete_message_silent(message)
        return
    await clear_admin_temp_messages()
    if not rebuild_excel_from_db:
        counts = get_status_counts()
        stage_counts = get_application_stage_counts()
        await update_admin_menu_message(
            "🤍 Экспорт в Excel недоступен. Установи openpyxl.",
            admin_menu_keyboard(counts, stage_counts),
        )
        await delete_message_silent(message)
        return
    file_path = rebuild_excel_from_db()
    if not file_path:
        counts = get_status_counts()
        stage_counts = get_application_stage_counts()
        await update_admin_menu_message(
            "🤍 Файл Excel ещё не создан. Отправь хотя бы одну заявку ✨",
            admin_menu_keyboard(counts, stage_counts),
        )
        await delete_message_silent(message)
        return
    msg = await message.answer_document(FSInputFile(str(file_path)))
    track_admin_temp_message(msg.message_id)
    await delete_message_silent(message)


@dp.callback_query()
async def fallback_stale_callback(call: CallbackQuery, state: FSMContext):
    if call.message and is_admin_chat(call.message.chat.id):
        counts = get_status_counts()
        stage_counts = get_application_stage_counts()
        await update_admin_menu_message(
            "⚠️ Кнопка устарела. Меню обновлено.",
            admin_menu_keyboard(counts, stage_counts),
        )
        await safe_call_answer(call)
        return

    if call.message and call.message.chat.type == "private":
        lang = lang_for(call.from_user.id)
        await safe_call_answer(call, t(lang, "stale_button"), show_alert=False)
        current = await state.get_state()
        if current in FORM_PROGRESS_STATES:
            await send_or_edit_user_text(
                call.from_user.id,
                t(lang, "resume_prompt"),
                reply_markup=continue_form_keyboard(lang),
            )
            return
        app = get_application(call.from_user.id)
        data = get_form_data(call.from_user.id) or {}
        site_stage2 = is_site_quick_application(app, data)
        await send_or_edit_user_text(
            call.from_user.id,
            t(lang, "menu_caption"),
            reply_markup=main_menu(
                lang,
                channel_url=stage2_channel_link(lang) if site_stage2 else None,
            ),
        )
        return

    await safe_call_answer(call)


@dp.message(F.chat.type == "private")
async def fallback_private_message(message: Message, state: FSMContext):
    if message.from_user and message.from_user.is_bot:
        return
    current = await state.get_state()
    if current:
        return
    lang = lang_for(message.from_user.id)
    app = get_application(message.from_user.id)
    data = get_form_data(message.from_user.id) or {}
    site_stage2 = is_site_quick_application(app, data)
    await send_or_edit_user_text(
        message.from_user.id,
        t(lang, "unknown_input_hint"),
        reply_markup=main_menu(
            lang,
            channel_url=stage2_channel_link(lang) if site_stage2 else None,
        ),
    )

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
    if STARFLOW_ENABLE_ADMIN_JOBS:
        await ensure_admin_menu_posted()
        tasks = [
            asyncio.create_task(daily_stats_task(), name="daily_stats_task"),
            asyncio.create_task(archive_admin_messages_task(), name="archive_admin_messages_task"),
            asyncio.create_task(auto_request_info_task(), name="auto_request_info_task"),
        ]
    else:
        logger.info("STARFLOW_ENABLE_ADMIN_JOBS=false: фоновые админ-джобы отключены")
        tasks = []
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
