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
        "menu_contact": "💬 Связь с администратором",
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
        "first_step_notice": "🤍 Это первый пункт анкеты",
        "reject_non_text": "🤍 Пожалуйста, отправь ответ текстом.",
        "field_name_short": "🤍 Имя должно быть чуть длиннее. Напиши, пожалуйста, полностью:",
        "field_city_short": "🤍 Подскажи город и страну проживания ещё раз:",
        "field_phone_invalid": "🤍 Кажется, номер введён некорректно. Пример: +7 900 000 00 00",
        "field_age_invalid": "🤍 Напиши дату рождения в формате 01.01.2000:",
        "field_yes_no": "🤍 Ответь, пожалуйста, «да» или «нет»:",
        "field_devices_short": "🤍 Уточни, пожалуйста, какие устройства есть:",
        "field_device_model_short": "🤍 Напиши модель устройства, пожалуйста:",
        "field_work_time_invalid": "🤍 Напиши, пожалуйста, количество часов цифрами (например: 6):",
        "field_headphones_prompt": "🤍 Подскажи, пожалуйста, есть ли наушники с микрофоном:",
        "field_telegram_invalid": "🤍 Укажи, пожалуйста, Telegram в формате @username:",
        "field_experience_prompt": "🤍 Напиши, пожалуйста, есть ли опыт:",
        "photo_face_required": "🤍 Здесь нужно отправить <b>ФОТО АНФАС</b>.\n\n📷 Пришли фотографию, пожалуйста",
        "photo_full_required": "🤍 Здесь нужно отправить <b>ФОТО В ПОЛНЫЙ РОСТ</b>.\n\n📷 Пришли фотографию, пожалуйста",
        "photo_face_label": "📷 Фото анфас",
        "photo_full_label": "🧍 Фото в полный рост",
        "profile_about_title": "ℹ️ <b>Подробнее о работе</b>\n\n• Удалённый формат\n• Без 18+\n• Поддержка 24/7\n• Обучение с нуля",
        "profile_contact_title": "💬 <b>Связь с администратором</b>\n\n{link}",
        "profile_portfolio_title": "📁 <b>Портфолио моделей</b>\n\nЗдесь ты можешь посмотреть примеры работы, отзывы и реальные кейсы.",
        "portfolio_send_error": "Не удалось отправить материалы",
        "video_cooldown": "🤍 Видео уже отправлены, посмотри, пожалуйста ✨",
        "video_send_error": "Не удалось отправить видео",
        "pdf_send_error": "Не удалось отправить документ",
        "preview_title": (
            "🌸 <b>АНКЕТА КАНДИДАТА</b> 🌸\n"
            "<i>Проверь, всё ли верно 🤍</i>\n\n"
            "🌷 <b>Личные данные</b>\n"
            "👤 <b>Имя:</b> {name}\n"
            "🌍 <b>Город и страна:</b> {city}\n"
            "📅 <b>Дата рождения:</b> {age}\n"
            "📞 <b>Телефон:</b> {phone}\n"
            "🏠 <b>Помещение без посторонних:</b> {living}\n\n"
            "💻 <b>Техника</b>\n"
            "📱 <b>Устройства:</b> {devices}\n"
            "📲 <b>Модель:</b> {device_model}\n"
            "🎧 <b>Наушники:</b> {headphones}\n\n"
            "🕒 <b>График и опыт</b>\n"
            "⏱ <b>Время работы:</b> {work_time}\n"
            "💼 <b>Опыт:</b> {experience}\n\n"
            "💬 <b>Контакт</b>\n"
            "💬 <b>Telegram:</b> {telegram}\n\n"
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
        "menu_contact": "💬 Contact admin",
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
        "first_step_notice": "🤍 This is the first step of the form",
        "reject_non_text": "🤍 Please send your answer as text.",
        "field_name_short": "🤍 Name is too short. Please enter full name:",
        "field_city_short": "🤍 Please enter city and country again:",
        "field_phone_invalid": "🤍 Phone number looks invalid. Example: +1 555 123 4567",
        "field_age_invalid": "🤍 Please enter birth date as 01.01.2000:",
        "field_yes_no": "🤍 Please answer \"yes\" or \"no\":",
        "field_devices_short": "🤍 Please specify your devices:",
        "field_device_model_short": "🤍 Please enter device model:",
        "field_work_time_invalid": "🤍 Please enter hours using digits (example: 6):",
        "field_headphones_prompt": "🤍 Please tell us if you have headphones with mic:",
        "field_telegram_invalid": "🤍 Please provide Telegram in format @username:",
        "field_experience_prompt": "🤍 Please write your experience (or none):",
        "photo_face_required": "🤍 A <b>FRONT-FACE PHOTO</b> is required here.\n\n📷 Please send a photo",
        "photo_full_required": "🤍 A <b>FULL-BODY PHOTO</b> is required here.\n\n📷 Please send a photo",
        "photo_face_label": "📷 Front-face photo",
        "photo_full_label": "🧍 Full-body photo",
        "profile_about_title": "ℹ️ <b>About the work</b>\n\n• Remote format\n• No 18+\n• 24/7 support\n• Training from scratch",
        "profile_contact_title": "💬 <b>Contact admin</b>\n\n{link}",
        "profile_portfolio_title": "📁 <b>Model portfolio</b>\n\nHere you can view work samples, reviews and real cases.",
        "portfolio_send_error": "Failed to send materials",
        "video_cooldown": "🤍 Videos were already sent, please check them ✨",
        "video_send_error": "Failed to send videos",
        "pdf_send_error": "Failed to send document",
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
        "menu_contact": "💬 Contatar admin",
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
        "first_step_notice": "🤍 Este é o primeiro passo do formulário",
        "reject_non_text": "🤍 Envie sua resposta em texto, por favor.",
        "field_name_short": "🤍 O nome está muito curto. Digite o nome completo:",
        "field_city_short": "🤍 Informe cidade e país novamente:",
        "field_phone_invalid": "🤍 O telefone parece inválido. Exemplo: +55 11 99999 9999",
        "field_age_invalid": "🤍 Informe a data de nascimento no formato 01.01.2000:",
        "field_yes_no": "🤍 Responda \"sim\" ou \"não\":",
        "field_devices_short": "🤍 Informe quais dispositivos você tem:",
        "field_device_model_short": "🤍 Informe o modelo do dispositivo:",
        "field_work_time_invalid": "🤍 Informe as horas com números (exemplo: 6):",
        "field_headphones_prompt": "🤍 Você tem fones com microfone?",
        "field_telegram_invalid": "🤍 Informe o Telegram no formato @username:",
        "field_experience_prompt": "🤍 Escreva sua experiência (ou nenhuma):",
        "photo_face_required": "🤍 Aqui precisa de <b>FOTO DE FRENTE</b>.\n\n📷 Envie uma foto, por favor",
        "photo_full_required": "🤍 Aqui precisa de <b>FOTO DE CORPO INTEIRO</b>.\n\n📷 Envie uma foto, por favor",
        "photo_face_label": "📷 Foto de frente",
        "photo_full_label": "🧍 Foto de corpo inteiro",
        "profile_about_title": "ℹ️ <b>Sobre o trabalho</b>\n\n• Formato remoto\n• Sem 18+\n• Suporte 24/7\n• Treinamento do zero",
        "profile_contact_title": "💬 <b>Contato do admin</b>\n\n{link}",
        "profile_portfolio_title": "📁 <b>Portfólio de modelos</b>\n\nAqui você pode ver exemplos, avaliações e casos reais.",
        "portfolio_send_error": "Não foi possível enviar os materiais",
        "video_cooldown": "🤍 Os vídeos já foram enviados, confira por favor ✨",
        "video_send_error": "Não foi possível enviar os vídeos",
        "pdf_send_error": "Não foi possível enviar o documento",
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
        "menu_contact": "💬 Contactar admin",
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
        "first_step_notice": "🤍 Este es el primer paso del formulario",
        "reject_non_text": "🤍 Por favor envía la respuesta en texto.",
        "field_name_short": "🤍 El nombre es muy corto. Escribe el nombre completo:",
        "field_city_short": "🤍 Indica ciudad y país nuevamente:",
        "field_phone_invalid": "🤍 El teléfono parece incorrecto. Ejemplo: +34 600 000 000",
        "field_age_invalid": "🤍 Escribe la fecha de nacimiento como 01.01.2000:",
        "field_yes_no": "🤍 Responde \"sí\" o \"no\":",
        "field_devices_short": "🤍 Indica qué dispositivos tienes:",
        "field_device_model_short": "🤍 Escribe el modelo del dispositivo:",
        "field_work_time_invalid": "🤍 Indica horas con números (ejemplo: 6):",
        "field_headphones_prompt": "🤍 ¿Tienes auriculares con micrófono?",
        "field_telegram_invalid": "🤍 Indica Telegram en formato @username:",
        "field_experience_prompt": "🤍 Escribe tu experiencia (o ninguna):",
        "photo_face_required": "🤍 Aquí necesitas <b>FOTO DE FRENTE</b>.\n\n📷 Envía una foto, por favor",
        "photo_full_required": "🤍 Aquí necesitas <b>FOTO DE CUERPO COMPLETO</b>.\n\n📷 Envía una foto, por favor",
        "photo_face_label": "📷 Foto de frente",
        "photo_full_label": "🧍 Foto de cuerpo completo",
        "profile_about_title": "ℹ️ <b>Sobre el trabajo</b>\n\n• Formato remoto\n• Sin 18+\n• Soporte 24/7\n• Formación desde cero",
        "profile_contact_title": "💬 <b>Contacto del admin</b>\n\n{link}",
        "profile_portfolio_title": "📁 <b>Portafolio de modelos</b>\n\nAquí puedes ver ejemplos, reseñas y casos reales.",
        "portfolio_send_error": "No se pudieron enviar los materiales",
        "video_cooldown": "🤍 Los videos ya fueron enviados, revísalos por favor ✨",
        "video_send_error": "No se pudieron enviar los videos",
        "pdf_send_error": "No se pudo enviar el documento",
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
        ApplicationStates.name: "1️⃣ Как тебя зовут?\n\nНапиши имя полностью:",
        ApplicationStates.city: "2️⃣ Город и страна проживания:",
        ApplicationStates.phone: "3️⃣ Контактный телефон (+код):",
        ApplicationStates.age: "4️⃣ Дата рождения\n\nПример: 01.01.2000",
        ApplicationStates.living: "5️⃣ Есть ли помещение без посторонних?",
        ApplicationStates.devices: "6️⃣ Устройства (телефон / ПК):",
        ApplicationStates.device_model: "7️⃣ Модель устройства:",
        ApplicationStates.work_time: "8️⃣ Время работы (часов в день):",
        ApplicationStates.headphones: "9️⃣ Есть ли наушники с микрофоном:",
        ApplicationStates.telegram: "🔟 Telegram (@username):",
        ApplicationStates.experience: "1️⃣1️⃣ Опыт (если нет — напиши «нет»):",
        ApplicationStates.photo_face: "1️⃣2️⃣ Фото анфас:",
        ApplicationStates.photo_full: "1️⃣3️⃣ Фото в полный рост:",
    },
    "en": {
        ApplicationStates.name: "1️⃣ What is your full name?",
        ApplicationStates.city: "2️⃣ City and country of residence:",
        ApplicationStates.phone: "3️⃣ Contact phone (+country code):",
        ApplicationStates.age: "4️⃣ Birth date\n\nExample: 01.01.2000",
        ApplicationStates.living: "5️⃣ Do you have a private room without outsiders?",
        ApplicationStates.devices: "6️⃣ Devices (phone / PC):",
        ApplicationStates.device_model: "7️⃣ Device model:",
        ApplicationStates.work_time: "8️⃣ Work time (hours per day):",
        ApplicationStates.headphones: "9️⃣ Do you have headphones with microphone?",
        ApplicationStates.telegram: "🔟 Telegram (@username):",
        ApplicationStates.experience: "1️⃣1️⃣ Experience (if none, write \"none\"):",
        ApplicationStates.photo_face: "1️⃣2️⃣ Front-face photo:",
        ApplicationStates.photo_full: "1️⃣3️⃣ Full-body photo:",
    },
    "pt": {
        ApplicationStates.name: "1️⃣ Qual é seu nome completo?",
        ApplicationStates.city: "2️⃣ Cidade e país de residência:",
        ApplicationStates.phone: "3️⃣ Telefone de contato (+código):",
        ApplicationStates.age: "4️⃣ Data de nascimento\n\nExemplo: 01.01.2000",
        ApplicationStates.living: "5️⃣ Você tem um espaço sem pessoas por perto?",
        ApplicationStates.devices: "6️⃣ Dispositivos (telefone / PC):",
        ApplicationStates.device_model: "7️⃣ Modelo do dispositivo:",
        ApplicationStates.work_time: "8️⃣ Tempo de trabalho (horas por dia):",
        ApplicationStates.headphones: "9️⃣ Você tem fones com microfone?",
        ApplicationStates.telegram: "🔟 Telegram (@username):",
        ApplicationStates.experience: "1️⃣1️⃣ Experiência (se não tiver, escreva \"não\"):",
        ApplicationStates.photo_face: "1️⃣2️⃣ Foto de frente:",
        ApplicationStates.photo_full: "1️⃣3️⃣ Foto de corpo inteiro:",
    },
    "es": {
        ApplicationStates.name: "1️⃣ ¿Cuál es tu nombre completo?",
        ApplicationStates.city: "2️⃣ Ciudad y país de residencia:",
        ApplicationStates.phone: "3️⃣ Teléfono de contacto (+código):",
        ApplicationStates.age: "4️⃣ Fecha de nacimiento\n\nEjemplo: 01.01.2000",
        ApplicationStates.living: "5️⃣ ¿Tienes una habitación sin personas externas?",
        ApplicationStates.devices: "6️⃣ Dispositivos (teléfono / PC):",
        ApplicationStates.device_model: "7️⃣ Modelo del dispositivo:",
        ApplicationStates.work_time: "8️⃣ Tiempo de trabajo (horas por día):",
        ApplicationStates.headphones: "9️⃣ ¿Tienes auriculares con micrófono?",
        ApplicationStates.telegram: "🔟 Telegram (@username):",
        ApplicationStates.experience: "1️⃣1️⃣ Experiencia (si no tienes, escribe \"no\"):",
        ApplicationStates.photo_face: "1️⃣2️⃣ Foto de frente:",
        ApplicationStates.photo_full: "1️⃣3️⃣ Foto de cuerpo completo:",
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
