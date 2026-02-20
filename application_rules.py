import re
from datetime import datetime

# Shared limits for Telegram + WhatsApp flows.
FORM_NAME_MAX_LEN = 64
FORM_CITY_MAX_LEN = 120
FORM_PHONE_MAX_LEN = 32
FORM_AGE_MAX_LEN = 16
FORM_DEVICE_MODEL_MAX_LEN = 80
FORM_WORK_TIME_MAX_LEN = 48
FORM_TELEGRAM_MAX_LEN = 64
FORM_EXPERIENCE_MAX_LEN = 700
FORM_YES_NO_MAX_LEN = 32
FORM_DEVICES_MAX_LEN = 140
FORM_HEADPHONES_MAX_LEN = 140
FORM_WA_TEXT_MAX_LEN = 700

_ZERO_WIDTH_RE = re.compile(r"[\u200b-\u200f\u202a-\u202e\u2060\ufeff\ufffd]")
_CONTROL_RE = re.compile(r"[\x00-\x1F\x7F]")
_SPACES_RE = re.compile(r"\s+")
_TG_USERNAME_RE = re.compile(r"[A-Za-z0-9_]{5,32}")

_YES_TOKENS = {
    "да",
    "есть",
    "имеется",
    "конечно",
    "ага",
    "y",
    "yes",
    "ok",
    "okay",
    "ок",
    "da",
    "sim",
    "si",
    "sí",
}
_NO_TOKENS = {"нет", "нету", "неа", "no", "n", "nao", "não"}


def clean_user_text(value: str | None, max_len: int | None = None) -> str:
    text = str(value or "")
    text = _ZERO_WIDTH_RE.sub("", text)
    text = _CONTROL_RE.sub(" ", text)
    text = _SPACES_RE.sub(" ", text).strip()
    if max_len is not None and max_len > 0 and len(text) > max_len:
        text = text[:max_len].rstrip()
    return text


def normalize_user_text_input(value: str | None, max_len: int) -> tuple[str, bool]:
    raw_clean = clean_user_text(value, max_len=None)
    if len(raw_clean) > max_len:
        return raw_clean[:max_len].rstrip(), True
    return raw_clean, False


def normalize_phone(text: str) -> str | None:
    value = re.sub(r"[()\s\-]+", "", str(text or "").strip())
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


def is_valid_phone(text: str) -> bool:
    normalized = normalize_phone(text)
    if not normalized:
        return False
    digits = re.sub(r"\D", "", normalized)
    return 10 <= len(digits) <= 15


def normalize_birthdate(text: str) -> str | None:
    value = str(text or "").strip()
    for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(value, fmt)
            if dt.year < 1900 or dt.date() > datetime.now().date():
                return None
            return dt.strftime("%d.%m.%Y")
        except ValueError:
            continue
    return None


def is_valid_birthdate(text: str, min_age: int = 18) -> bool:
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
    return age >= min_age


def has_any_digit(text: str) -> bool:
    return any(ch.isdigit() for ch in str(text or ""))


def normalize_yes_no(text: str) -> str | None:
    value = str(text or "").strip().lower()
    if not value:
        return None
    tokens = re.findall(r"[^\W\d_]+", value, flags=re.UNICODE)
    if not tokens:
        tokens = [value]
    for token in tokens:
        current = token.lower()
        if current in _YES_TOKENS:
            return "Да"
        if current in _NO_TOKENS:
            return "Нет"
    return None


def normalize_telegram(text: str) -> str | None:
    value = str(text or "").strip()
    lowered = value.lower()
    prefixes = (
        "https://t.me/",
        "http://t.me/",
        "t.me/",
        "https://telegram.me/",
        "http://telegram.me/",
        "telegram.me/",
    )
    for prefix in prefixes:
        if lowered.startswith(prefix):
            value = value[len(prefix):]
            break

    value = value.strip().lstrip("@").strip()
    if not value:
        return None

    # Keep only username-like part from links such as
    # `https://t.me/username/?start=abc`.
    value = value.split("?", 1)[0].split("#", 1)[0].strip("/")
    if "/" in value:
        value = value.split("/", 1)[0].strip()

    if _TG_USERNAME_RE.fullmatch(value):
        return f"@{value}"
    return None
