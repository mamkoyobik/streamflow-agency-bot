import os
from pathlib import Path
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()
else:
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            row = line.strip()
            if not row or row.startswith("#") or "=" not in row:
                continue
            key, value = row.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def _get_env(name: str, required: bool = True) -> str | None:
    value = os.getenv(name)
    if required and (value is None or value.strip() == ""):
        raise RuntimeError(f"❌ {name} не найден")
    return value


def _get_int_env(name: str, required: bool = True) -> int | None:
    value = _get_env(name, required=required)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"❌ {name} должен быть числом") from exc


def _get_int_env_any(names: tuple[str, ...], required: bool = False) -> int | None:
    for name in names:
        raw = os.getenv(name)
        if raw is None or raw.strip() == "":
            continue
        try:
            return int(raw)
        except ValueError as exc:
            raise RuntimeError(f"❌ {name} должен быть числом") from exc
    if required:
        joined = ", ".join(names)
        raise RuntimeError(f"❌ Не найдена ни одна переменная: {joined}")
    return None


def _dedupe_ids(values: list[int | None]) -> tuple[int, ...]:
    seen: set[int] = set()
    result: list[int] = []
    for value in values:
        if value is None or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return tuple(result)


BOT_TOKEN = _get_env("BOT_TOKEN", required=True)
ADMIN_GROUP_ID = _get_int_env("ADMIN_GROUP_ID", required=True)
CHANNEL_ID = _get_int_env("CHANNEL_ID", required=True)
CHANNEL_EN_ID = _get_int_env_any(
    (
        "CHANNEL_EN_ID",
        "CHANNEL_ID_EN",
        "EN_CHANNEL_ID",
        "CHANNEL_ENG_ID",
        "CHANNEL_EN",
        "CHANNEL_ENGLISH_ID",
    ),
    required=False,
)
CHANNEL_PT_ID = _get_int_env_any(
    (
        "CHANNEL_PT_ID",
        "CHANNEL_ID_PT",
        "PT_CHANNEL_ID",
        "CHANNEL_BR_ID",
        "CHANNEL_PT",
        "CHANNEL_PORTUGUESE_ID",
    ),
    required=False,
)
CHANNEL_ES_ID = _get_int_env_any(
    (
        "CHANNEL_ES_ID",
        "CHANNEL_ID_ES",
        "ES_CHANNEL_ID",
        "CHANNEL_SPANISH_ID",
        "CHANNEL_ES",
        "CHANNEL_LATAM_ID",
    ),
    required=False,
)
if CHANNEL_EN_ID is None:
    CHANNEL_EN_ID = -1003828410953
if CHANNEL_PT_ID is None:
    CHANNEL_PT_ID = -1003867037992
if CHANNEL_ES_ID is None:
    CHANNEL_ES_ID = -1003713812781
CHANNEL_ID_BY_LANG = {
    "ru": CHANNEL_ID,
    "en": CHANNEL_EN_ID,
    "pt": CHANNEL_PT_ID,
    "es": CHANNEL_ES_ID,
}
CHANNEL_IDS = _dedupe_ids([CHANNEL_ID, CHANNEL_EN_ID, CHANNEL_PT_ID, CHANNEL_ES_ID])
ADMIN_USERNAME = _get_env("ADMIN_USERNAME", required=True)
SITE_URL = (_get_env("SITE_URL", required=False) or "https://streamflowagency.com").strip().rstrip("/")
