(function () {
  'use strict';

  const LANG_STORAGE_KEY = 'starflow_lang_v2';
  const SUPPORTED_LANGS = ['ru', 'en', 'pt', 'es'];
  const DEFAULT_LANG = 'ru';
  const PROJECT_KEY = 'starflow_corp';
  const ALWAYS_SHOW_LANG_GATE = false;
  const METRIKA_COUNTER_ID = 106823371;
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const I18N = {
    ru: {
      'langGate.title': 'Выберите язык',
      'langGate.subtitle': 'Выберите язык, чтобы продолжить',
      'nav.proof': 'Преимущества',
      'nav.partners': 'Кого ищем',
      'nav.playbooks': 'Источники',
      'nav.terms': 'Оффер',
      'nav.flow': 'Как это работает',
      'nav.faq': 'FAQ',
      'nav.apply': 'Анкета',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Стать партнёром',
      'a11y.skip': 'Перейти к основному содержанию',
      'hero.overline': 'Performance-партнёрка для найма в стриминговые проекты',
      'hero.title': 'Масштабируйте интервью по понятной CPA-модели.',
      'hero.lead': 'Вы отвечаете за привлечение. Мы закрываем обработку, квалификацию и выплаты.',
      'hero.list1': 'Любой источник: таргет, аутрич, DM, job boards, рассылки.',
      'hero.list2': 'Еженедельные выплаты в USDT каждое воскресенье.',
      'hero.list3': 'CRM, скрипты и запуск с менеджером с первого дня.',
      'hero.signal': 'Панель оффера',
      'hero.signalMeta': 'Оффер активен сейчас',
      'hero.bar1': 'Доходимость до интервью',
      'hero.bar2': 'Качество аппрува',
      'hero.bar3': 'Надёжность еженедельной выплаты',
      'hero.cardA.title': 'Быстрый онбординг',
      'hero.cardA.text': 'Скрипты, CRM и шаблоны сразу после одобрения.',
      'hero.cardB.title': 'Одна KPI-логика',
      'hero.cardB.text': 'Вы приводите на интервью. Мы платим за подтверждённый результат.',
      'hero.line1': 'Таргет',
      'hero.line2': 'Job boards',
      'hero.line3': 'Рассылки',
      'hero.line4': 'Холодный аутрич',
      'hero.line5': 'DM / мессенджеры',
      'hero.line6': 'Источник не ограничен',
      'proof.item1': 'Без вступительных платежей',
      'proof.item2': 'Еженедельный payout в USDT',
      'proof.item3': 'Закреплённый менеджер',
      'proof.item4': 'Любой канал привлечения',
      'proof.item5': 'Прозрачная CRM-воронка',
      'proof.item6': 'Масштаб: от соло до команд',
      'kpi.years': 'лет работы с трафиком',
      'kpi.max': 'за подтверждённое интервью',
      'kpi.weekly': 'день еженедельной выплаты',
      'fit.overline': 'Быстрая квалификация',
      'fit.title': 'Partner Fit Scanner',
      'fit.lead': 'Проверьте за 20 секунд, готовы ли вы к запуску.',
      'fit.check1': 'Я могу стабильно приводить кандидатов каждую неделю.',
      'fit.check2': 'Я умею запускать хотя бы один канал (ads / DM / outreach / boards).',
      'fit.check3': 'Я готов работать по скриптам и фиксировать статусы в CRM.',
      'fit.check4': 'Я готов к недельной payout-модели и KPI-дисциплине.',
      'fit.scoreLabel': 'Индекс готовности',
      'fit.status.high': 'Высокий fit: можно запускаться сразу.',
      'fit.status.mid': 'Средний fit: запуск возможен после выравнивания процессов.',
      'fit.status.low': 'Низкий fit: сначала соберите базовую систему привлечения.',
      'fit.cta': 'Перейти к анкете',
      'play.overline': 'Система запуска',
      'play.title': 'Playbooks по каналам',
      'play.tab1': 'Paid Ads',
      'play.tab2': 'Job Boards',
      'play.tab3': 'Cold Outreach',
      'play.tab4': 'Direct DM',
      'play.p1.title': 'Запуск через paid ads',
      'play.p1.l1': 'Используйте креативы с чётким intent на интервью.',
      'play.p1.l2': 'Ведите трафик на квалификацию, затем на собеседование.',
      'play.p1.l3': 'Оптимизируйте кампании по подтверждённым интервью.',
      'play.p2.title': 'Запуск через job boards',
      'play.p2.l1': 'Публикуйте роли с прозрачными GEO и возрастными фильтрами.',
      'play.p2.l2': 'Используйте быстрый скрипт ответа для снижения отвалов.',
      'play.p2.l3': 'Сравнивайте board-to-interview ratio каждую неделю.',
      'play.p3.title': 'Запуск через cold outreach',
      'play.p3.l1': 'Сегментируйте базу по GEO и intent перед отправкой.',
      'play.p3.l2': 'В первом сообщении оставляйте один CTA: пройти интервью.',
      'play.p3.l3': 'Фиксируйте качество ответов в CRM и улучшайте скрипт.',
      'play.p4.title': 'Запуск через direct DM',
      'play.p4.l1': 'Начинайте с контекста, потом переходите к офферу.',
      'play.p4.l2': 'Перед ссылкой используйте короткий qualification-checklist.',
      'play.p4.l3': 'Тестируйте первые 2 строки DM для роста ответов.',
      'calc.overline': 'Планирование дохода',
      'calc.title': 'Оцените потенциальную выплату',
      'calc.interviews': 'Подтверждённых интервью в неделю',
      'calc.interviewsUnit': 'интервью / неделя',
      'calc.cpa': 'CPA за интервью (USD)',
      'calc.weekly': 'Прогноз выплаты за неделю',
      'calc.monthly': 'Прогноз выплаты за месяц (x4)',
      'calc.note': 'Это ориентировочный расчёт. Финальная сумма зависит от подтверждённых интервью в CRM.',
      'partners.overline': 'Кто нам подходит',
      'partners.title': 'Портрет партнёра',
      'partners.arb.title': 'Арбитражная команда',
      'partners.arb.text': 'Уже умеют работать с креативами, воронками, конверсией и оптимизацией.',
      'partners.call.title': 'Колл-центр',
      'partners.call.text': 'Есть менеджеры на звонках. Нужны оффер, скрипт и поток заявок.',
      'partners.agency.title': 'Маркетинговое агентство',
      'partners.agency.text': 'Процессы лидогенерации выстроены, команда готова к новому офферу.',
      'partners.solo.title': 'Соло-фрилансер',
      'partners.solo.text': 'Самостоятельно запускает рекламу или аутрич и доводит кандидатов до интервью.',
      'partners.notice1': 'Формат не важен: команда из 50 человек или один специалист.',
      'partners.notice2': 'Главное: вы умеете стабильно привлекать людей.',
      'terms.overline': 'Детали оффера',
      'terms.title': 'Как устроен оффер',
      'terms.whatWeDo.title': 'Что делаем мы',
      'terms.whatWeDo.text': 'Закрываем два направления: девушки 18-27 на стримерские позиции и парни 18-30 на модерацию. Клиенты платят нам за качественные собеседования.',
      'terms.partnerDoes.title': 'Что делает партнёр',
      'terms.partnerDoes.text': 'Ваша зона ответственности - привлекать кандидатов и доводить их до интервью. Можно использовать любой источник трафика.',
      'terms.conditions.title': 'Условия',
      'terms.conditions.cpa': 'CPA: $20-40 за каждое подтверждённое интервью',
      'terms.conditions.payout': 'Выплаты каждое воскресенье в USDT',
      'terms.conditions.limit': 'Без лимитов по объёму',
      'terms.conditions.assets': 'Предоставляем CRM, скрипты, материалы и поддержку',
      'terms.geo.title': 'GEO',
      'terms.geo.text': 'Стримеры: Европа и LatAm. Модераторы: Европа, LatAm и Азия.',
      'flow.overline': 'Пошаговый процесс',
      'flow.title': 'От трафика до выплаты',
      'flow.step1': 'Получаете оффер, CRM и скрипт запуска.',
      'flow.step2': 'Запускаете привлечение кандидатов из своего источника.',
      'flow.step3': 'Кандидаты проходят интервью, мы фиксируем статус в CRM.',
      'flow.step4': 'По подтверждённым интервью получаете выплату в USDT.',
      'faq.title': 'FAQ: важные вопросы',
      'faq.exp.q': 'У меня нет опыта',
      'faq.exp.a': 'Мы даём CRM и скрипты. Если умеете находить людей, вы быстро войдёте в процесс. Важен результат, а не «идеальный» опыт.',
      'faq.exp.follow': 'Что уточнить перед стартом:',
      'faq.exp.l1': 'Какой опыт уже есть (соцсети, рассылки, реклама)?',
      'faq.exp.l2': 'Готовы работать по материалам и скриптам?',
      'faq.exp.l3': 'Сколько времени можете уделять ежедневно?',
      'faq.mlm.q': 'Это MLM / пирамида?',
      'faq.mlm.a': 'Нет. Вход бесплатный, многоуровневой структуры нет. Вы приводите кандидатов, они проходят интервью, вы получаете оплату.',
      'faq.mlm.follow': 'Коротко о разнице:',
      'faq.mlm.l1': 'MLM: обычно есть входной платёж и уровни.',
      'faq.mlm.l2': 'Здесь: ноль вложений и оплата только за результат.',
      'faq.team.q': 'Нужна большая команда?',
      'faq.team.a': 'Нет. Можно работать как командой, так и в одиночку.',
      'faq.team.l1': 'Ключевое требование: умение привлекать кандидатов.',
      'faq.team.l2': 'Считается результат, а не размер команды.',
      'faq.sources.q': 'Какие источники трафика разрешены?',
      'faq.sources.a': 'Любые, если приводят качественных кандидатов на интервью.',
      'faq.sources.l1': 'Таргет, job boards, рассылки, DM, холодный аутрич.',
      'faq.sources.l2': 'Источник не ограничен, KPI - подтверждённые интервью.',
      'faq.pay.q': 'Как устроены выплаты и поддержка?',
      'faq.pay.a': 'Оплата идёт по CPA за подтверждённые интервью, плюс вы получаете сопровождение менеджера.',
      'faq.pay.l1': '$20-40 за каждое подтверждённое интервью.',
      'faq.pay.l2': 'Выплаты каждое воскресенье в USDT.',
      'faq.pay.l3': 'Без лимитов по объёму.',
      'faq.pay.l4': 'CRM, скрипты и материалы выдаём на старте.',
      'faq.geo.q': 'Какие GEO и типы кандидатов нужны?',
      'faq.geo.a': 'Работаем по понятным возрастным и региональным профилям.',
      'faq.geo.l1': 'Девушки 18-27 для стримерских ролей.',
      'faq.geo.l2': 'Парни 18-30 для ролей модерации.',
      'faq.geo.l3': 'Стримеры: Европа и LatAm. Модераторы: Европа, LatAm и Азия.',
      'apply.overline': 'Анкета',
      'apply.title': 'Анкета партнёра',
      'apply.copy': 'Заполнение занимает около 1 минуты. После отправки получите ссылку в мессенджер для быстрого старта.',
      'apply.hint1': 'Ответ менеджера в рабочее время',
      'apply.hint2': 'Подключение к CRM',
      'apply.hint3': 'Стартовые материалы и скрипты',
      'form.name': 'ФИО',
      'form.contact': 'Telegram или WhatsApp',
      'form.contactPlaceholderTelegram': '@username',
      'form.contactPlaceholderWhatsapp': '+7 900 000 00 00',
      'form.email': 'Email для доступа',
      'form.birth': 'Дата рождения (18+)',
      'form.phone': 'Телефон для связи',
      'form.privacy': 'Отправляя форму, вы подтверждаете согласие на обработку контактных данных для связи по заявке.',
      'form.submit': 'Отправить',
      'form.next': 'Следующий шаг',
      'form.telegram': 'Открыть Telegram',
      'form.whatsapp': 'Открыть WhatsApp',
      'msg.sending': 'Отправляем анкету...',
      'msg.success': 'Заявка принята. Переходите в мессенджер для старта.',
      'msg.required': 'Заполните все поля формы.',
      'msg.name': 'Введите корректное ФИО.',
      'msg.email': 'Введите корректный email.',
      'msg.phone': 'Телефон должен быть в международном формате.',
      'msg.birth': 'Формат даты: ДД.ММ.ГГГГ и возраст 18+.',
      'msg.telegram': 'Формат Telegram: @username',
      'msg.whatsapp': 'WhatsApp должен быть в международном формате.',
      'msg.error': 'Не удалось отправить заявку. Попробуйте ещё раз.',
      'msg.nextMissing': 'Ссылки пока не настроены. Напишите менеджеру в Telegram.',
    },
    en: {
      'langGate.title': 'Choose language',
      'langGate.subtitle': 'Select language to continue',
      'nav.proof': 'Why Starflow',
      'nav.partners': 'Who We Need',
      'nav.playbooks': 'Playbooks',
      'nav.terms': 'Offer',
      'nav.flow': 'How It Works',
      'nav.faq': 'FAQ',
      'nav.apply': 'Form',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Become Partner',
      'a11y.skip': 'Skip to main content',
      'hero.overline': 'Performance partner network for streaming recruitment',
      'hero.title': 'Scale interviews with a clean CPA model.',
      'hero.lead': 'You focus on acquisition. We handle processing, qualification, and payout infrastructure.',
      'hero.list1': 'Any source: paid ads, outreach, DM, job boards, mailing.',
      'hero.list2': 'Weekly payouts in USDT every Sunday.',
      'hero.list3': 'CRM, scripts, and launch support from day one.',
      'hero.signal': 'Offer control panel',
      'hero.signalMeta': 'Offer active now',
      'hero.bar1': 'Interview show-up rate',
      'hero.bar2': 'Approval quality',
      'hero.bar3': 'Weekly payout reliability',
      'hero.cardA.title': 'Fast onboarding',
      'hero.cardA.text': 'Scripts, CRM and templates right after approval.',
      'hero.cardB.title': 'Single KPI model',
      'hero.cardB.text': 'You bring candidates to interviews, we pay for approved results.',
      'hero.line1': 'Target Ads',
      'hero.line2': 'Job Boards',
      'hero.line3': 'Mailing Lists',
      'hero.line4': 'Cold Outreach',
      'hero.line5': 'DM / Messengers',
      'hero.line6': 'No source limits',
      'proof.item1': 'No setup fee',
      'proof.item2': 'Weekly USDT payout',
      'proof.item3': 'Dedicated manager',
      'proof.item4': 'Any acquisition channel',
      'proof.item5': 'Transparent CRM pipeline',
      'proof.item6': 'Scalable from solo to team',
      'kpi.years': 'years in traffic',
      'kpi.max': 'per approved interview',
      'kpi.weekly': 'weekly payout day',
      'fit.overline': 'Quick qualification',
      'fit.title': 'Partner Fit Scanner',
      'fit.lead': 'Check in 20 seconds if your current setup is launch-ready.',
      'fit.check1': 'I can source candidates consistently every week.',
      'fit.check2': 'I can run at least one channel (ads / DM / outreach / boards).',
      'fit.check3': 'I can follow scripts and track statuses in CRM.',
      'fit.check4': 'I can operate under weekly payout cadence and KPI discipline.',
      'fit.scoreLabel': 'Readiness score',
      'fit.status.high': 'High fit: you can launch right now.',
      'fit.status.mid': 'Medium fit: launch is possible after process alignment.',
      'fit.status.low': 'Low fit: build a stable acquisition baseline first.',
      'fit.cta': 'Start application',
      'play.overline': 'Execution system',
      'play.title': 'Channel playbooks by source',
      'play.tab1': 'Paid Ads',
      'play.tab2': 'Job Boards',
      'play.tab3': 'Cold Outreach',
      'play.tab4': 'Direct DM',
      'play.p1.title': 'Paid ads launch',
      'play.p1.l1': 'Use clear intent creatives focused on interviews.',
      'play.p1.l2': 'Route traffic to qualification first, then interview booking.',
      'play.p1.l3': 'Optimize on approved interview events, not only clicks.',
      'play.p2.title': 'Job boards launch',
      'play.p2.l1': 'Publish role-specific listings with clear GEO and age filters.',
      'play.p2.l2': 'Use fast response scripts to reduce candidate drop-off.',
      'play.p2.l3': 'Track board-to-interview ratio weekly and scale winners.',
      'play.p3.title': 'Cold outreach launch',
      'play.p3.l1': 'Segment audience by geography and role intent before outreach.',
      'play.p3.l2': 'Use one core CTA in outreach: pass interview screening.',
      'play.p3.l3': 'Log response quality in CRM and iterate weekly.',
      'play.p4.title': 'Direct DM launch',
      'play.p4.l1': 'Lead with contextual relevance before offer details.',
      'play.p4.l2': 'Run qualification checklist before sending booking link.',
      'play.p4.l3': 'A/B test the first two DM lines to improve response rate.',
      'calc.overline': 'Income planning',
      'calc.title': 'Estimate your potential payout',
      'calc.interviews': 'Approved interviews per week',
      'calc.interviewsUnit': 'interviews / week',
      'calc.cpa': 'CPA per interview (USD)',
      'calc.weekly': 'Estimated weekly payout',
      'calc.monthly': 'Estimated monthly payout (x4)',
      'calc.note': 'Planning estimate only. Final payout depends on approved interviews in CRM.',
      'partners.overline': 'Who we work with',
      'partners.title': 'Partner profile',
      'partners.arb.title': 'Arbitrage Team',
      'partners.arb.text': 'Already works with creatives, funnels, conversion and optimization.',
      'partners.call.title': 'Call-Center',
      'partners.call.text': 'Has active callers. Needs a clear offer, script and interview flow.',
      'partners.agency.title': 'Marketing Agency',
      'partners.agency.text': 'Lead generation process is already built and ready for a new offer.',
      'partners.solo.title': 'Solo Freelancer',
      'partners.solo.text': 'Runs ads or outreach independently and delivers candidates to interviews.',
      'partners.notice1': 'Format does not matter: a 50-person team or one specialist.',
      'partners.notice2': 'Only one thing matters: consistent candidate acquisition.',
      'terms.overline': 'Offer details',
      'terms.title': 'How the offer works',
      'terms.whatWeDo.title': 'What we do',
      'terms.whatWeDo.text': 'We cover two hiring streams: female candidates 18-27 for streamer roles and male candidates 18-30 for moderation roles. Clients pay us for qualified interviews.',
      'terms.partnerDoes.title': 'What partner does',
      'terms.partnerDoes.text': 'Your role is candidate acquisition and interview attendance. You can use any traffic source.',
      'terms.conditions.title': 'Conditions',
      'terms.conditions.cpa': 'CPA: $20-40 per approved interview',
      'terms.conditions.payout': 'Payouts every Sunday in USDT',
      'terms.conditions.limit': 'No volume limits',
      'terms.conditions.assets': 'CRM, scripts, materials and manager support are provided',
      'terms.geo.title': 'GEO',
      'terms.geo.text': 'Streamers: Europe and LatAm. Moderators: Europe, LatAm and Asia.',
      'flow.overline': 'Step-by-step process',
      'flow.title': 'From traffic to payout',
      'flow.step1': 'Get offer, CRM and launch scripts.',
      'flow.step2': 'Run candidate acquisition from your source.',
      'flow.step3': 'Candidates pass interviews, statuses are confirmed in CRM.',
      'flow.step4': 'Receive USDT payout for approved interviews.',
      'faq.title': 'FAQ: key questions',
      'faq.exp.q': 'I have no experience',
      'faq.exp.a': 'We provide CRM and scripts. If you know how to reach people, you can ramp up quickly. Results matter more than perfect background.',
      'faq.exp.follow': 'What to clarify before launch:',
      'faq.exp.l1': 'What experience do you already have (social, outreach, ads)?',
      'faq.exp.l2': 'Are you ready to follow scripts and materials?',
      'faq.exp.l3': 'How much time can you allocate daily?',
      'faq.mlm.q': 'Is this MLM / pyramid?',
      'faq.mlm.a': 'No. Joining is free, there is no multi-level structure. You bring candidates, they pass interviews, you get paid.',
      'faq.mlm.follow': 'Short difference:',
      'faq.mlm.l1': 'MLM: usually entry fee + levels.',
      'faq.mlm.l2': 'Here: zero investment + payment for result.',
      'faq.team.q': 'Do I need a big team?',
      'faq.team.a': 'No. You can work as a team or solo.',
      'faq.team.l1': 'Main requirement: ability to attract candidates.',
      'faq.team.l2': 'Performance matters more than team size.',
      'faq.sources.q': 'Which traffic sources are allowed?',
      'faq.sources.a': 'Any source is allowed if it brings qualified interview-ready candidates.',
      'faq.sources.l1': 'Target ads, job boards, mailing lists, DM, cold outreach.',
      'faq.sources.l2': 'Source is flexible, KPI is approved interviews.',
      'faq.pay.q': 'How do payout and support work?',
      'faq.pay.a': 'You are paid under CPA for approved interviews and get ongoing manager support.',
      'faq.pay.l1': '$20-40 per approved interview.',
      'faq.pay.l2': 'Payouts every Sunday in USDT.',
      'faq.pay.l3': 'No volume limits.',
      'faq.pay.l4': 'CRM, scripts and materials are provided on start.',
      'faq.geo.q': 'What GEO and candidate types do you need?',
      'faq.geo.a': 'We work with clear age and region profiles.',
      'faq.geo.l1': 'Female candidates 18-27 for streamer roles.',
      'faq.geo.l2': 'Male candidates 18-30 for moderation roles.',
      'faq.geo.l3': 'Streamers: Europe and LatAm. Moderators: Europe, LatAm and Asia.',
      'apply.overline': 'Application',
      'apply.title': 'Partner application',
      'apply.copy': 'Takes about 1 minute. After submission you get a messenger link to start quickly.',
      'apply.hint1': 'Manager response during business hours',
      'apply.hint2': 'CRM access setup',
      'apply.hint3': 'Launch materials and scripts',
      'form.name': 'Full name',
      'form.contact': 'Telegram or WhatsApp',
      'form.contactPlaceholderTelegram': '@username',
      'form.contactPlaceholderWhatsapp': '+34 600 000 000',
      'form.email': 'Email for access',
      'form.birth': 'Date of birth (18+)',
      'form.phone': 'Phone number',
      'form.privacy': 'By submitting this form, you agree to contact-data processing solely for application follow-up.',
      'form.submit': 'Submit',
      'form.next': 'Next step',
      'form.telegram': 'Open Telegram',
      'form.whatsapp': 'Open WhatsApp',
      'msg.sending': 'Submitting application...',
      'msg.success': 'Application received. Continue in messenger to start.',
      'msg.required': 'Please fill in all form fields.',
      'msg.name': 'Enter a valid full name.',
      'msg.email': 'Enter a valid email address.',
      'msg.phone': 'Phone must be in international format.',
      'msg.birth': 'Birth date format: DD.MM.YYYY and age 18+.',
      'msg.telegram': 'Telegram format: @username',
      'msg.whatsapp': 'WhatsApp must be in international format.',
      'msg.error': 'Could not send application. Please try again.',
      'msg.nextMissing': 'Links are not configured yet. Contact manager in Telegram.',
    },
    pt: {
      'langGate.title': 'Escolha o idioma',
      'langGate.subtitle': 'Escolha o idioma da interface para continuar',
      'nav.proof': 'Vantagens',
      'nav.partners': 'Tipos de Parceiro',
      'nav.playbooks': 'Playbooks',
      'nav.terms': 'Condições',
      'nav.flow': 'Fluxo do Parceiro',
      'nav.faq': 'FAQ',
      'nav.apply': 'Aplicar',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Aplicar',
      'a11y.skip': 'Ir para o conteúdo principal',
      'hero.overline': 'Rede de parceiros de performance para recrutamento em streaming',
      'hero.title': 'Escalone entrevistas com um modelo CPA claro.',
      'hero.lead': 'Você foca na aquisição. Nós cuidamos da qualificação, operação e pagamentos.',
      'hero.list1': 'Qualquer fonte: tráfego pago, outreach, DM, job boards, listas.',
      'hero.list2': 'Pagamentos semanais em USDT todo domingo.',
      'hero.list3': 'CRM, scripts e suporte de lançamento desde o início.',
      'hero.signal': 'Painel da oferta',
      'hero.signalMeta': 'Oferta ativa agora',
      'hero.bar1': 'Taxa de comparecimento em entrevistas',
      'hero.bar2': 'Qualidade de aprovação',
      'hero.bar3': 'Confiabilidade de pagamento semanal',
      'hero.cardA.title': 'Onboarding rápido',
      'hero.cardA.text': 'Scripts, CRM e templates logo após aprovação.',
      'hero.cardB.title': 'Modelo com KPI único',
      'hero.cardB.text': 'Você leva candidatos para entrevistas, nós pagamos por aprovados.',
      'hero.line1': 'Tráfego pago',
      'hero.line2': 'Job boards',
      'hero.line3': 'Listas de envio',
      'hero.line4': 'Outreach frio',
      'hero.line5': 'DM direto',
      'hero.line6': 'Sem limite de fontes',
      'proof.item1': 'Sem taxa de entrada',
      'proof.item2': 'Pagamento semanal em USDT',
      'proof.item3': 'Manager dedicado',
      'proof.item4': 'Qualquer canal de aquisição',
      'proof.item5': 'Pipeline CRM transparente',
      'proof.item6': 'Escala: solo ou equipe',
      'kpi.years': 'anos com tráfego',
      'kpi.max': 'CPA máximo por entrevista',
      'kpi.weekly': 'ciclo de pagamento',
      'fit.overline': 'Qualificação rápida',
      'fit.title': 'Partner Fit Scanner',
      'fit.lead': 'Verifique em 20 segundos se sua estrutura já está pronta.',
      'fit.check1': 'Consigo atrair candidatos de forma consistente toda semana.',
      'fit.check2': 'Consigo operar ao menos um canal (ads / DM / outreach / boards).',
      'fit.check3': 'Consigo seguir scripts e controlar status no CRM.',
      'fit.check4': 'Consigo trabalhar com ritmo semanal e disciplina de KPI.',
      'fit.scoreLabel': 'Índice de prontidão',
      'fit.status.high': 'Alta aderência: você pode lançar agora.',
      'fit.status.mid': 'Aderência média: lançamento possível com ajuste de processo.',
      'fit.status.low': 'Baixa aderência: monte a base de aquisição primeiro.',
      'fit.cta': 'Iniciar candidatura',
      'play.overline': 'Sistema de execução',
      'play.title': 'Playbooks por canal',
      'play.tab1': 'Paid Ads',
      'play.tab2': 'Job Boards',
      'play.tab3': 'Cold Outreach',
      'play.tab4': 'Direct DM',
      'play.p1.title': 'Lançamento com paid ads',
      'play.p1.l1': 'Use criativos com intenção clara de entrevista.',
      'play.p1.l2': 'Leve o tráfego para qualificação e depois para agendamento.',
      'play.p1.l3': 'Otimize por entrevistas aprovadas, não só por cliques.',
      'play.p2.title': 'Lançamento com job boards',
      'play.p2.l1': 'Publique vagas com filtros claros de GEO e faixa etária.',
      'play.p2.l2': 'Use script de resposta rápida para reduzir perda de candidatos.',
      'play.p2.l3': 'Acompanhe board-to-interview ratio semanalmente.',
      'play.p3.title': 'Lançamento com cold outreach',
      'play.p3.l1': 'Segmente a base por GEO e intenção antes do contato.',
      'play.p3.l2': 'Use um único CTA principal: passar na triagem de entrevista.',
      'play.p3.l3': 'Registre qualidade das respostas no CRM e itere semanalmente.',
      'play.p4.title': 'Lançamento com direct DM',
      'play.p4.l1': 'Comece com contexto e só depois apresente a oferta.',
      'play.p4.l2': 'Use checklist de qualificação antes do link de entrevista.',
      'play.p4.l3': 'Teste as duas primeiras linhas do DM para aumentar resposta.',
      'calc.overline': 'Planejamento de receita',
      'calc.title': 'Estime seu pagamento potencial',
      'calc.interviews': 'Entrevistas aprovadas por semana',
      'calc.interviewsUnit': 'entrevistas / semana',
      'calc.cpa': 'CPA por entrevista (USD)',
      'calc.weekly': 'Pagamento estimado semanal',
      'calc.monthly': 'Pagamento estimado mensal (x4)',
      'calc.note': 'Estimativa para planejamento. O valor final depende das entrevistas aprovadas no CRM.',
      'partners.overline': 'Quem Procuramos',
      'partners.title': 'Perfil do parceiro',
      'partners.arb.title': 'Equipe de Arbitragem',
      'partners.arb.text': 'Já domina criativos, funis, conversão e otimização.',
      'partners.call.title': 'Call-Center',
      'partners.call.text': 'Tem operadores em chamadas o dia inteiro. Precisa só de oferta + script.',
      'partners.agency.title': 'Agência de Marketing',
      'partners.agency.text': 'Processos de geração de leads já estão estruturados.',
      'partners.solo.title': 'Freelancer Solo',
      'partners.solo.text': 'Roda anúncios/outreach sozinho e entrega resultado.',
      'partners.notice1': 'Formato não importa: time de 50 pessoas ou uma pessoa com notebook.',
      'partners.notice2': 'Só importa uma coisa: você sabe atrair pessoas.',
      'terms.overline': 'Detalhes da Oferta',
      'terms.title': 'Como esta oferta funciona',
      'terms.whatWeDo.title': 'O que fazemos',
      'terms.whatWeDo.text': 'Buscamos candidatas 18-27 para streaming e candidatos 18-30 para moderação. Empresas pagam por entrevistas qualificadas.',
      'terms.partnerDoes.title': 'O que o parceiro faz',
      'terms.partnerDoes.text': 'Você leva candidatos para entrevistas por qualquer fonte: anúncios, DM, mailing, job boards, outreach frio.',
      'terms.conditions.title': 'Condições',
      'terms.conditions.cpa': 'Modelo CPA: $20-40 por entrevista bem-sucedida',
      'terms.conditions.payout': 'Pagamentos todo domingo em USDT',
      'terms.conditions.limit': 'Sem limites: quanto mais traz, mais recebe',
      'terms.conditions.assets': 'Fornecemos CRM, scripts e materiais',
      'terms.geo.title': 'GEO',
      'terms.geo.text': 'Modelos: Europa, LatAm. Operadores: Europa, LatAm, Ásia.',
      'flow.overline': 'Fluxo do Parceiro',
      'flow.title': 'Do tráfego ao pagamento',
      'flow.step1': 'Você ativa tráfego de qualquer fonte.',
      'flow.step2': 'Os candidatos chegam na etapa de entrevista.',
      'flow.step3': 'Entrevistas qualificadas são registradas no CRM.',
      'flow.step4': 'Você recebe pagamento semanal em USDT.',
      'faq.title': 'Objeções comuns',
      'faq.exp.q': 'Não tenho experiência',
      'faq.exp.a': 'Nós fornecemos CRM e scripts. Se você sabe encontrar pessoas, vai conseguir. O método não importa, o resultado sim.',
      'faq.exp.follow': 'Alinhe com o partner:',
      'faq.exp.l1': 'Qual experiência você já tem (social, outreach, ads)?',
      'faq.exp.l2': 'Está pronto para aprender com nossos materiais?',
      'faq.exp.l3': 'Quanto tempo pode dedicar?',
      'faq.mlm.q': 'Isso é MLM / pirâmide?',
      'faq.mlm.a': 'Não. Você não paga para entrar. Não há estrutura multinível. Você traz candidatos, eles passam entrevista, você recebe.',
      'faq.mlm.follow': 'Diferença:',
      'faq.mlm.l1': 'MLM: paga entrada + constrói níveis.',
      'faq.mlm.l2': 'Aqui: zero investimento, um nível, pagamento por resultado.',
      'faq.team.q': 'Preciso de uma equipe grande?',
      'faq.team.a': 'Não. O tamanho da equipe não importa. Vale time de 50 pessoas ou freelancer solo.',
      'faq.team.l1': 'Requisito principal: saber atrair pessoas.',
      'faq.team.l2': 'Importa o resultado, não o headcount.',
      'faq.sources.q': 'Quais fontes de tráfego são permitidas?',
      'faq.sources.a': 'Qualquer fonte é permitida se trouxer candidatos qualificados para entrevista.',
      'faq.sources.l1': 'Anúncios, job boards, listas, DM, outreach frio.',
      'faq.sources.l2': 'O método é flexível; KPI é qualidade da entrevista.',
      'faq.pay.q': 'Como funcionam pagamento e suporte?',
      'faq.pay.a': 'Você recebe no modelo CPA por entrevista aprovada e recebe suporte operacional desde o início.',
      'faq.pay.l1': '$20-40 por entrevista bem-sucedida.',
      'faq.pay.l2': 'Pagamentos todo domingo em USDT.',
      'faq.pay.l3': 'Sem limite de volume.',
      'faq.pay.l4': 'Fornecemos CRM, scripts e materiais.',
      'faq.geo.q': 'Quais GEOs e perfis de candidatos vocês precisam?',
      'faq.geo.a': 'Trabalhamos com perfis claros de idade e região.',
      'faq.geo.l1': 'Mulheres 18-27 para funções de streamer.',
      'faq.geo.l2': 'Homens 18-30 para funções de moderação.',
      'faq.geo.l3': 'Modelos: Europa + LatAm. Operadores: Europa + LatAm + Ásia.',
      'apply.overline': 'Aplicação',
      'apply.title': 'Comece como parceiro',
      'apply.copy': 'Preencha o formulário curto e continue no mensageiro.',
      'apply.hint1': 'Sem burocracia',
      'apply.hint2': 'Contato direto com gerente',
      'apply.hint3': 'Lançamento rápido com scripts',
      'form.name': 'Nome completo',
      'form.contact': 'Dados de contato',
      'form.contactPlaceholderTelegram': '@usuario',
      'form.contactPlaceholderWhatsapp': '+55 11 99999 9999',
      'form.email': 'Email para registro',
      'form.birth': 'Data de nascimento',
      'form.phone': 'Telefone',
      'form.privacy': 'Ao enviar o formulário, você concorda com o processamento de dados de contato apenas para retorno da aplicação.',
      'form.submit': 'Enviar aplicação',
      'form.next': 'Continuar no mensageiro',
      'form.telegram': 'Abrir Telegram',
      'form.whatsapp': 'Abrir WhatsApp',
      'msg.sending': 'Enviando aplicação...',
      'msg.success': 'Aplicação enviada com sucesso.',
      'msg.required': 'Preencha todos os campos obrigatórios.',
      'msg.name': 'Informe um nome completo válido.',
      'msg.email': 'Informe um email válido.',
      'msg.phone': 'Telefone no formato internacional.',
      'msg.birth': 'Formato: DD.MM.YYYY e idade 18+.',
      'msg.telegram': 'Formato do Telegram: @usuario',
      'msg.whatsapp': 'WhatsApp no formato internacional.',
      'msg.error': 'Não foi possível enviar. Tente novamente.',
      'msg.nextMissing': 'Links ainda não configurados. Fale com o manager no Telegram.',
    },
    es: {
      'langGate.title': 'Elige idioma',
      'langGate.subtitle': 'Elige el idioma de la interfaz para continuar',
      'nav.proof': 'Ventajas',
      'nav.partners': 'Tipos de Partner',
      'nav.playbooks': 'Playbooks',
      'nav.terms': 'Condiciones',
      'nav.flow': 'Flujo del Partner',
      'nav.faq': 'FAQ',
      'nav.apply': 'Aplicar',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Aplicar',
      'a11y.skip': 'Saltar al contenido principal',
      'hero.overline': 'Red de partners de performance para reclutamiento en streaming',
      'hero.title': 'Escala entrevistas con un modelo CPA claro.',
      'hero.lead': 'Tú te enfocas en adquisición. Nosotros cubrimos operación, validación y pagos.',
      'hero.list1': 'Cualquier fuente: ads, outreach, DM, job boards, mailings.',
      'hero.list2': 'Pagos semanales en USDT cada domingo.',
      'hero.list3': 'CRM, scripts y soporte de lanzamiento desde el día uno.',
      'hero.signal': 'Panel de oferta',
      'hero.signalMeta': 'Oferta activa ahora',
      'hero.bar1': 'Tasa de asistencia a entrevistas',
      'hero.bar2': 'Calidad de aprobación',
      'hero.bar3': 'Confiabilidad de pago semanal',
      'hero.cardA.title': 'Onboarding rápido',
      'hero.cardA.text': 'Scripts, CRM y plantillas justo después de la aprobación.',
      'hero.cardB.title': 'Modelo KPI único',
      'hero.cardB.text': 'Traes candidatos a entrevistas, pagamos por aprobados.',
      'hero.line1': 'Ads',
      'hero.line2': 'Job boards',
      'hero.line3': 'Mailings',
      'hero.line4': 'Outreach en frío',
      'hero.line5': 'DM directo',
      'hero.line6': 'Sin límite de fuentes',
      'proof.item1': 'Sin tarifa de entrada',
      'proof.item2': 'Pago semanal en USDT',
      'proof.item3': 'Manager dedicado',
      'proof.item4': 'Cualquier canal de adquisición',
      'proof.item5': 'Pipeline CRM transparente',
      'proof.item6': 'Escalable: solo o equipo',
      'kpi.years': 'años en tráfico',
      'kpi.max': 'CPA máximo por entrevista',
      'kpi.weekly': 'ciclo de pago',
      'fit.overline': 'Calificación rápida',
      'fit.title': 'Partner Fit Scanner',
      'fit.lead': 'Comprueba en 20 segundos si tu sistema está listo para lanzar.',
      'fit.check1': 'Puedo atraer candidatos de forma consistente cada semana.',
      'fit.check2': 'Puedo operar al menos un canal (ads / DM / outreach / boards).',
      'fit.check3': 'Puedo seguir scripts y controlar estados en CRM.',
      'fit.check4': 'Puedo trabajar con ritmo semanal y disciplina KPI.',
      'fit.scoreLabel': 'Índice de preparación',
      'fit.status.high': 'Alta compatibilidad: puedes lanzar ahora.',
      'fit.status.mid': 'Compatibilidad media: lanzamiento posible con ajustes.',
      'fit.status.low': 'Baja compatibilidad: arma primero la base de adquisición.',
      'fit.cta': 'Iniciar solicitud',
      'play.overline': 'Sistema de ejecución',
      'play.title': 'Playbooks por canal',
      'play.tab1': 'Paid Ads',
      'play.tab2': 'Job Boards',
      'play.tab3': 'Cold Outreach',
      'play.tab4': 'Direct DM',
      'play.p1.title': 'Lanzamiento con paid ads',
      'play.p1.l1': 'Usa creativos con intención clara de entrevista.',
      'play.p1.l2': 'Lleva tráfico a calificación y luego a agendamiento.',
      'play.p1.l3': 'Optimiza por entrevistas aprobadas, no solo clics.',
      'play.p2.title': 'Lanzamiento con job boards',
      'play.p2.l1': 'Publica roles con filtros claros de GEO y edad.',
      'play.p2.l2': 'Usa respuesta rápida para reducir abandono de candidatos.',
      'play.p2.l3': 'Mide board-to-interview ratio semanalmente.',
      'play.p3.title': 'Lanzamiento con cold outreach',
      'play.p3.l1': 'Segmenta audiencia por GEO e intención antes de contactar.',
      'play.p3.l2': 'Usa un solo CTA: pasar el filtro de entrevista.',
      'play.p3.l3': 'Registra calidad de respuestas en CRM e itera cada semana.',
      'play.p4.title': 'Lanzamiento con direct DM',
      'play.p4.l1': 'Empieza por contexto y luego pasa a la oferta.',
      'play.p4.l2': 'Aplica checklist de calificación antes del link.',
      'play.p4.l3': 'Testea las dos primeras líneas de DM para subir respuesta.',
      'calc.overline': 'Planificación de ingresos',
      'calc.title': 'Calcula tu pago potencial',
      'calc.interviews': 'Entrevistas aprobadas por semana',
      'calc.interviewsUnit': 'entrevistas / semana',
      'calc.cpa': 'CPA por entrevista (USD)',
      'calc.weekly': 'Pago semanal estimado',
      'calc.monthly': 'Pago mensual estimado (x4)',
      'calc.note': 'Estimación para planificación. El pago final depende de entrevistas aprobadas en CRM.',
      'partners.overline': 'A quién buscamos',
      'partners.title': 'Perfil de partner',
      'partners.arb.title': 'Equipo de Arbitraje',
      'partners.arb.text': 'Ya domina creativos, funnels, conversión y optimización.',
      'partners.call.title': 'Call-Center',
      'partners.call.text': 'Tiene managers llamando todo el día. Solo necesita oferta + script.',
      'partners.agency.title': 'Agencia de Marketing',
      'partners.agency.text': 'Procesos de generación de leads ya estructurados.',
      'partners.solo.title': 'Freelancer',
      'partners.solo.text': 'Lanza anuncios/outreach por su cuenta y entrega resultado.',
      'partners.notice1': 'El formato no importa: equipo de 50 personas o una persona con laptop.',
      'partners.notice2': 'Solo importa una cosa: sabes atraer gente.',
      'terms.overline': 'Detalles de la Oferta',
      'terms.title': 'Cómo funciona esta oferta',
      'terms.whatWeDo.title': 'Qué hacemos',
      'terms.whatWeDo.text': 'Buscamos candidatas 18-27 para streaming y candidatos 18-30 para moderación. Las empresas pagan por entrevistas calificadas.',
      'terms.partnerDoes.title': 'Qué hace el partner',
      'terms.partnerDoes.text': 'Llevas candidatos a entrevistas por cualquier fuente: anuncios, DM, mailing, bolsas de trabajo, outreach frío.',
      'terms.conditions.title': 'Condiciones',
      'terms.conditions.cpa': 'Modelo CPA: $20-40 por entrevista exitosa',
      'terms.conditions.payout': 'Pagos cada domingo en USDT',
      'terms.conditions.limit': 'Sin límites: más candidatos, más ingreso',
      'terms.conditions.assets': 'Damos CRM, scripts y materiales',
      'terms.geo.title': 'GEO',
      'terms.geo.text': 'Modelos: Europa, LatAm. Operadores: Europa, LatAm, Asia.',
      'flow.overline': 'Flujo del Partner',
      'flow.title': 'Del tráfico al pago',
      'flow.step1': 'Lanzas tráfico desde cualquier fuente.',
      'flow.step2': 'Los candidatos llegan a entrevistas.',
      'flow.step3': 'Entrevistas calificadas se registran en CRM.',
      'flow.step4': 'Recibes pago semanal en USDT.',
      'faq.title': 'Objeciones comunes',
      'faq.exp.q': 'No tengo experiencia',
      'faq.exp.a': 'Damos CRM y scripts. Si sabes llegar a la gente, lo resolverás. El método no importa, importa el resultado.',
      'faq.exp.follow': 'Aclarar con el partner:',
      'faq.exp.l1': '¿Qué experiencia tienes (social, outreach, ads)?',
      'faq.exp.l2': '¿Listo para aprender con nuestros materiales?',
      'faq.exp.l3': '¿Cuánto tiempo puedes dedicar?',
      'faq.mlm.q': '¿Es MLM / pirámide?',
      'faq.mlm.a': 'No. No pagas para entrar. No hay estructura multinivel. Traes candidatos, pasan entrevistas, cobras.',
      'faq.mlm.follow': 'Diferencia:',
      'faq.mlm.l1': 'MLM: pagas entrada + construyes niveles.',
      'faq.mlm.l2': 'Aquí: cero inversión, un nivel, pago por resultado.',
      'faq.team.q': '¿Necesito un equipo grande?',
      'faq.team.a': 'No. El tamaño del equipo no importa. Sirve un equipo grande o un freelancer solo.',
      'faq.team.l1': 'Requisito clave: saber atraer personas.',
      'faq.team.l2': 'Importa el resultado, no el tamaño del equipo.',
      'faq.sources.q': '¿Qué fuentes de tráfico están permitidas?',
      'faq.sources.a': 'Cualquier fuente sirve si trae candidatos calificados a entrevistas.',
      'faq.sources.l1': 'Ads, job boards, mailing, DM, outreach en frío.',
      'faq.sources.l2': 'El método es flexible; el KPI es la calidad de entrevista.',
      'faq.pay.q': '¿Cómo funcionan pagos y soporte?',
      'faq.pay.a': 'Cobras en modelo CPA por entrevistas exitosas y te damos soporte operativo desde el día uno.',
      'faq.pay.l1': '$20-40 por entrevista exitosa.',
      'faq.pay.l2': 'Pagos cada domingo en USDT.',
      'faq.pay.l3': 'Sin límites de volumen.',
      'faq.pay.l4': 'Damos CRM, scripts y materiales.',
      'faq.geo.q': '¿Qué GEO y perfiles de candidatos necesitan?',
      'faq.geo.a': 'Trabajamos con perfiles definidos por edad y región.',
      'faq.geo.l1': 'Mujeres 18-27 para roles de streamer.',
      'faq.geo.l2': 'Hombres 18-30 para roles de moderación.',
      'faq.geo.l3': 'Modelos: Europa + LatAm. Operadores: Europa + LatAm + Asia.',
      'apply.overline': 'Aplicación',
      'apply.title': 'Empieza como partner',
      'apply.copy': 'Completa el formulario corto y continúa en mensajería.',
      'apply.hint1': 'Sin burocracia',
      'apply.hint2': 'Contacto directo con manager',
      'apply.hint3': 'Lanzamiento rápido con scripts',
      'form.name': 'Nombre completo',
      'form.contact': 'Datos de contacto',
      'form.contactPlaceholderTelegram': '@usuario',
      'form.contactPlaceholderWhatsapp': '+34 600 000 000',
      'form.email': 'Email para registro',
      'form.birth': 'Fecha de nacimiento',
      'form.phone': 'Número de teléfono',
      'form.privacy': 'Al enviar el formulario, aceptas el tratamiento de datos de contacto únicamente para responder a tu solicitud.',
      'form.submit': 'Enviar aplicación',
      'form.next': 'Continuar en mensajería',
      'form.telegram': 'Abrir Telegram',
      'form.whatsapp': 'Abrir WhatsApp',
      'msg.sending': 'Enviando aplicación...',
      'msg.success': 'Aplicación enviada correctamente.',
      'msg.required': 'Completa todos los campos obligatorios.',
      'msg.name': 'Ingresa un nombre completo válido.',
      'msg.email': 'Ingresa un email válido.',
      'msg.phone': 'El teléfono debe estar en formato internacional.',
      'msg.birth': 'Formato: DD.MM.YYYY y edad 18+.',
      'msg.telegram': 'Formato de Telegram: @usuario',
      'msg.whatsapp': 'WhatsApp en formato internacional.',
      'msg.error': 'No se pudo enviar. Intenta de nuevo.',
      'msg.nextMissing': 'Links aún no configurados. Contacta al manager en Telegram.',
    },
  };

  const storedLang = getStoredLang();
  const state = {
    lang: storedLang || DEFAULT_LANG,
    hasStoredLang: Boolean(storedLang),
    calcUpdate: null,
    fitUpdate: null,
    config: {
      telegram_link: 'https://t.me/starflowcorp',
      bot_link: null,
      whatsapp_link: null,
    },
  };

  const dom = {
    form: document.getElementById('apply-form'),
    status: document.getElementById('form-status'),
    submit: document.getElementById('submit-btn'),
    birth: document.getElementById('birthdate'),
    phone: document.getElementById('phone'),
    lang: document.getElementById('lang-select'),
    loader: document.getElementById('site-loader'),
    langGate: document.getElementById('lang-gate'),
    langGateChoices: document.querySelectorAll('[data-lang-choice]'),
    langGateClose: document.querySelectorAll('[data-lang-close]'),
    preferred: document.getElementById('preferred-contact'),
    contactValue: document.getElementById('contact-value'),
    nextBox: document.getElementById('next-actions'),
    nextTelegram: document.getElementById('next-telegram'),
    nextWhatsapp: document.getElementById('next-whatsapp'),
    progressBar: document.getElementById('scroll-progress-bar'),
    heroLab: document.querySelector('[data-hero-lab]'),
    timelineItems: document.querySelectorAll('.timeline li'),
    calcInterviews: document.getElementById('calc-interviews'),
    calcCpa: document.getElementById('calc-cpa'),
    calcInterviewsValue: document.getElementById('calc-interviews-value'),
    calcCpaValue: document.getElementById('calc-cpa-value'),
    calcWeekly: document.getElementById('calc-weekly'),
    calcMonthly: document.getElementById('calc-monthly'),
    fitToggles: document.querySelectorAll('[data-fit-toggle]'),
    fitScore: document.getElementById('fit-score'),
    fitStatus: document.querySelector('[data-fit-status]'),
    playbookButtons: document.querySelectorAll('[data-playbook-btn]'),
    playbookPanels: document.querySelectorAll('[data-playbook-panel]'),
  };

  let langGateRestoreFocus = null;

  function getStoredLang() {
    try {
      const stored = localStorage.getItem(LANG_STORAGE_KEY);
      if (SUPPORTED_LANGS.includes(stored)) {
        return stored;
      }
    } catch (err) {
      // ignore
    }
    return null;
  }

  function persistLang(lang) {
    try {
      localStorage.setItem(LANG_STORAGE_KEY, lang);
    } catch (err) {
      // ignore
    }
  }

  function t(key) {
    return (I18N[state.lang] && I18N[state.lang][key]) || I18N.en[key] || key;
  }

  function escapeHtml(raw) {
    return String(raw || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function setSafeTextWithBreaks(node, value) {
    if (!node) return;
    const escaped = escapeHtml(value);
    node.innerHTML = escaped.replace(/&lt;br\s*\/?&gt;/gi, '<br>');
  }

  function applyI18n() {
    document.documentElement.lang = state.lang;
    if (dom.lang) {
      dom.lang.value = state.lang;
    }

    document.querySelectorAll('[data-i18n]').forEach((node) => {
      const key = node.getAttribute('data-i18n');
      const value = t(key);
      setSafeTextWithBreaks(node, value);
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach((node) => {
      const key = node.getAttribute('data-i18n-placeholder');
      node.setAttribute('placeholder', t(key));
    });

    document.querySelectorAll('[data-i18n-aria-label]').forEach((node) => {
      const key = node.getAttribute('data-i18n-aria-label');
      const value = t(key);
      if (value) {
        node.setAttribute('aria-label', value);
      }
    });

    if (dom.form) {
      const langInput = dom.form.querySelector('input[name="site_lang"]');
      if (langInput) {
        langInput.value = state.lang;
      }
    }

    updateContactPlaceholder();
    if (typeof state.calcUpdate === 'function') {
      state.calcUpdate();
    }
    if (typeof state.fitUpdate === 'function') {
      state.fitUpdate();
    }
  }

  function setLanguage(lang, persist = true) {
    const next = SUPPORTED_LANGS.includes(lang) ? lang : DEFAULT_LANG;
    state.lang = next;
    if (persist) {
      persistLang(next);
      state.hasStoredLang = true;
    }
    applyI18n();
  }

  function openLangGate() {
    if (!dom.langGate) {
      return;
    }
    if (document.activeElement instanceof HTMLElement) {
      langGateRestoreFocus = document.activeElement;
    }
    dom.langGate.hidden = false;
    document.body.classList.add('lang-gate-open');
    const firstChoice = dom.langGate.querySelector('[data-lang-choice]');
    if (firstChoice instanceof HTMLElement) {
      firstChoice.focus();
    }
  }

  function closeLangGate() {
    if (!dom.langGate) {
      return;
    }
    dom.langGate.hidden = true;
    document.body.classList.remove('lang-gate-open');
    if (langGateRestoreFocus instanceof HTMLElement && document.contains(langGateRestoreFocus)) {
      langGateRestoreFocus.focus();
    }
    langGateRestoreFocus = null;
  }

  function initLanguageGate() {
    if (!dom.langGate) {
      return;
    }
    dom.langGateChoices.forEach((button) => {
      button.addEventListener('click', () => {
        const lang = button.getAttribute('data-lang-choice') || DEFAULT_LANG;
        setLanguage(lang, true);
        closeLangGate();
      });
    });
    dom.langGateClose.forEach((node) => {
      node.addEventListener('click', () => {
        closeLangGate();
      });
    });

    document.addEventListener('keydown', (event) => {
      if (event.key !== 'Escape') return;
      if (dom.langGate && !dom.langGate.hidden) {
        closeLangGate();
      }
    });

    if (ALWAYS_SHOW_LANG_GATE || !state.hasStoredLang) {
      openLangGate();
    }
  }

  function initLoader() {
    if (!dom.loader) {
      document.body.classList.remove('is-loading');
      return;
    }
    const startedAt = performance.now();
    let hidden = false;

    const hide = () => {
      if (hidden) {
        return;
      }
      hidden = true;
      const elapsed = performance.now() - startedAt;
      const wait = Math.max(0, 900 - elapsed);
      window.setTimeout(() => {
        document.body.classList.remove('is-loading');
        document.body.classList.add('is-ready');
      }, wait);
    };

    if (document.readyState === 'complete') {
      hide();
    } else {
      window.addEventListener('load', hide, { once: true });
      window.setTimeout(hide, 2600);
    }
  }

  function updateContactPlaceholder() {
    if (!dom.preferred || !dom.contactValue) {
      return;
    }
    const method = dom.preferred.value;
    if (method === 'whatsapp') {
      dom.contactValue.placeholder = t('form.contactPlaceholderWhatsapp');
    } else {
      dom.contactValue.placeholder = t('form.contactPlaceholderTelegram');
    }
  }

  function setStatus(message, mode) {
    if (!dom.status) {
      return;
    }
    dom.status.textContent = message || '';
    dom.status.classList.remove('error', 'success');
    if (mode) {
      dom.status.classList.add(mode);
    }
  }

  function trackGoal(goal, params = {}) {
    try {
      if (typeof window.ym !== 'function') return;
      window.ym(METRIKA_COUNTER_ID, 'reachGoal', goal, params);
    } catch (err) {
      // ignore analytics failures
    }
  }

  function ensureHoneypotFields() {
    if (!dom.form) return;
    const fields = [
      { name: 'website', autocomplete: 'off' },
      { name: 'company', autocomplete: 'organization' },
    ];
    fields.forEach((meta) => {
      let field = dom.form.querySelector(`input[name="${meta.name}"]`);
      if (!field) {
        field = document.createElement('input');
        field.type = 'text';
        field.name = meta.name;
        field.value = '';
        field.className = 'hp-field';
        field.tabIndex = -1;
        field.autocomplete = meta.autocomplete;
        field.setAttribute('aria-hidden', 'true');
        dom.form.appendChild(field);
      }
    });
  }

  function normalizeBirthInput(raw) {
    const digits = String(raw || '').replace(/\D/g, '').slice(0, 8);
    if (digits.length <= 2) return digits;
    if (digits.length <= 4) return `${digits.slice(0, 2)}.${digits.slice(2)}`;
    return `${digits.slice(0, 2)}.${digits.slice(2, 4)}.${digits.slice(4)}`;
  }

  function isValidPhone(value) {
    return /^\+?[1-9]\d{7,15}$/.test(String(value || '').replace(/[\s()\-]/g, ''));
  }

  function normalizePhone(value) {
    const digits = String(value || '').replace(/[^\d+]/g, '');
    if (!digits) return '';
    if (digits[0] === '+') return `+${digits.slice(1).replace(/\D/g, '')}`;
    return `+${digits.replace(/\D/g, '')}`;
  }

  function isValidTelegram(value) {
    return /^@?[A-Za-z0-9_]{5,32}$/.test(String(value || '').trim());
  }

  function normalizeTelegram(value) {
    const raw = String(value || '').trim().replace(/^@+/, '');
    return raw ? `@${raw}` : '';
  }

  function isAdultBirthdate(value) {
    const match = String(value || '').trim().match(/^(\d{2})\.(\d{2})\.(\d{4})$/);
    if (!match) return false;
    const day = Number(match[1]);
    const month = Number(match[2]) - 1;
    const year = Number(match[3]);
    const date = new Date(year, month, day);
    if (
      date.getFullYear() !== year ||
      date.getMonth() !== month ||
      date.getDate() !== day
    ) {
      return false;
    }

    const now = new Date();
    let age = now.getFullYear() - year;
    const m = now.getMonth() - month;
    if (m < 0 || (m === 0 && now.getDate() < day)) {
      age -= 1;
    }
    return age >= 18;
  }

  function validateForm(values) {
    if (!values.name || !values.email || !values.age || !values.phone || !values.contact_value) {
      return t('msg.required');
    }
    if (values.name.length < 2) {
      return t('msg.name');
    }
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/i.test(values.email)) {
      return t('msg.email');
    }
    if (!isAdultBirthdate(values.age)) {
      return t('msg.birth');
    }
    if (!isValidPhone(values.phone)) {
      return t('msg.phone');
    }

    if (values.preferred_contact === 'whatsapp') {
      if (!isValidPhone(values.contact_value)) {
        return t('msg.whatsapp');
      }
    } else if (!isValidTelegram(values.contact_value)) {
      return t('msg.telegram');
    }

    return '';
  }

  function populateConfigLinks(config) {
    const telegram = config.telegram_link || state.config.telegram_link;
    const bot = config.bot_link || null;
    const wa = config.whatsapp_link || null;

    state.config.telegram_link = telegram;
    state.config.bot_link = bot;
    state.config.whatsapp_link = wa;

    document.querySelectorAll('[data-telegram-link]').forEach((node) => {
      node.setAttribute('href', telegram || 'https://t.me/starflowcorp');
    });
  }

  async function loadConfig() {
    try {
      const response = await fetch('/api/config?project=starflow_corp', { cache: 'no-store' });
      if (!response.ok) {
        return;
      }
      const json = await response.json();
      populateConfigLinks(json || {});
    } catch (err) {
      // ignore network issues for config
    }
  }

  function revealOnScroll() {
    const nodes = document.querySelectorAll('.reveal');
    if (!nodes.length) return;
    if (prefersReducedMotion) {
      nodes.forEach((node) => node.classList.add('visible'));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const delay = Number(entry.target.getAttribute('data-reveal-delay') || '0');
            if (delay > 0) {
              entry.target.style.transitionDelay = `${delay}ms`;
            }
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.2 }
    );

    nodes.forEach((node) => observer.observe(node));
  }

  function initFaqAccordion() {
    const items = Array.from(document.querySelectorAll('[data-faq-item]'));
    if (!items.length) {
      return;
    }

    function setOpen(item, open) {
      item.classList.toggle('is-open', open);
      const trigger = item.querySelector('[data-faq-toggle]');
      const panel = item.querySelector('[data-faq-panel]');
      if (trigger) {
        trigger.setAttribute('aria-expanded', open ? 'true' : 'false');
      }
      if (panel) {
        panel.setAttribute('aria-hidden', open ? 'false' : 'true');
      }
    }

    let hasOpen = false;
    items.forEach((item, index) => {
      const shouldOpen = item.classList.contains('is-open') && !hasOpen;
      if (shouldOpen) {
        hasOpen = true;
      }
      setOpen(item, shouldOpen || (!hasOpen && index === 0));
      if (!hasOpen && index === 0) {
        hasOpen = true;
      }
    });

    items.forEach((item) => {
      const trigger = item.querySelector('[data-faq-toggle]');
      if (!trigger) {
        return;
      }
      trigger.addEventListener('click', () => {
        const isOpen = item.classList.contains('is-open');
        items.forEach((entry) => setOpen(entry, false));
        if (!isOpen) {
          setOpen(item, true);
        }
      });
    });
  }

  function animateCounters() {
    const counters = document.querySelectorAll('[data-count]');
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const node = entry.target;
          observer.unobserve(node);

          const target = Number(node.getAttribute('data-count')) || 0;
          const start = performance.now();
          const duration = 1200;

          function frame(now) {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            node.textContent = String(Math.round(target * eased));
            if (progress < 1) {
              requestAnimationFrame(frame);
            }
          }

          requestAnimationFrame(frame);
        });
      },
      { threshold: 0.5 }
    );

    counters.forEach((node) => observer.observe(node));
  }

  function initScrollProgress() {
    if (!dom.progressBar) {
      return;
    }

    const onScroll = () => {
      const doc = document.documentElement;
      const scrollTop = doc.scrollTop || document.body.scrollTop || 0;
      const height = Math.max(doc.scrollHeight - doc.clientHeight, 1);
      const progress = Math.min(100, Math.max(0, (scrollTop / height) * 100));
      dom.progressBar.style.width = `${progress}%`;
    };

    let ticking = false;
    const onScrollThrottled = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        onScroll();
        ticking = false;
      });
    };

    onScroll();
    window.addEventListener('scroll', onScrollThrottled, { passive: true });
    window.addEventListener('resize', onScrollThrottled);
  }

  function initHeroBars() {
    const bars = document.querySelectorAll('.lab-bar');
    if (!bars.length) return;

    const activate = () => {
      bars.forEach((bar) => {
        const value = Number(bar.getAttribute('data-bar') || '0');
        const fill = bar.querySelector('.lab-bar-track i');
        if (fill) {
          fill.style.width = `${Math.max(0, Math.min(100, value))}%`;
        }
      });
    };

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      activate();
      return;
    }

    const hero = dom.heroLab;
    if (!hero) {
      activate();
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            activate();
            observer.disconnect();
          }
        });
      },
      { threshold: 0.25 }
    );

    observer.observe(hero);
  }

  function initEarningsCalculator() {
    if (!dom.calcInterviews || !dom.calcCpa || !dom.calcWeekly || !dom.calcMonthly) {
      return;
    }

    const localeMap = {
      ru: 'ru-RU',
      en: 'en-US',
      pt: 'pt-BR',
      es: 'es-ES',
    };

    const update = () => {
      const interviews = Number(dom.calcInterviews.value || '0');
      const cpa = Number(dom.calcCpa.value || '0');
      const weekly = interviews * cpa;
      const monthly = weekly * 4;
      const locale = localeMap[state.lang] || 'en-US';
      const formatter = new Intl.NumberFormat(locale, {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 0,
      });

      if (dom.calcInterviewsValue) {
        dom.calcInterviewsValue.textContent = String(interviews);
      }
      if (dom.calcCpaValue) {
        dom.calcCpaValue.textContent = formatter.format(cpa);
      }
      dom.calcWeekly.textContent = formatter.format(weekly);
      dom.calcMonthly.textContent = formatter.format(monthly);
    };

    dom.calcInterviews.addEventListener('input', update);
    dom.calcCpa.addEventListener('input', update);
    state.calcUpdate = update;
    update();
  }

  function initPartnerFit() {
    const toggles = Array.from(dom.fitToggles || []);
    if (!toggles.length || !dom.fitScore || !dom.fitStatus) {
      return;
    }

    const totalWeight = toggles.reduce((sum, toggle) => {
      const value = Number(toggle.value || '0');
      return sum + (Number.isFinite(value) ? value : 0);
    }, 0);

    const resolveStatus = (percent) => {
      if (percent >= 75) return { key: 'fit.status.high', level: 'high' };
      if (percent >= 45) return { key: 'fit.status.mid', level: 'mid' };
      return { key: 'fit.status.low', level: 'low' };
    };

    const update = () => {
      const activeWeight = toggles.reduce((sum, toggle) => {
        if (!toggle.checked) return sum;
        const value = Number(toggle.value || '0');
        return sum + (Number.isFinite(value) ? value : 0);
      }, 0);
      const percent = totalWeight > 0 ? Math.round((activeWeight / totalWeight) * 100) : 0;
      const status = resolveStatus(percent);

      dom.fitScore.textContent = `${percent}%`;
      dom.fitStatus.textContent = t(status.key);
      dom.fitStatus.setAttribute('data-level', status.level);
    };

    toggles.forEach((toggle) => {
      toggle.addEventListener('change', update);
    });

    state.fitUpdate = update;
    update();
  }

  function initPlaybooks() {
    const buttons = Array.from(dom.playbookButtons || []);
    const panels = Array.from(dom.playbookPanels || []);
    if (!buttons.length || !panels.length) {
      return;
    }

    function setActive(id) {
      buttons.forEach((button) => {
        const active = button.getAttribute('data-playbook-btn') === id;
        button.classList.toggle('is-active', active);
        button.setAttribute('aria-selected', active ? 'true' : 'false');
      });

      panels.forEach((panel) => {
        const active = panel.getAttribute('data-playbook-panel') === id;
        panel.classList.toggle('is-active', active);
        panel.hidden = !active;
      });
    }

    buttons.forEach((button) => {
      button.addEventListener('click', () => {
        const id = button.getAttribute('data-playbook-btn');
        if (id) {
          setActive(id);
        }
      });
      button.addEventListener('keydown', (event) => {
        const currentIndex = buttons.indexOf(button);
        if (currentIndex < 0) return;
        if (event.key === 'ArrowRight') {
          event.preventDefault();
          const nextButton = buttons[(currentIndex + 1) % buttons.length];
          nextButton.focus();
          const id = nextButton.getAttribute('data-playbook-btn');
          if (id) setActive(id);
          return;
        }
        if (event.key === 'ArrowLeft') {
          event.preventDefault();
          const prevButton = buttons[(currentIndex - 1 + buttons.length) % buttons.length];
          prevButton.focus();
          const id = prevButton.getAttribute('data-playbook-btn');
          if (id) setActive(id);
          return;
        }
        if (event.key === 'Home') {
          event.preventDefault();
          const firstButton = buttons[0];
          firstButton.focus();
          const id = firstButton.getAttribute('data-playbook-btn');
          if (id) setActive(id);
          return;
        }
        if (event.key === 'End') {
          event.preventDefault();
          const lastButton = buttons[buttons.length - 1];
          lastButton.focus();
          const id = lastButton.getAttribute('data-playbook-btn');
          if (id) setActive(id);
        }
      });
    });

    const initial = buttons.find((button) => button.classList.contains('is-active')) || buttons[0];
    const initialId = initial ? initial.getAttribute('data-playbook-btn') : null;
    if (initialId) {
      setActive(initialId);
    }
  }

  function initTimelineFocus() {
    const items = Array.from(dom.timelineItems || []);
    if (!items.length) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          entry.target.classList.toggle('is-active', entry.isIntersecting && entry.intersectionRatio >= 0.45);
        });
      },
      { threshold: [0.2, 0.45, 0.75] }
    );

    items.forEach((item) => observer.observe(item));
  }

  async function submitForm(event) {
    event.preventDefault();
    if (!dom.form || !dom.submit) {
      return;
    }

    const data = new FormData(dom.form);
    const values = {
      name: String(data.get('name') || '').trim(),
      preferred_contact: String(data.get('preferred_contact') || 'telegram').trim().toLowerCase(),
      contact_value: String(data.get('contact_value') || '').trim(),
      email: String(data.get('email') || '').trim(),
      age: String(data.get('age') || '').trim(),
      phone: normalizePhone(String(data.get('phone') || '').trim()),
      website: String(data.get('website') || '').trim(),
      company: String(data.get('company') || '').trim(),
      project: PROJECT_KEY,
      site_lang: state.lang,
    };

    if (values.preferred_contact === 'telegram') {
      values.contact_value = normalizeTelegram(values.contact_value);
      values.telegram = values.contact_value;
      values.whatsapp = '';
    } else {
      values.contact_value = normalizePhone(values.contact_value);
      values.telegram = '';
      values.whatsapp = values.contact_value;
    }

    const validationError = validateForm(values);
    if (validationError) {
      trackGoal('starflow_apply_validation_error', { lang: state.lang });
      setStatus(validationError, 'error');
      dom.nextBox.hidden = true;
      return;
    }

    const payload = new URLSearchParams();
    Object.entries(values).forEach(([key, value]) => payload.set(key, value));

    dom.submit.disabled = true;
    setStatus(t('msg.sending'));
    dom.nextBox.hidden = true;

    try {
      const response = await fetch('/api/apply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        },
        body: payload.toString(),
      });

      const json = await response.json().catch(() => ({}));
      if (!response.ok || !json.ok) {
        trackGoal('starflow_apply_submit_error', { lang: state.lang, field: String(json.field || '') });
        setStatus(json.message || t('msg.error'), 'error');
        return;
      }

      trackGoal('starflow_apply_submit_success', { lang: state.lang });
      setStatus(json.message || t('msg.success'), 'success');

      const telegramLink = (json.next_links && json.next_links.telegram) || json.telegram_bot_link || state.config.bot_link;
      const whatsappLink = (json.next_links && json.next_links.whatsapp) || json.whatsapp_bot_link || state.config.whatsapp_link;

      if (!telegramLink && !whatsappLink) {
        setStatus(t('msg.nextMissing'), 'success');
        dom.nextBox.hidden = true;
        return;
      }

      if (telegramLink) {
        dom.nextTelegram.href = telegramLink;
        dom.nextTelegram.hidden = false;
        if (!dom.nextTelegram.dataset.goalBound) {
          dom.nextTelegram.dataset.goalBound = '1';
          dom.nextTelegram.addEventListener('click', () => {
            trackGoal('starflow_apply_open_telegram', { lang: state.lang });
          });
        }
      } else {
        dom.nextTelegram.hidden = true;
      }

      if (whatsappLink) {
        dom.nextWhatsapp.href = whatsappLink;
        dom.nextWhatsapp.hidden = false;
        if (!dom.nextWhatsapp.dataset.goalBound) {
          dom.nextWhatsapp.dataset.goalBound = '1';
          dom.nextWhatsapp.addEventListener('click', () => {
            trackGoal('starflow_apply_open_whatsapp', { lang: state.lang });
          });
        }
      } else {
        dom.nextWhatsapp.hidden = true;
      }

      dom.nextBox.hidden = false;
      dom.form.reset();
      dom.form.querySelector('input[name="project"]').value = PROJECT_KEY;
      dom.form.querySelector('input[name="site_lang"]').value = state.lang;
      if (dom.preferred) {
        dom.preferred.value = 'telegram';
      }
      updateContactPlaceholder();
    } catch (err) {
      trackGoal('starflow_apply_submit_error', { lang: state.lang });
      setStatus(t('msg.error'), 'error');
    } finally {
      dom.submit.disabled = false;
    }
  }

  function bindEvents() {
    if (dom.lang) {
      dom.lang.addEventListener('change', () => {
        setLanguage(dom.lang.value, true);
      });
    }

    if (dom.birth) {
      dom.birth.addEventListener('input', () => {
        dom.birth.value = normalizeBirthInput(dom.birth.value);
      });
    }

    if (dom.preferred) {
      dom.preferred.addEventListener('change', () => {
        updateContactPlaceholder();
      });
    }

    if (dom.form) {
      dom.form.addEventListener('submit', submitForm);
    }
  }

  function boot() {
    const yearNode = document.getElementById('year');
    if (yearNode) {
      yearNode.textContent = String(new Date().getFullYear());
    }

    initLoader();
    ensureHoneypotFields();
    applyI18n();
    bindEvents();
    initLanguageGate();
    revealOnScroll();
    initFaqAccordion();
    animateCounters();
    initScrollProgress();
    initHeroBars();
    initPartnerFit();
    initPlaybooks();
    initEarningsCalculator();
    initTimelineFocus();
    loadConfig();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
