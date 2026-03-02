(function () {
  'use strict';

  const LANGS = ['ru', 'en', 'pt', 'es'];
  const DEFAULT_LANG = 'en';
  const STORAGE_KEY = 'starflow_site_lang_v3';
  const PROJECT = 'starflow_corp';
  const METRIKA_COUNTER_ID = 106823371;

  const I18N = {
    ru: {
      'a11y.skip': 'Перейти к основному контенту',
      'lang.title': 'Выберите язык',
      'lang.subtitle': 'Выберите язык интерфейса, чтобы продолжить',
      'brand.subtitle': 'Партнёрская сеть',
      'nav.offer': 'Оффер',
      'nav.flow': 'Процесс',
      'nav.fit': 'Готовность',
      'nav.apply': 'Анкета',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Стать партнёром',
      'mobile.menu': 'Меню',
      'mobile.close': 'Закрыть',
      'hero.eyebrow': 'Performance-партнёрская сеть',
      'hero.title': 'Масштабируйте объём интервью по прозрачной CPA-модели',
      'hero.lead': 'Вы приводите кандидатов из любого источника. Мы закрываем квалификацию, трекинг и еженедельные выплаты.',
      'hero.kpi1': 'CPA за подтверждённое интервью',
      'hero.kpi2': 'еженедельный цикл выплат',
      'hero.kpi3': 'источник трафика без ограничений',
      'hero.cardTitle': 'Фокус оффера',
      'hero.card1': 'Один KPI: подтверждённые интервью',
      'hero.card2': 'CRM и скрипты с первого дня',
      'hero.card3': 'Поддержка менеджера в запуске и масштабировании',
      'offer.eyebrow': 'Условия оффера',
      'offer.title': 'Простые условия, которыми удобно управлять',
      'offer.card1.title': 'Свобода источников',
      'offer.card1.text': 'Таргет, DM, аутрич, доски вакансий, рефералы: источник выбираете вы.',
      'offer.card2.title': 'Прозрачный учёт',
      'offer.card2.text': 'Подтверждённые интервью фиксируются в CRM и видны в едином потоке.',
      'offer.card3.title': 'Предсказуемая выплата',
      'offer.card3.text': 'Еженедельный USDT payout с понятной дисциплиной и без скрытых комиссий.',
      'flow.eyebrow': 'Процесс',
      'flow.title': 'Запуск в четыре шага',
      'flow.s1.title': 'Одобрение',
      'flow.s1.text': 'Заполняете партнёрскую анкету и получаете инструкции по онбордингу.',
      'flow.s2.title': 'Настройка',
      'flow.s2.text': 'Передаём скрипты, CRM-воронку и рабочий канал связи.',
      'flow.s3.title': 'Привлечение',
      'flow.s3.text': 'Запускаете трафик и доводите кандидатов до интервью.',
      'flow.s4.title': 'Выплата',
      'flow.s4.text': 'Подтверждённый объём интервью оплачивается еженедельно в USDT.',
      'fit.eyebrow': 'Быстрый fit',
      'fit.title': 'Оценка готовности партнёра за 20 секунд',
      'fit.c1': 'Я могу стабильно приводить кандидатов каждую неделю.',
      'fit.c2': 'У меня уже работает хотя бы один канал привлечения.',
      'fit.c3': 'Я готов работать по скриптам и статусам в CRM.',
      'fit.c4': 'Мне подходит еженедельный цикл выплат.',
      'fit.score': 'Индекс готовности',
      'fit.high': 'Высокий fit: можно запускаться сразу.',
      'fit.mid': 'Средний fit: выровняйте процесс и можно стартовать.',
      'fit.low': 'Низкий fit: сначала соберите базовую систему привлечения.',
      'form.eyebrow': 'Анкета',
      'form.title': 'Партнёрская заявка',
      'form.lead': 'Заполните короткую форму. После отправки откройте выбранный мессенджер и продолжите запуск.',
      'form.b1': 'Без лишних полей и длинных опросников',
      'form.b2': 'Дубли отправки автоматически блокируются',
      'form.b3': 'Ответ менеджера в рабочее время',
      'form.name': 'ФИО',
      'form.phone': 'Телефон',
      'form.age': 'Дата рождения (18+)',
      'form.email': 'Email',
      'form.contactType': 'Предпочтительный мессенджер',
      'form.contactValue': 'Контакт',
      'form.contactPlaceholderTelegram': '@username',
      'form.contactPlaceholderWhatsapp': '+7 900 000 00 00',
      'form.submit': 'Отправить',
      'form.privacy': 'Отправляя форму, вы соглашаетесь на обработку контактных данных для связи по партнёрской заявке.',
      'form.next': 'Продолжить в мессенджере',
      'form.openTelegram': 'Открыть Telegram',
      'form.openWhatsapp': 'Открыть WhatsApp',
      'footer.channel': 'Telegram канал',
      'msg.required': 'Заполните все обязательные поля.',
      'msg.name': 'Введите корректное имя (минимум 2 символа).',
      'msg.phone': 'Телефон должен быть в международном формате.',
      'msg.age': 'Формат даты: ДД.ММ.ГГГГ и возраст 18+.',
      'msg.email': 'Введите корректный email.',
      'msg.telegram': 'Telegram должен быть в формате @username.',
      'msg.whatsapp': 'WhatsApp должен быть в международном формате.',
      'msg.sending': 'Отправляем анкету...',
      'msg.success': 'Заявка принята. Переходите в мессенджер для старта.',
      'msg.error': 'Не удалось отправить заявку. Попробуйте ещё раз.',
      'msg.nextMissing': 'Ссылки не настроены. Напишите менеджеру в Telegram.',
      'msg.scoreHigh': 'Высокий fit: можно запускаться сразу.',
      'msg.scoreMid': 'Средний fit: выровняйте процесс и можно стартовать.',
      'msg.scoreLow': 'Низкий fit: сначала соберите базовую систему привлечения.'
    },
    en: {
      'a11y.skip': 'Skip to main content',
      'lang.title': 'Choose language',
      'lang.subtitle': 'Select interface language to continue',
      'brand.subtitle': 'Partner Network',
      'nav.offer': 'Offer',
      'nav.flow': 'Flow',
      'nav.fit': 'Fit',
      'nav.apply': 'Apply',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Become partner',
      'mobile.menu': 'Menu',
      'mobile.close': 'Close',
      'hero.eyebrow': 'Performance partner network',
      'hero.title': 'Grow interview volume on a clean CPA model',
      'hero.lead': 'You bring candidates from any acquisition source. We handle qualification, tracking, and weekly payouts.',
      'hero.kpi1': 'CPA per approved interview',
      'hero.kpi2': 'weekly payout cycle',
      'hero.kpi3': 'source of candidate traffic',
      'hero.cardTitle': 'Offer focus',
      'hero.card1': 'Single KPI: approved interviews',
      'hero.card2': 'CRM and scripts from day one',
      'hero.card3': 'Manager support for launch and scaling',
      'offer.eyebrow': 'Offer terms',
      'offer.title': 'Simple terms that are easy to operate',
      'offer.card1.title': 'Traffic freedom',
      'offer.card1.text': 'Ads, DM, outreach, boards, referrals: source is your choice.',
      'offer.card2.title': 'Transparent counting',
      'offer.card2.text': 'Approved interviews are recorded in CRM and visible in one flow.',
      'offer.card3.title': 'Predictable payout',
      'offer.card3.text': 'Weekly USDT settlement with clear cadence and no hidden fees.',
      'flow.eyebrow': 'Flow',
      'flow.title': 'Launch sequence in four steps',
      'flow.s1.title': 'Approval',
      'flow.s1.text': 'You submit partner form and receive onboarding instructions.',
      'flow.s2.title': 'Setup',
      'flow.s2.text': 'We share scripts, CRM pipeline, and communication channel.',
      'flow.s3.title': 'Acquisition',
      'flow.s3.text': 'You run traffic and bring candidates to interview stage.',
      'flow.s4.title': 'Payout',
      'flow.s4.text': 'Approved interview volume is paid out weekly in USDT.',
      'fit.eyebrow': 'Quick fit',
      'fit.title': 'Partner readiness in 20 seconds',
      'fit.c1': 'I can consistently drive candidate traffic every week.',
      'fit.c2': 'I already run at least one acquisition channel.',
      'fit.c3': 'I am ready to work with scripts and CRM statuses.',
      'fit.c4': 'I am comfortable with weekly payout cadence.',
      'fit.score': 'Readiness score',
      'fit.high': 'High fit: you can launch right now.',
      'fit.mid': 'Medium fit: align your process and launch fast.',
      'fit.low': 'Low fit: build a stable acquisition baseline first.',
      'form.eyebrow': 'Application',
      'form.title': 'Partner application',
      'form.lead': 'Fill the short form. After submit, open your preferred messenger and continue onboarding.',
      'form.b1': 'No extra fields or long onboarding quiz',
      'form.b2': 'Duplicate submit is blocked automatically',
      'form.b3': 'Response in working hours',
      'form.name': 'Full name',
      'form.phone': 'Phone',
      'form.age': 'Birth date (18+)',
      'form.email': 'Email',
      'form.contactType': 'Preferred messenger',
      'form.contactValue': 'Contact',
      'form.contactPlaceholderTelegram': '@username',
      'form.contactPlaceholderWhatsapp': '+1 555 123 4567',
      'form.submit': 'Submit',
      'form.privacy': 'By submitting this form you agree to processing of contact details for partnership communication.',
      'form.next': 'Continue in messenger',
      'form.openTelegram': 'Open Telegram',
      'form.openWhatsapp': 'Open WhatsApp',
      'footer.channel': 'Telegram channel',
      'msg.required': 'Please complete all required fields.',
      'msg.name': 'Enter a valid name (at least 2 characters).',
      'msg.phone': 'Phone number must be in international format.',
      'msg.age': 'Birth date format must be DD.MM.YYYY and age must be 18+.',
      'msg.email': 'Enter a valid email address.',
      'msg.telegram': 'Telegram must be in @username format.',
      'msg.whatsapp': 'WhatsApp must be in international format.',
      'msg.sending': 'Submitting application...',
      'msg.success': 'Application accepted. Continue in messenger to start.',
      'msg.error': 'Failed to submit application. Please try again.',
      'msg.nextMissing': 'Links are not configured yet. Contact manager in Telegram.',
      'msg.scoreHigh': 'High fit: you can launch right now.',
      'msg.scoreMid': 'Medium fit: align your process and launch fast.',
      'msg.scoreLow': 'Low fit: build a stable acquisition baseline first.'
    },
    pt: {
      'a11y.skip': 'Ir para o conteúdo principal',
      'lang.title': 'Escolha o idioma',
      'lang.subtitle': 'Selecione o idioma da interface para continuar',
      'brand.subtitle': 'Rede de Parceiros',
      'nav.offer': 'Oferta',
      'nav.flow': 'Fluxo',
      'nav.fit': 'Fit',
      'nav.apply': 'Formulário',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Virar parceiro',
      'mobile.menu': 'Menu',
      'mobile.close': 'Fechar',
      'hero.eyebrow': 'Rede de parceiros performance',
      'hero.title': 'Aumente entrevistas com modelo CPA transparente',
      'hero.lead': 'Você traz candidatos de qualquer fonte. Nós cuidamos de qualificação, tracking e pagamentos semanais.',
      'hero.kpi1': 'CPA por entrevista aprovada',
      'hero.kpi2': 'ciclo semanal de pagamento',
      'hero.kpi3': 'fonte de tráfego sem limite',
      'hero.cardTitle': 'Foco da oferta',
      'hero.card1': 'KPI único: entrevistas aprovadas',
      'hero.card2': 'CRM e scripts desde o primeiro dia',
      'hero.card3': 'Suporte do gerente para lançar e escalar',
      'offer.eyebrow': 'Termos da oferta',
      'offer.title': 'Termos simples e operáveis',
      'offer.card1.title': 'Liberdade de tráfego',
      'offer.card1.text': 'Ads, DM, outreach, boards e referrals: a fonte é sua escolha.',
      'offer.card2.title': 'Contagem transparente',
      'offer.card2.text': 'Entrevistas aprovadas são registradas no CRM com visibilidade total.',
      'offer.card3.title': 'Pagamento previsível',
      'offer.card3.text': 'Liquidação semanal em USDT com cadência clara e sem taxas ocultas.',
      'flow.eyebrow': 'Fluxo',
      'flow.title': 'Sequência de lançamento em quatro etapas',
      'flow.s1.title': 'Aprovação',
      'flow.s1.text': 'Você envia o formulário e recebe instruções de onboarding.',
      'flow.s2.title': 'Setup',
      'flow.s2.text': 'Compartilhamos scripts, CRM e canal operacional.',
      'flow.s3.title': 'Aquisição',
      'flow.s3.text': 'Você roda tráfego e leva candidatos para entrevista.',
      'flow.s4.title': 'Pagamento',
      'flow.s4.text': 'Volume aprovado é pago semanalmente em USDT.',
      'fit.eyebrow': 'Fit rápido',
      'fit.title': 'Prontidão do parceiro em 20 segundos',
      'fit.c1': 'Consigo trazer tráfego de candidatos de forma estável toda semana.',
      'fit.c2': 'Já opero pelo menos um canal de aquisição.',
      'fit.c3': 'Estou pronto para trabalhar com scripts e status no CRM.',
      'fit.c4': 'Estou confortável com cadência semanal de pagamento.',
      'fit.score': 'Índice de prontidão',
      'fit.high': 'Fit alto: pode lançar agora.',
      'fit.mid': 'Fit médio: alinhe processos e inicie rápido.',
      'fit.low': 'Fit baixo: monte primeiro uma base estável de aquisição.',
      'form.eyebrow': 'Formulário',
      'form.title': 'Inscrição de parceiro',
      'form.lead': 'Preencha o formulário curto. Após enviar, abra o mensageiro escolhido e continue o onboarding.',
      'form.b1': 'Sem campos extras e sem questionário longo',
      'form.b2': 'Envio duplicado bloqueado automaticamente',
      'form.b3': 'Resposta em horário comercial',
      'form.name': 'Nome completo',
      'form.phone': 'Telefone',
      'form.age': 'Data de nascimento (18+)',
      'form.email': 'Email',
      'form.contactType': 'Mensageiro preferido',
      'form.contactValue': 'Contato',
      'form.contactPlaceholderTelegram': '@username',
      'form.contactPlaceholderWhatsapp': '+55 11 99999 9999',
      'form.submit': 'Enviar',
      'form.privacy': 'Ao enviar, você concorda com o processamento de contatos para comunicação da parceria.',
      'form.next': 'Continuar no mensageiro',
      'form.openTelegram': 'Abrir Telegram',
      'form.openWhatsapp': 'Abrir WhatsApp',
      'footer.channel': 'Canal Telegram',
      'msg.required': 'Preencha todos os campos obrigatórios.',
      'msg.name': 'Informe um nome válido (mínimo 2 caracteres).',
      'msg.phone': 'Telefone deve estar em formato internacional.',
      'msg.age': 'Data no formato DD.MM.AAAA e idade 18+.',
      'msg.email': 'Informe um email válido.',
      'msg.telegram': 'Telegram deve estar no formato @username.',
      'msg.whatsapp': 'WhatsApp deve estar no formato internacional.',
      'msg.sending': 'Enviando inscrição...',
      'msg.success': 'Inscrição recebida. Continue no mensageiro para iniciar.',
      'msg.error': 'Falha no envio. Tente novamente.',
      'msg.nextMissing': 'Links não configurados. Fale com o gerente no Telegram.',
      'msg.scoreHigh': 'Fit alto: pode lançar agora.',
      'msg.scoreMid': 'Fit médio: alinhe processos e inicie rápido.',
      'msg.scoreLow': 'Fit baixo: monte primeiro uma base estável de aquisição.'
    },
    es: {
      'a11y.skip': 'Saltar al contenido principal',
      'lang.title': 'Elige idioma',
      'lang.subtitle': 'Selecciona idioma de interfaz para continuar',
      'brand.subtitle': 'Red de Partners',
      'nav.offer': 'Oferta',
      'nav.flow': 'Flujo',
      'nav.fit': 'Fit',
      'nav.apply': 'Solicitud',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Ser partner',
      'mobile.menu': 'Menú',
      'mobile.close': 'Cerrar',
      'hero.eyebrow': 'Red de partners performance',
      'hero.title': 'Escala entrevistas con un modelo CPA claro',
      'hero.lead': 'Tú traes candidatos desde cualquier fuente. Nosotros gestionamos calificación, tracking y pagos semanales.',
      'hero.kpi1': 'CPA por entrevista aprobada',
      'hero.kpi2': 'ciclo semanal de pagos',
      'hero.kpi3': 'fuente de tráfico sin límites',
      'hero.cardTitle': 'Foco de oferta',
      'hero.card1': 'KPI único: entrevistas aprobadas',
      'hero.card2': 'CRM y scripts desde el día uno',
      'hero.card3': 'Soporte de manager para lanzamiento y escala',
      'offer.eyebrow': 'Términos de oferta',
      'offer.title': 'Términos simples y operables',
      'offer.card1.title': 'Libertad de fuentes',
      'offer.card1.text': 'Ads, DM, outreach, boards, referrals: la fuente es tu elección.',
      'offer.card2.title': 'Conteo transparente',
      'offer.card2.text': 'Entrevistas aprobadas se registran en CRM con visibilidad total.',
      'offer.card3.title': 'Pago predecible',
      'offer.card3.text': 'Liquidación semanal en USDT con cadencia clara y sin comisiones ocultas.',
      'flow.eyebrow': 'Flujo',
      'flow.title': 'Secuencia de lanzamiento en cuatro pasos',
      'flow.s1.title': 'Aprobación',
      'flow.s1.text': 'Envías formulario y recibes instrucciones de onboarding.',
      'flow.s2.title': 'Setup',
      'flow.s2.text': 'Compartimos scripts, CRM y canal operativo.',
      'flow.s3.title': 'Adquisición',
      'flow.s3.text': 'Lanzas tráfico y llevas candidatos a entrevista.',
      'flow.s4.title': 'Pago',
      'flow.s4.text': 'El volumen aprobado se paga semanalmente en USDT.',
      'fit.eyebrow': 'Fit rápido',
      'fit.title': 'Preparación del partner en 20 segundos',
      'fit.c1': 'Puedo atraer tráfico de candidatos de forma estable cada semana.',
      'fit.c2': 'Ya opero al menos un canal de adquisición.',
      'fit.c3': 'Estoy listo para trabajar con scripts y estados en CRM.',
      'fit.c4': 'Estoy cómodo con la cadencia semanal de pagos.',
      'fit.score': 'Índice de preparación',
      'fit.high': 'Fit alto: puedes lanzar ahora mismo.',
      'fit.mid': 'Fit medio: alinea proceso y lanza rápido.',
      'fit.low': 'Fit bajo: primero construye una base estable de adquisición.',
      'form.eyebrow': 'Solicitud',
      'form.title': 'Solicitud de partner',
      'form.lead': 'Completa el formulario corto. Tras enviarlo, abre tu mensajero elegido y continúa onboarding.',
      'form.b1': 'Sin campos extra ni formularios largos',
      'form.b2': 'El envío duplicado se bloquea automáticamente',
      'form.b3': 'Respuesta en horario laboral',
      'form.name': 'Nombre completo',
      'form.phone': 'Teléfono',
      'form.age': 'Fecha de nacimiento (18+)',
      'form.email': 'Email',
      'form.contactType': 'Mensajero preferido',
      'form.contactValue': 'Contacto',
      'form.contactPlaceholderTelegram': '@username',
      'form.contactPlaceholderWhatsapp': '+34 600 000 000',
      'form.submit': 'Enviar',
      'form.privacy': 'Al enviar aceptas el tratamiento de datos de contacto para comunicación de partnership.',
      'form.next': 'Continuar en mensajería',
      'form.openTelegram': 'Abrir Telegram',
      'form.openWhatsapp': 'Abrir WhatsApp',
      'footer.channel': 'Canal Telegram',
      'msg.required': 'Completa todos los campos obligatorios.',
      'msg.name': 'Introduce un nombre válido (mínimo 2 caracteres).',
      'msg.phone': 'El teléfono debe estar en formato internacional.',
      'msg.age': 'Formato de fecha DD.MM.AAAA y edad 18+.',
      'msg.email': 'Introduce un email válido.',
      'msg.telegram': 'Telegram debe tener formato @username.',
      'msg.whatsapp': 'WhatsApp debe tener formato internacional.',
      'msg.sending': 'Enviando solicitud...',
      'msg.success': 'Solicitud aceptada. Continúa en mensajería para iniciar.',
      'msg.error': 'No se pudo enviar la solicitud. Inténtalo de nuevo.',
      'msg.nextMissing': 'Enlaces no configurados. Escribe al manager en Telegram.',
      'msg.scoreHigh': 'Fit alto: puedes lanzar ahora mismo.',
      'msg.scoreMid': 'Fit medio: alinea proceso y lanza rápido.',
      'msg.scoreLow': 'Fit bajo: primero construye una base estable de adquisición.'
    }
  };

  function qs(selector, root) {
    return (root || document).querySelector(selector);
  }

  function qsa(selector, root) {
    return Array.from((root || document).querySelectorAll(selector));
  }

  function normalizeLang(value) {
    const lang = String(value || '').trim().toLowerCase();
    return LANGS.includes(lang) ? lang : DEFAULT_LANG;
  }

  function t(key, lang) {
    const dict = I18N[lang] || I18N[DEFAULT_LANG];
    if (Object.prototype.hasOwnProperty.call(dict, key)) {
      return dict[key];
    }
    return (I18N[DEFAULT_LANG] && I18N[DEFAULT_LANG][key]) || key;
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

  function trackGoal(goal) {
    if (typeof window.ym !== 'function') {
      return;
    }
    try {
      window.ym(METRIKA_COUNTER_ID, 'reachGoal', goal);
    } catch (_err) {
      // ignore metrika errors
    }
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

  function isValidPhone(value) {
    const trimmed = String(value || '').trim();
    return /^\+?[0-9\s().-]{7,32}$/.test(trimmed) && /\d{7,}/.test(trimmed.replace(/\D/g, ''));
  }

  function isValidTelegram(value) {
    return /^@[a-zA-Z0-9_]{4,32}$/.test(String(value || '').trim());
  }

  function isValidEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(String(value || '').trim());
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

  function initReveal() {
    const items = qsa('.sfw-reveal');
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
      { threshold: 0.2 }
    );

    items.forEach((item) => observer.observe(item));
  }

  function initMobileMenu() {
    const openBtn = qs('[data-menu-open]');
    const closeBtns = qsa('[data-menu-close]');
    const panel = qs('.sfw-mobile-nav__panel');
    const links = qsa('.sfw-mobile-nav__links a');
    if (!openBtn || !panel) {
      return;
    }

    const closeMenu = () => {
      document.body.classList.remove('menu-open');
      openBtn.setAttribute('aria-expanded', 'false');
      qs('#sfw-mobile-nav')?.setAttribute('aria-hidden', 'true');
      openBtn.focus();
    };

    openBtn.addEventListener('click', () => {
      document.body.classList.add('menu-open');
      openBtn.setAttribute('aria-expanded', 'true');
      qs('#sfw-mobile-nav')?.setAttribute('aria-hidden', 'false');
      panel.focus();
    });

    closeBtns.forEach((btn) => btn.addEventListener('click', closeMenu));
    links.forEach((link) => link.addEventListener('click', closeMenu));

    window.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && document.body.classList.contains('menu-open')) {
        closeMenu();
      }
    });
  }

  function initLangGate(state, onLangChange) {
    const gate = qs('#sfw-lang-gate');
    const select = qs('#sfw-lang-select');
    const hiddenLang = qs('#sfw-site-lang');
    const choices = qsa('[data-lang-choice]');
    if (!gate || !select || !hiddenLang) {
      onLangChange(state.lang);
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
      onLangChange(next);
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

    onLangChange(state.lang);
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
        qsa('[data-telegram-link]').forEach((node) => {
          node.setAttribute('href', telegramLink);
        });
      }
    } catch (_err) {
      // silent fallback
    }
  }

  function initForm(state) {
    const form = qs('#sfw-apply-form');
    const submitBtn = qs('#sfw-submit');
    const status = qs('#sfw-form-status');
    const nextBox = qs('#sfw-form-next');
    const nextTg = qs('#sfw-next-telegram');
    const nextWa = qs('#sfw-next-whatsapp');
    const contactType = qs('#sfw-preferred-contact');
    const contactValue = qs('#sfw-contact-value');

    if (!form || !submitBtn || !status || !contactType || !contactValue) {
      return;
    }

    const getField = (name) => qs(`[name="${name}"]`, form);
    const hiddenTelegram = getField('telegram');
    const hiddenWhatsapp = getField('whatsapp');

    const switchContactPlaceholder = () => {
      const isTelegram = contactType.value === 'telegram';
      contactValue.placeholder = t(
        isTelegram ? 'form.contactPlaceholderTelegram' : 'form.contactPlaceholderWhatsapp',
        state.lang
      );
      contactValue.setAttribute('inputmode', isTelegram ? 'text' : 'tel');
    };

    const clearValidation = () => {
      qsa('input, select', form).forEach((field) => markFieldError(field, false));
    };

    const validate = () => {
      clearValidation();

      const name = String(getField('name')?.value || '').trim();
      const phone = String(getField('phone')?.value || '').trim();
      const age = String(getField('age')?.value || '').trim();
      const email = String(getField('email')?.value || '').trim();
      const contact = String(contactValue.value || '').trim();

      if (!name || !phone || !age || !email || !contact) {
        setStatus(status, t('msg.required', state.lang), true, false);
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
      if (!isValidEmail(email)) {
        markFieldError(getField('email'), true);
        setStatus(status, t('msg.email', state.lang), true, false);
        getField('email')?.focus();
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

      return true;
    };

    const setLoading = (loading) => {
      submitBtn.disabled = loading;
      submitBtn.setAttribute('aria-disabled', loading ? 'true' : 'false');
      form.setAttribute('aria-busy', loading ? 'true' : 'false');
      if (loading) {
        setStatus(status, t('msg.sending', state.lang), false, false);
      }
    };

    const resolveField = (apiField) => {
      if (!apiField) {
        return null;
      }
      if (apiField === 'contact_value') {
        return contactValue;
      }
      return getField(apiField);
    };

    contactType.addEventListener('change', switchContactPlaceholder);

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!validate()) {
        return;
      }

      const contact = String(contactValue.value || '').trim();
      if (hiddenTelegram && hiddenWhatsapp) {
        if (contactType.value === 'telegram') {
          hiddenTelegram.value = contact;
          hiddenWhatsapp.value = '';
        } else {
          hiddenTelegram.value = '';
          hiddenWhatsapp.value = contact;
        }
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
            const field = resolveField(String(payload.field));
            if (field) {
              markFieldError(field, true);
              field.focus();
            }
          }
          trackGoal('starflow_form_error');
          return;
        }

        const message = payload.message ? String(payload.message) : t('msg.success', state.lang);
        setStatus(status, message, false, true);
        trackGoal('starflow_form_success');

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
        const langInput = qs('#sfw-site-lang');
        if (langInput) {
          langInput.value = state.lang;
        }
        contactType.value = 'telegram';
        switchContactPlaceholder();
      } catch (_err) {
        setStatus(status, t('msg.error', state.lang), true, false);
        trackGoal('starflow_form_error');
      } finally {
        setLoading(false);
      }
    });

    switchContactPlaceholder();
  }

  function initYear() {
    const yearNode = qs('#sfw-year');
    if (yearNode) {
      yearNode.textContent = String(new Date().getFullYear());
    }
  }

  function initStarflowPage() {
    const state = {
      lang: normalizeLang(safeStorageGet(STORAGE_KEY) || DEFAULT_LANG)
    };

    const onLangChange = (lang) => {
      applyI18n(lang);
      const hidden = qs('#sfw-site-lang');
      if (hidden) {
        hidden.value = lang;
      }
    };

    initYear();
    initReveal();
    initMobileMenu();
    initLangGate(state, onLangChange);
    initFitScore(state);
    initForm(state);
    void syncLinks();
  }

  function init() {
    if (!document.body || document.body.getAttribute('data-site') !== 'starflow') {
      return;
    }
    initStarflowPage();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
