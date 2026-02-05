import json
import os
import re
import uuid
import urllib.parse
import urllib.request
from datetime import datetime
from email.parser import BytesParser
from email.policy import default
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from database import set_form_data, set_last_apply_at, set_source, set_status
from texts import STATUS_LABELS

ROOT_DIR = Path(__file__).parent
WEB_DIR = ROOT_DIR / "web"
ENV_PATH = ROOT_DIR / ".env"

MAX_BODY_SIZE = 30 * 1024 * 1024


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
    bot_username = os.getenv("BOT_USERNAME", "").strip()
    channel_link = os.getenv("CHANNEL_LINK", "https://t.me/+uuVr5gJFwoJjYmRi").strip()
    return bot_token, admin_group_id, admin_username, bot_username, channel_link


BOT_TOKEN, ADMIN_GROUP_ID, ADMIN_USERNAME, BOT_USERNAME, CHANNEL_LINK = load_settings()


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


def build_admin_full_text(data: dict, web_id: str) -> str:
    status_label = STATUS_LABELS.get("pending", "🟡 На рассмотрении")
    return (
        "📋 <b>Полная анкета</b>\n\n"
        f"👤 Имя: {data.get('name', '—')}\n"
        f"📅 Дата рождения: {data.get('age', '—')}\n"
        f"🌍 Город и страна: {data.get('city', '—')}\n"
        f"📞 Телефон: {data.get('phone', '—')}\n"
        f"🏠 Помещение без посторонних: {data.get('living', '—')}\n"
        f"📱 Устройства: {data.get('devices', '—')}\n"
        f"📲 Модель: {data.get('device_model', '—')}\n"
        f"🎧 Наушники: {data.get('headphones', '—')}\n"
        f"⏱ Время работы: {data.get('work_time', '—')}\n"
        f"💼 Опыт: {data.get('experience', '—')}\n"
        f"💬 Telegram: {data.get('telegram', '—')}\n"
        f"🆔 ID: {web_id}\n"
        "🧭 Источник: Сайт\n\n"
        f"Статус: <b>{status_label}</b>"
    )


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
        raise RuntimeError("BOT_TOKEN или ADMIN_GROUP_ID не заданы")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"

    if files:
        boundary, body = build_multipart(data, files)
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    else:
        body = urllib.parse.urlencode(data).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
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
            value = part.get_content()
            fields[name] = value.strip() if isinstance(value, str) else ""
    return fields, files


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/config":
            return self.handle_config()
        if parsed.path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/api/apply":
            self.send_error(404)
            return
        self.handle_apply()

    def handle_config(self):
        admin_username = ADMIN_USERNAME.lstrip("@")
        bot_username = BOT_USERNAME.strip().lstrip("@")
        bot_link = f"https://t.me/{bot_username}" if bot_username else None
        payload = {
            "telegram_link": CHANNEL_LINK or (f"https://t.me/{admin_username}" if admin_username else None),
            "bot_link": bot_link,
        }
        self.send_json(payload)

    def handle_apply(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length > MAX_BODY_SIZE:
            return self.send_json({"ok": False, "message": "Файлы слишком большие."}, status=413)

        body = self.rfile.read(content_length)
        content_type = self.headers.get("Content-Type", "")

        if content_type.startswith("multipart/form-data"):
            fields, files = parse_multipart(body, content_type)
        elif content_type.startswith("application/x-www-form-urlencoded"):
            data = urllib.parse.parse_qs(body.decode("utf-8"))
            fields = {k: v[0] for k, v in data.items()}
            files = {}
        else:
            return self.send_json({"ok": False, "message": "Неверный тип данных."}, status=400)

        def error(message: str, status: int = 400, field: str | None = None):
            payload = {"ok": False, "message": message}
            if field:
                payload["field"] = field
            return self.send_json(payload, status=status)

        name = (fields.get("name") or "").strip()
        if len(name) < 2:
            return error("🤍 Имя должно быть чуть длиннее. Напиши, пожалуйста, полностью:", field="name")

        city = (fields.get("city") or "").strip()
        if len(city) < 2:
            return error("🤍 Подскажи город и страну проживания ещё раз:", field="city")

        phone_raw = (fields.get("phone") or "").strip()
        if not is_valid_phone(phone_raw):
            return error("🤍 Кажется, номер введён некорректно. Пример: +7 900 000 00 00", field="phone")
        phone = normalize_phone(phone_raw) or phone_raw

        age_raw = (fields.get("age") or "").strip()
        if not is_valid_birthdate(age_raw):
            return error("🤍 Напиши дату рождения в формате 01.01.2000:", field="age")
        age = normalize_birthdate(age_raw) or age_raw

        living_raw = (fields.get("living") or "").strip()
        living = normalize_yes_no(living_raw)
        if not living:
            return error("🤍 Ответь, пожалуйста, «да» или «нет»:", field="living")

        devices = (fields.get("devices") or "").strip()
        if len(devices) < 2:
            return error("🤍 Уточни, пожалуйста, какие устройства есть:", field="devices")

        device_model = (fields.get("device_model") or "").strip()
        if len(device_model) < 2:
            return error("🤍 Напиши модель устройства, пожалуйста:", field="device_model")

        work_time = (fields.get("work_time") or "").strip()
        if not has_any_digit(work_time):
            return error("🤍 Напиши, пожалуйста, количество часов цифрами (например: 6):", field="work_time")

        headphones = (fields.get("headphones") or "").strip()
        if len(headphones) < 2:
            return error("🤍 Подскажи, пожалуйста, есть ли наушники с микрофоном:", field="headphones")

        telegram_raw = (fields.get("telegram") or "").strip()
        telegram = normalize_telegram(telegram_raw)
        if not telegram:
            return error("🤍 Укажи, пожалуйста, Telegram в формате @username:", field="telegram")

        experience = (fields.get("experience") or "").strip()
        if len(experience) < 1:
            return error("🤍 Напиши, пожалуйста, есть ли опыт:", field="experience")

        photo_face = files.get("photo_face")
        if not photo_face or not photo_face.get("data"):
            return error("🤍 Здесь нужно отправить <b>ФОТО АНФАС</b>.\n\n📷 Пришли фотографию, пожалуйста", field="photo_face")

        photo_full = files.get("photo_full")
        if not photo_full or not photo_full.get("data"):
            return error("🤍 Здесь нужно отправить <b>ФОТО В ПОЛНЫЙ РОСТ</b>.\n\n📷 Пришли фотографию, пожалуйста", field="photo_full")

        payload = {
            "name": name,
            "city": city,
            "phone": phone,
            "age": age,
            "living": living,
            "devices": devices,
            "device_model": device_model,
            "work_time": work_time,
            "headphones": headphones,
            "telegram": telegram,
            "experience": experience,
        }

        user_id = -int(datetime.now().timestamp() * 1000)
        web_id = str(user_id)

        try:
            telegram_request(
                "sendMessage",
                {
                    "chat_id": str(ADMIN_GROUP_ID),
                    "text": build_admin_full_text(payload, web_id),
                    "parse_mode": "HTML",
                },
            )

            face_result = telegram_request(
                "sendPhoto",
                {
                    "chat_id": str(ADMIN_GROUP_ID),
                    "caption": "1️⃣2️⃣ Фото анфас:",
                    "parse_mode": "HTML",
                },
                {
                    "photo": photo_face,
                },
            )

            full_result = telegram_request(
                "sendPhoto",
                {
                    "chat_id": str(ADMIN_GROUP_ID),
                    "caption": "1️⃣3️⃣ Фото в полный рост:",
                    "parse_mode": "HTML",
                },
                {
                    "photo": photo_full,
                },
            )

            try:
                payload["photo_face"] = face_result["result"]["photo"][-1]["file_id"]
            except Exception:
                payload["photo_face"] = None
            try:
                payload["photo_full"] = full_result["result"]["photo"][-1]["file_id"]
            except Exception:
                payload["photo_full"] = None
        except Exception:
            return error("Ошибка отправки анкеты. Попробуй ещё раз.", status=500)

        try:
            set_status(user_id, "pending")
            set_last_apply_at(user_id)
            set_form_data(user_id, payload)
            set_source(user_id, "site")
        except Exception:
            return error("Ошибка сохранения анкеты. Попробуй ещё раз.", status=500)

        bot_link = f"https://t.me/{BOT_USERNAME.strip().lstrip('@')}" if BOT_USERNAME.strip() else None
        return self.send_json({
            "ok": True,
            "message": "🤍 Спасибо! Анкета отправлена администратору ✨",
            "bot_link": bot_link,
        })

    def send_json(self, payload: dict, status: int = 200):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Running on http://127.0.0.1:{port}")
    server.serve_forever()
