import json
import html
import os
import re
import ssl
import uuid
import urllib.parse
import urllib.request
import urllib.error
import time
from datetime import datetime
from email.parser import BytesParser
from email.policy import default
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from database import save_web_application, get_status_counts, get_setting, set_setting
from texts import STATUS_LABELS

ROOT_DIR = Path(__file__).parent
WEB_DIR = ROOT_DIR / "web"
ENV_PATH = ROOT_DIR / ".env"

MAX_BODY_SIZE = 30 * 1024 * 1024
ADMIN_MENU_SETTING_KEY = "admin_menu_message_id"
ADMIN_NOTIFY_SETTING_KEY = "admin_notify_message_id"


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
try:
    from excel_export import append_application_row
except Exception:
    append_application_row = None
try:
    import certifi
except Exception:
    certifi = None


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
    yes_re = re.compile(r"\b(да|ага|есть|имеется|конечно|yes|y|da|ок|ok)\b", re.IGNORECASE)
    no_re = re.compile(r"\b(нет|нету|неа|no|n)\b", re.IGNORECASE)
    if yes_re.search(value):
        return "Да"
    if no_re.search(value):
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

def build_admin_full_text(data: dict, web_id: str) -> str:
    status_label = STATUS_LABELS.get("pending", "🟡 На рассмотрении")
    return (
        "📋 <b>Полная анкета</b>\n\n"
        f"👤 Имя: {_safe(data.get('name'))}\n"
        f"📅 Дата рождения: {_safe(data.get('age'))}\n"
        f"🌍 Город и страна: {_safe(data.get('city'))}\n"
        f"📞 Телефон: {_safe(data.get('phone'))}\n"
        f"🏠 Помещение без посторонних: {_safe(data.get('living'))}\n"
        f"📱 Устройства: {_safe(data.get('devices'))}\n"
        f"📲 Модель: {_safe(data.get('device_model'))}\n"
        f"🎧 Наушники: {_safe(data.get('headphones'))}\n"
        f"⏱ Время работы: {_safe(data.get('work_time'))}\n"
        f"💼 Опыт: {_safe(data.get('experience'))}\n"
        f"💬 Telegram: {_safe(data.get('telegram'))}\n"
        f"🆔 ID: {_safe(web_id)}\n"
        "🧭 Источник: Сайт\n\n"
        f"Статус: <b>{status_label}</b>"
    )

def build_admin_menu_text(counts: dict) -> str:
    return (
        "🛠 <b>Админ-меню</b>\n\n"
        f"Ожидают подтверждения: <b>{counts.get('pending', 0)}</b>\n"
        f"Принятые: <b>{counts.get('accepted', 0)}</b>\n"
        f"Отклонённые: <b>{counts.get('rejected', 0)}</b>\n\n"
        "Выбери раздел ниже ✨"
    )

def build_admin_menu_keyboard(counts: dict) -> dict:
    pending = counts.get("pending", 0)
    accepted = counts.get("accepted", 0)
    rejected = counts.get("rejected", 0)
    total = counts.get("total", pending + accepted + rejected)
    return {
        "inline_keyboard": [
            [
                {
                    "text": f"⏳ Ожидают подтверждения!! Просмотреть ({pending})",
                    "callback_data": "admin_menu:pending",
                }
            ],
            [
                {
                    "text": f"✅ Принятые ({accepted})",
                    "callback_data": "admin_menu:accepted",
                }
            ],
            [
                {
                    "text": f"❌ Отклонённые ({rejected})",
                    "callback_data": "admin_menu:rejected",
                }
            ],
            [
                {
                    "text": f"📚 Все заявки ({total})",
                    "callback_data": "admin_menu:all",
                }
            ],
            [
                {"text": "📊 Статистика", "callback_data": "admin_menu:stats"},
                {"text": "📁 Excel", "callback_data": "admin_menu:excel"},
            ],
            [
                {"text": "🧹 Архивировать старые", "callback_data": "admin_menu:archive"}
            ],
            [
                {"text": "⚠️ Сбросить базу", "callback_data": "admin_menu:reset"},
                {"text": "🔄 Обновить меню", "callback_data": "admin_menu:refresh"},
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
        except Exception:
            pass
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
                for enc in (charset, "utf-8", "cp1251", "latin-1"):
                    try:
                        value = raw.decode(enc, errors="strict")
                        break
                    except Exception:
                        value = ""
                if not value:
                    value = raw.decode(charset or "utf-8", errors="replace")
            else:
                value = str(raw)
            fields[name] = value.strip()
    return fields, files


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def copyfile(self, source, outputfile):
        try:
            super().copyfile(source, outputfile)
        except BrokenPipeError:
            # Client closed connection early (browser navigation/refresh).
            pass

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

        name = clean_text(fields.get("name") or "")
        if len(name) < 2:
            return error("🤍 Имя должно быть чуть длиннее. Напиши, пожалуйста, полностью:", field="name")

        city = clean_text(fields.get("city") or "")
        if len(city) < 2:
            return error("🤍 Подскажи город и страну проживания ещё раз:", field="city")

        phone_raw = clean_text(fields.get("phone") or "")
        if not is_valid_phone(phone_raw):
            return error("🤍 Кажется, номер введён некорректно. Пример: +7 900 000 00 00", field="phone")
        phone = normalize_phone(phone_raw) or phone_raw

        age_raw = clean_text(fields.get("age") or "")
        if not is_valid_birthdate(age_raw):
            return error("🤍 Напиши дату рождения в формате 01.01.2000:", field="age")
        age = normalize_birthdate(age_raw) or age_raw

        living_raw = clean_text(fields.get("living") or "")
        living = normalize_yes_no(living_raw)
        if not living:
            if len(living_raw) < 1:
                return error("🤍 Ответь, пожалуйста, «да» или «нет»:", field="living")
            living = living_raw

        devices = clean_text(fields.get("devices") or "")
        if len(devices) < 2:
            return error("🤍 Уточни, пожалуйста, какие устройства есть:", field="devices")

        device_model = clean_text(fields.get("device_model") or "")
        if len(device_model) < 2:
            return error("🤍 Напиши модель устройства, пожалуйста:", field="device_model")

        work_time = clean_text(fields.get("work_time") or "")
        if not has_any_digit(work_time):
            return error("🤍 Напиши, пожалуйста, количество часов цифрами (например: 6):", field="work_time")

        headphones = clean_text(fields.get("headphones") or "")
        if len(headphones) < 2:
            return error("🤍 Подскажи, пожалуйста, есть ли наушники с микрофоном:", field="headphones")

        telegram_raw = clean_text(fields.get("telegram") or "")
        telegram = normalize_telegram(telegram_raw)
        if not telegram:
            return error("🤍 Укажи, пожалуйста, Telegram в формате @username:", field="telegram")

        experience = clean_text(fields.get("experience") or "")
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

        user_id = -int(time.time_ns())
        web_id = str(user_id)

        try:
            send_full = os.getenv("WEB_SEND_FULL_TO_ADMIN", "").strip().lower() in {"1", "true", "yes"}
            if send_full:
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
                    "caption": "Фото анфас:",
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
                    "caption": "Фото в полный рост:",
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
            try:
                face_msg_id = face_result.get("result", {}).get("message_id")
                if face_msg_id:
                    telegram_request(
                        "deleteMessage",
                        {"chat_id": str(ADMIN_GROUP_ID), "message_id": int(face_msg_id)},
                    )
            except Exception:
                pass
            try:
                full_msg_id = full_result.get("result", {}).get("message_id")
                if full_msg_id:
                    telegram_request(
                        "deleteMessage",
                        {"chat_id": str(ADMIN_GROUP_ID), "message_id": int(full_msg_id)},
                    )
            except Exception:
                pass
        except Exception as err:
            print("Telegram error:", err)
            description = ""
            if isinstance(err, RuntimeError) and err.args:
                payload_err = err.args[0]
                if isinstance(payload_err, dict):
                    description = str(payload_err.get("description", ""))
                else:
                    description = str(payload_err)
            message = "Ошибка отправки анкеты. Попробуй ещё раз."
            if "not found" in description or "chat not found" in description:
                message = "Бот не видит админ‑группу. Проверь ADMIN_GROUP_ID и что бот добавлен в группу."
            elif "not enough rights" in description or "not a member" in description:
                message = "Бот без прав отправки в группу. Добавь бота и выдай права."
            elif "file is too big" in description:
                message = "Фото слишком большое. Пришли файл меньше 10 МБ."
            elif "TOKEN" in description or "not set" in description:
                message = "Не настроен BOT_TOKEN или ADMIN_GROUP_ID."
            return error(message, status=500)

        try:
            save_web_application(user_id, payload, source="site", status="pending")
            if append_application_row:
                try:
                    append_application_row(payload, user_id, "pending")
                except Exception as err:
                    print("Excel error:", err)
        except Exception as err:
            print("DB error:", err)
            return error("Ошибка сохранения анкеты. Попробуй ещё раз.", status=500)

        # синхронизируем админ-меню и уведомление так же, как в боте
        notify_admin_new_application()
        update_admin_menu_message()

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
