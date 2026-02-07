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


BOT_TOKEN = _get_env("BOT_TOKEN", required=True)
ADMIN_GROUP_ID = _get_int_env("ADMIN_GROUP_ID", required=True)
CHANNEL_ID = _get_int_env("CHANNEL_ID", required=True)
ADMIN_USERNAME = _get_env("ADMIN_USERNAME", required=True)
