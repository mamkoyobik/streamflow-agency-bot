from states import ApplicationStates

SUPPORTED_LANGS = ("ru", "en", "pt", "es")
DEFAULT_LANG = "ru"


def normalize_lang(lang: str | None) -> str:
    value = (lang or "").strip().lower()
    if value in SUPPORTED_LANGS:
        return value
    return DEFAULT_LANG


LANGUAGE_NAMES = {
    "ru": "Русский",
    "en": "English",
    "pt": "Português",
    "es": "Español",
}


TRANSLATIONS = {
    "ru": {
        "menu_caption": (
            "🌷 Добро пожаловать!\n"
            "Мы рады, что ты здесь 🤍\n"
            "Выбери интересующий раздел ниже ✨"
        ),
        "accept_caption": (
            "🌸 Ваша заявка одобрена! Добро пожаловать 🤍\n\n"
            "Выбери интересующий раздел ниже ✨"
        ),
        "ack_text": "✨ Отлично! Двигаемся дальше 🌸",
        "loading_text": "⏳ Формируем анкету...\nПочти готово 🤍",
        "support_line_1": "Ты отлично справляешься 🤍",
        "support_line_2": "Спасибо за ответы, это важно ✨",
        "support_line_3": "Ещё чуть-чуть — и готово 🌸",
        "status_line": "Статус заявки: {status}",
        "start_private_only": "🤍 Напиши мне в личку и нажми /start ✨",
        "open_private_prompt": "🤍 Открой чат с ботом и нажми /start ✨",
        "language_menu_title": "🌐 Выбери язык / Choose your language",
        "language_changed": "✅ Язык изменён: {language}",
        "language_button": "🌐 Язык / Language",
        "menu_home": "🏠 В меню",
        "menu_be_model": "🌸 Стать моделью",
        "menu_website": "🌐 Наш сайт",
        "menu_portfolio": "📁 Портфолио моделей",
        "menu_about": "ℹ️ Подробнее о работе",
        "menu_contact": "💬 @streamflowmanager",
        "menu_channel": "📣 Наш канал",
        "menu_lang": "🌐 Язык",
        "btn_back": "⬅ Назад",
        "btn_edit_data": "✏️ Исправить данные",
        "btn_edit_photo": "📷 Исправить фото",
        "btn_send": "✅ Отправить",
        "btn_continue": "▶️ Продолжить",
        "btn_restart": "🔄 Начать сначала",
        "btn_cancel": "⬅️ Отмена",
        "btn_apply_again": "✅ Заполнить заново",
        "btn_open_telegram": "Открыть Telegram",
        "btn_back_to_preview": "⬅ Назад к предпросмотру",
        "about_menu_work": "🌷 О формате работы",
        "about_menu_platforms": "💻 Площадки",
        "about_menu_income": "💰 Доход и выплаты",
        "about_work_text": (
            "🌷 <b>О работе в нашем проекте</b>\n\n"
            "Мы предлагаем современную онлайн-работу в формате стриминга.\n"
            "Это не офис и не «работа по расписанию», а гибкий формат, который\n"
            "можно легко встроить в свою жизнь 🤍\n\n"
            "<b>Как всё проходит:</b>\n"
            "• ты работаешь из любой точки мира\n"
            "• находишься в комфортной для себя обстановке\n"
            "• общаешься с аудиторией в дружелюбном формате\n"
            "• создаёшь свой образ и стиль общения\n\n"
            "<b>График:</b>\n"
            "Он гибкий и подбирается индивидуально.\n"
            "Обычно это от 6 часов в день, но всё обсуждается — мы за комфорт,\n"
            "а не за выгорание.\n\n"
            "<b>Стажировка:</b>\n"
            "Перед стартом есть короткий промо-период (2–5 дней).\n"
            "В это время ты:\n"
            "• знакомишься с форматом\n"
            "• получаешь поддержку и подсказки\n"
            "• и — важно — <b>каждый день оплачивается</b>\n\n"
            "Мы сопровождаем тебя на каждом этапе и всегда на связи ✨"
        ),
        "about_platforms_text": (
            "💻 <b>Площадки и формат работы</b>\n\n"
            "Работа проходит на современных онлайн-платформах,\n"
            "где важно качество картинки и стабильная связь.\n\n"
            "Мы заранее уточняем технику — не потому что «строго»,\n"
            "а чтобы ты чувствовала себя уверенно и комфортно в процессе 🌸\n\n"
            "<b>Что обычно подходит:</b>\n"
            "• современные модели смартфонов\n"
            "• либо ноутбук / ПК с камерой\n\n"
            "Если вдруг текущее устройство не идеально подходит —\n"
            "это не проблема.\n"
            "Мы просто подскажем, какие варианты лучше,\n"
            "или ты сможешь вернуться к нам позже 🤍\n\n"
            "Наша цель — чтобы работа приносила удовольствие,\n"
            "а не стресс из-за техники."
        ),
        "about_income_text": (
            "💰 <b>Доход и выплаты</b>\n\n"
            "На старте большинство моделей выходят\n"
            "на доход <b>$800–1000 в месяц</b>.\n\n"
            "<b>Что влияет на доход:</b>\n"
            "• твоя активность\n"
            "• умение общаться\n"
            "• регулярность выходов\n"
            "• следование рекомендациям @streamflowmanager\n\n"
            "<b>Выплаты:</b>\n"
            "• происходят еженедельно\n"
            "• без задержек\n"
            "• в удобном формате\n\n"
            "<b>Валюта:</b>\n"
            "USD или USDT\n\n"
            "<b>Способ получения:</b>\n"
            "• для РФ — банковская карта\n"
            "• для других стран — криптокошелёк\n\n"
            "Это стабильный формат работы,\n"
            "а не разовые подработки ✨"
        ),
        "portfolio_menu_reviews": "🤍 Отзывы моделей",
        "portfolio_menu_videos": "🎥 Примеры стримов",
        "portfolio_menu_pdf": "📄 PDF портфолио",
        "resume_prompt": "🤍 Похоже, анкета не завершена.\n\nХочешь продолжить заполнение?",
        "already_started_prompt": "🤍 Похоже, анкета уже начата.\n\nПродолжим с того места, где остановились?",
        "pending_status_text": "🤍 Твоя заявка сейчас на рассмотрении.",
        "accepted_status_text": "🤍 Твоя заявка уже одобрена.",
        "rejected_status_text": "🤍 Мы уже отвечали по твоей заявке.",
        "reapply_confirm": "Если хочешь заполнить новую — подтверди, пожалуйста:",
        "rate_limited": "🤍 Спасибо! Сейчас уже есть недавняя заявка.\n\nНовую можно отправить немного позже ✨",
        "cannot_send_message": "🤍 Не могу отправить сообщение. Проверь, что бот не заблокирован.",
        "temp_error_retry": "Временная ошибка. Попробуй ещё раз.",
        "stale_button": "⚠️ Эта кнопка устарела. Я обновила меню.",
        "unknown_input_hint": "🤍 Я не поняла сообщение. Выбери нужный раздел кнопками ниже ✨",
        "first_step_notice": "🤍 Это первый пункт анкеты",
        "reject_non_text": "🤍 Пожалуйста, отправь ответ текстом.",
        "field_too_long": "🤍 Ответ слишком длинный (максимум {max} символов). Отправь короче, пожалуйста.",
        "field_name_short": "🤍 Имя должно быть чуть длиннее. Напиши, пожалуйста, полностью:",
        "field_city_short": "🤍 Подскажи город и страну проживания ещё раз:",
        "field_phone_invalid": "🤍 Кажется, номер введён некорректно. Пример: +7 900 000 00 00",
        "field_age_invalid": "🤍 Напиши дату рождения в формате 01.01.2000 (только 18+):",
        "field_yes_no": "🤍 Ответь, пожалуйста, «да» или «нет»:",
        "field_devices_short": "🤍 Уточни, пожалуйста, какие устройства есть:",
        "field_device_model_short": "🤍 Напиши модель устройства, пожалуйста:",
        "field_work_time_invalid": "🤍 Напиши, пожалуйста, количество часов цифрами (например: 6):",
        "field_headphones_prompt": "🤍 Подскажи, пожалуйста, есть ли наушники с микрофоном:",
        "field_telegram_invalid": "🤍 Укажи, пожалуйста, Telegram в формате @username:",
        "field_experience_prompt": "🤍 Напиши, пожалуйста, есть ли опыт:",
        "normalized_phone_note": "🤍 Сохранила номер как: {value}",
        "normalized_birthdate_note": "🤍 Сохранила дату как: {value}",
        "normalized_yes_no_note": "🤍 Сохранила ответ как: {value}",
        "normalized_telegram_note": "🤍 Сохранила Telegram как: {value}",
        "photo_face_required": "🤍 Здесь нужно отправить <b>ФОТО АНФАС</b>.\n\n📷 Пришли фотографию, пожалуйста",
        "photo_full_required": "🤍 Здесь нужно отправить <b>ФОТО В ПРОФИЛЬ</b>.\n\n📷 Пришли фотографию, пожалуйста",
        "photo_face_label": "📷 Фото анфас",
        "photo_full_label": "🧍 Фото в профиль",
        "profile_about_title": "ℹ️ <b>Подробнее о работе</b>\n\n• Удалённый формат\n• Без 18+\n• Поддержка 24/7\n• Обучение с нуля",
        "profile_contact_title": "💬 <b>@streamflowmanager</b>\n\n{link}",
        "profile_portfolio_title": "📁 <b>Портфолио моделей</b>\n\nЗдесь ты можешь посмотреть примеры работы, отзывы и реальные кейсы.",
        "portfolio_send_error": "Не удалось отправить материалы",
        "video_cooldown": "🤍 Видео уже отправлены, посмотри, пожалуйста ✨",
        "video_send_error": "Не удалось отправить видео",
        "pdf_send_error": "Не удалось отправить документ",
        "preview_title": (
            "🌸 <b>АНКЕТА КАНДИДАТА</b> 🌸\n"
            "<i>Проверь, всё ли верно 🤍</i>\n\n"
            "👤 <b>Имя:</b> {name}\n"
            "📅 <b>Дата рождения:</b> {age}\n"
            "📞 <b>Телефон:</b> {phone}\n"
            "📲 <b>Модель устройства:</b> {device_model}\n"
            "💬 <b>Telegram:</b> {telegram}\n\n"
            "🌍 <b>Страна / город:</b> {city}\n"
            "⏱ <b>Время работы:</b> {work_time}\n"
            "💼 <b>Опыт:</b> {experience}\n"
            "🏠 <b>Отдельное помещение:</b> {living}\n\n"
            "────────\n"
            "🧾 <b>Статус:</b> {status}\n\n"
            "<i>Если нужно, используй кнопки ниже ✨</i>"
        ),
        "loading_stage_1": "✨ Проверяю детали...\nЕщё секунду 🌸",
        "loading_stage_2": "🌷 Оформляю карточку...\nПочти готово 🤍",
        "application_sent": "🤍 Спасибо! Анкета отправлена администратору ✨",
        "application_missing": "🤍 Кажется, анкета заполнена не полностью.\n\nДавай продолжим заполнение ✨",
        "recent_already_sent": "🤍 Похоже, недавно уже была отправлена заявка.\n\nНемного позже можно будет отправить новую ✨",
        "approved_tail": "🤍 Ожидайте, скоро админ напишет вам для записи на собеседование ✨",
        "rejected_reason_intro": "🤍 Спасибо за твою заявку!\n\nК сожалению, сейчас мы не можем принять её.\n\nПричина:\n{reason}\n\nЕсли появится возможность — мы обязательно напишем ✨",
    },
    "en": {
        "menu_caption": "🌷 Welcome!\nWe're happy to see you here 🤍\nChoose a section below ✨",
        "accept_caption": "🌸 Your application has been approved! Welcome 🤍\n\nChoose a section below ✨",
        "ack_text": "✨ Great! Let's keep going 🌸",
        "loading_text": "⏳ Preparing your application...\nAlmost done 🤍",
        "support_line_1": "You're doing great 🤍",
        "support_line_2": "Thanks for your answers, this matters ✨",
        "support_line_3": "Just one more step 🌸",
        "status_line": "Application status: {status}",
        "start_private_only": "🤍 Please open a private chat with me and tap /start ✨",
        "open_private_prompt": "🤍 Open a private chat with the bot and tap /start ✨",
        "language_menu_title": "🌐 Choose your language",
        "language_changed": "✅ Language changed: {language}",
        "language_button": "🌐 Language",
        "menu_home": "🏠 Menu",
        "menu_be_model": "🌸 Become a model",
        "menu_website": "🌐 Our website",
        "menu_portfolio": "📁 Model portfolio",
        "menu_about": "ℹ️ About the work",
        "menu_contact": "💬 @streamflowmanager",
        "menu_channel": "📣 Our channel",
        "menu_lang": "🌐 Language",
        "btn_back": "⬅ Back",
        "btn_edit_data": "✏️ Edit data",
        "btn_edit_photo": "📷 Edit photos",
        "btn_send": "✅ Submit",
        "btn_continue": "▶️ Continue",
        "btn_restart": "🔄 Start over",
        "btn_cancel": "⬅️ Cancel",
        "btn_apply_again": "✅ Apply again",
        "btn_open_telegram": "Open Telegram",
        "btn_back_to_preview": "⬅ Back to preview",
        "about_menu_work": "🌷 Work format",
        "about_menu_platforms": "💻 Platforms",
        "about_menu_income": "💰 Income & payouts",
        "about_work_text": (
            "🌷 <b>About working in our project</b>\n\n"
            "We offer modern online work in a streaming format.\n"
            "This is not an office and not a rigid 9-to-5 schedule.\n"
            "It is a flexible setup you can fit into your lifestyle 🤍\n\n"
            "<b>How it works:</b>\n"
            "• you work from any location\n"
            "• you stay in a comfortable environment\n"
            "• you communicate with the audience in a friendly format\n"
            "• you build your own style and presentation\n\n"
            "<b>Schedule:</b>\n"
            "Flexible and personalized.\n"
            "Usually from 6 hours per day, but we discuss details with you.\n"
            "Our goal is consistency without burnout.\n\n"
            "<b>Onboarding period:</b>\n"
            "Before launch, there is a short promo period (2-5 days).\n"
            "During this stage you:\n"
            "• learn the format\n"
            "• get support and practical guidance\n"
            "• and importantly, <b>each day is paid</b>\n\n"
            "We stay with you at every step and remain available for support ✨"
        ),
        "about_platforms_text": (
            "💻 <b>Platforms and work setup</b>\n\n"
            "Work is done on modern online platforms where stable connection\n"
            "and clear video are important for comfortable streaming.\n\n"
            "We ask about equipment in advance not to be strict,\n"
            "but to make your start calm and predictable 🌸\n\n"
            "<b>What usually works well:</b>\n"
            "• modern smartphones\n"
            "• or a laptop / desktop with camera\n\n"
            "If your current setup is not ideal yet, that's okay.\n"
            "We'll suggest practical options,\n"
            "or you can return a bit later when ready 🤍\n\n"
            "Our goal is enjoyable work, not technical stress."
        ),
        "about_income_text": (
            "💰 <b>Income and payouts</b>\n\n"
            "At the start, many models reach\n"
            "<b>$800-1000 per month</b>.\n\n"
            "<b>What affects income:</b>\n"
            "• your activity level\n"
            "• communication skills\n"
            "• regular streaming schedule\n"
            "• following @streamflowmanager recommendations\n\n"
            "<b>Payouts:</b>\n"
            "• weekly\n"
            "• without delays\n"
            "• in a convenient format\n\n"
            "<b>Currency:</b>\n"
            "USD or USDT\n\n"
            "<b>How you receive funds:</b>\n"
            "• bank card for Russia\n"
            "• crypto wallet for other countries\n\n"
            "This is a stable work format, not one-time gigs ✨"
        ),
        "portfolio_menu_reviews": "🤍 Model reviews",
        "portfolio_menu_videos": "🎥 Stream samples",
        "portfolio_menu_pdf": "📄 Portfolio PDF",
        "resume_prompt": "🤍 Looks like your form is not finished.\n\nDo you want to continue?",
        "already_started_prompt": "🤍 Looks like your application is already started.\n\nContinue where you left off?",
        "pending_status_text": "🤍 Your application is under review.",
        "accepted_status_text": "🤍 Your application has already been approved.",
        "rejected_status_text": "🤍 We have already replied to your application.",
        "reapply_confirm": "If you want to submit a new one, please confirm:",
        "rate_limited": "🤍 Thanks! A recent application already exists.\n\nYou can submit a new one a bit later ✨",
        "cannot_send_message": "🤍 I can't send a message. Please check if the bot is not blocked.",
        "temp_error_retry": "Temporary error. Please try again.",
        "stale_button": "⚠️ This button is outdated. I refreshed the menu.",
        "unknown_input_hint": "🤍 I didn't understand that message. Please use the buttons below ✨",
        "first_step_notice": "🤍 This is the first step of the form",
        "reject_non_text": "🤍 Please send your answer as text.",
        "field_too_long": "🤍 Your message is too long (maximum {max} characters). Please send a shorter one.",
        "field_name_short": "🤍 Name is too short. Please enter full name:",
        "field_city_short": "🤍 Please enter city and country again:",
        "field_phone_invalid": "🤍 Phone number looks invalid. Example: +1 555 123 4567",
        "field_age_invalid": "🤍 Please enter birth date as 01.01.2000 (18+ only):",
        "field_yes_no": "🤍 Please answer \"yes\" or \"no\":",
        "field_devices_short": "🤍 Please specify your devices:",
        "field_device_model_short": "🤍 Please enter device model:",
        "field_work_time_invalid": "🤍 Please enter hours using digits (example: 6):",
        "field_headphones_prompt": "🤍 Please tell us if you have headphones with mic:",
        "field_telegram_invalid": "🤍 Please provide Telegram in format @username:",
        "field_experience_prompt": "🤍 Please write your experience (or none):",
        "normalized_phone_note": "🤍 Saved phone as: {value}",
        "normalized_birthdate_note": "🤍 Saved birth date as: {value}",
        "normalized_yes_no_note": "🤍 Saved answer as: {value}",
        "normalized_telegram_note": "🤍 Saved Telegram as: {value}",
        "photo_face_required": "🤍 A <b>FRONT-FACE PHOTO</b> is required here.\n\n📷 Please send a photo",
        "photo_full_required": "🤍 A <b>PROFILE PHOTO</b> is required here.\n\n📷 Please send a photo",
        "photo_face_label": "📷 Front-face photo",
        "photo_full_label": "🧍 Profile photo",
        "profile_about_title": "ℹ️ <b>About the work</b>\n\n• Remote format\n• No 18+\n• 24/7 support\n• Training from scratch",
        "profile_contact_title": "💬 <b>@streamflowmanager</b>\n\n{link}",
        "profile_portfolio_title": "📁 <b>Model portfolio</b>\n\nHere you can view work samples, reviews and real cases.",
        "portfolio_send_error": "Failed to send materials",
        "video_cooldown": "🤍 Videos were already sent, please check them ✨",
        "video_send_error": "Failed to send videos",
        "pdf_send_error": "Failed to send document",
        "preview_title": (
            "🌸 <b>CANDIDATE APPLICATION</b> 🌸\n"
            "<i>Please review your details 🤍</i>\n\n"
            "👤 <b>Name:</b> {name}\n"
            "📅 <b>Birth date:</b> {age}\n"
            "📞 <b>Phone:</b> {phone}\n"
            "📲 <b>Device model:</b> {device_model}\n"
            "💬 <b>Telegram:</b> {telegram}\n\n"
            "🌍 <b>Country / city:</b> {city}\n"
            "⏱ <b>Work time:</b> {work_time}\n"
            "💼 <b>Experience:</b> {experience}\n"
            "🏠 <b>Private room available:</b> {living}\n\n"
            "────────\n"
            "🧾 <b>Status:</b> {status}\n\n"
            "<i>Use buttons below if you want to edit anything ✨</i>"
        ),
        "loading_stage_1": "✨ Checking details...\nOne more second 🌸",
        "loading_stage_2": "🌷 Building your card...\nAlmost done 🤍",
        "application_sent": "🤍 Thank you! Your application has been sent to the admin ✨",
        "application_missing": "🤍 Looks like your application is incomplete.\n\nLet's continue ✨",
        "recent_already_sent": "🤍 Looks like you have recently submitted an application.\n\nYou can send a new one later ✨",
        "approved_tail": "🤍 Please wait, admin will message you soon to schedule an interview ✨",
        "rejected_reason_intro": "🤍 Thanks for your application!\n\nUnfortunately, we can't accept it right now.\n\nReason:\n{reason}\n\nIf things change, we will contact you ✨",
    },
    "pt": {
        "menu_caption": "🌷 Bem-vinda!\nQue bom ter você aqui 🤍\nEscolha uma seção abaixo ✨",
        "accept_caption": "🌸 Sua candidatura foi aprovada! Bem-vinda 🤍\n\nEscolha uma seção abaixo ✨",
        "ack_text": "✨ Perfeito! Vamos continuar 🌸",
        "loading_text": "⏳ Preparando seu formulário...\nQuase pronto 🤍",
        "support_line_1": "Você está indo muito bem 🤍",
        "support_line_2": "Obrigada pelas respostas, isso é importante ✨",
        "support_line_3": "Falta pouco 🌸",
        "status_line": "Status da candidatura: {status}",
        "start_private_only": "🤍 Abra um chat privado comigo e toque em /start ✨",
        "open_private_prompt": "🤍 Abra um chat privado com o bot e toque em /start ✨",
        "language_menu_title": "🌐 Escolha seu idioma",
        "language_changed": "✅ Idioma alterado: {language}",
        "language_button": "🌐 Idioma",
        "menu_home": "🏠 Menu",
        "menu_be_model": "🌸 Tornar-se modelo",
        "menu_website": "🌐 Nosso site",
        "menu_portfolio": "📁 Portfólio de modelos",
        "menu_about": "ℹ️ Sobre o trabalho",
        "menu_contact": "💬 @streamflowmanager",
        "menu_channel": "📣 Nosso canal",
        "menu_lang": "🌐 Idioma",
        "btn_back": "⬅ Voltar",
        "btn_edit_data": "✏️ Editar dados",
        "btn_edit_photo": "📷 Editar fotos",
        "btn_send": "✅ Enviar",
        "btn_continue": "▶️ Continuar",
        "btn_restart": "🔄 Recomeçar",
        "btn_cancel": "⬅️ Cancelar",
        "btn_apply_again": "✅ Enviar novamente",
        "btn_open_telegram": "Abrir Telegram",
        "btn_back_to_preview": "⬅ Voltar à pré-visualização",
        "about_menu_work": "🌷 Formato de trabalho",
        "about_menu_platforms": "💻 Plataformas",
        "about_menu_income": "💰 Ganhos e pagamentos",
        "about_work_text": (
            "🌷 <b>Sobre o trabalho no nosso projeto</b>\n\n"
            "Oferecemos um formato moderno de trabalho online com streaming.\n"
            "Não é escritório e não é uma rotina rígida.\n"
            "É um formato flexível que se adapta à sua vida 🤍\n\n"
            "<b>Como funciona:</b>\n"
            "• você trabalha de qualquer lugar\n"
            "• em um ambiente confortável para você\n"
            "• conversa com a audiência em um formato amigável\n"
            "• constrói seu próprio estilo e apresentação\n\n"
            "<b>Horário:</b>\n"
            "Flexível e ajustado individualmente.\n"
            "Geralmente a partir de 6 horas por dia, mas tudo é conversado.\n"
            "Nosso foco é constância sem esgotamento.\n\n"
            "<b>Período inicial:</b>\n"
            "Antes do início oficial, existe um período curto de 2-5 dias.\n"
            "Nesse período você:\n"
            "• entende o formato\n"
            "• recebe suporte e orientações\n"
            "• e, importante: <b>cada dia é pago</b>\n\n"
            "Acompanhamos você em cada etapa e ficamos sempre disponíveis ✨"
        ),
        "about_platforms_text": (
            "💻 <b>Plataformas e formato de trabalho</b>\n\n"
            "O trabalho acontece em plataformas online modernas,\n"
            "onde conexão estável e imagem clara ajudam no conforto.\n\n"
            "Perguntamos sobre os dispositivos com antecedência não para impor,\n"
            "mas para garantir um início tranquilo 🌸\n\n"
            "<b>O que normalmente funciona bem:</b>\n"
            "• smartphones atuais\n"
            "• ou notebook / PC com câmera\n\n"
            "Se o dispositivo atual ainda não for ideal, sem problema.\n"
            "Vamos sugerir opções práticas,\n"
            "ou você pode voltar depois 🤍\n\n"
            "Nosso objetivo é trabalho estável, sem estresse técnico."
        ),
        "about_income_text": (
            "💰 <b>Ganhos e pagamentos</b>\n\n"
            "No início, muitas modelos chegam a\n"
            "<b>$800-1000 por mês</b>.\n\n"
            "<b>O que influencia o ganho:</b>\n"
            "• sua atividade\n"
            "• sua comunicação\n"
            "• regularidade nas transmissões\n"
            "• seguir recomendações de @streamflowmanager\n\n"
            "<b>Pagamentos:</b>\n"
            "• semanais\n"
            "• sem atrasos\n"
            "• em formato conveniente\n\n"
            "<b>Moeda:</b>\n"
            "USD ou USDT\n\n"
            "<b>Forma de recebimento:</b>\n"
            "• cartão bancário na Rússia\n"
            "• carteira cripto em outros países\n\n"
            "É um formato de trabalho estável,\n"
            "não uma renda pontual ✨"
        ),
        "portfolio_menu_reviews": "🤍 Avaliações",
        "portfolio_menu_videos": "🎥 Exemplos de stream",
        "portfolio_menu_pdf": "📄 PDF do portfólio",
        "resume_prompt": "🤍 Parece que seu formulário não foi concluído.\n\nQuer continuar?",
        "already_started_prompt": "🤍 Parece que sua candidatura já foi iniciada.\n\nContinuar de onde parou?",
        "pending_status_text": "🤍 Sua candidatura está em análise.",
        "accepted_status_text": "🤍 Sua candidatura já foi aprovada.",
        "rejected_status_text": "🤍 Já respondemos sua candidatura.",
        "reapply_confirm": "Se quiser enviar uma nova, confirme:",
        "rate_limited": "🤍 Obrigada! Já existe uma candidatura recente.\n\nVocê poderá enviar uma nova mais tarde ✨",
        "cannot_send_message": "🤍 Não consegui enviar a mensagem. Verifique se o bot não está bloqueado.",
        "temp_error_retry": "Erro temporário. Tente novamente.",
        "stale_button": "⚠️ Este botão está desatualizado. Atualizei o menu.",
        "unknown_input_hint": "🤍 Não entendi essa mensagem. Use os botões abaixo ✨",
        "first_step_notice": "🤍 Este é o primeiro passo do formulário",
        "reject_non_text": "🤍 Envie sua resposta em texto, por favor.",
        "field_too_long": "🤍 A resposta está muito longa (máximo de {max} caracteres). Envie uma versão menor.",
        "field_name_short": "🤍 O nome está muito curto. Digite o nome completo:",
        "field_city_short": "🤍 Informe cidade e país novamente:",
        "field_phone_invalid": "🤍 O telefone parece inválido. Exemplo: +55 11 99999 9999",
        "field_age_invalid": "🤍 Informe a data de nascimento no formato 01.01.2000 (somente 18+):",
        "field_yes_no": "🤍 Responda \"sim\" ou \"não\":",
        "field_devices_short": "🤍 Informe quais dispositivos você tem:",
        "field_device_model_short": "🤍 Informe o modelo do dispositivo:",
        "field_work_time_invalid": "🤍 Informe as horas com números (exemplo: 6):",
        "field_headphones_prompt": "🤍 Você tem fones com microfone?",
        "field_telegram_invalid": "🤍 Informe o Telegram no formato @username:",
        "field_experience_prompt": "🤍 Escreva sua experiência (ou nenhuma):",
        "normalized_phone_note": "🤍 Número salvo como: {value}",
        "normalized_birthdate_note": "🤍 Data salva como: {value}",
        "normalized_yes_no_note": "🤍 Resposta salva como: {value}",
        "normalized_telegram_note": "🤍 Telegram salvo como: {value}",
        "photo_face_required": "🤍 Aqui precisa de <b>FOTO DE FRENTE</b>.\n\n📷 Envie uma foto, por favor",
        "photo_full_required": "🤍 Aqui precisa de <b>FOTO DE PERFIL</b>.\n\n📷 Envie uma foto, por favor",
        "photo_face_label": "📷 Foto de frente",
        "photo_full_label": "🧍 Foto de perfil",
        "profile_about_title": "ℹ️ <b>Sobre o trabalho</b>\n\n• Formato remoto\n• Sem 18+\n• Suporte 24/7\n• Treinamento do zero",
        "profile_contact_title": "💬 <b>@streamflowmanager</b>\n\n{link}",
        "profile_portfolio_title": "📁 <b>Portfólio de modelos</b>\n\nAqui você pode ver exemplos, avaliações e casos reais.",
        "portfolio_send_error": "Não foi possível enviar os materiais",
        "video_cooldown": "🤍 Os vídeos já foram enviados, confira por favor ✨",
        "video_send_error": "Não foi possível enviar os vídeos",
        "pdf_send_error": "Não foi possível enviar o documento",
        "preview_title": (
            "🌸 <b>FICHA DA CANDIDATA</b> 🌸\n"
            "<i>Confira seus dados, por favor 🤍</i>\n\n"
            "👤 <b>Nome:</b> {name}\n"
            "📅 <b>Data de nascimento:</b> {age}\n"
            "📞 <b>Telefone:</b> {phone}\n"
            "📲 <b>Modelo do dispositivo:</b> {device_model}\n"
            "💬 <b>Telegram:</b> {telegram}\n\n"
            "🌍 <b>País / cidade:</b> {city}\n"
            "⏱ <b>Tempo de trabalho:</b> {work_time}\n"
            "💼 <b>Experiência:</b> {experience}\n"
            "🏠 <b>Ambiente privado disponível:</b> {living}\n\n"
            "────────\n"
            "🧾 <b>Status:</b> {status}\n\n"
            "<i>Use os botões abaixo se quiser ajustar algo ✨</i>"
        ),
        "loading_stage_1": "✨ Verificando detalhes...\nSó mais um segundo 🌸",
        "loading_stage_2": "🌷 Montando seu cartão...\nQuase pronto 🤍",
        "application_sent": "🤍 Obrigada! Sua candidatura foi enviada para o admin ✨",
        "application_missing": "🤍 Parece que sua candidatura está incompleta.\n\nVamos continuar ✨",
        "recent_already_sent": "🤍 Parece que você enviou uma candidatura recentemente.\n\nVocê poderá enviar outra mais tarde ✨",
        "approved_tail": "🤍 Aguarde, o admin vai te chamar em breve para agendar a entrevista ✨",
        "rejected_reason_intro": "🤍 Obrigada pela sua candidatura!\n\nInfelizmente não podemos aceitar agora.\n\nMotivo:\n{reason}\n\nSe mudar algo, entraremos em contato ✨",
    },
    "es": {
        "menu_caption": "🌷 ¡Bienvenida!\nNos alegra verte aquí 🤍\nElige una sección abajo ✨",
        "accept_caption": "🌸 ¡Tu solicitud fue aprobada! Bienvenida 🤍\n\nElige una sección abajo ✨",
        "ack_text": "✨ Perfecto, seguimos 🌸",
        "loading_text": "⏳ Preparando tu solicitud...\nCasi listo 🤍",
        "support_line_1": "Lo estás haciendo muy bien 🤍",
        "support_line_2": "Gracias por tus respuestas, son importantes ✨",
        "support_line_3": "Falta muy poco 🌸",
        "status_line": "Estado de la solicitud: {status}",
        "start_private_only": "🤍 Escríbeme en privado y pulsa /start ✨",
        "open_private_prompt": "🤍 Abre un chat privado con el bot y pulsa /start ✨",
        "language_menu_title": "🌐 Elige tu idioma",
        "language_changed": "✅ Idioma cambiado: {language}",
        "language_button": "🌐 Idioma",
        "menu_home": "🏠 Menú",
        "menu_be_model": "🌸 Ser modelo",
        "menu_website": "🌐 Nuestro sitio",
        "menu_portfolio": "📁 Portafolio de modelos",
        "menu_about": "ℹ️ Sobre el trabajo",
        "menu_contact": "💬 @streamflowmanager",
        "menu_channel": "📣 Nuestro canal",
        "menu_lang": "🌐 Idioma",
        "btn_back": "⬅ Atrás",
        "btn_edit_data": "✏️ Editar datos",
        "btn_edit_photo": "📷 Editar fotos",
        "btn_send": "✅ Enviar",
        "btn_continue": "▶️ Continuar",
        "btn_restart": "🔄 Empezar de nuevo",
        "btn_cancel": "⬅️ Cancelar",
        "btn_apply_again": "✅ Enviar de nuevo",
        "btn_open_telegram": "Abrir Telegram",
        "btn_back_to_preview": "⬅ Volver a la vista previa",
        "about_menu_work": "🌷 Formato de trabajo",
        "about_menu_platforms": "💻 Plataformas",
        "about_menu_income": "💰 Ingresos y pagos",
        "about_work_text": (
            "🌷 <b>Sobre el trabajo en nuestro proyecto</b>\n\n"
            "Ofrecemos trabajo online moderno en formato de streaming.\n"
            "No es oficina ni un horario rígido.\n"
            "Es un formato flexible que puedes adaptar a tu vida 🤍\n\n"
            "<b>Cómo funciona:</b>\n"
            "• trabajas desde cualquier lugar\n"
            "• en un entorno cómodo para ti\n"
            "• te comunicas con la audiencia en un formato amigable\n"
            "• construyes tu propio estilo y presentación\n\n"
            "<b>Horario:</b>\n"
            "Flexible e individual.\n"
            "Normalmente desde 6 horas al día, pero se ajusta contigo.\n"
            "Buscamos constancia sin agotamiento.\n\n"
            "<b>Período inicial:</b>\n"
            "Antes de empezar, hay un período corto de 2-5 días.\n"
            "En ese tiempo tú:\n"
            "• conoces el formato\n"
            "• recibes apoyo y guía\n"
            "• y, lo importante: <b>cada día es pagado</b>\n\n"
            "Te acompañamos en cada etapa y siempre estamos disponibles ✨"
        ),
        "about_platforms_text": (
            "💻 <b>Plataformas y formato de trabajo</b>\n\n"
            "El trabajo se realiza en plataformas online modernas,\n"
            "donde la conexión estable y la imagen clara mejoran la experiencia.\n\n"
            "Pedimos datos de equipo con antelación no por rigidez,\n"
            "sino para que empieces con confianza 🌸\n\n"
            "<b>Qué suele funcionar bien:</b>\n"
            "• smartphones actuales\n"
            "• o portátil / PC con cámara\n\n"
            "Si tu equipo actual aún no es ideal, no pasa nada.\n"
            "Te diremos opciones prácticas,\n"
            "o puedes volver más adelante 🤍\n\n"
            "Nuestro objetivo es trabajo cómodo, sin estrés técnico."
        ),
        "about_income_text": (
            "💰 <b>Ingresos y pagos</b>\n\n"
            "Al inicio, muchas modelos alcanzan\n"
            "<b>$800-1000 al mes</b>.\n\n"
            "<b>Qué influye en los ingresos:</b>\n"
            "• tu actividad\n"
            "• tu comunicación\n"
            "• regularidad de salidas\n"
            "• seguir recomendaciones de @streamflowmanager\n\n"
            "<b>Pagos:</b>\n"
            "• semanales\n"
            "• sin retrasos\n"
            "• en formato cómodo\n\n"
            "<b>Moneda:</b>\n"
            "USD o USDT\n\n"
            "<b>Forma de cobro:</b>\n"
            "• tarjeta bancaria en Rusia\n"
            "• billetera cripto en otros países\n\n"
            "Es un formato estable de trabajo,\n"
            "no ingresos puntuales ✨"
        ),
        "portfolio_menu_reviews": "🤍 Reseñas",
        "portfolio_menu_videos": "🎥 Ejemplos de stream",
        "portfolio_menu_pdf": "📄 PDF del portafolio",
        "resume_prompt": "🤍 Parece que tu formulario no está completo.\n\n¿Quieres continuar?",
        "already_started_prompt": "🤍 Parece que tu solicitud ya está iniciada.\n\n¿Continuamos desde donde quedaste?",
        "pending_status_text": "🤍 Tu solicitud está en revisión.",
        "accepted_status_text": "🤍 Tu solicitud ya fue aprobada.",
        "rejected_status_text": "🤍 Ya respondimos tu solicitud.",
        "reapply_confirm": "Si quieres enviar una nueva, confirma por favor:",
        "rate_limited": "🤍 ¡Gracias! Ya existe una solicitud reciente.\n\nPodrás enviar una nueva más tarde ✨",
        "cannot_send_message": "🤍 No puedo enviar el mensaje. Revisa que el bot no esté bloqueado.",
        "temp_error_retry": "Error temporal. Inténtalo de nuevo.",
        "stale_button": "⚠️ Este botón está desactualizado. Actualicé el menú.",
        "unknown_input_hint": "🤍 No entendí ese mensaje. Usa los botones de abajo ✨",
        "first_step_notice": "🤍 Este es el primer paso del formulario",
        "reject_non_text": "🤍 Por favor envía la respuesta en texto.",
        "field_too_long": "🤍 El mensaje es demasiado largo (máximo {max} caracteres). Envíalo más corto, por favor.",
        "field_name_short": "🤍 El nombre es muy corto. Escribe el nombre completo:",
        "field_city_short": "🤍 Indica ciudad y país nuevamente:",
        "field_phone_invalid": "🤍 El teléfono parece incorrecto. Ejemplo: +34 600 000 000",
        "field_age_invalid": "🤍 Escribe la fecha de nacimiento como 01.01.2000 (solo 18+):",
        "field_yes_no": "🤍 Responde \"sí\" o \"no\":",
        "field_devices_short": "🤍 Indica qué dispositivos tienes:",
        "field_device_model_short": "🤍 Escribe el modelo del dispositivo:",
        "field_work_time_invalid": "🤍 Indica horas con números (ejemplo: 6):",
        "field_headphones_prompt": "🤍 ¿Tienes auriculares con micrófono?",
        "field_telegram_invalid": "🤍 Indica Telegram en formato @username:",
        "field_experience_prompt": "🤍 Escribe tu experiencia (o ninguna):",
        "normalized_phone_note": "🤍 Número guardado como: {value}",
        "normalized_birthdate_note": "🤍 Fecha guardada como: {value}",
        "normalized_yes_no_note": "🤍 Respuesta guardada como: {value}",
        "normalized_telegram_note": "🤍 Telegram guardado como: {value}",
        "photo_face_required": "🤍 Aquí necesitas <b>FOTO DE FRENTE</b>.\n\n📷 Envía una foto, por favor",
        "photo_full_required": "🤍 Aquí necesitas <b>FOTO DE PERFIL</b>.\n\n📷 Envía una foto, por favor",
        "photo_face_label": "📷 Foto de frente",
        "photo_full_label": "🧍 Foto de perfil",
        "profile_about_title": "ℹ️ <b>Sobre el trabajo</b>\n\n• Formato remoto\n• Sin 18+\n• Soporte 24/7\n• Formación desde cero",
        "profile_contact_title": "💬 <b>@streamflowmanager</b>\n\n{link}",
        "profile_portfolio_title": "📁 <b>Portafolio de modelos</b>\n\nAquí puedes ver ejemplos, reseñas y casos reales.",
        "portfolio_send_error": "No se pudieron enviar los materiales",
        "video_cooldown": "🤍 Los videos ya fueron enviados, revísalos por favor ✨",
        "video_send_error": "No se pudieron enviar los videos",
        "pdf_send_error": "No se pudo enviar el documento",
        "preview_title": (
            "🌸 <b>SOLICITUD DE CANDIDATA</b> 🌸\n"
            "<i>Revisa tus datos, por favor 🤍</i>\n\n"
            "👤 <b>Nombre:</b> {name}\n"
            "📅 <b>Fecha de nacimiento:</b> {age}\n"
            "📞 <b>Teléfono:</b> {phone}\n"
            "📲 <b>Modelo del dispositivo:</b> {device_model}\n"
            "💬 <b>Telegram:</b> {telegram}\n\n"
            "🌍 <b>País / ciudad:</b> {city}\n"
            "⏱ <b>Tiempo de trabajo:</b> {work_time}\n"
            "💼 <b>Experiencia:</b> {experience}\n"
            "🏠 <b>Espacio privado disponible:</b> {living}\n\n"
            "────────\n"
            "🧾 <b>Estado:</b> {status}\n\n"
            "<i>Usa los botones de abajo si quieres corregir algo ✨</i>"
        ),
        "loading_stage_1": "✨ Revisando detalles...\nUn segundo más 🌸",
        "loading_stage_2": "🌷 Preparando tu ficha...\nCasi listo 🤍",
        "application_sent": "🤍 ¡Gracias! Tu solicitud fue enviada al admin ✨",
        "application_missing": "🤍 Parece que tu solicitud está incompleta.\n\nVamos a continuar ✨",
        "recent_already_sent": "🤍 Parece que enviaste una solicitud hace poco.\n\nPodrás enviar otra más tarde ✨",
        "approved_tail": "🤍 Espera, el admin te escribirá pronto para agendar entrevista ✨",
        "rejected_reason_intro": "🤍 ¡Gracias por tu solicitud!\n\nLamentablemente no podemos aceptarla ahora.\n\nMotivo:\n{reason}\n\nSi cambia algo, te escribiremos ✨",
    },
}


STATUS_LABELS_BY_LANG = {
    "ru": {
        "new": "📝 Черновик",
        "pending": "🟡 На рассмотрении",
        "accepted": "✅ Одобрена",
        "rejected": "❌ Отклонена",
    },
    "en": {
        "new": "📝 Draft",
        "pending": "🟡 Under review",
        "accepted": "✅ Approved",
        "rejected": "❌ Rejected",
    },
    "pt": {
        "new": "📝 Rascunho",
        "pending": "🟡 Em análise",
        "accepted": "✅ Aprovada",
        "rejected": "❌ Recusada",
    },
    "es": {
        "new": "📝 Borrador",
        "pending": "🟡 En revisión",
        "accepted": "✅ Aprobada",
        "rejected": "❌ Rechazada",
    },
}


FORM_QUESTIONS_BY_LANG = {
    "ru": {
        ApplicationStates.name: "Как тебя зовут?\n\nНапиши имя полностью:",
        ApplicationStates.phone: "Контактный телефон (+код):",
        ApplicationStates.age: "Дата рождения\n\nПример: 01.01.2000",
        ApplicationStates.device_model: "Модель устройства:",
        ApplicationStates.telegram: "Telegram (@username):",
        ApplicationStates.city: "В какой стране ты сейчас?\n\nМожно в формате: Город, Страна",
        ApplicationStates.work_time: "Сколько часов в день готова уделять?",
        ApplicationStates.experience: "Есть опыт в стримах/эфирах?\n\nЕсли нет — так и напиши.",
        ApplicationStates.living: "Есть отдельное помещение без посторонних?\n\nОтветь «да» или «нет».",
        ApplicationStates.devices: "Какие устройства у тебя есть? (необязательно)",
        ApplicationStates.headphones: "Есть ли наушники с микрофоном? (необязательно)",
        ApplicationStates.photo_face: "Пришли фото анфас:",
        ApplicationStates.photo_full: "Пришли фото в профиль:",
    },
    "en": {
        ApplicationStates.name: "What is your full name?",
        ApplicationStates.phone: "Contact phone (+country code):",
        ApplicationStates.age: "Birth date\n\nExample: 01.01.2000",
        ApplicationStates.device_model: "Device model:",
        ApplicationStates.telegram: "Telegram (@username):",
        ApplicationStates.city: "Which country are you currently in?\n\nYou can write: City, Country",
        ApplicationStates.work_time: "How many hours per day can you commit?",
        ApplicationStates.experience: "Do you have streaming/live experience?\n\nIf not, just write none.",
        ApplicationStates.living: "Do you have a private room without other people?\n\nPlease answer yes or no.",
        ApplicationStates.devices: "What devices do you have? (optional)",
        ApplicationStates.headphones: "Do you have headphones with mic? (optional)",
        ApplicationStates.photo_face: "Please send a front-face photo:",
        ApplicationStates.photo_full: "Please send a profile photo:",
    },
    "pt": {
        ApplicationStates.name: "Qual é seu nome completo?",
        ApplicationStates.phone: "Telefone de contato (+código):",
        ApplicationStates.age: "Data de nascimento\n\nExemplo: 01.01.2000",
        ApplicationStates.device_model: "Modelo do dispositivo:",
        ApplicationStates.telegram: "Telegram (@username):",
        ApplicationStates.city: "Em qual país você está agora?\n\nPode escrever: Cidade, País",
        ApplicationStates.work_time: "Quantas horas por dia você pode dedicar?",
        ApplicationStates.experience: "Você tem experiência com lives/streams?\n\nSe não tiver, escreva sem experiência.",
        ApplicationStates.living: "Você tem um ambiente privado sem outras pessoas?\n\nResponda sim ou não.",
        ApplicationStates.devices: "Quais dispositivos você tem? (opcional)",
        ApplicationStates.headphones: "Você tem fones com microfone? (opcional)",
        ApplicationStates.photo_face: "Envie uma foto de frente:",
        ApplicationStates.photo_full: "Envie uma foto de perfil:",
    },
    "es": {
        ApplicationStates.name: "¿Cuál es tu nombre completo?",
        ApplicationStates.phone: "Teléfono de contacto (+código):",
        ApplicationStates.age: "Fecha de nacimiento\n\nEjemplo: 01.01.2000",
        ApplicationStates.device_model: "Modelo del dispositivo:",
        ApplicationStates.telegram: "Telegram (@username):",
        ApplicationStates.city: "¿En qué país estás ahora?\n\nPuedes escribir: Ciudad, País",
        ApplicationStates.work_time: "¿Cuántas horas por día puedes dedicar?",
        ApplicationStates.experience: "¿Tienes experiencia en streams/directos?\n\nSi no, escribe sin experiencia.",
        ApplicationStates.living: "¿Tienes un espacio privado sin otras personas?\n\nResponde sí o no.",
        ApplicationStates.devices: "¿Qué dispositivos tienes? (opcional)",
        ApplicationStates.headphones: "¿Tienes auriculares con micrófono? (opcional)",
        ApplicationStates.photo_face: "Envía una foto de frente:",
        ApplicationStates.photo_full: "Envía una foto de perfil:",
    },
}


FIELD_TITLES_BY_LANG = {
    "ru": {
        "name": "👤 Имя",
        "city": "🌍 Город и страна",
        "phone": "📞 Телефон",
        "age": "📅 Дата рождения",
        "living": "🏠 Помещение без посторонних",
        "devices": "📱 Устройства",
        "device_model": "📲 Модель устройства",
        "work_time": "⏱ Время работы",
        "headphones": "🎧 Наушники",
        "telegram": "💬 Telegram",
        "experience": "💼 Опыт",
    },
    "en": {
        "name": "👤 Name",
        "city": "🌍 City and country",
        "phone": "📞 Phone",
        "age": "📅 Birth date",
        "living": "🏠 Private room",
        "devices": "📱 Devices",
        "device_model": "📲 Device model",
        "work_time": "⏱ Work time",
        "headphones": "🎧 Headphones",
        "telegram": "💬 Telegram",
        "experience": "💼 Experience",
    },
    "pt": {
        "name": "👤 Nome",
        "city": "🌍 Cidade e país",
        "phone": "📞 Telefone",
        "age": "📅 Data de nascimento",
        "living": "🏠 Espaço privado",
        "devices": "📱 Dispositivos",
        "device_model": "📲 Modelo do dispositivo",
        "work_time": "⏱ Tempo de trabalho",
        "headphones": "🎧 Fones",
        "telegram": "💬 Telegram",
        "experience": "💼 Experiência",
    },
    "es": {
        "name": "👤 Nombre",
        "city": "🌍 Ciudad y país",
        "phone": "📞 Teléfono",
        "age": "📅 Fecha de nacimiento",
        "living": "🏠 Espacio privado",
        "devices": "📱 Dispositivos",
        "device_model": "📲 Modelo del dispositivo",
        "work_time": "⏱ Tiempo de trabajo",
        "headphones": "🎧 Auriculares",
        "telegram": "💬 Telegram",
        "experience": "💼 Experiencia",
    },
}


def t(lang: str | None, key: str, **kwargs) -> str:
    code = normalize_lang(lang)
    value = TRANSLATIONS.get(code, {}).get(key)
    if value is None:
        value = TRANSLATIONS["ru"].get(key, key)
    if kwargs:
        try:
            return value.format(**kwargs)
        except Exception:
            return value
    return value


def status_label(status: str, lang: str | None = None) -> str:
    code = normalize_lang(lang)
    labels = STATUS_LABELS_BY_LANG.get(code) or STATUS_LABELS_BY_LANG["ru"]
    return labels.get(status, status)


def form_question(state: ApplicationStates, lang: str | None = None) -> str:
    code = normalize_lang(lang)
    questions = FORM_QUESTIONS_BY_LANG.get(code) or FORM_QUESTIONS_BY_LANG["ru"]
    return questions[state]


def field_title(field_key: str, lang: str | None = None) -> str:
    code = normalize_lang(lang)
    labels = FIELD_TITLES_BY_LANG.get(code) or FIELD_TITLES_BY_LANG["ru"]
    return labels.get(field_key, field_key)


def support_lines(lang: str | None = None) -> list[str]:
    code = normalize_lang(lang)
    return [
        t(code, "support_line_1"),
        t(code, "support_line_2"),
        t(code, "support_line_3"),
    ]


# Backward-compatible aliases (Russian default)
MENU_CAPTION = t("ru", "menu_caption")
ACCEPT_CAPTION = t("ru", "accept_caption")
ACK_TEXT = t("ru", "ack_text")
SUPPORT_LINES = support_lines("ru")
LOADING_TEXT = t("ru", "loading_text")
STATUS_LABELS = STATUS_LABELS_BY_LANG["ru"]
FORM_QUESTIONS = FORM_QUESTIONS_BY_LANG["ru"]
FIELD_TITLES = FIELD_TITLES_BY_LANG["ru"]
