import json
import html
import os
import re
import ssl
import uuid
import hashlib
from functools import lru_cache
import urllib.parse
import urllib.request
import urllib.error
import time
from datetime import datetime, timezone, timedelta
from email.parser import BytesParser
from email.policy import default
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from database import save_web_application, get_status_counts, get_setting, set_setting
from texts import STATUS_LABELS
from time_utils import format_submit_time

ROOT_DIR = Path(__file__).parent
WEB_DIR = ROOT_DIR / "web"
ENV_PATH = ROOT_DIR / ".env"

MAX_BODY_SIZE = 30 * 1024 * 1024
ADMIN_MENU_SETTING_KEY = "admin_menu_message_id"
ADMIN_NOTIFY_SETTING_KEY = "admin_notify_message_id"
YES_RE = re.compile(
    r"\b(да|ага|есть|имеется|конечно|yes|y|da|ok|okay|si|sí|sim)\b",
    re.IGNORECASE,
)
NO_RE = re.compile(
    r"\b(нет|нету|неа|no|n|nao|não|nao)\b",
    re.IGNORECASE,
)

SUPPORTED_SITE_LANGS = {"ru", "en", "pt", "es"}
SITE_LEAD_TOKEN_PREFIX = "site_lead_token:"

def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default

SITE_LEAD_TOKEN_TTL_HOURS = max(24, _env_int("SITE_LEAD_TOKEN_TTL_HOURS", 72))


def _env_flag(name: str, default: bool = False) -> bool:
    raw = (os.getenv(name, "") or "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "y", "on"}


INFOBIP_FORWARD_TO_ADMIN = _env_flag("INFOBIP_FORWARD_TO_ADMIN", True)

FIELD_ERRORS = {
    "ru": {
        "name": "🤍 Имя должно быть чуть длиннее. Напиши, пожалуйста, полностью:",
        "city": "🤍 Подскажи город и страну проживания ещё раз:",
        "phone": "🤍 Кажется, номер введён некорректно. Пример: +7 900 000 00 00",
        "age": "🤍 Напиши дату рождения в формате 01.01.2000:",
        "yes_no": "🤍 Ответь, пожалуйста, «да» или «нет»:",
        "devices": "🤍 Уточни, пожалуйста, какие устройства есть:",
        "device_model": "🤍 Напиши модель устройства, пожалуйста:",
        "work_time": "🤍 Напиши, пожалуйста, количество часов цифрами (например: 6):",
        "telegram": "🤍 Укажи, пожалуйста, Telegram в формате @username:",
        "experience": "🤍 Напиши, пожалуйста, есть ли опыт:",
        "photo_face": "🤍 Здесь нужно отправить ФОТО АНФАС.",
        "photo_full": "🤍 Здесь нужно отправить ФОТО В ПОЛНЫЙ РОСТ.",
    },
    "en": {
        "name": "Please enter your full name.",
        "city": "Please enter your city and country.",
        "phone": "Phone number looks incorrect. Example: +1 555 123 4567",
        "age": "Please enter birth date as 01.01.2000",
        "yes_no": "Please answer yes or no.",
        "devices": "Please specify available devices.",
        "device_model": "Please enter your device model.",
        "work_time": "Please enter work hours as a number (example: 6).",
        "telegram": "Please enter Telegram as @username.",
        "experience": "Please tell us about your experience.",
        "photo_face": "Please upload a front-face photo.",
        "photo_full": "Please upload a full-body photo.",
    },
    "pt": {
        "name": "Digite seu nome completo.",
        "city": "Informe sua cidade e país.",
        "phone": "Telefone inválido. Exemplo: +55 11 99999 9999",
        "age": "Informe a data no formato 01.01.2000",
        "yes_no": "Responda sim ou não.",
        "devices": "Informe os dispositivos disponíveis.",
        "device_model": "Informe o modelo do dispositivo.",
        "work_time": "Informe as horas com número (ex.: 6).",
        "telegram": "Informe o Telegram no formato @username.",
        "experience": "Informe se você tem experiência.",
        "photo_face": "Envie a foto frontal.",
        "photo_full": "Envie a foto de corpo inteiro.",
    },
    "es": {
        "name": "Escribe tu nombre completo.",
        "city": "Indica ciudad y país.",
        "phone": "Número de teléfono inválido. Ejemplo: +34 600 000 000",
        "age": "Indica la fecha en formato 01.01.2000",
        "yes_no": "Responde sí o no.",
        "devices": "Indica qué dispositivos tienes.",
        "device_model": "Indica el modelo del dispositivo.",
        "work_time": "Indica horas con número (ej.: 6).",
        "telegram": "Indica Telegram en formato @username.",
        "experience": "Indica si tienes experiencia.",
        "photo_face": "Sube una foto frontal.",
        "photo_full": "Sube una foto de cuerpo completo.",
    },
}

GENERAL_MESSAGES = {
    "ru": {
        "bad_size": "Некорректный размер запроса.",
        "too_big": "Файлы слишком большие.",
        "bad_type": "Неверный тип данных.",
        "send_error": "Ошибка отправки анкеты. Попробуй ещё раз.",
        "group_not_found": "Бот не видит админ‑группу. Проверь ADMIN_GROUP_ID и что бот добавлен в группу.",
        "group_no_rights": "Бот без прав отправки в группу. Добавь бота и выдай права.",
        "photo_too_big": "Фото слишком большое. Пришли файл меньше 10 МБ.",
        "token_missing": "Не настроен BOT_TOKEN или ADMIN_GROUP_ID.",
        "db_error": "Ошибка сохранения анкеты. Попробуй ещё раз.",
        "success": "✅ Заявка отправлена. Дальнейшие действия перейдут в Telegram.",
    },
    "en": {
        "bad_size": "Invalid request size.",
        "too_big": "Files are too large.",
        "bad_type": "Unsupported payload type.",
        "send_error": "Failed to send application. Please try again.",
        "group_not_found": "Bot cannot reach admin group. Check ADMIN_GROUP_ID and bot membership.",
        "group_no_rights": "Bot has no permission to post in admin group.",
        "photo_too_big": "Photo is too large. Please upload under 10MB.",
        "token_missing": "BOT_TOKEN or ADMIN_GROUP_ID is not configured.",
        "db_error": "Failed to save application. Please try again.",
        "success": "✅ Application sent. Next steps continue in Telegram.",
    },
    "pt": {
        "bad_size": "Tamanho da requisição inválido.",
        "too_big": "Arquivos muito grandes.",
        "bad_type": "Tipo de dados não suportado.",
        "send_error": "Falha ao enviar candidatura. Tente novamente.",
        "group_not_found": "O bot não alcança o grupo admin. Verifique ADMIN_GROUP_ID.",
        "group_no_rights": "O bot não tem permissão para enviar no grupo admin.",
        "photo_too_big": "Foto muito grande. Envie arquivo menor que 10MB.",
        "token_missing": "BOT_TOKEN ou ADMIN_GROUP_ID não configurado.",
        "db_error": "Falha ao salvar candidatura. Tente novamente.",
        "success": "✅ Cadastro enviado. Próximos passos no Telegram.",
    },
    "es": {
        "bad_size": "Tamaño de solicitud inválido.",
        "too_big": "Los archivos son demasiado grandes.",
        "bad_type": "Tipo de datos no soportado.",
        "send_error": "Error al enviar la solicitud. Inténtalo de nuevo.",
        "group_not_found": "El bot no puede llegar al grupo admin. Revisa ADMIN_GROUP_ID.",
        "group_no_rights": "El bot no tiene permisos para enviar en el grupo admin.",
        "photo_too_big": "La foto es demasiado grande. Sube un archivo menor de 10MB.",
        "token_missing": "BOT_TOKEN o ADMIN_GROUP_ID no están configurados.",
        "db_error": "Error al guardar la solicitud. Inténtalo de nuevo.",
        "success": "✅ Solicitud enviada. Los siguientes pasos van por Telegram.",
    },
}


def normalize_site_lang(value: str | None) -> str:
    raw = (value or "").strip().lower()
    return raw if raw in SUPPORTED_SITE_LANGS else "ru"


def msg(lang: str, key: str) -> str:
    locale = normalize_site_lang(lang)
    return GENERAL_MESSAGES.get(locale, GENERAL_MESSAGES["ru"]).get(key, GENERAL_MESSAGES["ru"][key])


def field_error(lang: str, key: str) -> str:
    locale = normalize_site_lang(lang)
    return FIELD_ERRORS.get(locale, FIELD_ERRORS["ru"]).get(key, FIELD_ERRORS["ru"].get(key, ""))


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_settings():
    load_env_file(ENV_PATH)
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    admin_group_id = os.getenv("ADMIN_GROUP_ID", "").strip()
    admin_username = os.getenv("ADMIN_USERNAME", "").strip()
    bot_username = os.getenv("BOT_USERNAME", "StreamFlowAgencybot").strip()
    channel_link = os.getenv("CHANNEL_LINK", "https://t.me/streamflowagency").strip()
    site_url = (os.getenv("SITE_URL", "https://streamflowagency.com") or "https://streamflowagency.com").strip()
    return bot_token, admin_group_id, admin_username, bot_username, channel_link, site_url


BOT_TOKEN, ADMIN_GROUP_ID, ADMIN_USERNAME, BOT_USERNAME, CHANNEL_LINK, SITE_URL = load_settings()
SITE_URL = SITE_URL.rstrip("/")
CANONICAL_HOST = (urllib.parse.urlparse(SITE_URL).netloc or "").split(":", 1)[0].lower()

def site_lead_setting_key(token: str) -> str:
    return f"{SITE_LEAD_TOKEN_PREFIX}{token}"

def save_site_lead_payload(token: str, payload: dict) -> None:
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=SITE_LEAD_TOKEN_TTL_HOURS)).isoformat()
    data = {
        "expires_at": expires_at,
        "data": payload,
    }
    set_setting(site_lead_setting_key(token), json.dumps(data, ensure_ascii=False))

def build_bot_stage2_link(token: str, lang: str | None = None) -> str | None:
    username = (BOT_USERNAME or "").strip().lstrip("@")
    if not username:
        return None
    locale = normalize_site_lang(lang)
    return f"https://t.me/{username}?start=s2_{token}_{locale}"
try:
    from excel_export import append_application_row
except Exception:
    append_application_row = None
try:
    import certifi
except Exception:
    certifi = None


@lru_cache(maxsize=1)
def get_ssl_context():
    disable_verify = os.getenv("SSL_NO_VERIFY", "").strip().lower() in {"1", "true", "yes"}
    if disable_verify:
        return ssl._create_unverified_context()
    cert_file = os.getenv("SSL_CERT_FILE", "").strip()
    cert_dir = os.getenv("SSL_CERT_DIR", "").strip()
    if cert_file:
        if Path(cert_file).exists():
            return ssl.create_default_context(cafile=cert_file)
        print(f"SSL_CERT_FILE not found: {cert_file}")
    context = ssl.create_default_context()
    if cert_dir:
        if Path(cert_dir).exists():
            context.load_verify_locations(capath=cert_dir)
            return context
        print(f"SSL_CERT_DIR not found: {cert_dir}")
    if certifi:
        return ssl.create_default_context(cafile=certifi.where())
    return context


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


PHONE_COUNTRY_BY_CODE = {
    "1": "United States/Canada",
    "7": "Russia/Kazakhstan",
    "34": "Spain",
    "44": "United Kingdom",
    "51": "Peru",
    "52": "Mexico",
    "53": "Cuba",
    "54": "Argentina",
    "55": "Brazil",
    "56": "Chile",
    "57": "Colombia",
    "58": "Venezuela",
    "63": "Philippines",
    "351": "Portugal",
    "380": "Ukraine",
    "381": "Serbia",
    "420": "Czech Republic",
    "421": "Slovakia",
    "591": "Bolivia",
    "592": "Guyana",
    "593": "Ecuador",
    "594": "French Guiana",
    "595": "Paraguay",
    "597": "Suriname",
    "598": "Uruguay",
    "994": "Azerbaijan",
    "995": "Georgia",
    "996": "Kyrgyzstan",
    "998": "Uzbekistan",
}
PHONE_COUNTRY_CODES_SORTED = sorted(PHONE_COUNTRY_BY_CODE.keys(), key=len, reverse=True)


def extract_country_from_phone(phone: str | None) -> str | None:
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

def clean_text(value: str) -> str:
    text = value or ""
    text = re.sub(r"[\u200b-\u200f\u202a-\u202e\u2060\ufeff\ufffd]", "", text)
    text = re.sub(r"[\x00-\x1F\x7F]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


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


def normalize_yes_no(text: str) -> str | None:
    value = text.strip().lower()
    if not value:
        return None
    if YES_RE.search(value):
        return "Да"
    if NO_RE.search(value):
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


def _safe(value: str | None) -> str:
    return html.escape(str(value)) if value is not None else "—"


def _shorten(text: str, max_len: int = 3200) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def _pick_first_string(*values) -> str | None:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned:
                return cleaned
            continue
        if isinstance(value, (int, float)):
            return str(value)
    return None


def _wa_open_link(phone: str | None) -> str | None:
    digits = re.sub(r"\D", "", phone or "")
    if not digits:
        return None
    return f"https://wa.me/{digits}"


def _extract_infobip_messages(payload: dict | None) -> list[dict]:
    if not isinstance(payload, dict):
        return []

    candidates: list[dict] = []
    for key in ("results", "messages", "items", "data"):
        items = payload.get(key)
        if isinstance(items, list):
            candidates.extend([row for row in items if isinstance(row, dict)])

    if not candidates and any(k in payload for k in ("from", "message", "text", "content", "messageId")):
        candidates.append(payload)

    normalized: list[dict] = []
    for row in candidates:
        message = row.get("message") if isinstance(row.get("message"), dict) else {}
        content = row.get("content") if isinstance(row.get("content"), dict) else {}
        contact = row.get("contact") if isinstance(row.get("contact"), dict) else {}
        sender = row.get("sender") if isinstance(row.get("sender"), dict) else {}
        contact_profile = contact.get("profile") if isinstance(contact.get("profile"), dict) else {}

        from_phone = _pick_first_string(
            row.get("from"),
            sender.get("phoneNumber"),
            sender.get("from"),
            contact.get("phoneNumber"),
            contact.get("waId"),
            row.get("senderAddress"),
        )
        to_phone = _pick_first_string(
            row.get("to"),
            row.get("destination"),
            row.get("toNumber"),
            row.get("recipient"),
        )
        msg_type = _pick_first_string(
            message.get("type"),
            content.get("type"),
            row.get("type"),
        )
        text = _pick_first_string(
            message.get("text"),
            content.get("text"),
            row.get("text"),
            row.get("body"),
        )
        media_url = _pick_first_string(
            message.get("url"),
            content.get("url"),
            row.get("url"),
        )
        profile_name = _pick_first_string(
            contact.get("name"),
            contact.get("firstName"),
            contact.get("profileName"),
            contact_profile.get("name"),
        )
        message_id = _pick_first_string(
            row.get("messageId"),
            message.get("id"),
            row.get("id"),
        )
        received_at = _pick_first_string(
            row.get("receivedAt"),
            row.get("timestamp"),
            row.get("time"),
        )
        if not any((from_phone, to_phone, text, media_url, message_id)):
            continue
        normalized.append(
            {
                "from": from_phone,
                "to": to_phone,
                "type": (msg_type or "TEXT").upper(),
                "text": text,
                "media_url": media_url,
                "profile_name": profile_name,
                "message_id": message_id,
                "received_at": received_at,
                "raw": row,
            }
        )
    return normalized


def _infobip_dedupe_key(message: dict) -> str:
    signature = (
        message.get("message_id")
        or f"{message.get('from')}|{message.get('to')}|{message.get('type')}|{message.get('text')}|{message.get('received_at')}"
    )
    digest = hashlib.sha1(str(signature).encode("utf-8")).hexdigest()[:20]
    return f"infobip_seen:{digest}"


def _mark_infobip_seen(message: dict) -> bool:
    key = _infobip_dedupe_key(message)
    exists = get_setting(key)
    if exists:
        return True
    set_setting(key, datetime.now(timezone.utc).isoformat())
    return False


def _format_infobip_forward_text(message: dict) -> str:
    message_type = (message.get("type") or "TEXT").upper()
    text = (message.get("text") or "").strip()
    media_url = (message.get("media_url") or "").strip()
    if text:
        body = _shorten(text, 2500)
    elif media_url:
        body = f"[{message_type}] {media_url}"
    else:
        body = f"[{message_type}]"
    return (
        "🟢 <b>WhatsApp: новое входящее сообщение</b>\n\n"
        f"👤 Имя: <b>{_safe(message.get('profile_name'))}</b>\n"
        f"📱 От: <code>{_safe(message.get('from'))}</code>\n"
        f"📨 На: <code>{_safe(message.get('to'))}</code>\n"
        f"🆔 ID: <code>{_safe(message.get('message_id'))}</code>\n"
        f"🕒 Время: {_safe(message.get('received_at'))}\n\n"
        f"💬 {_safe(body)}"
    )


def _forward_infobip_message_to_admin(message: dict) -> None:
    if not BOT_TOKEN or not ADMIN_GROUP_ID:
        return
    text = _format_infobip_forward_text(message)
    wa_link = _wa_open_link(message.get("from"))
    payload = {
        "chat_id": str(ADMIN_GROUP_ID),
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }
    if wa_link:
        payload["reply_markup"] = json.dumps(
            {
                "inline_keyboard": [
                    [{"text": "💬 Открыть чат WhatsApp", "url": wa_link}],
                ]
            },
            ensure_ascii=False,
        )
    telegram_request("sendMessage", payload)

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

def submission_country(data: dict) -> str:
    explicit = str(data.get("country") or "").strip()
    if explicit:
        return explicit
    derived = extract_country_from_location(str(data.get("city") or ""))
    if derived:
        return derived
    by_phone = extract_country_from_phone(str(data.get("phone") or ""))
    if by_phone:
        return by_phone
    return "—"

def build_admin_full_text(data: dict, web_id: str, submitted_at: str) -> str:
    status_label = STATUS_LABELS.get("pending", "🟡 На рассмотрении")
    return (
        "📋 <b>Полная анкета</b>\n\n"
        f"👤 Имя: {_safe(data.get('name'))}\n"
        f"📅 Дата рождения: {_safe(data.get('age'))}\n"
        f"🌍 Город и страна: {_safe(data.get('city'))}\n"
        f"🏳️ Страна подачи: {_safe(submission_country(data))}\n"
        f"📞 Телефон: {_safe(data.get('phone'))}\n"
        f"🏠 Помещение без посторонних: {_safe(data.get('living'))}\n"
        f"📱 Устройства: {_safe(data.get('devices'))}\n"
        f"📲 Модель: {_safe(data.get('device_model'))}\n"
        f"🎧 Наушники: {_safe(data.get('headphones'))}\n"
        f"⏱ Время работы: {_safe(data.get('work_time'))}\n"
        f"💼 Опыт: {_safe(data.get('experience'))}\n"
        f"💬 Telegram: {_safe(data.get('telegram'))}\n"
        f"🆔 ID: {_safe(web_id)}\n"
        "🧭 Источник: Сайт\n"
        f"🕒 Время подачи: {submitted_at}\n\n"
        f"Статус: <b>{status_label}</b>"
    )

def build_admin_menu_text(counts: dict) -> str:
    return (
        "🛠 <b>Админ-меню</b>\n\n"
        "Зоны:\n"
        "• Контент\n"
        "• Заявки\n"
        "• Аналитика\n"
        "• Сервис\n\n"
        f"Ожидают подтверждения: <b>{counts.get('pending', 0)}</b>\n"
        f"Принятые: <b>{counts.get('accepted', 0)}</b>\n"
        f"Отклонённые: <b>{counts.get('rejected', 0)}</b>\n\n"
        "Выбери раздел ниже ✨"
    )

def build_admin_menu_keyboard(counts: dict) -> dict:
    pending = counts.get("pending", 0)
    return {
        "inline_keyboard": [
            [
                {"text": "🗂 Контент", "callback_data": "admin_menu:cat_content"},
                {"text": f"📥 Заявки ({pending})", "callback_data": "admin_menu:cat_apps"},
            ],
            [
                {"text": "📊 Аналитика", "callback_data": "admin_menu:cat_analytics"},
                {"text": "⚙️ Сервис", "callback_data": "admin_menu:cat_service"},
            ],
            [
                {"text": "🔄 Обновить", "callback_data": "admin_menu:refresh"},
            ],
        ]
    }

def notify_admin_new_application():
    counts = get_status_counts()
    text = (
        "🔔 <b>Новая анкета</b>\n\n"
        f"Ожидают подтверждения: <b>{counts.get('pending', 0)}</b>\n"
        "Открой админ-меню, чтобы просмотреть ✨"
    )
    stored_id = get_setting(ADMIN_NOTIFY_SETTING_KEY)
    if stored_id and str(stored_id).isdigit():
        try:
            telegram_request("deleteMessage", {"chat_id": str(ADMIN_GROUP_ID), "message_id": int(stored_id)})
        except Exception:
            pass
    try:
        result = telegram_request(
            "sendMessage",
            {
                "chat_id": str(ADMIN_GROUP_ID),
                "text": text,
                "parse_mode": "HTML",
            },
        )
        msg_id = result.get("result", {}).get("message_id")
        if msg_id:
            set_setting(ADMIN_NOTIFY_SETTING_KEY, str(msg_id))
    except Exception:
        pass

def update_admin_menu_message():
    counts = get_status_counts()
    text = build_admin_menu_text(counts)
    markup = build_admin_menu_keyboard(counts)
    stored_id = get_setting(ADMIN_MENU_SETTING_KEY)
    if stored_id and str(stored_id).isdigit():
        try:
            telegram_request(
                "editMessageText",
                {
                    "chat_id": str(ADMIN_GROUP_ID),
                    "message_id": int(stored_id),
                    "text": text,
                    "parse_mode": "HTML",
                    "reply_markup": json.dumps(markup, ensure_ascii=False),
                },
            )
            return
        except Exception as err:
            payload = err.args[0] if err.args else {}
            description = ""
            if isinstance(payload, dict):
                description = str(payload.get("description", "")).lower()
            else:
                description = str(payload).lower()
            if "message is not modified" in description:
                return
    try:
        result = telegram_request(
            "sendMessage",
            {
                "chat_id": str(ADMIN_GROUP_ID),
                "text": text,
                "parse_mode": "HTML",
                "reply_markup": json.dumps(markup, ensure_ascii=False),
            },
        )
        msg_id = result.get("result", {}).get("message_id")
        if msg_id:
            set_setting(ADMIN_MENU_SETTING_KEY, str(msg_id))
    except Exception:
        pass


def build_multipart(fields: dict, files: dict):
    boundary = uuid.uuid4().hex
    body = bytearray()

    def add_line(line: str = ""):
        body.extend(line.encode("utf-8"))
        body.extend(b"\r\n")

    for name, value in fields.items():
        add_line(f"--{boundary}")
        add_line(f"Content-Disposition: form-data; name=\"{name}\"")
        add_line()
        add_line(str(value))

    for name, file_info in files.items():
        filename = file_info["filename"]
        content_type = file_info.get("content_type") or "application/octet-stream"
        data = file_info["data"]
        add_line(f"--{boundary}")
        add_line(f"Content-Disposition: form-data; name=\"{name}\"; filename=\"{filename}\"")
        add_line(f"Content-Type: {content_type}")
        add_line()
        body.extend(data)
        body.extend(b"\r\n")

    add_line(f"--{boundary}--")
    return boundary, bytes(body)


def telegram_request(method: str, data: dict, files: dict | None = None):
    if not BOT_TOKEN or not ADMIN_GROUP_ID:
        raise RuntimeError({"description": "BOT_TOKEN или ADMIN_GROUP_ID не заданы"})
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"

    if files:
        boundary, body = build_multipart(data, files)
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    else:
        body = urllib.parse.urlencode(data).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20, context=get_ssl_context()) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        try:
            payload = json.loads(err.read().decode("utf-8"))
        except Exception:
            payload = {"description": f"HTTP {err.code}"}
        raise RuntimeError(payload)
    if not payload.get("ok"):
        raise RuntimeError(payload)
    return payload


def parse_multipart(body: bytes, content_type: str):
    header = f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n"
    msg = BytesParser(policy=default).parsebytes(header.encode("utf-8") + body)
    fields: dict[str, str] = {}
    files: dict[str, dict] = {}
    for part in msg.iter_parts():
        if part.get_content_disposition() != "form-data":
            continue
        name = part.get_param("name", header="content-disposition")
        if not name:
            continue
        filename = part.get_filename()
        if filename:
            files[name] = {
                "filename": filename,
                "content_type": part.get_content_type(),
                "data": part.get_payload(decode=True) or b"",
            }
        else:
            raw = part.get_payload(decode=True)
            if raw is None:
                raw = b""
            charset = part.get_content_charset() or "utf-8"
            value = ""
            if isinstance(raw, (bytes, bytearray)):
                # Prefer utf-8/cp1251 first to avoid mojibake when browser sends wrong charset.
                for enc in ("utf-8", "cp1251", charset, "latin-1"):
                    if not enc:
                        continue
                    try:
                        value = raw.decode(enc, errors="strict")
                        break
                    except Exception:
                        value = ""
                if not value:
                    value = raw.decode("utf-8", errors="replace")
            else:
                value = str(raw)
            fields[name] = value.strip()
    return fields, files


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        proto = (self.headers.get("X-Forwarded-Proto") or "").strip().lower()
        if proto == "https":
            self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")
        # Keep HTML always fresh after deploys; static assets are versioned in URLs.
        path = urllib.parse.urlparse(self.path).path.lower()
        if path.endswith(".html") or path in {"", "/"}:
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
        else:
            self.send_header("Cache-Control", "public, max-age=3600")
        super().end_headers()

    def copyfile(self, source, outputfile):
        try:
            super().copyfile(source, outputfile)
        except BrokenPipeError:
            # Client closed connection early (browser navigation/refresh).
            pass

    def _host_header(self) -> str:
        return (self.headers.get("Host") or "").split(":", 1)[0].strip().lower()

    def _should_redirect_to_canonical(self) -> bool:
        if not CANONICAL_HOST:
            return False
        host = self._host_header()
        if not host:
            return False
        if host == CANONICAL_HOST:
            return False
        if host in {"127.0.0.1", "localhost"}:
            return False
        if host.endswith(".railway.internal"):
            return False
        return True

    def _redirect_canonical(self):
        target = f"{SITE_URL}{self.path}"
        self.send_response(301)
        self.send_header("Location", target)
        self.end_headers()

    def do_HEAD(self):
        if self._should_redirect_to_canonical():
            return self._redirect_canonical()
        return super().do_HEAD()

    def do_GET(self):
        if self._should_redirect_to_canonical():
            return self._redirect_canonical()
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/config":
            return self.handle_config()
        if parsed.path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/apply":
            self.handle_apply()
            return
        if parsed.path == "/api/infobip/webhook":
            self.handle_infobip_webhook()
            return
        self.send_error(404)

    def handle_config(self):
        admin_username = ADMIN_USERNAME.lstrip("@")
        bot_username = BOT_USERNAME.strip().lstrip("@")
        bot_link = f"https://t.me/{bot_username}" if bot_username else None
        payload = {
            "telegram_link": CHANNEL_LINK or (f"https://t.me/{admin_username}" if admin_username else None),
            "bot_link": bot_link,
            "site_url": SITE_URL,
        }
        self.send_json(payload)

    def handle_apply(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self.send_json({"ok": False, "message": msg("ru", "bad_size")}, status=400)
        if content_length > MAX_BODY_SIZE:
            return self.send_json({"ok": False, "message": msg("ru", "too_big")}, status=413)

        body = self.rfile.read(content_length)
        content_type = self.headers.get("Content-Type", "")

        if content_type.startswith("multipart/form-data"):
            fields, _files = parse_multipart(body, content_type)
        elif content_type.startswith("application/x-www-form-urlencoded"):
            data = urllib.parse.parse_qs(body.decode("utf-8"))
            fields = {k: v[0] for k, v in data.items()}
        else:
            return self.send_json({"ok": False, "message": msg("ru", "bad_type")}, status=400)

        site_lang = normalize_site_lang(fields.get("site_lang"))

        def error(message: str, status: int = 400, field: str | None = None):
            payload = {"ok": False, "message": message}
            if field:
                payload["field"] = field
            return self.send_json(payload, status=status)

        name = clean_text(fields.get("name") or "")
        if len(name) < 2:
            return error(field_error(site_lang, "name"), field="name")

        phone_raw = clean_text(fields.get("phone") or "")
        if not is_valid_phone(phone_raw):
            return error(field_error(site_lang, "phone"), field="phone")
        phone = normalize_phone(phone_raw) or phone_raw

        age_raw = clean_text(fields.get("age") or "")
        if not is_valid_birthdate(age_raw):
            return error(field_error(site_lang, "age"), field="age")
        age = normalize_birthdate(age_raw) or age_raw

        device_model = clean_text(fields.get("device_model") or "")
        if len(device_model) < 2:
            return error(field_error(site_lang, "device_model"), field="device_model")

        telegram_raw = clean_text(fields.get("telegram") or "")
        telegram = normalize_telegram(telegram_raw)
        if not telegram:
            return error(field_error(site_lang, "telegram"), field="telegram")

        country = clean_text(fields.get("country") or "")
        if not country:
            country = (
                extract_country_from_location(clean_text(fields.get("city") or ""))
                or extract_country_from_phone(phone)
                or ""
            )

        user_id = -int(time.time_ns())
        lead_token = uuid.uuid4().hex[:24]
        payload = {
            "name": name,
            "lang": site_lang,
            "phone": phone,
            "age": age,
            "device_model": device_model,
            "telegram": telegram,
            "country": country,
            "application_stage": "quick",
            "site_lead_token": lead_token,
            "site_pending_user_id": user_id,
        }

        try:
            save_site_lead_payload(lead_token, payload)
            save_web_application(user_id, payload, source="site", status="pending")
            if append_application_row:
                try:
                    append_application_row(payload, user_id, "pending")
                except Exception as err:
                    print("Excel error:", err)
        except Exception as err:
            print("DB error:", err)
            return error(msg(site_lang, "db_error"), status=500)

        notify_admin_new_application()
        update_admin_menu_message()

        bot_link = build_bot_stage2_link(lead_token, site_lang)
        return self.send_json(
            {
                "ok": True,
                "message": msg(site_lang, "success"),
                "bot_link": bot_link or CHANNEL_LINK,
            }
        )

    def handle_infobip_webhook(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0
        if content_length > MAX_BODY_SIZE:
            return self.send_json({"ok": False, "message": "payload too large"}, status=413)

        body = self.rfile.read(content_length) if content_length > 0 else b""
        content_type = (self.headers.get("Content-Type", "") or "").lower()

        payload: dict | None = None
        try:
            if "application/json" in content_type:
                payload = json.loads(body.decode("utf-8") or "{}")
            elif "application/x-www-form-urlencoded" in content_type:
                parsed = urllib.parse.parse_qs(body.decode("utf-8"), keep_blank_values=True)
                payload = {k: (v[0] if isinstance(v, list) and len(v) == 1 else v) for k, v in parsed.items()}
            else:
                decoded = body.decode("utf-8", errors="replace")
                payload = {"raw": decoded}
        except Exception:
            payload = {"raw": body.decode("utf-8", errors="replace")}

        forwarded = 0
        duplicates = 0
        errors = 0
        try:
            messages = _extract_infobip_messages(payload)
            if INFOBIP_FORWARD_TO_ADMIN:
                for message in messages:
                    if _mark_infobip_seen(message):
                        duplicates += 1
                        continue
                    try:
                        _forward_infobip_message_to_admin(message)
                        forwarded += 1
                    except Exception as err:
                        errors += 1
                        print("Failed to forward infobip message to admin:", err)
        except Exception as err:
            print("Failed to parse infobip webhook payload:", err)

        try:
            set_setting(
                "infobip_last_webhook",
                json.dumps(
                    {
                        "received_at": datetime.now(timezone.utc).isoformat(),
                        "payload": payload,
                        "forwarded": forwarded,
                        "duplicates": duplicates,
                        "errors": errors,
                        "headers": {
                            "Content-Type": self.headers.get("Content-Type", ""),
                            "User-Agent": self.headers.get("User-Agent", ""),
                        },
                    },
                    ensure_ascii=False,
                ),
            )
        except Exception as err:
            print("Failed to store infobip webhook payload:", err)

        return self.send_json(
            {
                "ok": True,
                "forwarded": forwarded,
                "duplicates": duplicates,
                "errors": errors,
            }
        )

    def send_json(self, payload: dict, status: int = 200):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    host = os.getenv("HOST", "").strip()
    railway_runtime = bool(
        os.getenv("RAILWAY_ENVIRONMENT")
        or os.getenv("RAILWAY_PROJECT_ID")
        or os.getenv("RAILWAY_PUBLIC_DOMAIN")
    )
    if not host:
        host = "0.0.0.0"
    # Railway requires binding to 0.0.0.0, localhost causes 502.
    if railway_runtime and host in {"127.0.0.1", "localhost"}:
        host = "0.0.0.0"
    port = int(os.getenv("PORT", "8080"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Running on http://{host}:{port}")
    server.serve_forever()
