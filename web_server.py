import json
import html
import os
import re
import ssl
import uuid
import hashlib
import hmac
from functools import lru_cache
import urllib.parse
import urllib.request
import urllib.error
import time
import threading
from collections import deque
from datetime import datetime, timezone, timedelta
from email.parser import BytesParser
from email.policy import default
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from database import (
    save_web_application,
    get_status_counts,
    get_setting,
    set_setting,
    set_admin_message_id,
    find_recent_site_lead_by_phone,
)
from texts import STATUS_LABELS
from time_utils import format_submit_time
from application_rules import (
    FORM_NAME_MAX_LEN as SHARED_FORM_NAME_MAX_LEN,
    FORM_CITY_MAX_LEN as SHARED_FORM_CITY_MAX_LEN,
    FORM_PHONE_MAX_LEN as SHARED_FORM_PHONE_MAX_LEN,
    FORM_AGE_MAX_LEN as SHARED_FORM_AGE_MAX_LEN,
    FORM_DEVICE_MODEL_MAX_LEN as SHARED_FORM_DEVICE_MODEL_MAX_LEN,
    FORM_WORK_TIME_MAX_LEN as SHARED_FORM_WORK_TIME_MAX_LEN,
    FORM_TELEGRAM_MAX_LEN as SHARED_FORM_TELEGRAM_MAX_LEN,
    FORM_EXPERIENCE_MAX_LEN as SHARED_FORM_EXPERIENCE_MAX_LEN,
    FORM_WA_TEXT_MAX_LEN as SHARED_FORM_WA_TEXT_MAX_LEN,
    clean_user_text as shared_clean_user_text,
    normalize_phone as shared_normalize_phone,
    is_valid_phone as shared_is_valid_phone,
    normalize_birthdate as shared_normalize_birthdate,
    is_valid_birthdate as shared_is_valid_birthdate,
    has_any_digit as shared_has_any_digit,
    normalize_yes_no as shared_normalize_yes_no,
    normalize_telegram as shared_normalize_telegram,
)

ROOT_DIR = Path(__file__).parent
WEB_DIR = ROOT_DIR / "web"
ENV_PATH = ROOT_DIR / ".env"

MAX_APPLY_BODY_SIZE = 2 * 1024 * 1024
MAX_WEBHOOK_BODY_SIZE = 4 * 1024 * 1024
MAX_NAME_LEN = SHARED_FORM_NAME_MAX_LEN
MAX_CITY_LEN = SHARED_FORM_CITY_MAX_LEN
MAX_PHONE_LEN = SHARED_FORM_PHONE_MAX_LEN
MAX_BIRTHDATE_LEN = SHARED_FORM_AGE_MAX_LEN
MAX_DEVICE_LEN = SHARED_FORM_DEVICE_MODEL_MAX_LEN
MAX_CONTACT_VALUE_LEN = max(SHARED_FORM_TELEGRAM_MAX_LEN, SHARED_FORM_PHONE_MAX_LEN)
MAX_COUNTRY_LEN = 80
MAX_EMAIL_LEN = 160
MAX_WORK_TIME_LEN = SHARED_FORM_WORK_TIME_MAX_LEN
MAX_EXPERIENCE_LEN = SHARED_FORM_EXPERIENCE_MAX_LEN
MAX_WA_TEXT_LEN = SHARED_FORM_WA_TEXT_MAX_LEN
MAX_URL_VALUE_LEN = 2048
ADMIN_MENU_SETTING_KEY = "admin_menu_message_id"
ADMIN_NOTIFY_SETTING_KEY = "admin_notify_message_id"
SUPPORTED_SITE_LANGS = {"ru", "en", "pt", "es"}
SITE_LEAD_TOKEN_PREFIX = "site_lead_token:"
PROJECT_STREAMFLOW = "streamflow_agency"
PROJECT_STARFLOW = "starflow_corp"
SUPPORTED_PROJECTS = {PROJECT_STREAMFLOW, PROJECT_STARFLOW}
HONEYPOT_FIELD_NAMES = ("website", "company")
MAX_HONEYPOT_LEN = 120


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


load_env_file(ENV_PATH)

def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default

SITE_LEAD_TOKEN_TTL_HOURS = max(24, _env_int("SITE_LEAD_TOKEN_TTL_HOURS", 72))
APPLY_RATE_WINDOW_SECONDS = max(10, _env_int("APPLY_RATE_WINDOW_SECONDS", 60))
APPLY_RATE_MAX_PER_WINDOW = max(1, _env_int("APPLY_RATE_MAX_PER_WINDOW", 10))
WEBHOOK_RATE_WINDOW_SECONDS = max(10, _env_int("WEBHOOK_RATE_WINDOW_SECONDS", 60))
WEBHOOK_RATE_MAX_PER_WINDOW = max(1, _env_int("WEBHOOK_RATE_MAX_PER_WINDOW", 180))
APPLY_SAME_PHONE_COOLDOWN_SECONDS = max(30, _env_int("APPLY_SAME_PHONE_COOLDOWN_SECONDS", 300))

_RATE_LIMIT_LOCK = threading.Lock()
_RATE_LIMIT_WINDOWS: dict[str, deque[float]] = {}
_PHONE_COOLDOWN_CACHE: dict[str, float] = {}
_ADMIN_REFRESH_LOCK = threading.Lock()
_ADMIN_REFRESH_RUNNING = False
_ADMIN_REFRESH_DIRTY = False


def _env_flag(name: str, default: bool = False) -> bool:
    raw = (os.getenv(name, "") or "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "y", "on"}


INFOBIP_FORWARD_TO_ADMIN = _env_flag("INFOBIP_FORWARD_TO_ADMIN", False)
INFOBIP_RELAY_MODE = _env_flag("INFOBIP_RELAY_MODE", False)
INFOBIP_BOT_ENABLED = _env_flag("INFOBIP_BOT_ENABLED", True)
INFOBIP_INTERACTIVE_ENABLED = _env_flag("INFOBIP_INTERACTIVE_ENABLED", True)
INFOBIP_API_KEY = (os.getenv("INFOBIP_API_KEY", "") or "").strip()
INFOBIP_BASE_URL = (os.getenv("INFOBIP_BASE_URL", "") or "").strip().rstrip("/")
INFOBIP_WHATSAPP_SENDER = (os.getenv("INFOBIP_WHATSAPP_SENDER", "") or "").strip()
INFOBIP_WEBHOOK_SECRET = (os.getenv("INFOBIP_WEBHOOK_SECRET", "") or "").strip()
WA_MENU_IMAGE_URL = (os.getenv("WA_MENU_IMAGE_URL", "") or "").strip()
WHATSAPP_FLOW_PREFIX = "wa_flow:"

print(
    "Infobip config:",
    {
        "bot_enabled": INFOBIP_BOT_ENABLED,
        "interactive_enabled": INFOBIP_INTERACTIVE_ENABLED,
        "has_api_key": bool(INFOBIP_API_KEY),
        "has_webhook_secret": bool(INFOBIP_WEBHOOK_SECRET),
        "base_url": INFOBIP_BASE_URL or "",
        "sender": INFOBIP_WHATSAPP_SENDER or "",
    },
)

FIELD_ERRORS = {
    "ru": {
        "name": "🤍 Имя должно быть чуть длиннее. Напиши, пожалуйста, полностью:",
        "city": "🤍 Подскажи город и страну проживания ещё раз:",
        "phone": "🤍 Кажется, номер введён некорректно. Укажи международный формат, например: +44 7307 810222",
        "age": "🤍 Напиши дату рождения в формате 01.01.2000 (только 18+):",
        "yes_no": "🤍 Ответь, пожалуйста, «да» или «нет»:",
        "devices": "🤍 Уточни, пожалуйста, какие устройства есть:",
        "device_model": "🤍 Напиши устройство, на котором будешь работать (например: iPhone 13 / Samsung A54 / ноутбук):",
        "work_time": "🤍 Напиши, пожалуйста, количество часов цифрами (например: 6):",
        "telegram": "🤍 Укажи, пожалуйста, Telegram в формате @username:",
        "whatsapp": "🤍 Укажи, пожалуйста, WhatsApp в международном формате, например: +44 7307 810222:",
        "email": "🤍 Укажи корректный email, например name@example.com:",
        "experience": "🤍 Напиши, пожалуйста, есть ли опыт:",
        "photo_face": "🤍 Здесь нужно отправить ФОТО АНФАС.",
        "photo_full": "🤍 Здесь нужно отправить ФОТО В ПОЛНЫЙ РОСТ.",
    },
    "en": {
        "name": "Please enter your full name.",
        "city": "Please enter your city and country.",
        "phone": "Phone number looks incorrect. Example: +1 555 123 4567",
        "age": "Please enter birth date as 01.01.2000 (18+ only).",
        "yes_no": "Please answer yes or no.",
        "devices": "Please specify available devices.",
        "device_model": "Please enter the device you will work on (for example: iPhone 13 / Samsung A54 / laptop).",
        "work_time": "Please enter work hours as a number (example: 6).",
        "telegram": "Please enter Telegram as @username.",
        "whatsapp": "Please enter WhatsApp in international format, example: +1 555 123 4567",
        "email": "Please enter a valid email, for example: name@example.com.",
        "experience": "Please tell us about your experience.",
        "photo_face": "Please upload a front-face photo.",
        "photo_full": "Please upload a full-body photo.",
    },
    "pt": {
        "name": "Digite seu nome completo.",
        "city": "Informe sua cidade e país.",
        "phone": "Telefone inválido. Exemplo: +55 11 99999 9999",
        "age": "Informe a data no formato 01.01.2000 (somente 18+).",
        "yes_no": "Responda sim ou não.",
        "devices": "Informe os dispositivos disponíveis.",
        "device_model": "Informe o dispositivo em que você vai trabalhar (ex.: iPhone 13 / Samsung A54 / notebook).",
        "work_time": "Informe as horas com número (ex.: 6).",
        "telegram": "Informe o Telegram no formato @username.",
        "whatsapp": "Informe o WhatsApp no formato internacional, ex.: +55 11 99999 9999",
        "email": "Informe um email válido, por exemplo: nome@exemplo.com.",
        "experience": "Informe se você tem experiência.",
        "photo_face": "Envie a foto frontal.",
        "photo_full": "Envie a foto de corpo inteiro.",
    },
    "es": {
        "name": "Escribe tu nombre completo.",
        "city": "Indica ciudad y país.",
        "phone": "Número de teléfono inválido. Ejemplo: +34 600 000 000",
        "age": "Indica la fecha en formato 01.01.2000 (solo 18+).",
        "yes_no": "Responde sí o no.",
        "devices": "Indica qué dispositivos tienes.",
        "device_model": "Indica el dispositivo con el que trabajarás (ej.: iPhone 13 / Samsung A54 / portátil).",
        "work_time": "Indica horas con número (ej.: 6).",
        "telegram": "Indica Telegram en formato @username.",
        "whatsapp": "Indica WhatsApp en formato internacional, ejemplo: +34 600 000 000",
        "email": "Indica un email válido, por ejemplo: nombre@ejemplo.com.",
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
        "invalid_form": "Проверь поля формы и попробуй ещё раз.",
        "send_error": "Ошибка отправки анкеты. Попробуй ещё раз.",
        "group_not_found": "Бот не видит админ‑группу. Проверь ADMIN_GROUP_ID и что бот добавлен в группу.",
        "group_no_rights": "Бот без прав отправки в группу. Добавь бота и выдай права.",
        "photo_too_big": "Фото слишком большое. Пришли файл меньше 10 МБ.",
        "token_missing": "Не настроен BOT_TOKEN или ADMIN_GROUP_ID.",
        "db_error": "Ошибка сохранения анкеты. Попробуй ещё раз.",
        "success": "✅ Заявка принята мгновенно и автоматически.",
        "rate_limited_ip": "Слишком много попыток за короткое время. Подожди немного и попробуй снова.",
        "rate_limited_phone": "Похоже, заявка с этим номером уже отправлялась недавно. Повтори чуть позже.",
    },
    "en": {
        "bad_size": "Invalid request size.",
        "too_big": "Files are too large.",
        "bad_type": "Unsupported payload type.",
        "invalid_form": "Please check form fields and try again.",
        "send_error": "Failed to send application. Please try again.",
        "group_not_found": "Bot cannot reach admin group. Check ADMIN_GROUP_ID and bot membership.",
        "group_no_rights": "Bot has no permission to post in admin group.",
        "photo_too_big": "Photo is too large. Please upload under 10MB.",
        "token_missing": "BOT_TOKEN or ADMIN_GROUP_ID is not configured.",
        "db_error": "Failed to save application. Please try again.",
        "success": "✅ Application received instantly and automatically.",
        "rate_limited_ip": "Too many attempts in a short time. Please wait and try again.",
        "rate_limited_phone": "An application with this phone was submitted recently. Please try again later.",
    },
    "pt": {
        "bad_size": "Tamanho da requisição inválido.",
        "too_big": "Arquivos muito grandes.",
        "bad_type": "Tipo de dados não suportado.",
        "invalid_form": "Verifique os campos do formulário e tente novamente.",
        "send_error": "Falha ao enviar candidatura. Tente novamente.",
        "group_not_found": "O bot não alcança o grupo admin. Verifique ADMIN_GROUP_ID.",
        "group_no_rights": "O bot não tem permissão para enviar no grupo admin.",
        "photo_too_big": "Foto muito grande. Envie arquivo menor que 10MB.",
        "token_missing": "BOT_TOKEN ou ADMIN_GROUP_ID não configurado.",
        "db_error": "Falha ao salvar candidatura. Tente novamente.",
        "success": "✅ Cadastro recebido instantaneamente e automaticamente.",
        "rate_limited_ip": "Muitas tentativas em pouco tempo. Aguarde e tente novamente.",
        "rate_limited_phone": "Uma candidatura com este telefone foi enviada recentemente. Tente novamente mais tarde.",
    },
    "es": {
        "bad_size": "Tamaño de solicitud inválido.",
        "too_big": "Los archivos son demasiado grandes.",
        "bad_type": "Tipo de datos no soportado.",
        "invalid_form": "Revisa los campos del formulario y vuelve a intentarlo.",
        "send_error": "Error al enviar la solicitud. Inténtalo de nuevo.",
        "group_not_found": "El bot no puede llegar al grupo admin. Revisa ADMIN_GROUP_ID.",
        "group_no_rights": "El bot no tiene permisos para enviar en el grupo admin.",
        "photo_too_big": "La foto es demasiado grande. Sube un archivo menor de 10MB.",
        "token_missing": "BOT_TOKEN o ADMIN_GROUP_ID no están configurados.",
        "db_error": "Error al guardar la solicitud. Inténtalo de nuevo.",
        "success": "✅ Solicitud recibida al instante y automáticamente.",
        "rate_limited_ip": "Demasiados intentos en poco tiempo. Espera y vuelve a intentarlo.",
        "rate_limited_phone": "Ya hubo una solicitud reciente con este teléfono. Inténtalo de nuevo más tarde.",
    },
}

WA_TEXTS = {
    "ru": {
        "choose_lang": (
            "🤍 Привет! Это WhatsApp-бот Streamflow.\n\n"
            "Выбери язык: RU / EN / PT / ES"
        ),
        "lang_more": "🌍 Ещё языки. Выбери PT или ES:",
        "invalid_lang": "Выбери язык: RU / EN / PT / ES",
        "menu": (
            "✨ Streamflow WhatsApp\n\n"
            "Ты в главной панели. Всё сделано без лишней суеты:\n"
            "• подача анкеты в пару шагов\n"
            "• живое портфолио с удобным листанием\n"
            "• быстрый выход на менеджера\n\n"
            "Выбери действие кнопками ниже."
        ),
        "menu_invalid": "Не поняла команду. Нажми кнопку ниже 👇",
        "menu_more": (
            "⚙️ Дополнительно\n\n"
            "Здесь можно:\n"
            "• открыть канал\n"
            "• написать менеджеру\n"
            "• сменить язык\n\n"
            "Выбери нужный пункт кнопками."
        ),
        "menu_more_invalid": "Не поняла команду. Нажми кнопку ниже 👇",
        "about_menu": (
            "ℹ️ О работе в Streamflow\n\n"
            "Формат спокойный и понятный:\n"
            "• удалённо, из дома\n"
            "• без 18+ контента\n"
            "• поддержка на каждом этапе\n"
            "• анкета проверяется автоматически и быстро\n\n"
            "Если готова, можно сразу подать заявку или посмотреть портфолио."
        ),
        "portfolio_menu": (
            "📁 Портфолио моделей\n\n"
            "Сейчас открою галерею фото.\n"
            "Листай кнопками «назад/вперёд», без лишнего спама в чате."
        ),
        "about": (
            "Streamflow — модельное стрим-агентство.\n"
            "Удалённый формат, поддержка, обучение и понятные правила старта."
        ),
        "about_work": (
            "👩‍💻 Формат работы\n\n"
            "• удалённо, из дома\n"
            "• без 18+ контента\n"
            "• гибкий график\n"
            "• поддержка на каждом этапе"
        ),
        "about_platforms": (
            "🛠 Площадки и запуск\n\n"
            "• помогаем с настройкой\n"
            "• объясняем рабочую механику\n"
            "• даём понятный план старта"
        ),
        "about_income": (
            "💸 Доход и рост\n\n"
            "Доход зависит от графика, дисциплины и стабильности.\n"
            "Показываем рабочие кейсы и даём рекомендации по росту."
        ),
        "ask_name": "Как тебя зовут? Напиши имя:",
        "invalid_name": "Имя слишком короткое. Напиши, пожалуйста, имя ещё раз:",
        "ask_phone": "Укажи номер телефона (или напиши SAME, чтобы использовать этот WhatsApp номер):",
        "invalid_phone": "Номер некорректный. Укажи международный формат, например: +44 7307 810222",
        "ask_age": "Укажи дату рождения в формате 01.01.2000 (только 18+):",
        "invalid_age": "Дата некорректна. Нужен формат 01.01.2000 и возраст 18+.",
        "ask_device": "Напиши устройство, на котором будешь работать (например: iPhone 13 / Samsung A54 / ноутбук):",
        "invalid_device": "Ответ слишком короткий. Напиши устройство ещё раз:",
        "ask_telegram": "Укажи Telegram для связи в формате @username:",
        "invalid_telegram": "Telegram некорректный. Пример: @username",
        "ask_city": "Город и страна проживания:",
        "invalid_city": "Напиши город и страну полностью.",
        "ask_work_time": "Сколько часов в день готова работать?",
        "invalid_work_time": "Укажи часы цифрами, например: 6",
        "ask_experience": "Есть ли опыт? Если нет — так и напиши.",
        "invalid_experience": "Напиши пару слов про опыт (или что опыта нет).",
        "ask_living": "Есть ли помещение без посторонних? Ответь: да или нет.",
        "invalid_living": "Ответь, пожалуйста, да или нет.",
        "ask_photo_face": "Пришли фото анфас.",
        "invalid_photo_face": "Нужна именно фотография анфас (изображение).",
        "ask_photo_full": "Пришли фото в профиль/полный рост.",
        "invalid_photo_full": "Нужна именно фотография в профиль/полный рост (изображение).",
        "saved": (
            "✅ Заявка принята!\n\n"
            "Мы передали её менеджеру. Ожидай ответ в ближайшее время."
        ),
        "already": "Заявка уже отправлена. Если хочешь отправить новую, напиши START.",
    },
    "en": {
        "choose_lang": (
            "🤍 Hi! This is Streamflow WhatsApp bot.\n\n"
            "Choose language: RU / EN / PT / ES"
        ),
        "lang_more": "🌍 More languages. Choose PT or ES:",
        "invalid_lang": "Choose language: RU / EN / PT / ES",
        "menu": (
            "✨ Streamflow WhatsApp\n\n"
            "You are in the main panel. Everything is simple and clear:\n"
            "• quick application flow\n"
            "• live photo portfolio with easy browsing\n"
            "• direct manager contact\n\n"
            "Choose an action using the buttons below."
        ),
        "menu_invalid": "I didn't catch that. Please tap a button below 👇",
        "menu_more": (
            "⚙️ More options\n\n"
            "Here you can:\n"
            "• open the channel\n"
            "• message the manager\n"
            "• change language\n\n"
            "Choose using the buttons below."
        ),
        "menu_more_invalid": "I didn't catch that. Please tap a button below 👇",
        "about_menu": (
            "ℹ️ About work at Streamflow\n\n"
            "The format is soft and structured:\n"
            "• fully remote\n"
            "• no 18+ content\n"
            "• support on every step\n"
            "• applications are reviewed fast and automatically\n\n"
            "If you're ready, start your application or open portfolio."
        ),
        "portfolio_menu": (
            "📁 Model portfolio\n\n"
            "I will open a photo gallery now.\n"
            "Use back/next buttons to browse without chat clutter."
        ),
        "about": (
            "Streamflow is a model streaming agency.\n"
            "Remote format, support, training and clear onboarding rules."
        ),
        "about_work": (
            "👩‍💻 Work format\n\n"
            "• fully remote\n"
            "• no 18+ content\n"
            "• flexible schedule\n"
            "• full team support"
        ),
        "about_platforms": (
            "🛠 Platforms and setup\n\n"
            "• we help with setup\n"
            "• clear onboarding steps\n"
            "• practical launch guidance"
        ),
        "about_income": (
            "💸 Income and growth\n\n"
            "Income depends on schedule, consistency and discipline.\n"
            "We share real cases and growth recommendations."
        ),
        "ask_name": "What is your name?",
        "invalid_name": "Name is too short. Please enter it again:",
        "ask_phone": "Send your phone number (or type SAME to use this WhatsApp number):",
        "invalid_phone": "Invalid phone number. Example: +1 555 123 4567",
        "ask_age": "Enter birth date in format 01.01.2000 (18+ only):",
        "invalid_age": "Invalid date. Use 01.01.2000 format and 18+ age.",
        "ask_device": "Send the device you will work on (example: iPhone 13 / Samsung A54 / laptop):",
        "invalid_device": "Answer is too short. Please enter your device again:",
        "ask_telegram": "Send your Telegram username in format @username:",
        "invalid_telegram": "Invalid Telegram username. Example: @username",
        "ask_city": "Your city and country:",
        "invalid_city": "Please enter city and country.",
        "ask_work_time": "How many hours per day can you work?",
        "invalid_work_time": "Please enter hours as a number, example: 6",
        "ask_experience": "Do you have experience? If no, write it.",
        "invalid_experience": "Please add a short experience note.",
        "ask_living": "Do you have a private room without interruptions? Reply yes or no.",
        "invalid_living": "Please reply yes or no.",
        "ask_photo_face": "Send a front-face photo.",
        "invalid_photo_face": "Please send a front-face image.",
        "ask_photo_full": "Send a profile/full-body photo.",
        "invalid_photo_full": "Please send a profile/full-body image.",
        "saved": (
            "✅ Application received!\n\n"
            "We sent it to the manager. You will get a reply soon."
        ),
        "already": "Application already sent. If you want to start again, type START.",
    },
    "pt": {
        "choose_lang": (
            "🤍 Oi! Este é o bot de WhatsApp da Streamflow.\n\n"
            "Escolha o idioma: RU / EN / PT / ES"
        ),
        "lang_more": "🌍 Mais idiomas. Escolha PT ou ES:",
        "invalid_lang": "Escolha o idioma: RU / EN / PT / ES",
        "menu": (
            "✨ Streamflow WhatsApp\n\n"
            "Você está no painel principal. Tudo é simples e claro:\n"
            "• candidatura rápida\n"
            "• portfólio real com navegação por botões\n"
            "• contato direto com o gerente\n\n"
            "Escolha uma ação nos botões abaixo."
        ),
        "menu_invalid": "Não entendi. Toque em um botão abaixo 👇",
        "menu_more": (
            "⚙️ Mais opções\n\n"
            "Aqui você pode:\n"
            "• abrir o canal\n"
            "• falar com o gerente\n"
            "• trocar o idioma\n\n"
            "Escolha pelos botões abaixo."
        ),
        "menu_more_invalid": "Não entendi. Toque em um botão abaixo 👇",
        "about_menu": (
            "ℹ️ Sobre o trabalho na Streamflow\n\n"
            "Formato leve e organizado:\n"
            "• totalmente remoto\n"
            "• sem conteúdo 18+\n"
            "• suporte em todas as etapas\n"
            "• candidatura analisada rápido e automaticamente\n\n"
            "Se quiser, já pode iniciar a candidatura ou abrir o portfólio."
        ),
        "portfolio_menu": (
            "📁 Portfólio de modelos\n\n"
            "Vou abrir uma galeria de fotos agora.\n"
            "Use os botões de voltar/avançar sem poluir o chat."
        ),
        "about": (
            "A Streamflow é uma agência de modelos para streaming.\n"
            "Formato remoto, suporte, treinamento e regras claras de início."
        ),
        "about_work": (
            "👩‍💻 Formato de trabalho\n\n"
            "• totalmente remoto\n"
            "• sem conteúdo 18+\n"
            "• horário flexível\n"
            "• suporte da equipe"
        ),
        "about_platforms": (
            "🛠 Plataformas e setup\n\n"
            "• ajudamos na configuração\n"
            "• passo a passo claro\n"
            "• orientação prática de início"
        ),
        "about_income": (
            "💸 Renda e crescimento\n\n"
            "A renda depende de rotina, consistência e disciplina.\n"
            "Mostramos casos reais e recomendações de crescimento."
        ),
        "ask_name": "Qual é o seu nome?",
        "invalid_name": "Nome muito curto. Envie novamente:",
        "ask_phone": "Informe seu telefone (ou digite SAME para usar este número do WhatsApp):",
        "invalid_phone": "Telefone inválido. Exemplo: +55 11 99999 9999",
        "ask_age": "Informe sua data de nascimento no formato 01.01.2000 (somente 18+):",
        "invalid_age": "Data inválida. Use o formato 01.01.2000 e idade 18+.",
        "ask_device": "Informe o dispositivo em que você vai trabalhar (ex.: iPhone 13 / Samsung A54 / notebook):",
        "invalid_device": "Resposta muito curta. Informe o dispositivo novamente:",
        "ask_telegram": "Informe seu Telegram no formato @username:",
        "invalid_telegram": "Telegram inválido. Exemplo: @username",
        "ask_city": "Cidade e país onde você mora:",
        "invalid_city": "Informe cidade e país completos.",
        "ask_work_time": "Quantas horas por dia você pode trabalhar?",
        "invalid_work_time": "Informe as horas em número, ex.: 6",
        "ask_experience": "Você tem experiência? Se não, escreva isso.",
        "invalid_experience": "Escreva um breve texto sobre experiência.",
        "ask_living": "Você tem um ambiente privado sem interrupções? Responda: sim ou não.",
        "invalid_living": "Responda, por favor, sim ou não.",
        "ask_photo_face": "Envie uma foto de frente (rosto).",
        "invalid_photo_face": "Envie uma imagem de frente, por favor.",
        "ask_photo_full": "Envie uma foto de perfil/corpo inteiro.",
        "invalid_photo_full": "Envie uma imagem de perfil/corpo inteiro, por favor.",
        "saved": (
            "✅ Candidatura recebida!\n\n"
            "Enviamos para o gerente. Você receberá retorno em breve."
        ),
        "already": "Candidatura já enviada. Se quiser começar de novo, digite START.",
    },
    "es": {
        "choose_lang": (
            "🤍 Hola, este es el bot de WhatsApp de Streamflow.\n\n"
            "Elige idioma: RU / EN / PT / ES"
        ),
        "lang_more": "🌍 Más idiomas. Elige PT o ES:",
        "invalid_lang": "Elige idioma: RU / EN / PT / ES",
        "menu": (
            "✨ Streamflow WhatsApp\n\n"
            "Estás en el panel principal. Todo es claro y simple:\n"
            "• solicitud rápida\n"
            "• portafolio real con navegación por botones\n"
            "• contacto directo con manager\n\n"
            "Elige una acción con los botones de abajo."
        ),
        "menu_invalid": "No entendí el comando. Pulsa un botón abajo 👇",
        "menu_more": (
            "⚙️ Más opciones\n\n"
            "Aquí puedes:\n"
            "• abrir el canal\n"
            "• escribir al manager\n"
            "• cambiar idioma\n\n"
            "Elige una opción con botones."
        ),
        "menu_more_invalid": "No entendí el comando. Pulsa un botón abajo 👇",
        "about_menu": (
            "ℹ️ Sobre el trabajo en Streamflow\n\n"
            "Formato cómodo y ordenado:\n"
            "• totalmente remoto\n"
            "• sin contenido 18+\n"
            "• soporte en cada paso\n"
            "• la solicitud se revisa rápido y automáticamente\n\n"
            "Si quieres, inicia solicitud o abre el portafolio."
        ),
        "portfolio_menu": (
            "📁 Portafolio de modelos\n\n"
            "Ahora abriré una galería de fotos.\n"
            "Usa los botones atrás/siguiente sin ensuciar el chat."
        ),
        "about": (
            "Streamflow es una agencia de modelos para streaming.\n"
            "Formato remoto, soporte, formación y reglas claras de inicio."
        ),
        "about_work": (
            "👩‍💻 Formato de trabajo\n\n"
            "• totalmente remoto\n"
            "• sin contenido 18+\n"
            "• horario flexible\n"
            "• soporte del equipo"
        ),
        "about_platforms": (
            "🛠 Plataformas y configuración\n\n"
            "• ayudamos con la configuración\n"
            "• pasos claros de inicio\n"
            "• guía práctica de lanzamiento"
        ),
        "about_income": (
            "💸 Ingresos y crecimiento\n\n"
            "Los ingresos dependen del horario, constancia y disciplina.\n"
            "Mostramos casos reales y recomendaciones de crecimiento."
        ),
        "ask_name": "¿Cómo te llamas?",
        "invalid_name": "Nombre demasiado corto. Escríbelo otra vez:",
        "ask_phone": "Indica tu teléfono (o escribe SAME para usar este número de WhatsApp):",
        "invalid_phone": "Número inválido. Ejemplo: +34 600 000 000",
        "ask_age": "Indica fecha de nacimiento en formato 01.01.2000 (solo 18+):",
        "invalid_age": "Fecha inválida. Usa formato 01.01.2000 y edad 18+.",
        "ask_device": "Indica el dispositivo con el que trabajarás (ej.: iPhone 13 / Samsung A54 / portátil):",
        "invalid_device": "La respuesta es demasiado corta. Escríbelo otra vez:",
        "ask_telegram": "Indica tu Telegram en formato @username:",
        "invalid_telegram": "Telegram inválido. Ejemplo: @username",
        "ask_city": "Ciudad y país de residencia:",
        "invalid_city": "Indica ciudad y país completos.",
        "ask_work_time": "¿Cuántas horas al día puedes trabajar?",
        "invalid_work_time": "Indica horas con número, por ejemplo: 6",
        "ask_experience": "¿Tienes experiencia? Si no, escríbelo.",
        "invalid_experience": "Escribe una nota breve sobre tu experiencia.",
        "ask_living": "¿Tienes espacio privado sin interrupciones? Responde: sí o no.",
        "invalid_living": "Responde, por favor, sí o no.",
        "ask_photo_face": "Envía una foto de frente.",
        "invalid_photo_face": "Necesito una imagen de frente, por favor.",
        "ask_photo_full": "Envía una foto de perfil/cuerpo completo.",
        "invalid_photo_full": "Necesito una imagen de perfil/cuerpo completo, por favor.",
        "saved": (
            "✅ Solicitud recibida.\n\n"
            "La enviamos al manager. Te responderemos pronto."
        ),
        "already": "La solicitud ya fue enviada. Si quieres reiniciar, escribe START.",
    },
}

WA_LANG_ALIASES = {
    "ru": {"ru", "рус", "русский", "russian", "lang_ru"},
    "en": {"en", "eng", "english", "lang_en"},
    "pt": {"pt", "por", "pt-br", "br", "brazil", "portuguese", "portugues", "português", "lang_pt"},
    "es": {"es", "esp", "spanish", "español", "espanol", "lang_es"},
}

WA_RESET_COMMANDS = {
    "start",
    "/start",
    "restart",
    "new",
    "menu",
    "начать",
    "старт",
    "заново",
}

WA_MENU_ALIASES = {
    "menu": {"menu", "меню", "main menu", "главное меню", "menu_main"},
    "apply": {"1", "apply", "заявка", "подать", "candidatura", "solicitud", "menu_apply"},
    "site": {"2", "site", "website", "сайт", "menu_site"},
    "portfolio": {"3", "portfolio", "портфолио", "portafolio", "portfólio", "menu_portfolio", "menu_portfolio_cases"},
    "portfolio_cases": {"portfolio_cases", "menu_portfolio_cases", "кейсы", "cases", "casos"},
    "portfolio_reviews": {"portfolio_reviews", "menu_portfolio_reviews", "отзывы", "reviews", "reseñas", "avaliacoes"},
    "portfolio_videos": {"portfolio_videos", "menu_portfolio_videos", "стримы", "streams", "videos", "vídeos"},
    "portfolio_pdf": {"portfolio_pdf", "menu_portfolio_pdf", "pdf", "портфолио pdf"},
    "portfolio_next": {"portfolio_next", "next", "далее", "seguinte", "siguiente"},
    "portfolio_prev": {"portfolio_prev", "prev", "назад", "voltar", "atras"},
    "portfolio_back": {"portfolio_back", "menu_portfolio_back", "к разделам", "sections", "seções", "secciones"},
    "about": {"4", "about", "о работе", "sobre", "sobre o trabalho", "menu_about"},
    "about_work": {"about_work", "menu_about_work", "формат работы", "work format", "formato de trabalho"},
    "about_platforms": {"about_platforms", "menu_about_platforms", "платформы", "platforms", "plataformas"},
    "about_income": {"about_income", "menu_about_income", "доход", "income", "renda", "ingresos"},
    "about_back": {"about_back", "menu_about_back", "в меню", "to menu", "voltar ao menu", "volver al menú"},
    "manager": {"5", "manager", "админ", "менеджер", "gerente", "menu_manager"},
    "channel": {"6", "channel", "канал", "canal", "menu_channel"},
    "language": {"7", "lang", "language", "язык", "idioma", "menu_language"},
    "language_more": {"lang_more", "menu_lang_more", "more languages", "ещё языки", "mais idiomas", "mas idiomas"},
    "language_back": {"lang_back", "menu_lang_back", "back", "назад", "voltar", "volver"},
    "more": {"more", "ещё", "еще", "mais", "más", "mas", "menu_more"},
}

WA_YES_ALIASES = {
    "yes",
    "y",
    "да",
    "1",
    "true",
    "si",
    "sí",
    "sim",
    "yn_yes",
}

WA_NO_ALIASES = {
    "no",
    "n",
    "нет",
    "0",
    "false",
    "nao",
    "não",
    "yn_no",
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


def field_too_long_error(lang: str, max_len: int) -> str:
    locale = normalize_site_lang(lang)
    templates = {
        "ru": "🤍 Ответ слишком длинный (максимум {max} символов). Отправь короче, пожалуйста.",
        "en": "Your message is too long (maximum {max} characters). Please send a shorter one.",
        "pt": "Sua resposta está muito longa (máximo de {max} caracteres). Envie uma versão menor.",
        "es": "Tu mensaje es demasiado largo (máximo {max} caracteres). Envíalo más corto, por favor.",
    }
    template = templates.get(locale, templates["ru"])
    return template.format(max=max_len)


def load_settings():
    load_env_file(ENV_PATH)
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    admin_group_id = os.getenv("ADMIN_GROUP_ID", "").strip()
    admin_username = os.getenv("ADMIN_USERNAME", "streamflowmanager").strip()
    bot_username = os.getenv("BOT_USERNAME", "StreamFlowAgencybot").strip()
    channel_link = os.getenv("CHANNEL_LINK", "https://t.me/streamflowagency").strip()
    site_url = (os.getenv("SITE_URL", "https://streamflowagency.com") or "https://streamflowagency.com").strip()
    return bot_token, admin_group_id, admin_username, bot_username, channel_link, site_url


BOT_TOKEN, ADMIN_GROUP_ID, ADMIN_USERNAME, BOT_USERNAME, CHANNEL_LINK, SITE_URL = load_settings()
SITE_URL = SITE_URL.rstrip("/")
PUBLIC_MANAGER_HANDLE = "@streamflowmanager"
PUBLIC_MANAGER_USERNAME = PUBLIC_MANAGER_HANDLE.lstrip("@")
WA_MANAGER_PHONE = (os.getenv("WA_MANAGER_PHONE", "+380998074928") or "+380998074928").strip()
STARFLOW_BOT_USERNAME = (os.getenv("STARFLOW_BOT_USERNAME", "") or "").strip()
STARFLOW_BOT_LINK = (os.getenv("STARFLOW_BOT_LINK", "") or "").strip()
STARFLOW_CHANNEL_LINK = (os.getenv("STARFLOW_CHANNEL_LINK", "") or "").strip()
STARFLOW_SITE_URL = (os.getenv("STARFLOW_SITE_URL", "") or "").strip().rstrip("/")


def normalize_project(value: str | None) -> str:
    raw = (value or "").strip().lower()
    if raw in {PROJECT_STREAMFLOW, "streamflow", "streamflow_agency"}:
        return PROJECT_STREAMFLOW
    if raw in {PROJECT_STARFLOW, "starflow", "starflow_corp"}:
        return PROJECT_STARFLOW
    return PROJECT_STREAMFLOW


def project_bot_username(project: str) -> str:
    normalized = normalize_project(project)
    if normalized == PROJECT_STARFLOW and STARFLOW_BOT_USERNAME:
        return STARFLOW_BOT_USERNAME
    return BOT_USERNAME


def project_bot_public_link(project: str) -> str | None:
    normalized = normalize_project(project)
    if normalized == PROJECT_STARFLOW and STARFLOW_BOT_LINK:
        return STARFLOW_BOT_LINK
    username = project_bot_username(project).strip().lstrip("@")
    if not username:
        return None
    return f"https://t.me/{username}"


def project_channel_link(project: str) -> str:
    normalized = normalize_project(project)
    if normalized == PROJECT_STARFLOW and STARFLOW_CHANNEL_LINK:
        return STARFLOW_CHANNEL_LINK
    return CHANNEL_LINK


def project_site_url(project: str) -> str:
    normalized = normalize_project(project)
    if normalized == PROJECT_STARFLOW and STARFLOW_SITE_URL:
        return STARFLOW_SITE_URL
    return SITE_URL


def normalize_host(value: str | None) -> str:
    raw = (value or "").strip().lower()
    if not raw:
        return ""
    raw = raw.split(",", 1)[0].strip()
    if raw.startswith("[") and "]" in raw:
        return raw[1 : raw.index("]")].strip().rstrip(".")
    return raw.split(":", 1)[0].strip().rstrip(".")


def _host_from_url(url: str | None) -> str:
    raw = (url or "").strip()
    if not raw:
        return ""
    candidate = raw if "://" in raw else f"https://{raw}"
    parsed = urllib.parse.urlparse(candidate)
    return normalize_host(parsed.netloc)


def _host_aliases(host: str) -> set[str]:
    value = normalize_host(host)
    if not value:
        return set()
    aliases = {value}
    if value.startswith("www."):
        aliases.add(value[4:])
    else:
        aliases.add(f"www.{value}")
    return aliases


CANONICAL_HOST = _host_from_url(SITE_URL)
RAILWAY_INTERNAL_SUFFIXES = (".railway.internal", ".up.railway.app")


def canonical_public_hosts() -> set[str]:
    hosts: set[str] = set()
    hosts.update(_host_aliases(_host_from_url(SITE_URL)))
    hosts.update(_host_aliases(_host_from_url(STARFLOW_SITE_URL)))
    return hosts


def infer_project_from_host(host: str | None) -> str:
    normalized = normalize_host(host)
    if not normalized:
        return PROJECT_STREAMFLOW
    starflow_host = _host_from_url(STARFLOW_SITE_URL)
    if starflow_host and normalized in _host_aliases(starflow_host):
        return PROJECT_STARFLOW
    streamflow_host = _host_from_url(SITE_URL)
    if streamflow_host and normalized in _host_aliases(streamflow_host):
        return PROJECT_STREAMFLOW
    return PROJECT_STREAMFLOW


def resolve_project(project: str | None, host: str | None = None) -> str:
    raw = (project or "").strip()
    if raw:
        return normalize_project(raw)
    return infer_project_from_host(host)


def homepage_path_for_host(host: str | None) -> str:
    project = infer_project_from_host(host)
    if project == PROJECT_STARFLOW:
        return "/starflow.html"
    return "/index.html"


def canonical_site_url_for_host(host: str | None) -> str:
    project = infer_project_from_host(host)
    target = project_site_url(project).strip().rstrip("/")
    if target:
        return target
    return SITE_URL


def is_internal_proxy_host(host: str | None) -> bool:
    normalized = normalize_host(host)
    if not normalized:
        return False
    return normalized.endswith(RAILWAY_INTERNAL_SUFFIXES)


def request_host_from_headers(host_header: str | None, forwarded_host_header: str | None) -> str:
    direct = normalize_host(host_header)
    forwarded = normalize_host(forwarded_host_header)
    allowed = canonical_public_hosts()
    # Prefer explicit public host from client-facing Host header.
    for candidate in (direct, forwarded):
        if candidate and candidate in allowed:
            return candidate
    return direct or forwarded


def _client_ip_from_headers(handler: SimpleHTTPRequestHandler) -> str:
    forwarded_for = (handler.headers.get("X-Forwarded-For") or "").strip()
    if forwarded_for:
        first = forwarded_for.split(",", 1)[0].strip()
        # Keep a safe subset only; avoid header-injected junk.
        first = re.sub(r"[^0-9a-fA-F:.\[\]]", "", first)[:64]
        if first:
            return first
    direct = handler.client_address[0] if handler.client_address else ""
    direct = re.sub(r"[^0-9a-fA-F:.\[\]]", "", str(direct or ""))[:64]
    return direct or "unknown"


def _hash_for_logs(value: str | None) -> str:
    raw = (value or "").strip()
    if not raw:
        return "unknown"
    return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()[:12]


def log_apply_event(
    *,
    outcome: str,
    project: str,
    lang: str,
    client_ip: str,
    status: int,
    field: str | None = None,
    retry_after: int | None = None,
) -> None:
    print(
        "Apply event:",
        {
            "outcome": outcome,
            "project": normalize_project(project),
            "lang": normalize_site_lang(lang),
            "status": int(status),
            "field": (field or "").strip(),
            "retry_after": int(retry_after) if retry_after is not None else 0,
            "ip_hash": _hash_for_logs(client_ip),
        },
    )


def _rate_limit_key(scope: str, key: str) -> str:
    return f"rl:{scope}:{key}"


def _consume_rate_limit(scope: str, key: str, window_seconds: int, max_hits: int) -> tuple[bool, int]:
    now = time.monotonic()
    key_name = _rate_limit_key(scope, key)
    with _RATE_LIMIT_LOCK:
        bucket = _RATE_LIMIT_WINDOWS.get(key_name)
        if bucket is None:
            bucket = deque()
            _RATE_LIMIT_WINDOWS[key_name] = bucket
        while bucket and now - bucket[0] > window_seconds:
            bucket.popleft()
        if len(bucket) >= max_hits:
            retry_after = max(1, int(window_seconds - (now - bucket[0])))
            return False, retry_after
        bucket.append(now)
        return True, 0


def _phone_digits(value: str | None) -> str:
    return re.sub(r"\D", "", value or "")


def _parse_recent_apply_ts(value: str | None) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            parsed = datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
            return parsed
        except Exception:
            continue
    return None


def _is_phone_apply_cooldown(phone: str | None) -> tuple[bool, int]:
    digits = _phone_digits(phone)
    if len(digits) < 8:
        return False, 0
    now = time.monotonic()
    with _RATE_LIMIT_LOCK:
        ts = _PHONE_COOLDOWN_CACHE.get(digits)
        if ts and (now - ts) < APPLY_SAME_PHONE_COOLDOWN_SECONDS:
            return True, max(1, int(APPLY_SAME_PHONE_COOLDOWN_SECONDS - (now - ts)))
    return False, 0


def _mark_phone_apply(phone: str | None) -> None:
    digits = _phone_digits(phone)
    if len(digits) < 8:
        return
    with _RATE_LIMIT_LOCK:
        _PHONE_COOLDOWN_CACHE[digits] = time.monotonic()

def site_lead_setting_key(token: str) -> str:
    return f"{SITE_LEAD_TOKEN_PREFIX}{token}"

def save_site_lead_payload(token: str, payload: dict) -> None:
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=SITE_LEAD_TOKEN_TTL_HOURS)).isoformat()
    data = {
        "expires_at": expires_at,
        "data": payload,
    }
    set_setting(site_lead_setting_key(token), json.dumps(data, ensure_ascii=False))

def consume_site_lead_payload(token: str) -> dict | None:
    raw = get_setting(site_lead_setting_key(token))
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
    except Exception:
        set_setting(site_lead_setting_key(token), None)
        return None
    if not isinstance(parsed, dict):
        set_setting(site_lead_setting_key(token), None)
        return None
    expires_at_raw = str(parsed.get("expires_at") or "").strip()
    payload = parsed.get("data")
    if not isinstance(payload, dict):
        set_setting(site_lead_setting_key(token), None)
        return None
    if expires_at_raw:
        try:
            expires_at = datetime.fromisoformat(expires_at_raw)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > expires_at:
                set_setting(site_lead_setting_key(token), None)
                return None
        except Exception:
            set_setting(site_lead_setting_key(token), None)
            return None
    set_setting(site_lead_setting_key(token), None)
    return payload

def build_bot_stage2_link(token: str, lang: str | None = None, project: str = PROJECT_STREAMFLOW) -> str | None:
    username = project_bot_username(project).strip().lstrip("@")
    if not username:
        return None
    locale = normalize_site_lang(lang)
    return f"https://t.me/{username}?start=s2_{token}_{locale}"

def build_whatsapp_base_link() -> str | None:
    digits = re.sub(r"\D", "", INFOBIP_WHATSAPP_SENDER or "")
    if not digits:
        return None
    return f"https://wa.me/{digits}"

def build_whatsapp_stage2_link(token: str, lang: str | None = None) -> str | None:
    base = build_whatsapp_base_link()
    if not base:
        return None
    locale = normalize_site_lang(lang)
    start_payload = f"s2_{token}_{locale}"
    return f"{base}?text={urllib.parse.quote(start_payload, safe='')}"
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
    return shared_normalize_phone(text)


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

def clean_text(value: str, max_len: int | None = None) -> str:
    return shared_clean_user_text(value, max_len=max_len)


def detect_honeypot_field(fields: dict[str, str] | None) -> str | None:
    if not isinstance(fields, dict):
        return None
    for field_name in HONEYPOT_FIELD_NAMES:
        raw = clean_text(str(fields.get(field_name) or ""), max_len=MAX_HONEYPOT_LEN)
        if raw:
            return field_name
    return None


def is_valid_phone(text: str) -> bool:
    return shared_is_valid_phone(text)


def normalize_birthdate(text: str) -> str | None:
    return shared_normalize_birthdate(text)


def is_adult_birthdate(text: str, min_age: int = 18) -> bool:
    return shared_is_valid_birthdate(text, min_age=min_age)


def is_valid_birthdate(text: str) -> bool:
    return shared_is_valid_birthdate(text, min_age=18)


def has_any_digit(text: str) -> bool:
    return shared_has_any_digit(text)


YES_NO_BY_LANG = {
    "ru": {"yes": "Да", "no": "Нет"},
    "en": {"yes": "Yes", "no": "No"},
    "pt": {"yes": "Sim", "no": "Não"},
    "es": {"yes": "Sí", "no": "No"},
}


def normalize_yes_no(text: str, lang: str | None = None) -> str | None:
    value = shared_normalize_yes_no(text)
    if not value:
        return None
    raw = str(value).strip().lower()
    if raw in {"да", "yes", "sim", "sí", "si"}:
        key = "yes"
    elif raw in {"нет", "no", "não", "nao"}:
        key = "no"
    else:
        return value
    locale = normalize_site_lang(lang or "ru")
    return YES_NO_BY_LANG.get(locale, YES_NO_BY_LANG["ru"]).get(key, value)


def normalize_telegram(text: str) -> str | None:
    return shared_normalize_telegram(text)


def is_valid_email(value: str) -> bool:
    raw = (value or "").strip()
    if not raw or len(raw) > MAX_EMAIL_LEN:
        return False
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]{2,}", raw, flags=re.IGNORECASE) is not None


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
    sender_digits = re.sub(r"\D", "", INFOBIP_WHATSAPP_SENDER or "")

    def _pick_phone(candidates: list[str | None]) -> str | None:
        cleaned: list[str] = []
        for raw in candidates:
            value = _pick_first_string(raw)
            if not value:
                continue
            digits = re.sub(r"\D", "", value)
            if len(digits) < 8:
                continue
            cleaned.append(value)
        if not cleaned:
            return None
        if sender_digits:
            for value in cleaned:
                if re.sub(r"\D", "", value) != sender_digits:
                    return value
        return cleaned[0]

    for row in candidates:
        message = row.get("message") if isinstance(row.get("message"), dict) else {}
        content = row.get("content") if isinstance(row.get("content"), dict) else {}
        contact = row.get("contact") if isinstance(row.get("contact"), dict) else {}
        sender = row.get("sender") if isinstance(row.get("sender"), dict) else {}
        contact_profile = contact.get("profile") if isinstance(contact.get("profile"), dict) else {}
        interactive = row.get("interactive") if isinstance(row.get("interactive"), dict) else {}
        message_interactive = message.get("interactive") if isinstance(message.get("interactive"), dict) else {}
        content_interactive = content.get("interactive") if isinstance(content.get("interactive"), dict) else {}
        message_text_obj = message.get("text") if isinstance(message.get("text"), dict) else {}
        content_text_obj = content.get("text") if isinstance(content.get("text"), dict) else {}
        message_media = message.get("media") if isinstance(message.get("media"), dict) else {}
        content_media = content.get("media") if isinstance(content.get("media"), dict) else {}

        from_phone = _pick_phone(
            [
                contact.get("phoneNumber"),
                contact.get("waId"),
                row.get("from"),
                sender.get("phoneNumber"),
                sender.get("from"),
                row.get("senderAddress"),
            ]
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
            row.get("payload"),
            message.get("payload"),
            content.get("payload"),
            message.get("title"),
            content.get("title"),
            message.get("buttonText"),
            content.get("buttonText"),
            interactive.get("title"),
            interactive.get("id"),
            message_interactive.get("title"),
            message_interactive.get("id"),
            content_interactive.get("title"),
            content_interactive.get("id"),
            message_text_obj.get("body"),
            message_text_obj.get("text"),
            message_text_obj.get("title"),
            content_text_obj.get("body"),
            content_text_obj.get("text"),
            content_text_obj.get("title"),
        )
        media_url = _pick_first_string(
            message.get("url"),
            content.get("url"),
            row.get("url"),
            message_media.get("url"),
            content_media.get("url"),
            message.get("imageUrl"),
            content.get("imageUrl"),
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
        has_user_payload = bool((text or "").strip() or (media_url or "").strip())
        if not has_user_payload:
            continue
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


def _extract_infobip_statuses(payload: dict | None) -> list[dict]:
    if not isinstance(payload, dict):
        return []
    items = payload.get("results")
    if not isinstance(items, list):
        return []
    statuses: list[dict] = []
    for row in items:
        if not isinstance(row, dict):
            continue
        status = row.get("status") if isinstance(row.get("status"), dict) else {}
        if not status:
            continue
        statuses.append(
            {
                "to": _pick_first_string(row.get("to"), row.get("destination")),
                "messageId": _pick_first_string(row.get("messageId"), row.get("id")),
                "groupName": _pick_first_string(status.get("groupName")),
                "name": _pick_first_string(status.get("name")),
                "description": _pick_first_string(status.get("description")),
            }
        )
    return statuses


def _infobip_dedupe_key(message: dict) -> str:
    signature = (
        message.get("message_id")
        or f"{message.get('from')}|{message.get('to')}|{message.get('type')}|{message.get('text')}|{message.get('received_at')}"
    )
    digest = hashlib.sha1(
        str(signature).encode("utf-8"),
        usedforsecurity=False,
    ).hexdigest()[:20]
    return f"infobip_seen:{digest}"


def _is_infobip_seen(message: dict) -> bool:
    key = _infobip_dedupe_key(message)
    return bool(get_setting(key))


def _mark_infobip_seen(message: dict) -> None:
    key = _infobip_dedupe_key(message)
    set_setting(key, datetime.now(timezone.utc).isoformat())


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


def wa_t(lang: str, key: str) -> str:
    locale = normalize_site_lang(lang)
    return WA_TEXTS.get(locale, WA_TEXTS["ru"]).get(key, WA_TEXTS["ru"].get(key, ""))


def _wa_digits(phone: str | None) -> str:
    return re.sub(r"\D", "", phone or "")


def _wa_phone_e164(phone: str | None) -> str | None:
    digits = _wa_digits(phone)
    if not digits:
        return None
    if len(digits) < 8:
        return None
    return f"+{digits}"


def _wa_flow_key(phone: str | None) -> str | None:
    digits = _wa_digits(phone)
    if not digits:
        return None
    return f"{WHATSAPP_FLOW_PREFIX}{digits}"


def _load_wa_flow(phone: str | None) -> dict:
    key = _wa_flow_key(phone)
    if not key:
        return {}
    raw = get_setting(key)
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _save_wa_flow(phone: str | None, data: dict) -> None:
    key = _wa_flow_key(phone)
    if not key:
        return
    set_setting(key, json.dumps(data, ensure_ascii=False))


def _wa_user_id(phone: str | None) -> int | None:
    digits = _wa_digits(phone)
    if not digits:
        return None
    # Stable pseudo-user ID for non-Telegram channels.
    digest = hashlib.sha1(
        digits.encode("utf-8"),
        usedforsecurity=False,
    ).hexdigest()[:15]
    value = int(digest, 16)
    return -value


def _is_wa_sender_number(phone: str | None) -> bool:
    incoming = _wa_digits(phone)
    sender = _wa_digits(INFOBIP_WHATSAPP_SENDER)
    return bool(incoming and sender and incoming == sender)


def _parse_wa_lang_choice(text: str | None) -> str | None:
    raw = (text or "").strip().lower()
    if not raw:
        return None
    compact = re.sub(r"\s+", "", raw)
    for lang, aliases in WA_LANG_ALIASES.items():
        if raw in aliases or compact in aliases:
            return lang
    if "рус" in raw:
        return "ru"
    if "english" in raw:
        return "en"
    if "portu" in raw or "brasil" in raw:
        return "pt"
    if "espa" in raw:
        return "es"
    return None


def _parse_wa_menu_choice(text: str | None) -> str | None:
    raw = (text or "").strip().lower()
    if not raw:
        return None
    compact = re.sub(r"\s+", " ", raw)
    for key, aliases in WA_MENU_ALIASES.items():
        if raw in aliases or compact in aliases:
            return key
    return None


def _wa_manager_link() -> str | None:
    digits = _wa_digits(WA_MANAGER_PHONE)
    if len(digits) < 8:
        return None
    return f"https://wa.me/{digits}"


def _wa_menu_text_for_step(lang: str, step: str) -> str:
    active_step = str(step or "menu").strip().lower()
    if active_step == "lang":
        return wa_t(lang, "choose_lang")
    if active_step == "lang_more":
        return wa_t(lang, "lang_more")
    if active_step == "menu_more":
        return wa_t(lang, "menu_more")
    if active_step == "about_menu":
        return wa_t(lang, "about_menu")
    if active_step == "portfolio_menu":
        return wa_t(lang, "portfolio_menu")
    return wa_t(lang, "menu")


def _wa_menu_response(lang: str, menu_key: str, step: str = "menu") -> str:
    site_link = (SITE_URL or "https://streamflowagency.com").strip().rstrip("/")
    channel_link = (CHANNEL_LINK or "https://t.me/streamflowagency").strip()
    manager_link = _wa_manager_link()
    locale = normalize_site_lang(lang)
    channel_titles = {
        "ru": "📣 Канал",
        "en": "📣 Channel",
        "pt": "📣 Canal",
        "es": "📣 Canal",
    }
    manager_titles = {
        "ru": "💬 Связь с менеджером",
        "en": "💬 Manager contact",
        "pt": "💬 Falar com gerente",
        "es": "💬 Contactar manager",
    }
    if menu_key == "menu":
        return _wa_menu_text_for_step(lang, "menu")
    if menu_key == "site":
        return f"🌐 {site_link}\n\n{_wa_menu_text_for_step(lang, step)}"
    if menu_key == "portfolio":
        return _wa_menu_text_for_step(lang, "portfolio_menu")
    if menu_key == "about":
        return _wa_menu_text_for_step(lang, "about_menu")
    if menu_key == "manager":
        if manager_link:
            return f"{manager_titles.get(locale, manager_titles['ru'])}\n{manager_link}"
        return _wa_menu_text_for_step(lang, "menu")
    if menu_key == "channel":
        return f"{channel_titles.get(locale, channel_titles['ru'])}\n{channel_link}"
    return _wa_menu_text_for_step(lang, step)


def _wa_media_sort_key(path: Path) -> tuple[int, str]:
    match = re.search(r"(\d+)(?!.*\d)", path.stem)
    order = int(match.group(1)) if match else 10_000
    return order, path.name.lower()


def _site_asset_url(path: str) -> str:
    site = (SITE_URL or "https://streamflowagency.com").strip().rstrip("/")
    suffix = f"/{path.lstrip('/')}"
    return f"{site}{suffix}"


def _wa_portfolio_sources() -> dict[str, dict]:
    return {
        "cases": {
            "globs": [
                "assets/portfolio/*.jpg",
                "assets/models/income-*.jpg",
                "assets/models/model-*.jpg",
                "assets/models/milena.jpg",
                "assets/models/confident.jpg",
            ],
            "media_type": "IMAGE",
            "title": {
                "ru": "Портфолио Streamflow",
                "en": "Streamflow portfolio",
                "pt": "Portfólio Streamflow",
                "es": "Portafolio Streamflow",
            },
        },
    }


def _wa_portfolio_items(kind: str) -> list[dict]:
    source = _wa_portfolio_sources().get(kind) or _wa_portfolio_sources()["cases"]
    patterns = source.get("globs")
    if not isinstance(patterns, list) or not patterns:
        legacy = source.get("glob")
        patterns = [legacy] if isinstance(legacy, str) and legacy.strip() else []
    found_files: list[Path] = []
    for pattern in patterns:
        found_files.extend(list(WEB_DIR.glob(pattern)))
    unique_files = sorted({path.resolve(): path for path in found_files}.values(), key=_wa_media_sort_key)
    items: list[dict] = []
    for file_path in unique_files:
        rel = file_path.relative_to(WEB_DIR).as_posix()
        items.append(
            {
                "kind": kind,
                "title": source["title"],
                "media_type": source["media_type"],
                "url": _site_asset_url(rel),
            }
        )
    return items


def _wa_portfolio_caption(lang: str, item: dict, index: int, total: int) -> str:
    locale = normalize_site_lang(lang)
    titles = item.get("title") if isinstance(item.get("title"), dict) else {}
    title = str(titles.get(locale) or titles.get("ru") or "Portfolio")
    hint_by_lang = {
        "ru": (
            "Листай фото кнопками ниже ⬇️\n"
            "Если понравился формат, жми «Заявка» в меню и начнём."
        ),
        "en": (
            "Browse photos with buttons below ⬇️\n"
            "If you like the format, tap Apply in menu to start."
        ),
        "pt": (
            "Navegue pelas fotos nos botões abaixo ⬇️\n"
            "Se curtir o formato, toque em candidatura no menu."
        ),
        "es": (
            "Navega por fotos con los botones de abajo ⬇️\n"
            "Si te gusta el formato, toca solicitud en el menú."
        ),
    }
    hint = hint_by_lang.get(locale, hint_by_lang["ru"])
    frame_word = {"ru": "Кадр", "en": "Frame", "pt": "Foto", "es": "Foto"}
    frame = frame_word.get(locale, frame_word["ru"])
    return f"📁 {title}\n{frame} {index + 1}/{max(total, 1)}\n\n{hint}".strip()


def _wa_portfolio_buttons(lang: str, index: int, total: int) -> list[dict]:
    locale = normalize_site_lang(lang)
    prev_title = {"ru": "⬅️ Назад", "en": "⬅️ Back", "pt": "⬅️ Voltar", "es": "⬅️ Atrás"}
    next_title = {"ru": "Вперёд ➡️", "en": "Next ➡️", "pt": "Avançar ➡️", "es": "Siguiente ➡️"}
    menu_title = {"ru": "🏠 Меню", "en": "🏠 Menu", "pt": "🏠 Menu", "es": "🏠 Menú"}
    buttons: list[dict] = []
    if total > 1:
        if index > 0:
            buttons.append({"id": "portfolio_prev", "title": prev_title.get(locale, prev_title["ru"])})
        if index < total - 1 and len(buttons) < 2:
            buttons.append({"id": "portfolio_next", "title": next_title.get(locale, next_title["ru"])})
    buttons.append({"id": "menu", "title": menu_title.get(locale, menu_title["ru"])})
    return buttons[:3]


def _wa_portfolio_item_from_flow(flow: dict | None) -> tuple[dict | None, int, int, str]:
    data = flow.get("data") if isinstance(flow, dict) and isinstance(flow.get("data"), dict) else {}
    kind = str(data.get("portfolio_kind") or "cases").strip().lower()
    if kind not in _wa_portfolio_sources():
        kind = "cases"
    items = _wa_portfolio_items(kind)
    if not items:
        return None, 0, 0, kind
    try:
        index = int(data.get("portfolio_index") or 0)
    except Exception:
        index = 0
    if index < 0:
        index = 0
    if index >= len(items):
        index = len(items) - 1
    return items[index], index, len(items), kind


def _wa_start_portfolio_flow(from_phone: str, lang: str, mode: str = "quick") -> str:
    items = _wa_portfolio_items("cases")
    if not items:
        _save_wa_flow(from_phone, {"mode": "quick", "step": "menu", "lang": lang, "data": {}})
        empty_by_lang = {
            "ru": "📁 Портфолио пока обновляется. Попробуй позже.",
            "en": "📁 Portfolio is being updated right now. Please try again later.",
            "pt": "📁 O portfólio está sendo atualizado agora. Tente novamente mais tarde.",
            "es": "📁 El portafolio se está actualizando. Inténtalo más tarde.",
        }
        locale = normalize_site_lang(lang)
        return empty_by_lang.get(locale, empty_by_lang["ru"])
    first_item = items[0]
    _save_wa_flow(
        from_phone,
        {
            "mode": mode,
            "step": "portfolio_view",
            "lang": lang,
            "data": {"portfolio_kind": "cases", "portfolio_index": 0},
        },
    )
    return _wa_portfolio_caption(lang, first_item, 0, len(items))


def _is_wa_reset_command(text: str | None) -> bool:
    raw = (text or "").strip().lower()
    return raw in WA_RESET_COMMANDS


def _parse_wa_yes_no_choice(text: str | None, lang: str) -> str | None:
    raw = clean_text(text or "", max_len=32).lower()
    if not raw:
        return None
    if raw in WA_YES_ALIASES:
        return "Да"
    if raw in WA_NO_ALIASES:
        return "Нет"
    return normalize_yes_no(raw, lang=lang)


def _build_admin_whatsapp_application_text(data: dict, user_id: int, submitted_at: str) -> str:
    prepared = dict(data or {})
    wa_contact = prepared.get("whatsapp") or prepared.get("wa_phone")
    if not prepared.get("telegram"):
        prepared["telegram"] = f"wa:{_wa_digits(wa_contact or '')}" if wa_contact else "—"
    return build_admin_full_text(prepared, str(user_id), submitted_at, source_label="WhatsApp")


def _wa_media_url(value: str | None) -> str | None:
    raw = (value or "").strip()
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    return None


def _download_wa_photo(url: str) -> tuple[bytes, str] | None:
    headers = {"Accept": "*/*"}
    if INFOBIP_API_KEY and "infobip" in url.lower():
        headers["Authorization"] = f"App {INFOBIP_API_KEY}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=20, context=get_ssl_context()) as resp:
            data = resp.read()
            content_type = (resp.headers.get("Content-Type", "") or "").split(";", 1)[0].strip().lower()
            if not content_type.startswith("image/"):
                content_type = "image/jpeg"
            if not data:
                return None
            return data, content_type
    except Exception as err:
        print("Failed to download WhatsApp photo:", err)
        return None


def _extract_telegram_photo_file_id(payload: dict | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    message = payload.get("result")
    if not isinstance(message, dict):
        return None
    photos = message.get("photo")
    if not isinstance(photos, list):
        return None
    for item in reversed(photos):
        if not isinstance(item, dict):
            continue
        file_id = str(item.get("file_id") or "").strip()
        if file_id:
            return file_id
    return None


def _send_whatsapp_photo_to_admin(url: str, filename: str) -> str | None:
    try:
        result = telegram_request("sendPhoto", {"chat_id": str(ADMIN_GROUP_ID), "photo": url})
        file_id = _extract_telegram_photo_file_id(result)
        if file_id:
            return file_id
    except Exception as err:
        print("sendPhoto by URL failed:", err)

    downloaded = _download_wa_photo(url)
    if not downloaded:
        return None
    payload, content_type = downloaded
    try:
        result = telegram_request(
            "sendPhoto",
            {"chat_id": str(ADMIN_GROUP_ID)},
            files={
                "photo": {
                    "filename": filename,
                    "content_type": content_type,
                    "data": payload,
                }
            },
        )
        file_id = _extract_telegram_photo_file_id(result)
        if file_id:
            return file_id
    except Exception as err:
        print("sendPhoto by upload failed:", err)
    return None


def _build_admin_whatsapp_keyboard(user_id: int, wa_phone: str | None) -> dict:
    wa_link = _wa_open_link(wa_phone)
    rows: list[list[dict]] = [
        [
            {"text": "✅ Принять", "callback_data": f"admin_accept:{user_id}"},
            {"text": "❌ Отклонить", "callback_data": f"admin_reject:{user_id}"},
        ]
    ]
    if wa_link:
        rows.append([{"text": "💬 Открыть WhatsApp", "url": wa_link}])
    return {"inline_keyboard": rows}


def _send_application_to_admin_from_whatsapp(
    data: dict,
    user_id: int,
    wa_phone: str | None,
    source: str = "whatsapp_bot",
    status: str = "pending",
) -> None:
    if not BOT_TOKEN or not ADMIN_GROUP_ID:
        return
    photo_refs_changed = False
    for field, filename in (
        ("photo_face", f"wa_face_{abs(user_id)}.jpg"),
        ("photo_full", f"wa_full_{abs(user_id)}.jpg"),
    ):
        raw_url = data.get(field)
        media_url = _wa_media_url(raw_url)
        if not media_url:
            continue
        try:
            file_id = _send_whatsapp_photo_to_admin(media_url, filename)
            if file_id:
                data[field] = file_id
                photo_refs_changed = True
        except Exception as err:
            print("Failed to send WhatsApp photo to admin:", err)
    if photo_refs_changed:
        try:
            save_web_application(user_id, data, source=source, status=status)
        except Exception as err:
            print("Failed to persist Telegram photo file_id for WhatsApp application:", err)
    # Полная карточка больше не отправляется отдельным сообщением в админ-чат.
    # Уведомление и просмотр выполняются через общее админ-меню.
    try:
        set_admin_message_id(user_id, None)
    except Exception:
        pass


def infobip_send_whatsapp_text(to_phone: str | None, text: str) -> bool:
    to_e164 = _wa_phone_e164(to_phone)
    if not to_e164 or not text.strip():
        return False
    if not INFOBIP_API_KEY or not INFOBIP_BASE_URL or not INFOBIP_WHATSAPP_SENDER:
        print("Infobip send skipped: INFOBIP_API_KEY / INFOBIP_BASE_URL / INFOBIP_WHATSAPP_SENDER is missing")
        return False

    payload = {
        "from": INFOBIP_WHATSAPP_SENDER,
        "to": to_e164,
        "content": {"text": text.strip()},
    }
    req = urllib.request.Request(
        f"{INFOBIP_BASE_URL}/whatsapp/1/message/text",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"App {INFOBIP_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20, context=get_ssl_context()) as resp:
            resp.read()
        return True
    except urllib.error.HTTPError as err:
        try:
            details = err.read().decode("utf-8", errors="replace")
        except Exception:
            details = ""
        print(f"Infobip send failed HTTP {err.code}: {details}")
        return False
    except Exception as err:
        print("Infobip send failed:", err)
        return False


def _wa_menu_image_url() -> str:
    if WA_MENU_IMAGE_URL:
        return WA_MENU_IMAGE_URL
    site = (SITE_URL or "https://streamflowagency.com").strip().rstrip("/")
    return f"{site}/assets/wa-menu.jpg"


def infobip_send_whatsapp_image(to_phone: str | None, image_url: str, caption: str | None = None) -> bool:
    to_e164 = _wa_phone_e164(to_phone)
    media_url = clean_text(image_url, max_len=MAX_URL_VALUE_LEN)
    if not to_e164 or not media_url:
        return False
    if not INFOBIP_API_KEY or not INFOBIP_BASE_URL or not INFOBIP_WHATSAPP_SENDER:
        return False
    payload = {
        "from": INFOBIP_WHATSAPP_SENDER,
        "to": to_e164,
        "content": {
            "mediaUrl": media_url,
        },
    }
    caption_value = clean_text(caption or "", max_len=500)
    if caption_value:
        payload["content"]["caption"] = caption_value
    req = urllib.request.Request(
        f"{INFOBIP_BASE_URL}/whatsapp/1/message/image",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"App {INFOBIP_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20, context=get_ssl_context()) as resp:
            resp.read()
        return True
    except urllib.error.HTTPError as err:
        try:
            details = err.read().decode("utf-8", errors="replace")
        except Exception:
            details = ""
        print(f"Infobip image send failed HTTP {err.code}: {details}")
        return False
    except Exception as err:
        print("Infobip image send failed:", err)
        return False


def infobip_send_whatsapp_interactive_list(
    to_phone: str | None,
    body_text: str,
    action_title: str,
    sections: list[dict],
) -> bool:
    to_e164 = _wa_phone_e164(to_phone)
    if not to_e164:
        return False
    if not INFOBIP_API_KEY or not INFOBIP_BASE_URL or not INFOBIP_WHATSAPP_SENDER:
        return False
    if not body_text.strip() or not action_title.strip() or not sections:
        return False

    payload = {
        "from": INFOBIP_WHATSAPP_SENDER,
        "to": to_e164,
        "content": {
            "body": {"text": body_text.strip()},
            "action": {
                "title": action_title.strip(),
                "sections": sections,
            },
        },
    }

    req = urllib.request.Request(
        f"{INFOBIP_BASE_URL}/whatsapp/1/message/interactive/list",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"App {INFOBIP_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20, context=get_ssl_context()) as resp:
            resp.read()
        return True
    except urllib.error.HTTPError as err:
        try:
            details = err.read().decode("utf-8", errors="replace")
        except Exception:
            details = ""
        print(f"Infobip interactive list failed HTTP {err.code}: {details}")
        return False
    except Exception as err:
        print("Infobip interactive list failed:", err)
        return False


def infobip_send_whatsapp_interactive_buttons(
    to_phone: str | None,
    body_text: str,
    buttons: list[dict],
    *,
    header_media_url: str | None = None,
    header_media_type: str | None = None,
) -> bool:
    to_e164 = _wa_phone_e164(to_phone)
    if not to_e164:
        return False
    if not INFOBIP_API_KEY or not INFOBIP_BASE_URL or not INFOBIP_WHATSAPP_SENDER:
        return False
    if not body_text.strip() or not buttons:
        return False

    normalized_buttons: list[dict] = []
    for row in buttons[:3]:
        button_id = clean_text(str(row.get("id") or ""), max_len=60)
        title = clean_text(str(row.get("title") or ""), max_len=20)
        if not button_id or not title:
            continue
        normalized_buttons.append({"type": "REPLY", "id": button_id, "title": title})
    if not normalized_buttons:
        return False

    normalized_header_url = clean_text(header_media_url or "", max_len=MAX_URL_VALUE_LEN)
    normalized_header_type = (header_media_type or "").strip().upper()
    if normalized_header_type not in {"IMAGE", "VIDEO", "DOCUMENT"}:
        normalized_header_type = "IMAGE"

    def _send(include_header: bool) -> bool:
        payload = {
            "from": INFOBIP_WHATSAPP_SENDER,
            "to": to_e164,
            "content": {
                "body": {"text": body_text.strip()},
                "action": {
                    "buttons": normalized_buttons,
                },
            },
        }
        if include_header and normalized_header_url:
            payload["content"]["header"] = {
                "type": normalized_header_type,
                "mediaUrl": normalized_header_url,
            }
        req = urllib.request.Request(
            f"{INFOBIP_BASE_URL}/whatsapp/1/message/interactive/buttons",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"App {INFOBIP_API_KEY}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=20, context=get_ssl_context()) as resp:
                resp.read()
            return True
        except urllib.error.HTTPError as err:
            try:
                details = err.read().decode("utf-8", errors="replace")
            except Exception:
                details = ""
            print(f"Infobip interactive buttons failed HTTP {err.code}: {details}")
            return False
        except Exception as err:
            print("Infobip interactive buttons failed:", err)
            return False

    if normalized_header_url and _send(include_header=True):
        return True
    return _send(include_header=False)


def _wa_menu_buttons_config(lang: str, step: str) -> tuple[str, list[dict]]:
    locale = normalize_site_lang(lang)
    active_step = str(step or "menu").strip().lower()
    if active_step == "lang":
        if locale == "en":
            return wa_t(locale, "choose_lang"), [
                {"id": "lang_ru", "title": "Russian"},
                {"id": "lang_en", "title": "English"},
                {"id": "menu_lang_more", "title": "PT / ES"},
            ]
        if locale == "pt":
            return wa_t(locale, "choose_lang"), [
                {"id": "lang_ru", "title": "Russo"},
                {"id": "lang_en", "title": "Inglês"},
                {"id": "menu_lang_more", "title": "PT / ES"},
            ]
        if locale == "es":
            return wa_t(locale, "choose_lang"), [
                {"id": "lang_ru", "title": "Ruso"},
                {"id": "lang_en", "title": "Ingles"},
                {"id": "menu_lang_more", "title": "PT / ES"},
            ]
        return wa_t("ru", "choose_lang"), [
            {"id": "lang_ru", "title": "Русский"},
            {"id": "lang_en", "title": "English"},
            {"id": "menu_lang_more", "title": "PT / ES"},
        ]

    if active_step == "lang_more":
        if locale == "en":
            return wa_t(locale, "lang_more"), [
                {"id": "lang_pt", "title": "Portuguese"},
                {"id": "lang_es", "title": "Spanish"},
                {"id": "menu_lang_back", "title": "Back"},
            ]
        if locale == "pt":
            return wa_t(locale, "lang_more"), [
                {"id": "lang_pt", "title": "Portugues"},
                {"id": "lang_es", "title": "Espanhol"},
                {"id": "menu_lang_back", "title": "Voltar"},
            ]
        if locale == "es":
            return wa_t(locale, "lang_more"), [
                {"id": "lang_pt", "title": "Portugues"},
                {"id": "lang_es", "title": "Espanol"},
                {"id": "menu_lang_back", "title": "Volver"},
            ]
        return wa_t("ru", "lang_more"), [
            {"id": "lang_pt", "title": "Portugues"},
            {"id": "lang_es", "title": "Espanol"},
            {"id": "menu_lang_back", "title": "Назад"},
        ]

    if active_step == "menu_more":
        if locale == "en":
            return wa_t(locale, "menu_more"), [
                {"id": "menu_channel", "title": "Channel"},
                {"id": "menu_manager", "title": "Manager"},
                {"id": "menu_language", "title": "Language"},
            ]
        if locale == "pt":
            return wa_t(locale, "menu_more"), [
                {"id": "menu_channel", "title": "Canal"},
                {"id": "menu_manager", "title": "Gerente"},
                {"id": "menu_language", "title": "Idioma"},
            ]
        if locale == "es":
            return wa_t(locale, "menu_more"), [
                {"id": "menu_channel", "title": "Canal"},
                {"id": "menu_manager", "title": "Manager"},
                {"id": "menu_language", "title": "Idioma"},
            ]
        return wa_t("ru", "menu_more"), [
            {"id": "menu_channel", "title": "Канал"},
            {"id": "menu_manager", "title": "Менеджер"},
            {"id": "menu_language", "title": "Язык"},
        ]

    if active_step == "about_menu":
        if locale == "en":
            return wa_t(locale, "about_menu"), [
                {"id": "menu_apply", "title": "Apply"},
                {"id": "menu_more", "title": "More"},
                {"id": "menu", "title": "Menu"},
            ]
        if locale == "pt":
            return wa_t(locale, "about_menu"), [
                {"id": "menu_apply", "title": "Candidatura"},
                {"id": "menu_more", "title": "Mais"},
                {"id": "menu", "title": "Menu"},
            ]
        if locale == "es":
            return wa_t(locale, "about_menu"), [
                {"id": "menu_apply", "title": "Solicitud"},
                {"id": "menu_more", "title": "Más"},
                {"id": "menu", "title": "Menu"},
            ]
        return wa_t("ru", "about_menu"), [
            {"id": "menu_apply", "title": "Заявка"},
            {"id": "menu_more", "title": "Ещё"},
            {"id": "menu", "title": "Меню"},
        ]

    if locale == "en":
        return wa_t(locale, "menu"), [
            {"id": "menu_apply", "title": "Apply"},
            {"id": "menu_portfolio", "title": "Portfolio"},
            {"id": "menu_about", "title": "About"},
        ]
    if locale == "pt":
        return wa_t(locale, "menu"), [
            {"id": "menu_apply", "title": "Candidatura"},
            {"id": "menu_portfolio", "title": "Portfólio"},
            {"id": "menu_about", "title": "Sobre"},
        ]
    if locale == "es":
        return wa_t(locale, "menu"), [
            {"id": "menu_apply", "title": "Solicitud"},
            {"id": "menu_portfolio", "title": "Portafolio"},
            {"id": "menu_about", "title": "Info"},
        ]
    return wa_t("ru", "menu"), [
        {"id": "menu_apply", "title": "Заявка"},
        {"id": "menu_portfolio", "title": "Портфолио"},
        {"id": "menu_about", "title": "О работе"},
    ]


def _wa_yes_no_buttons(lang: str) -> list[dict]:
    locale = normalize_site_lang(lang)
    if locale == "en":
        return [{"id": "yn_yes", "title": "Yes"}, {"id": "yn_no", "title": "No"}]
    if locale == "pt":
        return [{"id": "yn_yes", "title": "Sim"}, {"id": "yn_no", "title": "Nao"}]
    if locale == "es":
        return [{"id": "yn_yes", "title": "Si"}, {"id": "yn_no", "title": "No"}]
    return [{"id": "yn_yes", "title": "Да"}, {"id": "yn_no", "title": "Нет"}]


def send_wa_interactive_controls(to_phone: str | None, body_override: str | None = None) -> bool:
    if not INFOBIP_INTERACTIVE_ENABLED:
        return False
    flow = _load_wa_flow(to_phone)
    if not flow:
        return False
    step = str(flow.get("step") or "").strip().lower()
    lang = normalize_site_lang(flow.get("lang"))

    if step in {"lang", "lang_more", "menu", "menu_more", "about_menu"}:
        body, buttons = _wa_menu_buttons_config(lang, step)
        custom_body = clean_text(body_override or "", max_len=900)
        if custom_body:
            body = custom_body
        use_menu_header = step in {"menu", "menu_more"}
        return infobip_send_whatsapp_interactive_buttons(
            to_phone,
            body,
            buttons,
            header_media_url=_wa_menu_image_url() if use_menu_header else None,
            header_media_type="IMAGE" if use_menu_header else None,
        )

    if step == "portfolio_menu":
        locale = normalize_site_lang(lang)
        open_title = {"ru": "Открыть", "en": "Open", "pt": "Abrir", "es": "Abrir"}
        apply_title = {"ru": "Заявка", "en": "Apply", "pt": "Candidatura", "es": "Solicitud"}
        menu_title = {"ru": "Меню", "en": "Menu", "pt": "Menu", "es": "Menu"}
        body = wa_t(lang, "portfolio_menu")
        custom_body = clean_text(body_override or "", max_len=900)
        if custom_body:
            body = custom_body
        return infobip_send_whatsapp_interactive_buttons(
            to_phone,
            body,
            [
                {"id": "menu_portfolio", "title": open_title.get(locale, open_title["ru"])},
                {"id": "menu_apply", "title": apply_title.get(locale, apply_title["ru"])},
                {"id": "menu", "title": menu_title.get(locale, menu_title["ru"])},
            ],
        )

    if step == "portfolio_view":
        item, index, total, _ = _wa_portfolio_item_from_flow(flow)
        if not item:
            return False
        body = _wa_portfolio_caption(lang, item, index, total)
        custom_body = clean_text(body_override or "", max_len=900)
        if custom_body:
            body = custom_body
        header_media_url = clean_text(str(item.get("url") or ""), max_len=MAX_URL_VALUE_LEN)
        header_media_type = str(item.get("media_type") or "IMAGE").strip().upper()
        buttons = _wa_portfolio_buttons(lang, index, total)
        if infobip_send_whatsapp_interactive_buttons(
            to_phone,
            body,
            buttons,
            header_media_url=header_media_url,
            header_media_type=header_media_type,
        ):
            return True
        media_sent = False
        if header_media_url and header_media_type == "IMAGE":
            media_sent = infobip_send_whatsapp_image(to_phone, header_media_url, caption=body)
        buttons_sent = infobip_send_whatsapp_interactive_buttons(to_phone, body, buttons)
        return media_sent or buttons_sent

    if step == "living":
        mode = str(flow.get("mode") or "quick").strip().lower()
        body = _wa_stage2_text(lang, "living") if mode == "site_stage2" else wa_t(lang, "ask_living")
        custom_body = clean_text(body_override or "", max_len=900)
        if custom_body:
            body = custom_body
        return infobip_send_whatsapp_interactive_buttons(to_phone, body, _wa_yes_no_buttons(lang))

    return False


def _next_wa_step_message(lang: str, step: str) -> str:
    mapping = {
        "name": "ask_name",
        "phone": "ask_phone",
        "age": "ask_age",
        "device_model": "ask_device",
        "telegram": "ask_telegram",
    }
    key = mapping.get(step, "ask_name")
    return wa_t(lang, key)


def _parse_site_stage2_command(text: str | None) -> tuple[str, str | None] | None:
    raw = (text or "").strip()
    if not raw:
        return None
    if raw.startswith("/start"):
        parts = raw.split(maxsplit=1)
        raw = parts[1].strip() if len(parts) > 1 else ""
    match = re.fullmatch(r"s2_([a-zA-Z0-9]{12,64})(?:_([a-z]{2}))?", raw, flags=re.IGNORECASE)
    if not match:
        return None
    token = match.group(1)
    lang = match.group(2).lower() if match.group(2) else None
    return token, lang


def _build_site_stage2_flow(
    from_phone: str,
    profile_name: str | None,
    lead: dict,
    fallback_user_id: int | None = None,
    preferred_lang: str | None = None,
) -> str | None:
    chosen_lang = normalize_site_lang(preferred_lang or lead.get("lang") or "ru")
    user_id = lead.get("site_pending_user_id")
    try:
        user_id = int(user_id)
    except Exception:
        user_id = fallback_user_id
    if user_id is None:
        user_id = _wa_user_id(from_phone)
    if user_id is None:
        return None

    stage_data = {
        "name": clean_text(str(lead.get("name") or "")),
        "phone": normalize_phone(str(lead.get("phone") or "")) or from_phone,
        "age": normalize_birthdate(str(lead.get("age") or "")) or clean_text(str(lead.get("age") or "")),
        "device_model": clean_text(str(lead.get("device_model") or "")),
        "telegram": clean_text(str(lead.get("telegram") or "")),
        "whatsapp": normalize_phone(str(lead.get("whatsapp") or "")) or from_phone,
        "preferred_contact": clean_text(str(lead.get("preferred_contact") or "")) or "telegram",
        "country": clean_text(str(lead.get("country") or "")),
        "lang": chosen_lang,
        "application_stage": "full",
        "site_lead_token": clean_text(str(lead.get("site_lead_token") or "")),
        "site_pending_user_id": user_id,
        "wa_phone": from_phone,
        "wa_profile_name": clean_text(profile_name or ""),
    }
    _save_wa_flow(
        from_phone,
        {
            "mode": "site_stage2",
            "step": "living",
            "lang": chosen_lang,
            "user_id": user_id,
            "source": "site_whatsapp",
            "data": stage_data,
        },
    )
    return f"{_wa_stage2_text(chosen_lang, 'intro')}\n\n{_wa_stage2_text(chosen_lang, 'living')}"


def _resume_site_stage2_from_phone(from_phone: str, profile_name: str | None) -> str | None:
    try:
        recent = find_recent_site_lead_by_phone(from_phone)
    except Exception as err:
        print("Failed to lookup site lead by WhatsApp phone:", err)
        return None
    if not recent:
        return None

    lead = dict(recent.get("data") if isinstance(recent.get("data"), dict) else {})
    if not lead:
        return None

    token = clean_text(str(lead.get("site_lead_token") or ""))
    if token:
        consumed = consume_site_lead_payload(token)
        if isinstance(consumed, dict) and consumed:
            lead = consumed
            lead.setdefault("site_lead_token", token)

    return _build_site_stage2_flow(
        from_phone,
        profile_name,
        lead,
        fallback_user_id=recent.get("user_id"),
        preferred_lang=lead.get("lang"),
    )


def _wa_stage2_text(lang: str, key: str) -> str:
    locale = normalize_site_lang(lang)
    texts = {
        "ru": {
            "intro": (
                "✨ Первый этап с сайта уже сохранён.\n"
                "Сейчас быстро дозаполним анкету здесь (2-3 минуты)."
            ),
            "living": "1/6 Есть ли помещение без посторонних? Ответь: да или нет.",
            "living_invalid": "Ответь, пожалуйста, да или нет.",
            "city": "2/6 Город и страна проживания:",
            "city_invalid": "Напиши город и страну полностью.",
            "work_time": "3/6 Сколько часов в день готова работать?",
            "work_time_invalid": "Укажи часы цифрами, например: 6",
            "experience": "4/6 Есть ли опыт? Если нет — так и напиши.",
            "experience_invalid": "Напиши пару слов про опыт (или что опыта нет).",
            "photo_face": "5/6 Пришли фото анфас (нужно для быстрой проверки, конфиденциально).",
            "photo_face_invalid": "Нужна именно фотография анфас (изображение).",
            "photo_full": "6/6 Пришли фото в полный рост (конфиденциально, только для проверки анкеты).",
            "photo_full_invalid": "Нужна именно фотография в полный рост (изображение).",
            "done": "✅ Готово. Полная анкета отправлена менеджеру.",
            "expired": "⚠️ Ссылка устарела. Оставь новую заявку на сайте.",
        },
        "en": {
            "intro": "✨ Your first stage from the website is saved.\nNow let’s finish the form here (about 2-3 minutes).",
            "living": "1/6 Do you have a private room without interruptions? Reply: yes or no.",
            "living_invalid": "Please reply yes or no.",
            "city": "2/6 Your city and country:",
            "city_invalid": "Please enter city and country.",
            "work_time": "3/6 How many hours per day can you work?",
            "work_time_invalid": "Please enter hours as a number, example: 6",
            "experience": "4/6 Do you have experience? If not, write “no experience”.",
            "experience_invalid": "Please add a short experience note.",
            "photo_face": "5/6 Send a front-face photo (used for fast review, kept confidential).",
            "photo_face_invalid": "Please send an image (front-face photo).",
            "photo_full": "6/6 Send a full-body photo (confidential, only for profile review).",
            "photo_full_invalid": "Please send an image (full-body photo).",
            "done": "✅ Done. Your full application was sent to the manager.",
            "expired": "⚠️ This link has expired. Please submit a new form on the website.",
        },
        "pt": {
            "intro": "✨ A primeira etapa do site já foi salva.\nAgora vamos concluir aqui (2-3 minutos).",
            "living": "1/6 Você tem um ambiente privado sem interrupções? Responda: sim ou não.",
            "living_invalid": "Responda, por favor, sim ou não.",
            "city": "2/6 Cidade e país onde você mora:",
            "city_invalid": "Informe cidade e país completos.",
            "work_time": "3/6 Quantas horas por dia você pode trabalhar?",
            "work_time_invalid": "Informe as horas em número, ex.: 6",
            "experience": "4/6 Você tem experiência? Se não, escreva isso.",
            "experience_invalid": "Escreva um breve texto sobre experiência.",
            "photo_face": "5/6 Envie uma foto de frente (rosto) (uso interno, confidencial).",
            "photo_face_invalid": "Envie uma imagem de frente, por favor.",
            "photo_full": "6/6 Envie uma foto de corpo inteiro (confidencial, só para análise).",
            "photo_full_invalid": "Envie uma imagem de corpo inteiro, por favor.",
            "done": "✅ Pronto. Seu cadastro completo foi enviado para o gerente.",
            "expired": "⚠️ Este link expirou. Envie um novo formulário no site.",
        },
        "es": {
            "intro": "✨ La primera etapa del sitio ya está guardada.\nAhora terminamos el formulario aquí (2-3 minutos).",
            "living": "1/6 ¿Tienes espacio privado sin interrupciones? Responde: sí o no.",
            "living_invalid": "Responde, por favor, sí o no.",
            "city": "2/6 Ciudad y país de residencia:",
            "city_invalid": "Indica ciudad y país completos.",
            "work_time": "3/6 ¿Cuántas horas al día puedes trabajar?",
            "work_time_invalid": "Indica horas con número, por ejemplo: 6",
            "experience": "4/6 ¿Tienes experiencia? Si no, escríbelo.",
            "experience_invalid": "Escribe una nota breve sobre tu experiencia.",
            "photo_face": "5/6 Envía una foto de frente (solo para revisión rápida, confidencial).",
            "photo_face_invalid": "Necesito una imagen de frente, por favor.",
            "photo_full": "6/6 Envía una foto de cuerpo completo (confidencial, solo para revisión del perfil).",
            "photo_full_invalid": "Necesito una imagen de cuerpo completo, por favor.",
            "done": "✅ Listo. Tu solicitud completa fue enviada al manager.",
            "expired": "⚠️ Este enlace venció. Envía una nueva solicitud desde el sitio.",
        },
    }
    return texts.get(locale, texts["ru"]).get(key, texts["ru"][key])


def handle_whatsapp_application_message(message: dict) -> tuple[bool, str | None]:
    from_phone = _wa_phone_e164(message.get("from"))
    if not from_phone or _is_wa_sender_number(from_phone):
        return False, None
    raw_text = clean_text(message.get("text") or "")
    text_too_long = len(raw_text) > MAX_WA_TEXT_LEN
    text = raw_text[:MAX_WA_TEXT_LEN].rstrip() if text_too_long else raw_text
    media_url = clean_text(message.get("media_url") or "", max_len=MAX_URL_VALUE_LEN)
    message_type = (message.get("type") or "").upper()
    if message_type not in {"TEXT", "INTERACTIVE", "BUTTON", "UNKNOWN", ""} and not text and not media_url:
        return True, None
    if not INFOBIP_BOT_ENABLED:
        return False, None

    flow = _load_wa_flow(from_phone)
    lang = normalize_site_lang(flow.get("lang") if isinstance(flow, dict) else None)
    mode = str((flow or {}).get("mode") or "quick").strip().lower() or "quick"
    step = str((flow or {}).get("step") or "")
    data = dict(flow.get("data") if isinstance(flow.get("data"), dict) else {})
    if text_too_long:
        return True, field_too_long_error(lang, MAX_WA_TEXT_LEN)

    site_stage2 = _parse_site_stage2_command(text)
    if site_stage2:
        token, start_lang = site_stage2
        lead = consume_site_lead_payload(token)
        if not lead:
            chosen_lang = normalize_site_lang(start_lang or lang or "ru")
            _save_wa_flow(from_phone, {"mode": "quick", "step": "lang", "lang": chosen_lang, "data": {}})
            return True, _wa_stage2_text(chosen_lang, "expired")
        lead = dict(lead)
        lead.setdefault("site_lead_token", token)
        start_reply = _build_site_stage2_flow(
            from_phone,
            message.get("profile_name"),
            lead,
            fallback_user_id=_wa_user_id(from_phone),
            preferred_lang=start_lang or lead.get("lang") or lang,
        )
        if not start_reply:
            chosen_lang = normalize_site_lang(start_lang or lead.get("lang") or lang or "ru")
            _save_wa_flow(from_phone, {"mode": "quick", "step": "lang", "lang": chosen_lang, "data": {}})
            return True, _wa_stage2_text(chosen_lang, "expired")
        return True, start_reply

    if not step:
        resumed_reply = _resume_site_stage2_from_phone(from_phone, message.get("profile_name"))
        if resumed_reply:
            return True, resumed_reply
        _save_wa_flow(from_phone, {"mode": "quick", "step": "lang", "lang": "ru", "data": {}})
        return True, wa_t("ru", "choose_lang")

    if _is_wa_reset_command(text):
        resumed_reply = _resume_site_stage2_from_phone(from_phone, message.get("profile_name"))
        if resumed_reply:
            return True, resumed_reply
        if step in {"", "lang"}:
            _save_wa_flow(from_phone, {"mode": "quick", "step": "lang", "lang": "ru", "data": {}})
            return True, wa_t("ru", "choose_lang")
        next_lang = normalize_site_lang(lang or "ru")
        _save_wa_flow(
            from_phone,
            {
                "mode": "quick",
                "step": "menu",
                "lang": next_lang,
                "data": {},
            },
        )
        return True, _wa_menu_text_for_step(next_lang, "menu")

    if step == "done":
        menu_key = _parse_wa_menu_choice(text)
        if menu_key in {None, "menu", "about_back", "portfolio_back"}:
            _save_wa_flow(from_phone, {"mode": "quick", "step": "menu", "lang": lang, "data": {}})
            return True, _wa_menu_text_for_step(lang, "menu")
        if menu_key == "more":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "menu_more", "lang": lang, "data": {}})
            return True, _wa_menu_text_for_step(lang, "menu_more")
        if menu_key == "language":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "lang", "lang": lang, "data": {}})
            return True, wa_t(lang, "choose_lang")
        if menu_key == "apply":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "name", "lang": lang, "data": {}})
            return True, wa_t(lang, "ask_name")
        if menu_key in {"portfolio", "portfolio_cases", "portfolio_reviews", "portfolio_videos", "portfolio_pdf"}:
            return True, _wa_start_portfolio_flow(from_phone, lang, mode="quick")
        if menu_key == "about":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "about_menu", "lang": lang, "data": {}})
            return True, wa_t(lang, "about_menu")
        if menu_key == "manager":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "menu", "lang": lang, "data": {}})
            return True, _wa_menu_response(lang, "manager", step="menu")
        if menu_key == "channel":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "menu", "lang": lang, "data": {}})
            return True, _wa_menu_response(lang, "channel", step="menu")
        _save_wa_flow(from_phone, {"mode": "quick", "step": "menu", "lang": lang, "data": {}})
        return True, _wa_menu_text_for_step(lang, "menu")

    if mode == "site_stage2":
        if step == "living":
            living = _parse_wa_yes_no_choice(text, lang)
            if not living:
                return True, _wa_stage2_text(lang, "living_invalid")
            data["living"] = living
            _save_wa_flow(
                from_phone,
                {"mode": mode, "step": "city", "lang": lang, "user_id": flow.get("user_id"), "source": "site", "data": data},
            )
            return True, _wa_stage2_text(lang, "city")

        if step == "city":
            city = clean_text(text, max_len=MAX_CITY_LEN)
            if len(city) < 2:
                return True, _wa_stage2_text(lang, "city_invalid")
            data["city"] = city
            _save_wa_flow(
                from_phone,
                {"mode": mode, "step": "work_time", "lang": lang, "user_id": flow.get("user_id"), "source": "site", "data": data},
            )
            return True, _wa_stage2_text(lang, "work_time")

        if step == "work_time":
            work_time = clean_text(text, max_len=MAX_WORK_TIME_LEN)
            if not re.search(r"\d", work_time):
                return True, _wa_stage2_text(lang, "work_time_invalid")
            data["work_time"] = work_time
            _save_wa_flow(
                from_phone,
                {"mode": mode, "step": "experience", "lang": lang, "user_id": flow.get("user_id"), "source": "site", "data": data},
            )
            return True, _wa_stage2_text(lang, "experience")

        if step == "experience":
            experience = clean_text(text, max_len=MAX_EXPERIENCE_LEN)
            if len(experience) < 2:
                return True, _wa_stage2_text(lang, "experience_invalid")
            data["experience"] = experience
            _save_wa_flow(
                from_phone,
                {"mode": mode, "step": "photo_face", "lang": lang, "user_id": flow.get("user_id"), "source": "site", "data": data},
            )
            return True, _wa_stage2_text(lang, "photo_face")

        if step == "photo_face":
            photo_face = media_url or (text if text.startswith("http") else "")
            if not photo_face:
                return True, _wa_stage2_text(lang, "photo_face_invalid")
            data["photo_face"] = photo_face
            _save_wa_flow(
                from_phone,
                {"mode": mode, "step": "photo_full", "lang": lang, "user_id": flow.get("user_id"), "source": "site", "data": data},
            )
            return True, _wa_stage2_text(lang, "photo_full")

        if step == "photo_full":
            photo_full = media_url or (text if text.startswith("http") else "")
            if not photo_full:
                return True, _wa_stage2_text(lang, "photo_full_invalid")
            data["photo_full"] = photo_full
            data["application_stage"] = "full"
            data["lang"] = lang
            data["wa_phone"] = from_phone
            data["country"] = data.get("country") or extract_country_from_phone(data.get("phone")) or ""
            if not data.get("telegram"):
                data["telegram"] = f"wa:{_wa_digits(data.get('whatsapp') or from_phone)}"

            user_id = flow.get("user_id")
            try:
                user_id = int(user_id)
            except Exception:
                user_id = _wa_user_id(from_phone)
            if user_id is None:
                return True, _wa_stage2_text(lang, "expired")

            try:
                save_web_application(user_id, data, source="site_whatsapp", status="pending")
            except Exception as err:
                print("Failed to save site->whatsapp application:", err)
                return True, msg(lang, "db_error")

            if append_application_row:
                try:
                    append_application_row(data, user_id, "pending")
                except Exception as err:
                    print("Excel error (site->whatsapp):", err)
            try:
                _send_application_to_admin_from_whatsapp(data, user_id, from_phone, source="site_whatsapp", status="pending")
            except Exception as err:
                print("Failed to send site->whatsapp application to admin:", err)
            try:
                schedule_admin_refresh()
            except Exception as err:
                print("Failed to refresh admin menu after site->whatsapp application:", err)

            _save_wa_flow(
                from_phone,
                {
                    "mode": "quick",
                    "step": "menu",
                    "lang": lang,
                    "user_id": user_id,
                    "source": "site_whatsapp",
                    "data": {
                        "last_user_id": user_id,
                        "submitted_at": datetime.now(timezone.utc).isoformat(),
                    },
                },
            )
            return True, f"{_wa_stage2_text(lang, 'done')}\n\n{_wa_menu_text_for_step(lang, 'menu')}"

        _save_wa_flow(from_phone, {"mode": "quick", "step": "lang", "lang": "ru", "data": {}})
        return True, wa_t("ru", "choose_lang")

    if step == "lang":
        menu_key = _parse_wa_menu_choice(text)
        if menu_key == "language_more":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "lang_more", "lang": lang, "data": {}})
            return True, wa_t(lang, "lang_more")
        chosen = _parse_wa_lang_choice(text)
        if not chosen:
            return True, wa_t("ru", "invalid_lang")
        _save_wa_flow(from_phone, {"mode": "quick", "step": "menu", "lang": chosen, "data": {}})
        return True, _wa_menu_text_for_step(chosen, "menu")

    if step == "lang_more":
        menu_key = _parse_wa_menu_choice(text)
        if menu_key in {"language_back", "menu"}:
            _save_wa_flow(from_phone, {"mode": "quick", "step": "lang", "lang": lang, "data": {}})
            return True, wa_t(lang, "choose_lang")
        chosen = _parse_wa_lang_choice(text)
        if not chosen:
            return True, wa_t("ru", "invalid_lang")
        _save_wa_flow(from_phone, {"mode": "quick", "step": "menu", "lang": chosen, "data": {}})
        return True, _wa_menu_text_for_step(chosen, "menu")

    if step in {"menu", "menu_more"}:
        menu_key = _parse_wa_menu_choice(text)
        if not menu_key:
            if step == "menu_more":
                return True, wa_t(lang, "menu_more_invalid")
            return True, wa_t(lang, "menu_invalid")
        if menu_key == "menu":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "menu", "lang": lang, "data": {}})
            return True, _wa_menu_text_for_step(lang, "menu")
        if menu_key == "more":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "menu_more", "lang": lang, "data": {}})
            return True, _wa_menu_text_for_step(lang, "menu_more")
        if menu_key == "language":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "lang", "lang": lang, "data": {}})
            return True, wa_t(lang, "choose_lang")
        if menu_key == "language_more":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "lang_more", "lang": lang, "data": {}})
            return True, wa_t(lang, "lang_more")
        if menu_key == "apply":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "name", "lang": lang, "data": {}})
            return True, wa_t(lang, "ask_name")
        if menu_key in {"portfolio", "portfolio_cases", "portfolio_reviews", "portfolio_videos", "portfolio_pdf"}:
            return True, _wa_start_portfolio_flow(from_phone, lang, mode="quick")
        if menu_key == "about":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "about_menu", "lang": lang, "data": {}})
            return True, wa_t(lang, "about_menu")
        if menu_key in {"manager", "channel", "site"}:
            _save_wa_flow(from_phone, {"mode": "quick", "step": step, "lang": lang, "data": {}})
            return True, _wa_menu_response(lang, menu_key, step=step)
        _save_wa_flow(from_phone, {"mode": "quick", "step": "menu", "lang": lang, "data": {}})
        return True, _wa_menu_text_for_step(lang, "menu")

    if step == "about_menu":
        menu_key = _parse_wa_menu_choice(text)
        if not menu_key:
            return True, wa_t(lang, "about_menu")
        if menu_key in {"about_back", "menu"}:
            _save_wa_flow(from_phone, {"mode": "quick", "step": "menu", "lang": lang, "data": {}})
            return True, wa_t(lang, "menu")
        if menu_key == "more":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "menu_more", "lang": lang, "data": {}})
            return True, wa_t(lang, "menu_more")
        if menu_key == "language":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "lang", "lang": lang, "data": {}})
            return True, wa_t(lang, "choose_lang")
        if menu_key in {"manager", "channel"}:
            _save_wa_flow(from_phone, {"mode": "quick", "step": "about_menu", "lang": lang, "data": {}})
            return True, _wa_menu_response(lang, menu_key, step="about_menu")
        if menu_key in {"portfolio", "portfolio_cases", "portfolio_reviews", "portfolio_videos", "portfolio_pdf"}:
            return True, _wa_start_portfolio_flow(from_phone, lang, mode="quick")
        if menu_key == "apply":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "name", "lang": lang, "data": {}})
            return True, wa_t(lang, "ask_name")
        if menu_key == "language_more":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "lang_more", "lang": lang, "data": {}})
            return True, wa_t(lang, "lang_more")
        return True, wa_t(lang, "about_menu")

    if step == "portfolio_menu":
        menu_key = _parse_wa_menu_choice(text)
        if not menu_key:
            return True, _wa_start_portfolio_flow(from_phone, lang, mode="quick")
        if menu_key in {"portfolio", "portfolio_cases", "portfolio_reviews", "portfolio_videos", "portfolio_pdf"}:
            return True, _wa_start_portfolio_flow(from_phone, lang, mode="quick")
        if menu_key in {"portfolio_back", "menu"}:
            _save_wa_flow(from_phone, {"mode": "quick", "step": "menu", "lang": lang, "data": {}})
            return True, wa_t(lang, "menu")
        if menu_key == "more":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "menu_more", "lang": lang, "data": {}})
            return True, wa_t(lang, "menu_more")
        return True, _wa_start_portfolio_flow(from_phone, lang, mode="quick")

    if step == "portfolio_view":
        menu_key = _parse_wa_menu_choice(text)
        current_item, current_index, total_items, current_kind = _wa_portfolio_item_from_flow(flow)
        if not current_item:
            return True, _wa_start_portfolio_flow(from_phone, lang, mode="quick")
        if not menu_key:
            return True, _wa_portfolio_caption(lang, current_item, current_index, total_items)
        if menu_key in {"portfolio_back", "menu", "about_back"}:
            _save_wa_flow(from_phone, {"mode": "quick", "step": "menu", "lang": lang, "data": {}})
            return True, wa_t(lang, "menu")
        if menu_key == "more":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "menu_more", "lang": lang, "data": {}})
            return True, wa_t(lang, "menu_more")
        if menu_key == "apply":
            _save_wa_flow(from_phone, {"mode": "quick", "step": "name", "lang": lang, "data": {}})
            return True, wa_t(lang, "ask_name")
        if menu_key == "portfolio_next":
            next_index = min(current_index + 1, max(total_items - 1, 0))
            items = _wa_portfolio_items(current_kind)
            if not items:
                return True, _wa_start_portfolio_flow(from_phone, lang, mode="quick")
            item = items[next_index]
            _save_wa_flow(
                from_phone,
                {
                    "mode": "quick",
                    "step": "portfolio_view",
                    "lang": lang,
                    "data": {"portfolio_kind": current_kind, "portfolio_index": next_index},
                },
            )
            return True, _wa_portfolio_caption(lang, item, next_index, total_items)
        if menu_key == "portfolio_prev":
            prev_index = max(current_index - 1, 0)
            items = _wa_portfolio_items(current_kind)
            if not items:
                return True, _wa_start_portfolio_flow(from_phone, lang, mode="quick")
            item = items[prev_index]
            _save_wa_flow(
                from_phone,
                {
                    "mode": "quick",
                    "step": "portfolio_view",
                    "lang": lang,
                    "data": {"portfolio_kind": current_kind, "portfolio_index": prev_index},
                },
            )
            return True, _wa_portfolio_caption(lang, item, prev_index, total_items)
        if menu_key in {"portfolio", "portfolio_cases", "portfolio_reviews", "portfolio_videos", "portfolio_pdf"}:
            return True, _wa_start_portfolio_flow(from_phone, lang, mode="quick")
        if menu_key in {"about", "about_work", "about_platforms", "about_income"}:
            _save_wa_flow(from_phone, {"mode": "quick", "step": "about_menu", "lang": lang, "data": {}})
            return True, wa_t(lang, "about_menu")
        return True, _wa_portfolio_caption(lang, current_item, current_index, total_items)

    if step == "name":
        value = clean_text(text, max_len=MAX_NAME_LEN)
        if len(value) < 2 or has_any_digit(value):
            return True, wa_t(lang, "invalid_name")
        data["name"] = value
        _save_wa_flow(from_phone, {"mode": "quick", "step": "phone", "lang": lang, "data": data})
        return True, wa_t(lang, "ask_phone")

    if step == "phone":
        raw = clean_text(text, max_len=MAX_PHONE_LEN)
        if raw.strip().lower() == "same":
            value = from_phone
        else:
            value = normalize_phone(raw) or ""
        if not is_valid_phone(value):
            return True, wa_t(lang, "invalid_phone")
        data["phone"] = value
        _save_wa_flow(from_phone, {"mode": "quick", "step": "age", "lang": lang, "data": data})
        return True, wa_t(lang, "ask_age")

    if step == "age":
        age_input = clean_text(text, max_len=MAX_BIRTHDATE_LEN)
        normalized = normalize_birthdate(age_input)
        if not normalized or not is_valid_birthdate(normalized):
            return True, wa_t(lang, "invalid_age")
        data["age"] = normalized
        _save_wa_flow(from_phone, {"mode": "quick", "step": "device_model", "lang": lang, "data": data})
        return True, wa_t(lang, "ask_device")

    if step == "device_model":
        value = clean_text(text, max_len=MAX_DEVICE_LEN)
        if len(value) < 2:
            return True, wa_t(lang, "invalid_device")
        data["device_model"] = value
        _save_wa_flow(from_phone, {"mode": "quick", "step": "telegram", "lang": lang, "data": data})
        return True, wa_t(lang, "ask_telegram")

    if step == "telegram":
        username = normalize_telegram(clean_text(text, max_len=MAX_CONTACT_VALUE_LEN))
        if not username:
            return True, wa_t(lang, "invalid_telegram")
        data["telegram"] = username
        _save_wa_flow(from_phone, {"mode": "quick", "step": "city", "lang": lang, "data": data})
        return True, wa_t(lang, "ask_city")

    if step == "city":
        city = clean_text(text, max_len=MAX_CITY_LEN)
        if len(city) < 2:
            return True, wa_t(lang, "invalid_city")
        data["city"] = city
        _save_wa_flow(from_phone, {"mode": "quick", "step": "work_time", "lang": lang, "data": data})
        return True, wa_t(lang, "ask_work_time")

    if step == "work_time":
        work_time = clean_text(text, max_len=MAX_WORK_TIME_LEN)
        if not re.search(r"\d", work_time):
            return True, wa_t(lang, "invalid_work_time")
        data["work_time"] = work_time
        _save_wa_flow(from_phone, {"mode": "quick", "step": "experience", "lang": lang, "data": data})
        return True, wa_t(lang, "ask_experience")

    if step == "experience":
        experience = clean_text(text, max_len=MAX_EXPERIENCE_LEN)
        if len(experience) < 2:
            return True, wa_t(lang, "invalid_experience")
        data["experience"] = experience
        _save_wa_flow(from_phone, {"mode": "quick", "step": "living", "lang": lang, "data": data})
        return True, wa_t(lang, "ask_living")

    if step == "living":
        living = _parse_wa_yes_no_choice(text, lang)
        if not living:
            return True, wa_t(lang, "invalid_living")
        data["living"] = living
        _save_wa_flow(from_phone, {"mode": "quick", "step": "photo_face", "lang": lang, "data": data})
        return True, wa_t(lang, "ask_photo_face")

    if step == "photo_face":
        photo_face = media_url or (text if text.startswith("http") else "")
        if not photo_face:
            return True, wa_t(lang, "invalid_photo_face")
        data["photo_face"] = photo_face
        _save_wa_flow(from_phone, {"mode": "quick", "step": "photo_full", "lang": lang, "data": data})
        return True, wa_t(lang, "ask_photo_full")

    if step == "photo_full":
        photo_full = media_url or (text if text.startswith("http") else "")
        if not photo_full:
            return True, wa_t(lang, "invalid_photo_full")
        data["photo_full"] = photo_full
        data["lang"] = lang
        data["country"] = (
            data.get("country")
            or extract_country_from_location(data.get("city"))
            or extract_country_from_phone(data.get("phone"))
            or ""
        )
        data["application_stage"] = "full"
        data["wa_phone"] = from_phone
        data["wa_profile_name"] = clean_text(message.get("profile_name") or "", max_len=MAX_NAME_LEN)

        user_id = _wa_user_id(from_phone)
        if user_id is None:
            return True, wa_t(lang, "invalid_phone")

        try:
            save_web_application(user_id, data, source="whatsapp_bot", status="pending")
        except Exception as err:
            print("Failed to save whatsapp application:", err)
            return True, msg(lang, "db_error")

        if append_application_row:
            try:
                append_application_row(data, user_id, "pending")
            except Exception as err:
                print("Excel error (whatsapp):", err)
        try:
            _send_application_to_admin_from_whatsapp(data, user_id, from_phone, source="whatsapp_bot", status="pending")
        except Exception as err:
            print("Failed to send whatsapp application card to admin:", err)
        try:
            schedule_admin_refresh()
        except Exception as err:
            print("Failed to refresh admin menu after whatsapp application:", err)

        _save_wa_flow(
            from_phone,
            {
                "mode": "quick",
                "step": "menu",
                "lang": lang,
                "source": "whatsapp_bot",
                "data": {
                    "last_user_id": user_id,
                    "submitted_at": datetime.now(timezone.utc).isoformat(),
                },
            },
        )
        return True, f"{wa_t(lang, 'saved')}\n\n{_wa_menu_text_for_step(lang, 'menu')}"

    _save_wa_flow(from_phone, {"mode": "quick", "step": "menu", "lang": lang or "ru", "data": {}})
    return True, _wa_menu_text_for_step(lang or "ru", "menu")

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


PROJECT_LABELS = {
    PROJECT_STREAMFLOW: "Streamflow Agency",
    PROJECT_STARFLOW: "Starflow Inc.",
}


def project_label(value: str | None) -> str:
    return PROJECT_LABELS.get(normalize_project(value), PROJECT_LABELS[PROJECT_STREAMFLOW])


def build_admin_full_text(data: dict, web_id: str, submitted_at: str, source_label: str = "Сайт") -> str:
    status_label = STATUS_LABELS.get("pending", "🟡 На рассмотрении")
    device_value = _safe(data.get("device_model") or data.get("devices"))
    return (
        "📋 <b>Полная анкета</b>\n\n"
        f"👤 Имя: {_safe(data.get('name'))}\n"
        f"📅 Дата рождения: {_safe(data.get('age'))}\n"
        f"🌍 Город и страна: {_safe(data.get('city'))}\n"
        f"🏳️ Страна подачи: {_safe(submission_country(data))}\n"
        f"📞 Телефон: {_safe(data.get('phone'))}\n"
        f"🏠 Помещение без посторонних: {_safe(data.get('living'))}\n"
        f"📱 Устройство для работы: {device_value}\n"
        f"⏱ Время работы: {_safe(data.get('work_time'))}\n"
        f"💼 Опыт: {_safe(data.get('experience'))}\n"
        f"💬 Telegram: {_safe(data.get('telegram'))}\n"
        f"📧 Email: {_safe(data.get('email'))}\n"
        f"🏷 Проект: {_safe(project_label(str(data.get('project') or '')))}\n"
        f"🆔 ID: {_safe(web_id)}\n"
        f"🧭 Источник: {_safe(source_label)}\n"
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


def _admin_refresh_worker() -> None:
    global _ADMIN_REFRESH_RUNNING
    global _ADMIN_REFRESH_DIRTY
    while True:
        try:
            notify_admin_new_application()
        except Exception:
            pass
        try:
            update_admin_menu_message()
        except Exception:
            pass
        with _ADMIN_REFRESH_LOCK:
            if _ADMIN_REFRESH_DIRTY:
                _ADMIN_REFRESH_DIRTY = False
                continue
            _ADMIN_REFRESH_RUNNING = False
            return


def schedule_admin_refresh() -> None:
    global _ADMIN_REFRESH_RUNNING
    global _ADMIN_REFRESH_DIRTY
    with _ADMIN_REFRESH_LOCK:
        if _ADMIN_REFRESH_RUNNING:
            _ADMIN_REFRESH_DIRTY = True
            return
        _ADMIN_REFRESH_RUNNING = True
        _ADMIN_REFRESH_DIRTY = False
    threading.Thread(
        target=_admin_refresh_worker,
        name="admin-refresh-worker",
        daemon=True,
    ).start()


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
        filename = str(file_info.get("filename") or "file.bin")
        filename = re.sub(r"[\r\n\"\\\\]", "_", filename)[:180]
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


def _extract_authorization_secret(value: str | None) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    if " " not in raw:
        return raw
    scheme, token = raw.split(" ", 1)
    if scheme.strip().lower() in {"bearer", "token", "app"}:
        return token.strip()
    return raw


def _infobip_webhook_secret_candidates(handler: SimpleHTTPRequestHandler) -> list[str]:
    candidates: list[str] = []
    for header_name in ("X-Webhook-Secret", "X-Infobip-Secret", "X-Infobip-Webhook-Secret"):
        value = (handler.headers.get(header_name) or "").strip()
        if value:
            candidates.append(value)
    auth_secret = _extract_authorization_secret(handler.headers.get("Authorization"))
    if auth_secret:
        candidates.append(auth_secret)
    parsed = urllib.parse.urlparse(handler.path)
    query = urllib.parse.parse_qs(parsed.query or "", keep_blank_values=True)
    for key in ("secret", "webhook_secret", "token"):
        value = str((query.get(key) or [""])[0]).strip()
        if value:
            candidates.append(value)
    return candidates


def _is_infobip_webhook_authorized(handler: SimpleHTTPRequestHandler) -> bool:
    expected = INFOBIP_WEBHOOK_SECRET
    if not expected:
        return False
    for candidate in _infobip_webhook_secret_candidates(handler):
        if hmac.compare_digest(candidate, expected):
            return True
    return False


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def handle(self):
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            # Client dropped socket while response was in flight.
            pass

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; "
            "base-uri 'self'; "
            "frame-ancestors 'none'; "
            "object-src 'none'; "
            "form-action 'self'; "
            "img-src 'self' data: https:; "
            "media-src 'self' blob: https:; "
            "font-src 'self' data: https://fonts.gstatic.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "script-src 'self' 'unsafe-inline' https://mc.yandex.ru; "
            "connect-src 'self' https://mc.yandex.ru wss://mc.yandex.ru https://*.yandex.net wss://*.yandex.net",
        )
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header(
            "Permissions-Policy",
            "accelerometer=(), autoplay=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=(), browsing-topics=()",
        )
        self.send_header("X-Permitted-Cross-Domain-Policies", "none")
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
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            # Client closed connection early (browser navigation/refresh).
            pass

    def _request_host(self) -> str:
        return request_host_from_headers(
            self.headers.get("Host"),
            self.headers.get("X-Forwarded-Host"),
        )

    def _is_allowed_request_host(self) -> bool:
        host = self._request_host()
        if not host:
            return False
        if host in {"127.0.0.1", "0.0.0.0", "localhost"}:
            return True
        if is_internal_proxy_host(host):
            return True
        return host in canonical_public_hosts()

    def _request_origin_host(self) -> str:
        for header_name in ("Origin", "Referer"):
            raw = (self.headers.get(header_name) or "").strip()
            if not raw:
                continue
            try:
                parsed = urllib.parse.urlparse(raw)
            except Exception:
                continue
            host = normalize_host(parsed.netloc)
            if host:
                return host
        return ""

    def _is_allowed_site_origin(self) -> bool:
        origin_host = self._request_origin_host()
        if not origin_host:
            return True
        allowed_hosts = set(canonical_public_hosts())
        allowed_hosts.update({"127.0.0.1", "localhost", "0.0.0.0"})
        request_host = self._request_host()
        if request_host in allowed_hosts or is_internal_proxy_host(request_host):
            allowed_hosts.update(_host_aliases(request_host))
        return origin_host in allowed_hosts

    def _should_redirect_to_canonical(self) -> bool:
        allowed_hosts = canonical_public_hosts()
        if not allowed_hosts:
            return False
        host = self._request_host()
        if not host:
            return False
        if host in allowed_hosts:
            return False
        if host in {"127.0.0.1", "0.0.0.0", "localhost"}:
            return False
        if is_internal_proxy_host(host):
            return False
        return True

    def _redirect_canonical(self):
        target_base = canonical_site_url_for_host(self._request_host())
        parsed = urllib.parse.urlsplit(self.path)
        safe_path = parsed.path or "/"
        safe_query = f"?{parsed.query}" if parsed.query else ""
        target = f"{target_base}{safe_path}{safe_query}"
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
            self.path = homepage_path_for_host(self._request_host())
        elif parsed.path in {"/starflow", "/starflow/"}:
            self.path = "/starflow.html"
        return super().do_GET()

    def do_POST(self):
        if not self._is_allowed_request_host():
            return self.send_json({"ok": False, "message": "misdirected host"}, status=421)
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/apply":
            self.handle_apply()
            return
        if parsed.path == "/api/infobip/webhook":
            self.handle_infobip_webhook()
            return
        self.send_error(404)

    def handle_config(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query or "")
        requested_project = (query.get("project") or [None])[0]
        project = resolve_project(requested_project, self._request_host())
        admin_username = ADMIN_USERNAME.lstrip("@")
        bot_link = project_bot_public_link(project)
        wa_link = build_whatsapp_base_link()
        channel_link = project_channel_link(project)
        site_url = project_site_url(project)
        payload = {
            "telegram_link": channel_link or (f"https://t.me/{admin_username}" if admin_username else None),
            "bot_link": bot_link,
            "whatsapp_link": wa_link,
            "site_url": site_url,
            "project": project,
        }
        self.send_json(payload)

    def handle_apply(self):
        if not self._is_allowed_site_origin():
            return self.send_json({"ok": False, "message": "forbidden"}, status=403)
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self.send_json({"ok": False, "message": msg("ru", "bad_size")}, status=400)
        if content_length <= 0:
            return self.send_json({"ok": False, "message": msg("ru", "bad_size")}, status=400)
        if content_length > MAX_APPLY_BODY_SIZE:
            return self.send_json({"ok": False, "message": msg("ru", "too_big")}, status=413)

        body = self.rfile.read(content_length)
        content_type = self.headers.get("Content-Type", "")

        if content_type.startswith("multipart/form-data"):
            fields, _files = parse_multipart(body, content_type)
        elif content_type.startswith("application/x-www-form-urlencoded"):
            data = urllib.parse.parse_qs(body.decode("utf-8", errors="replace"))
            fields = {k: v[0] for k, v in data.items()}
        else:
            return self.send_json({"ok": False, "message": msg("ru", "bad_type")}, status=400)

        site_lang = normalize_site_lang(fields.get("site_lang"))
        client_ip = _client_ip_from_headers(self)
        project = resolve_project(fields.get("project"), self._request_host())

        def error(
            message: str,
            status: int = 400,
            field: str | None = None,
            retry_after: int | None = None,
        ):
            payload = {"ok": False, "message": message}
            if field:
                payload["field"] = field
            if retry_after is not None:
                payload["retry_after"] = int(retry_after)
            extra_headers = {"Retry-After": str(int(retry_after))} if retry_after is not None else None
            log_apply_event(
                outcome="reject",
                project=project,
                lang=site_lang,
                client_ip=client_ip,
                status=status,
                field=field,
                retry_after=retry_after,
            )
            return self.send_json(payload, status=status, extra_headers=extra_headers)

        def get_limited(field_name: str, max_len: int, error_field: str | None = None) -> tuple[str | None, bool]:
            raw = clean_text(fields.get(field_name) or "")
            if len(raw) > max_len:
                error(
                    field_too_long_error(site_lang, max_len),
                    field=error_field or field_name,
                )
                return None, False
            return raw, True

        honeypot_field = detect_honeypot_field(fields)
        if honeypot_field:
            return error(
                msg(site_lang, "invalid_form"),
                status=400,
                field=honeypot_field,
            )

        allowed, retry_after = _consume_rate_limit(
            "apply_ip",
            client_ip,
            APPLY_RATE_WINDOW_SECONDS,
            APPLY_RATE_MAX_PER_WINDOW,
        )
        if not allowed:
            return error(
                msg(site_lang, "rate_limited_ip"),
                status=429,
                retry_after=retry_after,
            )

        name, ok = get_limited("name", MAX_NAME_LEN, "name")
        if not ok or name is None:
            return
        if len(name) < 2:
            return error(field_error(site_lang, "name"), field="name")

        phone_raw, ok = get_limited("phone", MAX_PHONE_LEN, "phone")
        if not ok or phone_raw is None:
            return
        if not is_valid_phone(phone_raw):
            return error(field_error(site_lang, "phone"), field="phone")
        phone = normalize_phone(phone_raw) or phone_raw
        cooldown_hit, cooldown_retry = _is_phone_apply_cooldown(phone)
        if cooldown_hit:
            return error(
                msg(site_lang, "rate_limited_phone"),
                status=429,
                field="phone",
                retry_after=cooldown_retry,
            )
        try:
            recent = find_recent_site_lead_by_phone(phone)
        except Exception:
            recent = None
        if recent:
            recent_ts = _parse_recent_apply_ts(recent.get("updated_at"))
            if recent_ts:
                now_utc = datetime.now(timezone.utc)
                age_seconds = (now_utc - recent_ts).total_seconds()
                if age_seconds < APPLY_SAME_PHONE_COOLDOWN_SECONDS:
                    retry = max(1, int(APPLY_SAME_PHONE_COOLDOWN_SECONDS - max(0, age_seconds)))
                    return error(
                        msg(site_lang, "rate_limited_phone"),
                        status=429,
                        field="phone",
                        retry_after=retry,
                    )

        age_raw, ok = get_limited("age", MAX_BIRTHDATE_LEN, "age")
        if not ok or age_raw is None:
            return
        if not is_valid_birthdate(age_raw):
            return error(field_error(site_lang, "age"), field="age")
        age = normalize_birthdate(age_raw) or age_raw

        preferred_contact_raw = clean_text(fields.get("preferred_contact") or "", max_len=16).lower()
        preferred_contact = "whatsapp" if preferred_contact_raw in {"whatsapp", "wa"} else "telegram"
        contact_value, ok = get_limited("contact_value", MAX_CONTACT_VALUE_LEN, "contact_value")
        if not ok or contact_value is None:
            return
        telegram_raw, ok = get_limited("telegram", MAX_CONTACT_VALUE_LEN, "telegram")
        if not ok or telegram_raw is None:
            return
        whatsapp_raw, ok = get_limited("whatsapp", MAX_CONTACT_VALUE_LEN, "whatsapp")
        if not ok or whatsapp_raw is None:
            return

        telegram: str | None = normalize_telegram(telegram_raw) if telegram_raw else None
        whatsapp: str | None = None
        if whatsapp_raw and is_valid_phone(whatsapp_raw):
            whatsapp = normalize_phone(whatsapp_raw)

        if preferred_contact == "telegram":
            candidate = telegram_raw or contact_value
            telegram = normalize_telegram(candidate)
            if not telegram:
                return error(field_error(site_lang, "telegram"), field="contact_value")
        else:
            candidate = whatsapp_raw or contact_value
            normalized_wa = normalize_phone(candidate) or ""
            if not is_valid_phone(normalized_wa):
                return error(field_error(site_lang, "whatsapp"), field="contact_value")
            whatsapp = normalized_wa

        country, ok = get_limited("country", MAX_COUNTRY_LEN, "country")
        if not ok or country is None:
            return
        if not country:
            country = (
                extract_country_from_location(clean_text(fields.get("city") or "", max_len=MAX_CITY_LEN))
                or extract_country_from_phone(phone)
                or ""
            )

        payload: dict[str, object] = {
            "name": name,
            "lang": site_lang,
            "phone": phone,
            "age": age,
            "telegram": telegram or "",
            "whatsapp": whatsapp or "",
            "preferred_contact": preferred_contact,
            "country": country,
            "project": project,
            "application_stage": "quick",
        }

        if project == PROJECT_STARFLOW:
            email, ok = get_limited("email", MAX_EMAIL_LEN, "email")
            if not ok or email is None:
                return
            if not is_valid_email(email):
                return error(field_error(site_lang, "email"), field="email")
            payload["email"] = email
        else:
            device_model, ok = get_limited("device_model", MAX_DEVICE_LEN, "device_model")
            if not ok or device_model is None:
                return
            if len(device_model) < 2:
                return error(field_error(site_lang, "device_model"), field="device_model")
            payload["device_model"] = device_model

        user_id = -int(time.time_ns())
        lead_token = uuid.uuid4().hex[:24]
        payload["site_lead_token"] = lead_token
        payload["site_pending_user_id"] = user_id
        site_source = "site_whatsapp" if preferred_contact == "whatsapp" else "site_tg"

        try:
            save_site_lead_payload(lead_token, payload)
            save_web_application(user_id, payload, source=site_source, status="pending")
            _mark_phone_apply(phone)
            if append_application_row:
                try:
                    append_application_row(payload, user_id, "pending")
                except Exception as err:
                    print("Excel error:", err)
        except Exception as err:
            print("DB error:", err)
            return error(msg(site_lang, "db_error"), status=500)

        schedule_admin_refresh()

        tg_link = build_bot_stage2_link(lead_token, site_lang, project=project) or project_bot_public_link(project)
        wa_link = build_whatsapp_stage2_link(lead_token, site_lang)
        if preferred_contact == "whatsapp" and wa_link:
            preferred_link = wa_link
        else:
            preferred_link = tg_link
        log_apply_event(
            outcome="accepted",
            project=project,
            lang=site_lang,
            client_ip=client_ip,
            status=200,
        )
        return self.send_json(
            {
                "ok": True,
                "message": msg(site_lang, "success"),
                "project": project,
                "bot_link": preferred_link,
                "telegram_bot_link": tg_link,
                "whatsapp_bot_link": wa_link,
                "preferred_contact": preferred_contact,
                "next_links": {
                    "telegram": tg_link,
                    "whatsapp": wa_link,
                },
            }
        )

    def handle_infobip_webhook(self):
        if not INFOBIP_WEBHOOK_SECRET:
            print("Infobip webhook auth error: INFOBIP_WEBHOOK_SECRET is not configured")
            return self.send_json({"ok": False, "message": "webhook auth misconfigured"}, status=503)
        if not _is_infobip_webhook_authorized(self):
            return self.send_json({"ok": False, "message": "unauthorized"}, status=401)
        client_ip = _client_ip_from_headers(self)
        allowed, retry_after = _consume_rate_limit(
            "infobip_ip",
            client_ip,
            WEBHOOK_RATE_WINDOW_SECONDS,
            WEBHOOK_RATE_MAX_PER_WINDOW,
        )
        if not allowed:
            return self.send_json(
                {"ok": False, "message": "rate limited", "retry_after": retry_after},
                status=429,
                extra_headers={"Retry-After": str(retry_after)},
            )
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0
        if content_length > MAX_WEBHOOK_BODY_SIZE:
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
        bot_replies = 0
        duplicates = 0
        errors = 0
        messages_count = 0
        try:
            messages = _extract_infobip_messages(payload)
            messages_count = len(messages)
            for message in messages:
                if _is_infobip_seen(message):
                    duplicates += 1
                    continue
                mark_seen = False
                handled = False
                reply = None
                pre_flow = _load_wa_flow(message.get("from"))
                pre_step = str((pre_flow or {}).get("step") or "").strip().lower()
                try:
                    handled, reply = handle_whatsapp_application_message(message)
                    if handled:
                        target_phone = message.get("from")
                        post_flow = _load_wa_flow(target_phone)
                        post_step = str((post_flow or {}).get("step") or "").strip().lower()
                        expect_interactive = post_step in {
                            "lang",
                            "lang_more",
                            "menu",
                            "menu_more",
                            "about_menu",
                            "portfolio_menu",
                            "portfolio_view",
                            "living",
                        }
                        reply_sent = False

                        if expect_interactive:
                            interactive_body = None
                            if post_step in {"menu", "menu_more", "about_menu", "portfolio_menu", "portfolio_view", "living", "lang", "lang_more"} and reply:
                                interactive_body = reply
                            try:
                                if send_wa_interactive_controls(target_phone, body_override=interactive_body):
                                    bot_replies += 1
                                    reply_sent = True
                            except Exception as err:
                                errors += 1
                                print("Failed to send whatsapp interactive controls:", err)

                        if not reply_sent and reply:
                            if infobip_send_whatsapp_text(target_phone, reply):
                                bot_replies += 1
                                reply_sent = True
                                print(
                                    "Infobip reply sent:",
                                    {
                                        "to": target_phone,
                                        "type": message.get("type"),
                                        "preview": (reply[:80] + "…") if len(reply) > 80 else reply,
                                    },
                                )
                            else:
                                errors += 1

                        if reply_sent:
                            mark_seen = True
                        elif not reply and not expect_interactive:
                            mark_seen = True
                    else:
                        mark_seen = True
                except Exception as err:
                    errors += 1
                    print("Failed to handle whatsapp bot flow:", err)
                # Keep WhatsApp bot autonomous: do not relay user messages to Telegram admin chat.
                # This avoids accidental "forward-only" behavior when old env values remain in deploy.
                if False and INFOBIP_FORWARD_TO_ADMIN and INFOBIP_RELAY_MODE and not handled:
                    try:
                        _forward_infobip_message_to_admin(message)
                        forwarded += 1
                    except Exception as err:
                        errors += 1
                        print("Failed to forward infobip message to admin:", err)
                if mark_seen:
                    _mark_infobip_seen(message)
        except Exception as err:
            print("Failed to parse infobip webhook payload:", err)

        status_events = _extract_infobip_statuses(payload)
        if status_events:
            print("Infobip status events:", status_events[:5])

        print(
            "Infobip webhook summary:",
            {
                "messages": messages_count,
                "forwarded": forwarded,
                "bot_replies": bot_replies,
                "duplicates": duplicates,
                "errors": errors,
            },
        )

        try:
            set_setting(
                "infobip_last_webhook",
                json.dumps(
                    {
                        "received_at": datetime.now(timezone.utc).isoformat(),
                        "payload": payload,
                        "forwarded": forwarded,
                        "bot_replies": bot_replies,
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
                "bot_replies": bot_replies,
                "duplicates": duplicates,
                "errors": errors,
            }
        )

    def send_json(self, payload: dict, status: int = 200, extra_headers: dict | None = None):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        if extra_headers:
            for key, value in extra_headers.items():
                if value is None:
                    continue
                self.send_header(str(key), str(value))
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass


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
