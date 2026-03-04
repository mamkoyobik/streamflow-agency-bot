(function () {
  'use strict';

  const LANGS = ['ru', 'en', 'pt', 'es'];
  const DEFAULT_LANG = 'ru';
  const STORAGE_KEY = 'streamflow_site_lang_v3';
  const PROJECT = 'streamflow_agency';
  const METRIKA_COUNTER_ID = 106823371;

  const I18N = {
    ru: {
      'a11y.skip': 'Перейти к основному контенту',
      'lang.title': 'Выберите язык',
      'lang.subtitle': 'Select your language to continue',
      'brand.subtitle': 'Model Agency',
      'nav.model': 'Формат',
      'nav.process': 'Этапы',
      'nav.income': 'Доход',
      'nav.planner': 'Калькулятор',
      'nav.portfolio': 'Портфолио',
      'nav.apply': 'Анкета',
      'cta.apply': 'Оставить заявку',
      'cta.telegram': 'Telegram',
      'mobile.menu': 'Меню',
      'mobile.close': 'Закрыть',
      'hero.eyebrow': 'Calm onboarding model',
      'hero.title': 'Агентство стриминговых моделей с понятным стартом',
      'hero.lead': 'Заполняешь короткую анкету, выбираешь мессенджер и получаешь сопровождение менеджера по шагам.',
      'hero.kpi1': 'до первого ответа',
      'hero.kpi2': 'персональный менеджер',
      'hero.kpi3': 'лет операционного опыта',
      'hero.cardTitle': 'Что получаешь сразу',
      'hero.card1': 'Пошаговый старт без хаоса',
      'hero.card2': 'Прозрачную коммуникацию в мессенджере',
      'hero.card3': 'План запуска и поддержку',
      'hero.modeLabel': 'Выбери темп старта',
      'hero.modeSoft': 'Мягкий',
      'hero.modeBalanced': 'Сбалансированный',
      'hero.modePro': 'Интенсивный',
      'hero.modeSoftValue': '3-4 ч/день',
      'hero.modeBalancedValue': '4-6 ч/день',
      'hero.modeProValue': '6-8 ч/день',
      'hero.modeSoftNote': 'Комфортный вход без перегруза в первые недели.',
      'hero.modeBalancedNote': 'Ровный темп с быстрым ростом навыков и дохода.',
      'hero.modeProNote': 'Максимальный фокус для быстрого масштабирования результата.',
      'model.eyebrow': 'Формат работы',
      'model.title': 'Аккуратная система, где каждый шаг понятен заранее',
      'model.card1.title': 'Чёткие правила',
      'model.card1.text': 'Без скрытых условий: ты заранее видишь, как устроен процесс.',
      'model.card2.title': 'Контроль темпа',
      'model.card2.text': 'Запуск без гонки: адаптация под твой ритм и доступное время.',
      'model.card3.title': 'Поддержка в диалоге',
      'model.card3.text': 'Менеджер ведёт по этапам и даёт обратную связь без перегруза.',
      'steps.eyebrow': 'Процесс',
      'steps.title': 'Три шага от заявки до старта',
      'steps.s1.title': 'Анкета',
      'steps.s1.text': 'Оставляешь короткую заявку на сайте.',
      'steps.s2.title': 'Связь в мессенджере',
      'steps.s2.text': 'Выбираешь Telegram или WhatsApp и получаешь ответ.',
      'steps.s3.title': 'Запуск',
      'steps.s3.text': 'Получаешь план действий и стартуешь с поддержкой.',
      'income.eyebrow': 'Примеры',
      'income.title': 'Ориентиры по доходу при стабильном графике',
      'income.subtitle': 'Реальные ориентиры моделей при рабочем ритме и поддержке менеджера.',
      'income.note': 'Рост дохода',
      'streams.eyebrow': 'Стрим-примеры',
      'streams.title': 'Посмотри, как выглядит рабочий эфир',
      'streams.subtitle': 'Отдельный блок с короткими примерами стримов из твоих файлов.',
      'streams.sample1': 'Стрим 01',
      'streams.sample2': 'Стрим 02',
      'streams.sample3': 'Стрим 03',
      'planner.eyebrow': 'Калькулятор',
      'planner.title': 'Оцени потенциальный доход по своему графику',
      'planner.subtitle': 'Ориентировочный расчёт по часам, дням и этапу адаптации.',
      'planner.hours': 'Часов в день',
      'planner.hoursUnit': 'часа / день',
      'planner.days': 'Дней в неделю',
      'planner.daysUnit': 'дней / неделя',
      'planner.level': 'Этап адаптации',
      'planner.level.start': 'Старт',
      'planner.level.steady': 'Стабильный ритм',
      'planner.level.pro': 'Продвинутый',
      'planner.monthly': 'Оценка в месяц',
      'planner.note': 'Это ориентировочная оценка для планирования.',
      'portfolio.eyebrow': 'Портфолио',
      'portfolio.title': 'Примеры профилей и кейсов',
      'portfolio.lead': 'Язык слайдов подстраивается под выбранную локализацию сайта.',
      'portfolio.caption': 'Слайд портфолио',
      'portfolio.prevAria': 'Предыдущий слайд',
      'portfolio.nextAria': 'Следующий слайд',
      'fit.eyebrow': 'Быстрый чек',
      'fit.title': 'Оцени готовность к старту за 20 секунд',
      'fit.c1': 'Есть стабильный интернет и личное пространство.',
      'fit.c2': 'Готова уделять минимум 3-4 часа в день.',
      'fit.c3': 'Готова работать по шагам с менеджером.',
      'fit.c4': 'Есть устройство с камерой и микрофоном.',
      'fit.c5': 'Готова перейти в мессенджер после анкеты.',
      'fit.score': 'Индекс готовности',
      'fit.high': 'Высокая готовность: можно стартовать сразу.',
      'fit.mid': 'Средняя готовность: небольшой блок подготовки улучшит запуск.',
      'fit.low': 'Низкая готовность: сначала закрой базовые условия старта.',
      'form.eyebrow': 'Анкета',
      'form.title': 'Оставь заявку за минуту',
      'form.lead': 'Сначала короткая анкета, затем переход в выбранный мессенджер для второго этапа.',
      'form.b1': 'Короткая форма без лишних полей',
      'form.b2': 'Никаких повторных отправок',
      'form.b3': 'Ответ в рабочее время',
      'form.stepLabel': 'Шаг',
      'form.step1Title': 'Шаг 1. Базовые данные',
      'form.step2Title': 'Шаг 2. Куда написать',
      'form.name': 'Имя',
      'form.phone': 'Телефон',
      'form.age': 'Дата рождения (18+)',
      'form.device': 'Модель устройства',
      'form.contactType': 'Куда написать',
      'form.contactValue': 'Контакт',
      'form.contactPlaceholderTelegram': '@username',
      'form.contactPlaceholderWhatsapp': '+7 900 000 00 00',
      'form.nextStep': 'Далее',
      'form.prevStep': 'Назад',
      'form.submit': 'Отправить заявку',
      'form.privacy': 'Отправляя форму, ты подтверждаешь согласие на обработку контактных данных для связи по заявке.',
      'form.next': 'Продолжить в мессенджере',
      'form.openTelegram': 'Открыть Telegram',
      'form.openWhatsapp': 'Открыть WhatsApp',
      'footer.channel': 'Telegram канал',
      'msg.required': 'Заполни все обязательные поля.',
      'msg.name': 'Введите корректное имя (минимум 2 символа).',
      'msg.phone': 'Укажи телефон в международном формате.',
      'msg.age': 'Укажи дату рождения в формате ДД.ММ.ГГГГ (18+).',
      'msg.device': 'Укажи модель устройства.',
      'msg.telegram': 'Telegram должен быть в формате @username.',
      'msg.whatsapp': 'WhatsApp должен быть в международном формате.',
      'msg.sending': 'Отправляем анкету...',
      'msg.success': 'Заявка принята. Перейди в мессенджер для старта.',
      'msg.error': 'Не удалось отправить заявку. Попробуйте ещё раз.',
      'msg.nextMissing': 'Ссылки пока не настроены. Напишите менеджеру в Telegram.',
      'msg.scoreLow': 'Низкая готовность: сначала закрой базовые условия старта.',
      'msg.scoreMid': 'Средняя готовность: небольшой блок подготовки улучшит запуск.',
      'msg.scoreHigh': 'Высокая готовность: можно стартовать сразу.'
    },
    en: {
      'a11y.skip': 'Skip to main content',
      'lang.title': 'Choose language',
      'lang.subtitle': 'Select your language to continue',
      'brand.subtitle': 'Model Agency',
      'nav.model': 'Format',
      'nav.process': 'Steps',
      'nav.income': 'Income',
      'nav.planner': 'Calculator',
      'nav.portfolio': 'Portfolio',
      'nav.apply': 'Form',
      'cta.apply': 'Apply now',
      'cta.telegram': 'Telegram',
      'mobile.menu': 'Menu',
      'mobile.close': 'Close',
      'hero.eyebrow': 'Calm onboarding model',
      'hero.title': 'Streaming model agency with a clear start',
      'hero.lead': 'Submit a short form, choose your messenger, and get 1:1 manager guidance.',
      'hero.kpi1': 'to first reply',
      'hero.kpi2': 'personal manager',
      'hero.kpi3': 'years of operating experience',
      'hero.cardTitle': 'What you get right away',
      'hero.card1': 'Step-by-step start without chaos',
      'hero.card2': 'Clear communication in messenger',
      'hero.card3': 'Launch plan and support',
      'hero.modeLabel': 'Pick your launch pace',
      'hero.modeSoft': 'Soft',
      'hero.modeBalanced': 'Balanced',
      'hero.modePro': 'Intense',
      'hero.modeSoftValue': '3-4 h/day',
      'hero.modeBalancedValue': '4-6 h/day',
      'hero.modeProValue': '6-8 h/day',
      'hero.modeSoftNote': 'Comfort-first onboarding with low pressure.',
      'hero.modeBalancedNote': 'Steady tempo with faster growth in skills and income.',
      'hero.modeProNote': 'High-focus mode for rapid scaling.',
      'model.eyebrow': 'Work format',
      'model.title': 'A clean system where every step is clear in advance',
      'model.card1.title': 'Clear rules',
      'model.card1.text': 'No hidden terms: you see the process upfront.',
      'model.card2.title': 'Pace control',
      'model.card2.text': 'No rush launch: adaptation to your real schedule.',
      'model.card3.title': 'Guided support',
      'model.card3.text': 'Manager helps at each stage with focused feedback.',
      'steps.eyebrow': 'Process',
      'steps.title': 'Three steps from form to launch',
      'steps.s1.title': 'Form',
      'steps.s1.text': 'You submit a short application on the site.',
      'steps.s2.title': 'Messenger contact',
      'steps.s2.text': 'Choose Telegram or WhatsApp and receive a reply.',
      'steps.s3.title': 'Launch',
      'steps.s3.text': 'Get the launch plan and start with support.',
      'income.eyebrow': 'Examples',
      'income.title': 'Income references with a stable work rhythm',
      'income.subtitle': 'Real benchmarks with a stable schedule and manager support.',
      'income.note': 'Income growth',
      'streams.eyebrow': 'Stream examples',
      'streams.title': 'See what real working streams look like',
      'streams.subtitle': 'Separate block with short stream examples from your media files.',
      'streams.sample1': 'Stream 01',
      'streams.sample2': 'Stream 02',
      'streams.sample3': 'Stream 03',
      'planner.eyebrow': 'Calculator',
      'planner.title': 'Estimate potential income based on your schedule',
      'planner.subtitle': 'Planning estimate by hours, days, and adaptation stage.',
      'planner.hours': 'Hours per day',
      'planner.hoursUnit': 'hours / day',
      'planner.days': 'Days per week',
      'planner.daysUnit': 'days / week',
      'planner.level': 'Adaptation stage',
      'planner.level.start': 'Start',
      'planner.level.steady': 'Steady rhythm',
      'planner.level.pro': 'Advanced',
      'planner.monthly': 'Monthly estimate',
      'planner.note': 'This is an approximate planning estimate.',
      'portfolio.eyebrow': 'Portfolio',
      'portfolio.title': 'Profile and case examples',
      'portfolio.lead': 'Slide language switches automatically with the selected site language.',
      'portfolio.caption': 'Portfolio slide',
      'portfolio.prevAria': 'Previous slide',
      'portfolio.nextAria': 'Next slide',
      'fit.eyebrow': 'Quick check',
      'fit.title': 'Assess launch readiness in 20 seconds',
      'fit.c1': 'Stable internet and private space are available.',
      'fit.c2': 'Ready to work at least 3-4 hours daily.',
      'fit.c3': 'Ready to follow the manager step-by-step process.',
      'fit.c4': 'A device with camera and microphone is available.',
      'fit.c5': 'Ready to continue in messenger after submitting the form.',
      'fit.score': 'Readiness score',
      'fit.high': 'High readiness: you can launch now.',
      'fit.mid': 'Medium readiness: a short prep block will improve launch quality.',
      'fit.low': 'Low readiness: close core prerequisites first.',
      'form.eyebrow': 'Application',
      'form.title': 'Submit your form in one minute',
      'form.lead': 'First complete a short form, then continue to the second step in your chosen messenger.',
      'form.b1': 'Short form with no extra fields',
      'form.b2': 'No duplicate submissions',
      'form.b3': 'Reply during business hours',
      'form.stepLabel': 'Step',
      'form.step1Title': 'Step 1. Basic details',
      'form.step2Title': 'Step 2. Preferred contact',
      'form.name': 'Name',
      'form.phone': 'Phone',
      'form.age': 'Birth date (18+)',
      'form.device': 'Device model',
      'form.contactType': 'Preferred messenger',
      'form.contactValue': 'Contact',
      'form.contactPlaceholderTelegram': '@username',
      'form.contactPlaceholderWhatsapp': '+1 555 123 4567',
      'form.nextStep': 'Next',
      'form.prevStep': 'Back',
      'form.submit': 'Submit application',
      'form.privacy': 'By submitting this form, you consent to processing of contact data for application follow-up.',
      'form.next': 'Continue in messenger',
      'form.openTelegram': 'Open Telegram',
      'form.openWhatsapp': 'Open WhatsApp',
      'footer.channel': 'Telegram channel',
      'msg.required': 'Please complete all required fields.',
      'msg.name': 'Enter a valid name (at least 2 characters).',
      'msg.phone': 'Enter phone number in international format.',
      'msg.age': 'Use birth date format DD.MM.YYYY (18+).',
      'msg.device': 'Enter your device model.',
      'msg.telegram': 'Telegram must be in @username format.',
      'msg.whatsapp': 'WhatsApp must be in international format.',
      'msg.sending': 'Submitting your application...',
      'msg.success': 'Application accepted. Continue in messenger to start.',
      'msg.error': 'Failed to submit application. Please try again.',
      'msg.nextMissing': 'Links are not configured yet. Contact manager in Telegram.',
      'msg.scoreLow': 'Low readiness: close core prerequisites first.',
      'msg.scoreMid': 'Medium readiness: a short prep block will improve launch quality.',
      'msg.scoreHigh': 'High readiness: you can launch now.'
    },
    pt: {
      'a11y.skip': 'Ir para o conteúdo principal',
      'lang.title': 'Escolha o idioma',
      'lang.subtitle': 'Select your language to continue',
      'brand.subtitle': 'Model Agency',
      'nav.model': 'Formato',
      'nav.process': 'Etapas',
      'nav.income': 'Renda',
      'nav.planner': 'Calculadora',
      'nav.portfolio': 'Portfólio',
      'nav.apply': 'Formulário',
      'cta.apply': 'Enviar formulário',
      'cta.telegram': 'Telegram',
      'mobile.menu': 'Menu',
      'mobile.close': 'Fechar',
      'hero.eyebrow': 'Modelo de onboarding calmo',
      'hero.title': 'Agência de modelos de streaming com início claro',
      'hero.lead': 'Preencha um formulário curto, escolha o mensageiro e receba suporte individual.',
      'hero.kpi1': 'até a primeira resposta',
      'hero.kpi2': 'gerente pessoal',
      'hero.kpi3': 'anos de experiência operacional',
      'hero.cardTitle': 'O que você recebe de imediato',
      'hero.card1': 'Início por etapas sem caos',
      'hero.card2': 'Comunicação clara no mensageiro',
      'hero.card3': 'Plano de lançamento e suporte',
      'hero.modeLabel': 'Escolha seu ritmo de início',
      'hero.modeSoft': 'Suave',
      'hero.modeBalanced': 'Equilibrado',
      'hero.modePro': 'Intenso',
      'hero.modeSoftValue': '3-4 h/dia',
      'hero.modeBalancedValue': '4-6 h/dia',
      'hero.modeProValue': '6-8 h/dia',
      'hero.modeSoftNote': 'Entrada confortável, sem sobrecarga nas primeiras semanas.',
      'hero.modeBalancedNote': 'Ritmo estável com crescimento mais rápido de habilidades e renda.',
      'hero.modeProNote': 'Foco máximo para escalar resultados com rapidez.',
      'model.eyebrow': 'Formato de trabalho',
      'model.title': 'Um sistema claro onde cada etapa é previsível',
      'model.card1.title': 'Regras claras',
      'model.card1.text': 'Sem condições ocultas: você vê o processo antecipadamente.',
      'model.card2.title': 'Controle de ritmo',
      'model.card2.text': 'Lançamento sem pressa, adaptado à sua rotina.',
      'model.card3.title': 'Suporte guiado',
      'model.card3.text': 'Gerente acompanha cada fase com feedback direto.',
      'steps.eyebrow': 'Processo',
      'steps.title': 'Três etapas do formulário ao início',
      'steps.s1.title': 'Formulário',
      'steps.s1.text': 'Você envia uma inscrição curta no site.',
      'steps.s2.title': 'Contato no mensageiro',
      'steps.s2.text': 'Escolhe Telegram ou WhatsApp e recebe resposta.',
      'steps.s3.title': 'Início',
      'steps.s3.text': 'Recebe o plano e inicia com suporte.',
      'income.eyebrow': 'Exemplos',
      'income.title': 'Referências de renda com rotina estável',
      'income.subtitle': 'Referências reais com rotina estável e suporte do gerente.',
      'income.note': 'Crescimento da renda',
      'streams.eyebrow': 'Exemplos de stream',
      'streams.title': 'Veja como é uma transmissão real de trabalho',
      'streams.subtitle': 'Bloco separado com trechos curtos de stream dos seus arquivos.',
      'streams.sample1': 'Stream 01',
      'streams.sample2': 'Stream 02',
      'streams.sample3': 'Stream 03',
      'planner.eyebrow': 'Calculadora',
      'planner.title': 'Estime sua renda potencial pelo seu ritmo',
      'planner.subtitle': 'Estimativa por horas, dias e estágio de adaptação.',
      'planner.hours': 'Horas por dia',
      'planner.hoursUnit': 'horas / dia',
      'planner.days': 'Dias por semana',
      'planner.daysUnit': 'dias / semana',
      'planner.level': 'Estágio de adaptação',
      'planner.level.start': 'Início',
      'planner.level.steady': 'Ritmo estável',
      'planner.level.pro': 'Avançado',
      'planner.monthly': 'Estimativa mensal',
      'planner.note': 'Estimativa aproximada para planejamento.',
      'portfolio.eyebrow': 'Portfólio',
      'portfolio.title': 'Exemplos de perfis e casos',
      'portfolio.lead': 'O idioma dos slides muda automaticamente com o idioma selecionado no site.',
      'portfolio.caption': 'Slide do portfólio',
      'portfolio.prevAria': 'Slide anterior',
      'portfolio.nextAria': 'Próximo slide',
      'fit.eyebrow': 'Verificação rápida',
      'fit.title': 'Avalie sua prontidão em 20 segundos',
      'fit.c1': 'Internet estável e espaço privado disponíveis.',
      'fit.c2': 'Pronta para trabalhar pelo menos 3-4 horas por dia.',
      'fit.c3': 'Pronta para seguir etapas com o gerente.',
      'fit.c4': 'Dispositivo com câmera e microfone disponível.',
      'fit.c5': 'Pronta para continuar no mensageiro após o formulário.',
      'fit.score': 'Índice de prontidão',
      'fit.high': 'Prontidão alta: você pode começar agora.',
      'fit.mid': 'Prontidão média: uma preparação curta melhora o início.',
      'fit.low': 'Prontidão baixa: primeiro feche os requisitos básicos.',
      'form.eyebrow': 'Formulário',
      'form.title': 'Envie sua inscrição em um minuto',
      'form.lead': 'Primeiro preencha um formulário curto e depois continue para a segunda etapa no mensageiro escolhido.',
      'form.b1': 'Formulário curto sem campos extras',
      'form.b2': 'Sem envios duplicados',
      'form.b3': 'Resposta em horário comercial',
      'form.stepLabel': 'Etapa',
      'form.step1Title': 'Etapa 1. Dados básicos',
      'form.step2Title': 'Etapa 2. Contato',
      'form.name': 'Nome',
      'form.phone': 'Telefone',
      'form.age': 'Data de nascimento (18+)',
      'form.device': 'Modelo do dispositivo',
      'form.contactType': 'Mensageiro preferido',
      'form.contactValue': 'Contato',
      'form.contactPlaceholderTelegram': '@username',
      'form.contactPlaceholderWhatsapp': '+55 11 99999 9999',
      'form.nextStep': 'Avançar',
      'form.prevStep': 'Voltar',
      'form.submit': 'Enviar inscrição',
      'form.privacy': 'Ao enviar, você concorda com o processamento dos dados de contato para retorno da inscrição.',
      'form.next': 'Continuar no mensageiro',
      'form.openTelegram': 'Abrir Telegram',
      'form.openWhatsapp': 'Abrir WhatsApp',
      'footer.channel': 'Canal Telegram',
      'msg.required': 'Preencha todos os campos obrigatórios.',
      'msg.name': 'Informe um nome válido (mínimo 2 caracteres).',
      'msg.phone': 'Informe telefone no formato internacional.',
      'msg.age': 'Use data no formato DD.MM.AAAA (18+).',
      'msg.device': 'Informe o modelo do dispositivo.',
      'msg.telegram': 'Telegram deve estar no formato @username.',
      'msg.whatsapp': 'WhatsApp deve estar no formato internacional.',
      'msg.sending': 'Enviando inscrição...',
      'msg.success': 'Inscrição recebida. Continue no mensageiro para iniciar.',
      'msg.error': 'Falha ao enviar inscrição. Tente novamente.',
      'msg.nextMissing': 'Links ainda não configurados. Fale com o gerente no Telegram.',
      'msg.scoreLow': 'Prontidão baixa: primeiro feche os requisitos básicos.',
      'msg.scoreMid': 'Prontidão média: uma preparação curta melhora o início.',
      'msg.scoreHigh': 'Prontidão alta: você pode começar agora.'
    },
    es: {
      'a11y.skip': 'Saltar al contenido principal',
      'lang.title': 'Elige idioma',
      'lang.subtitle': 'Select your language to continue',
      'brand.subtitle': 'Model Agency',
      'nav.model': 'Formato',
      'nav.process': 'Etapas',
      'nav.income': 'Ingresos',
      'nav.planner': 'Calculadora',
      'nav.portfolio': 'Portafolio',
      'nav.apply': 'Formulario',
      'cta.apply': 'Enviar solicitud',
      'cta.telegram': 'Telegram',
      'mobile.menu': 'Menú',
      'mobile.close': 'Cerrar',
      'hero.eyebrow': 'Modelo de onboarding tranquilo',
      'hero.title': 'Agencia de modelos de streaming con inicio claro',
      'hero.lead': 'Completa un formulario corto, elige mensajero y recibe acompañamiento 1:1.',
      'hero.kpi1': 'hasta la primera respuesta',
      'hero.kpi2': 'manager personal',
      'hero.kpi3': 'años de experiencia operativa',
      'hero.cardTitle': 'Qué recibes de inmediato',
      'hero.card1': 'Inicio paso a paso sin caos',
      'hero.card2': 'Comunicación clara en mensajería',
      'hero.card3': 'Plan de lanzamiento y soporte',
      'hero.modeLabel': 'Elige tu ritmo de inicio',
      'hero.modeSoft': 'Suave',
      'hero.modeBalanced': 'Equilibrado',
      'hero.modePro': 'Intensivo',
      'hero.modeSoftValue': '3-4 h/día',
      'hero.modeBalancedValue': '4-6 h/día',
      'hero.modeProValue': '6-8 h/día',
      'hero.modeSoftNote': 'Inicio cómodo sin sobrecarga en las primeras semanas.',
      'hero.modeBalancedNote': 'Ritmo estable con crecimiento más rápido de habilidades e ingresos.',
      'hero.modeProNote': 'Enfoque máximo para escalar resultados rápidamente.',
      'model.eyebrow': 'Formato de trabajo',
      'model.title': 'Sistema claro donde cada paso es predecible',
      'model.card1.title': 'Reglas claras',
      'model.card1.text': 'Sin condiciones ocultas: ves el proceso por adelantado.',
      'model.card2.title': 'Control del ritmo',
      'model.card2.text': 'Lanzamiento sin prisa, adaptado a tu horario real.',
      'model.card3.title': 'Soporte guiado',
      'model.card3.text': 'Manager acompaña cada etapa con feedback concreto.',
      'steps.eyebrow': 'Proceso',
      'steps.title': 'Tres pasos del formulario al inicio',
      'steps.s1.title': 'Formulario',
      'steps.s1.text': 'Envías una solicitud corta en el sitio.',
      'steps.s2.title': 'Contacto en mensajería',
      'steps.s2.text': 'Eliges Telegram o WhatsApp y recibes respuesta.',
      'steps.s3.title': 'Inicio',
      'steps.s3.text': 'Recibes plan de acción e inicias con soporte.',
      'income.eyebrow': 'Ejemplos',
      'income.title': 'Referencias de ingresos con ritmo estable',
      'income.subtitle': 'Referencias reales con ritmo estable y soporte del manager.',
      'income.note': 'Crecimiento de ingresos',
      'streams.eyebrow': 'Ejemplos de stream',
      'streams.title': 'Mira cómo se ve un stream de trabajo real',
      'streams.subtitle': 'Bloque separado con fragmentos cortos de stream de tus archivos.',
      'streams.sample1': 'Stream 01',
      'streams.sample2': 'Stream 02',
      'streams.sample3': 'Stream 03',
      'planner.eyebrow': 'Calculadora',
      'planner.title': 'Calcula ingresos potenciales según tu agenda',
      'planner.subtitle': 'Estimación por horas, días y etapa de adaptación.',
      'planner.hours': 'Horas por día',
      'planner.hoursUnit': 'horas / día',
      'planner.days': 'Días por semana',
      'planner.daysUnit': 'días / semana',
      'planner.level': 'Etapa de adaptación',
      'planner.level.start': 'Inicio',
      'planner.level.steady': 'Ritmo estable',
      'planner.level.pro': 'Avanzado',
      'planner.monthly': 'Estimación mensual',
      'planner.note': 'Estimación aproximada para planificación.',
      'portfolio.eyebrow': 'Portafolio',
      'portfolio.title': 'Ejemplos de perfiles y casos',
      'portfolio.lead': 'El idioma de las diapositivas cambia automáticamente según el idioma del sitio.',
      'portfolio.caption': 'Diapositiva de portafolio',
      'portfolio.prevAria': 'Diapositiva anterior',
      'portfolio.nextAria': 'Siguiente diapositiva',
      'fit.eyebrow': 'Chequeo rápido',
      'fit.title': 'Evalúa tu preparación en 20 segundos',
      'fit.c1': 'Internet estable y espacio privado disponibles.',
      'fit.c2': 'Lista para dedicar al menos 3-4 horas al día.',
      'fit.c3': 'Lista para seguir pasos con el manager.',
      'fit.c4': 'Dispositivo con cámara y micrófono disponible.',
      'fit.c5': 'Lista para pasar a mensajería tras el formulario.',
      'fit.score': 'Índice de preparación',
      'fit.high': 'Preparación alta: puedes iniciar ahora.',
      'fit.mid': 'Preparación media: una breve preparación mejorará el inicio.',
      'fit.low': 'Preparación baja: primero cubre requisitos básicos.',
      'form.eyebrow': 'Formulario',
      'form.title': 'Envía tu solicitud en un minuto',
      'form.lead': 'Primero completa un formulario corto y luego continúa al segundo paso en el mensajero elegido.',
      'form.b1': 'Formulario corto sin campos extra',
      'form.b2': 'Sin envíos duplicados',
      'form.b3': 'Respuesta en horario laboral',
      'form.stepLabel': 'Paso',
      'form.step1Title': 'Paso 1. Datos básicos',
      'form.step2Title': 'Paso 2. Contacto',
      'form.name': 'Nombre',
      'form.phone': 'Teléfono',
      'form.age': 'Fecha de nacimiento (18+)',
      'form.device': 'Modelo de dispositivo',
      'form.contactType': 'Mensajero preferido',
      'form.contactValue': 'Contacto',
      'form.contactPlaceholderTelegram': '@username',
      'form.contactPlaceholderWhatsapp': '+34 600 000 000',
      'form.nextStep': 'Siguiente',
      'form.prevStep': 'Atrás',
      'form.submit': 'Enviar solicitud',
      'form.privacy': 'Al enviar, aceptas el tratamiento de datos de contacto para respuesta de esta solicitud.',
      'form.next': 'Continuar en mensajería',
      'form.openTelegram': 'Abrir Telegram',
      'form.openWhatsapp': 'Abrir WhatsApp',
      'footer.channel': 'Canal Telegram',
      'msg.required': 'Completa todos los campos obligatorios.',
      'msg.name': 'Escribe un nombre válido (mínimo 2 caracteres).',
      'msg.phone': 'Escribe teléfono en formato internacional.',
      'msg.age': 'Usa fecha en formato DD.MM.AAAA (18+).',
      'msg.device': 'Indica el modelo de dispositivo.',
      'msg.telegram': 'Telegram debe tener formato @username.',
      'msg.whatsapp': 'WhatsApp debe tener formato internacional.',
      'msg.sending': 'Enviando solicitud...',
      'msg.success': 'Solicitud recibida. Continúa en mensajería para iniciar.',
      'msg.error': 'No se pudo enviar la solicitud. Inténtalo de nuevo.',
      'msg.nextMissing': 'Los enlaces aún no están configurados. Escribe al manager en Telegram.',
      'msg.scoreLow': 'Preparación baja: primero cubre requisitos básicos.',
      'msg.scoreMid': 'Preparación media: una breve preparación mejorará el inicio.',
      'msg.scoreHigh': 'Preparación alta: puedes iniciar ahora.'
    }
  };

  function qs(selector, root) {
    return (root || document).querySelector(selector);
  }

  function qsa(selector, root) {
    return Array.from((root || document).querySelectorAll(selector));
  }

  function t(key, lang) {
    const dict = I18N[lang] || I18N[DEFAULT_LANG];
    if (Object.prototype.hasOwnProperty.call(dict, key)) {
      return dict[key];
    }
    return (I18N[DEFAULT_LANG] && I18N[DEFAULT_LANG][key]) || key;
  }

  function trackGoal(goal) {
    if (typeof window.ym === 'function') {
      try {
        window.ym(METRIKA_COUNTER_ID, 'reachGoal', goal);
      } catch (_err) {
        // ignore metrika errors
      }
    }
  }

  function safeStorageGet(key) {
    try {
      return window.localStorage.getItem(key);
    } catch (_err) {
      return null;
    }
  }

  function safeStorageSet(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch (_err) {
      // ignore storage errors
    }
  }

  function normalizeLang(value) {
    const lang = String(value || '').trim().toLowerCase();
    return LANGS.includes(lang) ? lang : DEFAULT_LANG;
  }

  function applyI18n(lang) {
    qsa('[data-i18n]').forEach((node) => {
      node.textContent = t(node.getAttribute('data-i18n'), lang);
    });

    qsa('[data-i18n-placeholder]').forEach((node) => {
      const key = node.getAttribute('data-i18n-placeholder');
      node.setAttribute('placeholder', t(key, lang));
    });

    qsa('[data-i18n-aria-label]').forEach((node) => {
      const key = node.getAttribute('data-i18n-aria-label');
      node.setAttribute('aria-label', t(key, lang));
    });

    document.documentElement.setAttribute('lang', lang);
  }

  function isValidPhone(value) {
    const trimmed = String(value || '').trim();
    return /^\+?[0-9\s().-]{7,32}$/.test(trimmed) && /\d{7,}/.test(trimmed.replace(/\D/g, ''));
  }

  function isValidTelegram(value) {
    return /^@[a-zA-Z0-9_]{4,32}$/.test(String(value || '').trim());
  }

  function parseBirthDate(value) {
    const match = String(value || '').trim().match(/^(\d{2})\.(\d{2})\.(\d{4})$/);
    if (!match) {
      return null;
    }
    const day = Number(match[1]);
    const month = Number(match[2]);
    const year = Number(match[3]);
    const date = new Date(Date.UTC(year, month - 1, day));
    if (
      Number.isNaN(date.getTime()) ||
      date.getUTCFullYear() !== year ||
      date.getUTCMonth() !== month - 1 ||
      date.getUTCDate() !== day
    ) {
      return null;
    }
    return date;
  }

  function isAdultBirthDate(value) {
    const birth = parseBirthDate(value);
    if (!birth) {
      return false;
    }
    const now = new Date();
    let age = now.getUTCFullYear() - birth.getUTCFullYear();
    const monthDiff = now.getUTCMonth() - birth.getUTCMonth();
    if (monthDiff < 0 || (monthDiff === 0 && now.getUTCDate() < birth.getUTCDate())) {
      age -= 1;
    }
    return age >= 18;
  }

  function setStatus(node, text, isError, isSuccess) {
    if (!node) {
      return;
    }
    node.textContent = String(text || '');
    node.classList.toggle('is-error', Boolean(isError));
    node.classList.toggle('is-success', Boolean(isSuccess));
  }

  function markFieldError(field, enabled) {
    if (!field) {
      return;
    }
    field.setAttribute('aria-invalid', enabled ? 'true' : 'false');
    field.classList.toggle('is-field-error', Boolean(enabled));
  }

  function formatIncomeAmount(rubAmount, lang) {
    const rub = Number(rubAmount || 0);
    if (!Number.isFinite(rub) || rub <= 0) {
      return '0 ₽';
    }
    const locale = normalizeLang(lang);
    const currencyByLang = {
      ru: { code: 'RUB', locale: 'ru-RU', rate: 1 },
      en: { code: 'USD', locale: 'en-US', rate: 1 / 92 },
      pt: { code: 'BRL', locale: 'pt-BR', rate: 1 / 18 },
      es: { code: 'EUR', locale: 'es-ES', rate: 1 / 100 }
    };
    const config = currencyByLang[locale] || currencyByLang.ru;
    const amount = Math.round(rub * config.rate);
    return new Intl.NumberFormat(config.locale, {
      style: 'currency',
      currency: config.code,
      maximumFractionDigits: 0
    }).format(amount);
  }

  function updateIncomeByLang(lang) {
    qsa('[data-income-rub]').forEach((node) => {
      const rub = Number(node.getAttribute('data-income-rub') || 0);
      if (!Number.isFinite(rub) || rub <= 0) {
        return;
      }
      node.textContent = formatIncomeAmount(rub, lang);
    });
  }

  function initReveal() {
    const items = qsa('.sf-reveal');
    if (!items.length) {
      return;
    }

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced || typeof window.IntersectionObserver !== 'function') {
      items.forEach((item) => item.classList.add('is-visible'));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) {
            return;
          }
          const delay = Number(entry.target.getAttribute('data-reveal-delay') || 0);
          window.setTimeout(() => {
            entry.target.classList.add('is-visible');
          }, Math.max(0, delay));
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.12 }
    );

    items.forEach((item) => observer.observe(item));
  }

  function attachPointerTilt(node, className, maxTilt) {
    if (!node) {
      return;
    }
    node.classList.add(className);

    const tilt = Number.isFinite(maxTilt) ? maxTilt : 5;
    let frame = 0;
    let spotX = 50;
    let spotY = 50;
    let rotateX = 0;
    let rotateY = 0;

    const render = () => {
      node.style.setProperty('--spot-x', `${spotX}%`);
      node.style.setProperty('--spot-y', `${spotY}%`);
      node.style.transform = `perspective(980px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
      frame = 0;
    };

    const queueRender = () => {
      if (frame) {
        return;
      }
      frame = window.requestAnimationFrame(render);
    };

    const onMove = (event) => {
      const rect = node.getBoundingClientRect();
      if (!rect.width || !rect.height) {
        return;
      }
      const x = Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width));
      const y = Math.min(1, Math.max(0, (event.clientY - rect.top) / rect.height));
      spotX = Math.round(x * 100);
      spotY = Math.round(y * 100);
      rotateX = Number((((0.5 - y) * 2) * tilt).toFixed(2));
      rotateY = Number((((x - 0.5) * 2) * tilt).toFixed(2));
      node.classList.add('is-interactive-active');
      queueRender();
    };

    const reset = () => {
      spotX = 50;
      spotY = 50;
      rotateX = 0;
      rotateY = 0;
      node.classList.remove('is-interactive-active');
      queueRender();
    };

    node.addEventListener('pointermove', onMove, { passive: true });
    node.addEventListener('pointerleave', reset);
    node.addEventListener('pointercancel', reset);
    reset();
  }

  function initStreamflowInteractivity() {
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const finePointer = window.matchMedia('(pointer: fine)').matches;
    if (reduced || !finePointer) {
      return;
    }

    const spotlightTargets = qsa(
      '.sf-hero__copy, .sf-hero__card, .sf-hero-flow, .sf-card, .sf-income-card, .sf-stream-card, .sf-planner, .sf-portfolio, .sf-fit, .sf-apply__copy'
    );
    spotlightTargets.forEach((node, index) => {
      const maxTilt = index < 2 ? 6 : 3.8;
      attachPointerTilt(node, 'sf-interactive-surface', maxTilt);
    });
  }

  function initLegacyReveal() {
    const items = qsa('.reveal');
    if (!items.length) {
      return;
    }

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced || typeof window.IntersectionObserver !== 'function') {
      items.forEach((item) => item.classList.add('is-visible'));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) {
            return;
          }
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.14 }
    );

    items.forEach((item) => observer.observe(item));
  }

  function initLegacyInteractivity() {
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const finePointer = window.matchMedia('(pointer: fine)').matches;
    if (reduced || !finePointer) {
      return;
    }

    const heroSurface = qs('.page-hero .container');
    if (heroSurface) {
      attachPointerTilt(heroSurface, 'st-interactive-surface', 5.2);
    }

    const cardTargets = qsa(
      '.split-content, .note, .info-card, .offer-item, .steps-item, .video-card, .portfolio-block, .form-card, .form-intro, .stat-item'
    );
    cardTargets.forEach((node) => {
      attachPointerTilt(node, 'st-interactive-surface', 3.1);
    });
  }

  function initFitScore(state) {
    const checks = qsa('[data-fit-check]');
    const scoreNode = qs('[data-fit-score]');
    const statusNode = qs('[data-fit-status]');
    if (!checks.length || !scoreNode || !statusNode) {
      return;
    }

    const update = () => {
      const total = checks.reduce((sum, input) => sum + Number(input.value || 0), 0);
      const checked = checks
        .filter((input) => input.checked)
        .reduce((sum, input) => sum + Number(input.value || 0), 0);
      const score = total > 0 ? Math.round((checked / total) * 100) : 0;

      scoreNode.textContent = score + '%';
      if (score >= 80) {
        statusNode.textContent = t('msg.scoreHigh', state.lang);
        statusNode.setAttribute('data-level', 'high');
      } else if (score >= 50) {
        statusNode.textContent = t('msg.scoreMid', state.lang);
        statusNode.setAttribute('data-level', 'mid');
      } else {
        statusNode.textContent = t('msg.scoreLow', state.lang);
        statusNode.setAttribute('data-level', 'low');
      }
    };

    checks.forEach((input) => {
      input.addEventListener('change', update);
    });

    update();
  }

  function initPlanner(state) {
    const hoursInput = qs('#sf-planner-hours');
    const daysInput = qs('#sf-planner-days');
    const levelInput = qs('#sf-planner-level');
    const hoursOut = qs('[data-planner-hours]');
    const daysOut = qs('[data-planner-days]');
    const incomeOut = qs('[data-planner-income]');

    if (!hoursInput || !daysInput || !levelInput || !incomeOut) {
      return () => {};
    }

    const levelMultiplier = {
      start: 0.85,
      steady: 1.1,
      pro: 1.4
    };

    const estimateRubIncome = () => {
      const hours = Math.max(1, Math.min(10, Number(hoursInput.value || 0)));
      const days = Math.max(2, Math.min(7, Number(daysInput.value || 0)));
      const level = String(levelInput.value || 'steady');
      const multiplier = levelMultiplier[level] || levelMultiplier.steady;
      const monthlyHours = hours * days * 4.2;
      const monthlyRub = Math.round(monthlyHours * 1400 * multiplier);
      return { hours, days, monthlyRub };
    };

    const update = () => {
      const estimate = estimateRubIncome();
      if (hoursOut) {
        hoursOut.textContent = String(estimate.hours);
      }
      if (daysOut) {
        daysOut.textContent = String(estimate.days);
      }
      incomeOut.textContent = formatIncomeAmount(estimate.monthlyRub, state.lang);
    };

    hoursInput.addEventListener('input', update);
    daysInput.addEventListener('input', update);
    levelInput.addEventListener('change', update);
    update();
    return update;
  }

  function initHeroFlow(state) {
    const buttons = qsa('[data-hero-step]');
    const textNode = qs('#sf-hero-step-text');
    if (!buttons.length || !textNode) {
      return () => {};
    }

    const stepTextMap = {
      '1': 'steps.s1.text',
      '2': 'steps.s2.text',
      '3': 'steps.s3.text'
    };

    let activeStep = '1';

    const render = () => {
      const textKey = stepTextMap[activeStep] || stepTextMap['1'];
      textNode.textContent = t(textKey, state.lang);
      buttons.forEach((button) => {
        button.classList.toggle('is-active', button.getAttribute('data-hero-step') === activeStep);
      });
    };

    buttons.forEach((button) => {
      button.addEventListener('click', () => {
        activeStep = String(button.getAttribute('data-hero-step') || '1');
        render();
      });
    });

    render();
    return render;
  }

  function initAmbientStreams() {
    const videos = qsa('.sf-stream-card video');
    if (!videos.length) {
      return;
    }

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const playVideo = (video) => {
      if (!video) {
        return;
      }
      video.defaultMuted = true;
      video.muted = true;
      video.autoplay = true;
      video.loop = true;
      video.playsInline = true;
      if (reduced) {
        video.pause();
        return;
      }
      void video.play().catch(() => {});
    };

    videos.forEach((video) => {
      playVideo(video);
      video.addEventListener('loadeddata', () => playVideo(video), { once: true });
    });

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        return;
      }
      videos.forEach((video) => playVideo(video));
    });
  }

  function portfolioPath(lang, slideNumber) {
    const index = Math.max(1, Math.min(8, Number(slideNumber) || 1));
    const locale = normalizeLang(lang);
    if (locale === 'ru') {
      return `assets/portfolio/${index}.jpg`;
    }
    return `assets/portfolio/${locale}/${index}.jpg`;
  }

  function initPortfolio(state) {
    const image = qs('#sf-portfolio-image');
    const counter = qs('#sf-portfolio-counter');
    const prevBtn = qs('[data-portfolio-prev]');
    const nextBtn = qs('[data-portfolio-next]');
    const stage = qs('.sf-portfolio__stage');
    if (!image || !counter || !prevBtn || !nextBtn || !stage) {
      return () => {};
    }

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let index = 0;
    const total = 8;
    let autoplayTimer = 0;
    let touchStartX = 0;
    let touchStartY = 0;

    const render = () => {
      const slide = index + 1;
      image.dataset.fallback = '';
      image.src = portfolioPath(state.lang, slide);
      image.alt = `${t('portfolio.caption', state.lang)} ${slide}`;
      counter.textContent = `${slide}/${total}`;
    };

    const goPrev = () => {
      index = (index - 1 + total) % total;
      render();
    };

    const goNext = () => {
      index = (index + 1) % total;
      render();
    };

    const stopAutoplay = () => {
      if (!autoplayTimer) {
        return;
      }
      window.clearInterval(autoplayTimer);
      autoplayTimer = 0;
    };

    const startAutoplay = () => {
      if (reduced) {
        return;
      }
      stopAutoplay();
      autoplayTimer = window.setInterval(goNext, 7000);
    };

    prevBtn.addEventListener('click', () => {
      goPrev();
      startAutoplay();
    });

    nextBtn.addEventListener('click', () => {
      goNext();
      startAutoplay();
    });

    image.addEventListener('error', () => {
      if (image.dataset.fallback === '1') {
        return;
      }
      image.dataset.fallback = '1';
      image.src = `assets/portfolio/${index + 1}.jpg`;
    });

    stage.addEventListener(
      'touchstart',
      (event) => {
        const point = event.changedTouches && event.changedTouches[0];
        if (!point) {
          return;
        }
        touchStartX = point.clientX;
        touchStartY = point.clientY;
      },
      { passive: true }
    );

    stage.addEventListener(
      'touchend',
      (event) => {
        const point = event.changedTouches && event.changedTouches[0];
        if (!point) {
          return;
        }
        const deltaX = point.clientX - touchStartX;
        const deltaY = point.clientY - touchStartY;
        if (Math.abs(deltaX) < 36 || Math.abs(deltaX) < Math.abs(deltaY)) {
          return;
        }
        if (deltaX > 0) {
          goPrev();
        } else {
          goNext();
        }
        startAutoplay();
      },
      { passive: true }
    );

    [stage, prevBtn, nextBtn].forEach((node) => {
      node.addEventListener('pointerenter', stopAutoplay);
      node.addEventListener('pointerleave', startAutoplay);
      node.addEventListener('focusin', stopAutoplay);
      node.addEventListener('focusout', startAutoplay);
    });

    render();
    startAutoplay();
    return render;
  }

  function initMobileMenu() {
    const openBtn = qs('[data-menu-open]');
    const closeBtns = qsa('[data-menu-close]');
    const panel = qs('.sf-mobile-nav__panel');
    const links = qsa('.sf-mobile-nav__links a');
    if (!openBtn || !panel) {
      return;
    }

    const closeMenu = () => {
      document.body.classList.remove('menu-open');
      openBtn.setAttribute('aria-expanded', 'false');
      qs('#sf-mobile-nav')?.setAttribute('aria-hidden', 'true');
      openBtn.focus();
    };

    openBtn.addEventListener('click', () => {
      document.body.classList.add('menu-open');
      openBtn.setAttribute('aria-expanded', 'true');
      qs('#sf-mobile-nav')?.setAttribute('aria-hidden', 'false');
      panel.focus();
    });

    closeBtns.forEach((btn) => {
      btn.addEventListener('click', closeMenu);
    });

    links.forEach((link) => link.addEventListener('click', closeMenu));

    window.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && document.body.classList.contains('menu-open')) {
        closeMenu();
      }
    });
  }

  function initLangGate(state, onChange) {
    const gate = qs('#sf-lang-gate');
    const select = qs('#sf-lang-select');
    const hiddenLang = qs('#sf-site-lang');
    const choices = qsa('[data-lang-choice]');
    if (!gate || !select || !hiddenLang) {
      onChange(state.lang);
      return;
    }

    const openGate = () => {
      gate.hidden = false;
      gate.setAttribute('aria-hidden', 'false');
      document.body.classList.add('is-locked');
      const first = qs('[data-lang-choice]', gate);
      if (first) {
        first.focus();
      }
    };

    const closeGate = () => {
      gate.hidden = true;
      gate.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('is-locked');
    };

    const setLang = (value) => {
      const next = normalizeLang(value);
      state.lang = next;
      select.value = next;
      hiddenLang.value = next;
      safeStorageSet(STORAGE_KEY, next);
      onChange(next);
      closeGate();
    };

    select.value = state.lang;
    hiddenLang.value = state.lang;

    choices.forEach((button) => {
      button.addEventListener('click', () => {
        setLang(button.getAttribute('data-lang-choice'));
      });
    });

    select.addEventListener('change', () => {
      setLang(select.value);
    });

    if (!safeStorageGet(STORAGE_KEY)) {
      openGate();
    } else {
      closeGate();
    }

    onChange(state.lang);
  }

  async function syncLinks() {
    try {
      const response = await fetch('/api/config?project=' + encodeURIComponent(PROJECT), {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
          Accept: 'application/json'
        }
      });
      if (!response.ok) {
        return;
      }
      const payload = await response.json();
      const telegramLink = typeof payload.telegram_link === 'string' && payload.telegram_link ? payload.telegram_link : null;
      if (telegramLink) {
        qsa('[data-telegram-link]').forEach((link) => {
          link.setAttribute('href', telegramLink);
        });
      }
    } catch (_err) {
      // silent fallback
    }
  }

  function initForm(state) {
    const form = qs('#sf-apply-form');
    const submitBtn = qs('#sf-submit');
    const nextBtn = qs('[data-form-next]', form || document);
    const prevBtn = qs('[data-form-prev]', form || document);
    const status = qs('#sf-form-status');
    const nextBox = qs('#sf-form-next');
    const nextTg = qs('#sf-next-telegram');
    const nextWa = qs('#sf-next-whatsapp');
    const contactType = qs('#sf-preferred-contact');
    const contactValue = qs('#sf-contact-value');
    const steps = qsa('[data-form-step]', form || document);
    const stepCurrent = qs('[data-form-step-current]', form || document);
    const stepTotal = qs('[data-form-step-total]', form || document);
    const stepBar = qs('[data-form-step-bar]', form || document);
    const hiddenTelegram = qs('input[name="telegram"]', form || document);
    const hiddenWhatsapp = qs('input[name="whatsapp"]', form || document);

    if (
      !form ||
      !submitBtn ||
      !status ||
      !contactType ||
      !contactValue ||
      !hiddenTelegram ||
      !hiddenWhatsapp ||
      !steps.length
    ) {
      return;
    }

    const totalSteps = steps.length;
    let currentStep = 0;

    const switchContactPlaceholder = () => {
      const isTelegram = contactType.value === 'telegram';
      contactValue.placeholder = t(
        isTelegram ? 'form.contactPlaceholderTelegram' : 'form.contactPlaceholderWhatsapp',
        state.lang
      );
      contactValue.setAttribute('inputmode', isTelegram ? 'text' : 'tel');
    };

    const setStep = (index, focusFieldName) => {
      currentStep = Math.max(0, Math.min(totalSteps - 1, Number(index) || 0));
      steps.forEach((stepNode, stepIndex) => {
        stepNode.classList.toggle('is-active', stepIndex === currentStep);
      });
      if (stepCurrent) {
        stepCurrent.textContent = String(currentStep + 1);
      }
      if (stepTotal) {
        stepTotal.textContent = String(totalSteps);
      }
      if (stepBar) {
        stepBar.style.width = `${((currentStep + 1) / totalSteps) * 100}%`;
      }
      if (typeof focusFieldName === 'string' && focusFieldName) {
        const focusTarget = qs(`[name="${focusFieldName}"]`, form);
        if (focusTarget) {
          focusTarget.focus();
        }
      }
    };

    const getField = (name) => qs(`[name="${name}"]`, form);

    const clearValidation = (fieldNames) => {
      fieldNames.forEach((fieldName) => {
        const field = getField(fieldName);
        if (field) {
          markFieldError(field, false);
        }
      });
    };

    const validateStepOne = () => {
      clearValidation(['name', 'phone', 'age', 'device_model']);

      const name = String(getField('name')?.value || '').trim();
      const phone = String(getField('phone')?.value || '').trim();
      const age = String(getField('age')?.value || '').trim();
      const device = String(getField('device_model')?.value || '').trim();

      if (!name || !phone || !age || !device) {
        setStatus(status, t('msg.required', state.lang), true, false);
        if (!name) {
          markFieldError(getField('name'), true);
          getField('name')?.focus();
        } else if (!phone) {
          markFieldError(getField('phone'), true);
          getField('phone')?.focus();
        } else if (!age) {
          markFieldError(getField('age'), true);
          getField('age')?.focus();
        } else {
          markFieldError(getField('device_model'), true);
          getField('device_model')?.focus();
        }
        return false;
      }
      if (name.length < 2) {
        markFieldError(getField('name'), true);
        setStatus(status, t('msg.name', state.lang), true, false);
        getField('name')?.focus();
        return false;
      }
      if (!isValidPhone(phone)) {
        markFieldError(getField('phone'), true);
        setStatus(status, t('msg.phone', state.lang), true, false);
        getField('phone')?.focus();
        return false;
      }
      if (!isAdultBirthDate(age)) {
        markFieldError(getField('age'), true);
        setStatus(status, t('msg.age', state.lang), true, false);
        getField('age')?.focus();
        return false;
      }
      if (device.length < 2) {
        markFieldError(getField('device_model'), true);
        setStatus(status, t('msg.device', state.lang), true, false);
        getField('device_model')?.focus();
        return false;
      }
      setStatus(status, '', false, false);
      return true;
    };

    const validateStepTwo = () => {
      clearValidation(['contact_value', 'preferred_contact', 'telegram', 'whatsapp']);
      const contact = String(contactValue.value || '').trim();

      if (!contact) {
        markFieldError(contactValue, true);
        setStatus(status, t('msg.required', state.lang), true, false);
        contactValue.focus();
        return false;
      }
      if (contactType.value === 'telegram') {
        if (!isValidTelegram(contact)) {
          markFieldError(contactValue, true);
          setStatus(status, t('msg.telegram', state.lang), true, false);
          contactValue.focus();
          return false;
        }
      } else if (!isValidPhone(contact)) {
        markFieldError(contactValue, true);
        setStatus(status, t('msg.whatsapp', state.lang), true, false);
        contactValue.focus();
        return false;
      }

      setStatus(status, '', false, false);
      return true;
    };

    const setLoading = (loading) => {
      submitBtn.disabled = loading;
      if (nextBtn) {
        nextBtn.disabled = loading;
      }
      if (prevBtn) {
        prevBtn.disabled = loading;
      }
      submitBtn.setAttribute('aria-disabled', loading ? 'true' : 'false');
      form.setAttribute('aria-busy', loading ? 'true' : 'false');
      if (loading) {
        setStatus(status, t('msg.sending', state.lang), false, false);
      }
    };

    const resolveInputByApiField = (field) => {
      if (!field) {
        return null;
      }
      if (field === 'contact_value') {
        return contactValue;
      }
      return getField(field);
    };

    contactType.addEventListener('change', switchContactPlaceholder);
    document.addEventListener('streamflow-language-change', switchContactPlaceholder);
    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        if (!validateStepOne()) {
          return;
        }
        trackGoal('streamflow_form_step_2');
        setStep(1, 'contact_value');
      });
    }
    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        setStatus(status, '', false, false);
        setStep(0, 'name');
      });
    }

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (currentStep === 0) {
        if (validateStepOne()) {
          setStep(1, 'contact_value');
        }
        return;
      }

      const stepOneValid = validateStepOne();
      if (!stepOneValid) {
        setStep(0);
        return;
      }
      const stepTwoValid = validateStepTwo();
      if (!stepTwoValid) {
        setStep(1);
        return;
      }

      const contact = String(contactValue.value || '').trim();
      if (contactType.value === 'telegram') {
        hiddenTelegram.value = contact;
        hiddenWhatsapp.value = '';
      } else {
        hiddenTelegram.value = '';
        hiddenWhatsapp.value = contact;
      }

      if (nextBox) {
        nextBox.hidden = true;
      }

      const body = new URLSearchParams(new FormData(form));
      setLoading(true);

      try {
        const response = await fetch('/api/apply', {
          method: 'POST',
          credentials: 'same-origin',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            Accept: 'application/json'
          },
          body
        });

        const payload = await response.json().catch(() => null);
        if (!response.ok || !payload || payload.ok !== true) {
          const message = payload && payload.message ? String(payload.message) : t('msg.error', state.lang);
          setStatus(status, message, true, false);
          if (payload && payload.field) {
            const field = resolveInputByApiField(String(payload.field));
            if (field) {
              const fieldName = String(payload.field);
              if (['name', 'phone', 'age', 'device_model'].includes(fieldName)) {
                setStep(0);
              } else {
                setStep(1);
              }
              markFieldError(field, true);
              field.focus();
            }
          }
          trackGoal('streamflow_form_error');
          return;
        }

        const message = payload.message ? String(payload.message) : t('msg.success', state.lang);
        setStatus(status, message, false, true);
        trackGoal('streamflow_form_success');

        const nextLinks = payload.next_links && typeof payload.next_links === 'object' ? payload.next_links : {};
        const tgLink = nextLinks.telegram || payload.telegram_bot_link || payload.bot_link || '';
        const waLink = nextLinks.whatsapp || payload.whatsapp_bot_link || '';

        let hasNextLink = false;
        if (nextTg && tgLink) {
          nextTg.setAttribute('href', tgLink);
          nextTg.hidden = false;
          hasNextLink = true;
        } else if (nextTg) {
          nextTg.hidden = true;
        }
        if (nextWa && waLink) {
          nextWa.setAttribute('href', waLink);
          nextWa.hidden = false;
          hasNextLink = true;
        } else if (nextWa) {
          nextWa.hidden = true;
        }

        if (nextBox) {
          nextBox.hidden = !hasNextLink;
        }

        if (!hasNextLink) {
          setStatus(status, t('msg.nextMissing', state.lang), true, false);
        }

        form.reset();
        qs('#sf-site-lang')?.setAttribute('value', state.lang);
        const langInput = qs('#sf-site-lang');
        if (langInput) {
          langInput.value = state.lang;
        }
        setStep(0);
        contactType.value = 'telegram';
        switchContactPlaceholder();
      } catch (_err) {
        setStatus(status, t('msg.error', state.lang), true, false);
        trackGoal('streamflow_form_error');
      } finally {
        setLoading(false);
      }
    });

    setStep(0);
    switchContactPlaceholder();
  }

  function initYear() {
    const node = qs('#sf-year');
    if (node) {
      node.textContent = String(new Date().getFullYear());
    }
  }

  function initStreamflowPage() {
    const state = {
      lang: normalizeLang(safeStorageGet(STORAGE_KEY) || DEFAULT_LANG)
    };

    const refreshHeroFlow = initHeroFlow(state);
    const refreshPortfolio = initPortfolio(state);
    const refreshPlanner = initPlanner(state);

    const onLangChange = (lang) => {
      applyI18n(lang);
      updateIncomeByLang(lang);
      refreshHeroFlow();
      refreshPortfolio();
      refreshPlanner();
      const langInput = qs('#sf-site-lang');
      if (langInput) {
        langInput.value = lang;
      }
      document.dispatchEvent(new Event('streamflow-language-change'));
    };

    initYear();
    initReveal();
    initStreamflowInteractivity();
    initAmbientStreams();
    initMobileMenu();
    initLangGate(state, onLangChange);
    initFitScore(state);
    initForm(state);
    void syncLinks();
  }

  function initLegacyFallback() {
    initLegacyReveal();
    initLegacyInteractivity();
    void syncLinks();
  }

  function init() {
    const site = document.body && document.body.getAttribute('data-site');
    if (site === 'streamflow') {
      initStreamflowPage();
      return;
    }
    initLegacyFallback();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
