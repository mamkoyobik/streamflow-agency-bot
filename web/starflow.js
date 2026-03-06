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
      'nav.fit': 'Для кого',
      'nav.geos': 'Приоритет GEO',
      'nav.apply': 'Анкета',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Начать заявку',
      'mobile.menu': 'Меню',
      'mobile.close': 'Закрыть',
      'mobile.open': 'Открыть меню',
      'hero.eyebrow': 'B2B-партнёрская программа для команд с трафиком',
      'hero.title': 'CPA-оффер: подтверждённые интервью и еженедельные выплаты в USDT.',
      'hero.lead': 'Если у вас уже есть рабочий источник трафика, запуск идёт по прямой схеме: форма, проверка, онбординг и старт.',
      'hero.quick1.title': 'Кому подходит',
      'hero.quick1.text': 'Командам и соло-операторам с активными источниками трафика.',
      'hero.quick2.title': 'Как считаются выплаты',
      'hero.quick2.text': '$20-40 за подтверждённое интервью, выплаты каждую неделю.',
      'hero.quick3.title': 'Что делать сейчас',
      'hero.quick3.text': 'Заполнить короткую форму и перейти в мессенджер.',
      'hero.step1': 'Отправляете короткую форму',
      'hero.step2': 'Получаете онбординг и скрипты',
      'hero.step3': 'Доводите до интервью и получаете оплату',
      'hero.kpi1Value': '$20-40',
      'hero.kpi1': 'за подтверждённое интервью',
      'hero.kpi2Value': 'Еженедельно',
      'hero.kpi2': 'фиксированный цикл выплат в USDT',
      'hero.kpi3Value': 'Любой источник',
      'hero.kpi3': 'который вы умеете масштабировать',
      'hero.cardKicker': 'Быстрый self-check',
      'hero.cardTitle': 'Проверьте fit перед отправкой формы',
      'hero.cardGoodTitle': 'Подходит',
      'hero.cardBadTitle': 'Не подходит',
      'hero.card1': 'У вас уже есть трафик из рекламы, аутрича, job boards или рефералов.',
      'hero.card2': 'Вы готовы держать стабильный объём каждую неделю.',
      'hero.card3': 'Вам комфортно работать по скриптам и статусам CRM.',
      'hero.card4': 'Вы ищете фиксированную зарплату, а не performance-модель.',
      'hero.card5': 'У вас пока нет активного источника трафика.',
      'hero.card6': 'Вы не готовы работать по процессу и отчётности.',
      'hero.note': 'Если блок "Подходит" про вас, отправляйте заявку и продолжим в мессенджере.',
      'hero.summaryKicker': 'Сводка оффера',
      'hero.summaryTitle': 'Чёткая модель перед запуском',
      'hero.summary1': 'Подтверждённое интервью -> выплата.',
      'hero.summary2': '$20 старт, рост до $35-40 при качестве.',
      'hero.summary3': 'Выплаты по воскресеньям в USDT + бонус $700 за быстрый старт.',
      'offer.eyebrow': 'Условия оффера',
      'offer.title': 'Прозрачная модель без размытых условий',
      'offer.lead': 'Один KPI, фиксированный ритм выплат и понятный операционный процесс с первого дня.',
      'offer.card1.title': 'Подтверждённое интервью = оплачиваемое событие',
      'offer.card1.text': 'Оплата идёт за подтверждённые интервью, а не за размытый трафик или обещания без результата.',
      'offer.card2.title': 'Любой источник, который вы умеете вести',
      'offer.card2.text': 'Реклама, аутрич, job boards, прямые сообщения и рефералы подходят, если вы умеете держать объём.',
      'offer.card3.title': 'Операционный стек включён',
      'offer.card3.text': 'Вы получаете скрипты, видимость в CRM, поддержку менеджера и фиксированный цикл выплат в USDT.',
      'flow.eyebrow': 'Что дальше',
      'flow.title': 'После заявки путь запуска понятен по шагам',
      'flow.lead': 'Без неопределённости: проверка, онбординг, запуск и выплаты идут в одном рабочем цикле.',
      'flow.tab1': '1. Регистрация',
      'flow.tab2': '2. Онбординг',
      'flow.tab3': '3. Кандидаты',
      'flow.tab4': '4. Выплата',
      'flow.s1.title': 'Короткая заявка',
      'flow.s1.text': 'Вы отправляете форму и выбираете мессенджер, в котором продолжим общение.',
      'flow.s2.title': 'Проверка менеджером',
      'flow.s2.text': 'Мы сверяем fit, фиксируем ожидания и открываем путь в онбординг.',
      'flow.s3.title': 'Пакет запуска',
      'flow.s3.text': 'Вы получаете скрипты, логику CRM и рабочую точку контакта для ежедневной работы.',
      'flow.s4.title': 'Трафик и выплата',
      'flow.s4.text': 'Вы доводите кандидатов до подтверждённых интервью, а объём оплачивается еженедельно в USDT.',
      'fit.eyebrow': 'Для кого',
      'fit.title': 'Подавайте заявку, если ваша текущая работа уже выглядит так',
      'fit.c1': 'Вы уже работаете с рекламой, аутричем, job boards или рефералами.',
      'fit.c2': 'Вы можете держать трафик каждую неделю, а не время от времени.',
      'fit.c3': 'Вам нормально работать по скриптам и статусам CRM.',
      'fit.c4': 'Вы ищете performance-оффер, а не роль с фиксированной зарплатой.',
      'fit.score': 'После одобрения',
      'fit.resultTitle': 'Вы получаете готовый рабочий стек',
      'fit.resultLead': 'Скрипты, видимость в CRM, контакт менеджера и фиксированный еженедельный цикл выплат.',
      'fit.high': 'Высокий fit: можно запускаться сразу.',
      'fit.mid': 'Средний fit: выровняйте процесс и можно стартовать.',
      'fit.low': 'Низкий fit: сначала соберите базовую систему привлечения.',
      'form.eyebrow': 'Старт',
      'form.title': 'Начните партнёрскую заявку',
      'form.lead': 'Анкета занимает около двух минут. При fit вы сразу переходите в Telegram или WhatsApp для запуска.',
      'form.b1': 'Короткая форма только с теми полями, которые нужны для проверки',
      'form.b2': 'Один контактный путь, чтобы менеджер быстро вышел на связь',
      'form.b3': 'После отправки сразу переходите в мессенджер',
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
      'comp.startLabel': 'Стартовый уровень',
      'comp.goodLabel': 'Хорошее качество',
      'comp.topLabel': 'Топ-партнёры',
      'comp.perInterview': 'за подтверждённое интервью',
      'comp.kpiStart': 'Стартовая ставка за интервью',
      'comp.kpiTop': 'Диапазон для топ-партнёров',
      'comp.kpiBonus': 'Бонус за быстрый старт (50 в 1-й месяц)',
      'comp.cta': 'Готовы протестировать источник трафика с еженедельными выплатами?',
      'sticky.text': 'Можете запуститься уже на этой неделе',
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
      'nav.fit': 'Who it is for',
      'nav.geos': 'Priority GEOs',
      'nav.apply': 'Apply',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Start application',
      'mobile.menu': 'Menu',
      'mobile.close': 'Close',
      'mobile.open': 'Open menu',
      'hero.eyebrow': 'B2B partner program for traffic teams',
      'hero.title': 'CPA offer: approved interviews with weekly USDT payouts.',
      'hero.lead': 'If you already run at least one active traffic source, launch is direct: short form, review, onboarding, and operations.',
      'hero.quick1.title': 'Who this page is for',
      'hero.quick1.text': 'Teams and solo operators with active traffic sources.',
      'hero.quick2.title': 'How payouts work',
      'hero.quick2.text': '$20-40 per approved interview with weekly USDT payouts.',
      'hero.quick3.title': 'What to do now',
      'hero.quick3.text': 'Complete the short form and continue in messenger.',
      'hero.step1': 'Send the short form',
      'hero.step2': 'Get onboarding and scripts',
      'hero.step3': 'Drive interviews and get paid',
      'hero.kpi1Value': '$20-40',
      'hero.kpi1': 'per approved interview',
      'hero.kpi2Value': 'Weekly',
      'hero.kpi2': 'USDT payout rhythm',
      'hero.kpi3Value': 'Any source',
      'hero.kpi3': 'that you can scale',
      'hero.cardKicker': 'Quick self-check',
      'hero.cardTitle': 'Check fit before you submit the form',
      'hero.cardGoodTitle': 'Good fit',
      'hero.cardBadTitle': 'Not for this page',
      'hero.card1': 'You already run traffic from ads, outreach, job boards, or referrals.',
      'hero.card2': 'You can keep acquisition active every week.',
      'hero.card3': 'You are ready to work with scripts and CRM statuses.',
      'hero.card4': 'You are looking for a fixed salary job format.',
      'hero.card5': 'You do not have any active traffic source yet.',
      'hero.card6': 'You are not ready for process and reporting.',
      'hero.note': 'If the Good fit block matches your setup, send the form and continue in messenger.',
      'hero.summaryKicker': 'Offer summary',
      'hero.summaryTitle': 'Clear model before you launch',
      'hero.summary1': 'Approved interview -> payout.',
      'hero.summary2': '$20 start, up to $35-40 by quality.',
      'hero.summary3': 'Sunday payouts in USDT + $700 fast-start bonus.',
      'offer.eyebrow': 'Offer terms',
      'offer.title': 'Transparent model with no vague conditions',
      'offer.lead': 'One KPI, fixed payout rhythm, and a clear operating process from day one.',
      'offer.card1.title': 'Approved interview = paid event',
      'offer.card1.text': 'You get paid for approved interviews, not vague traffic volume or passive-income promises.',
      'offer.card2.title': 'Any source you can operate',
      'offer.card2.text': 'Ads, outreach, job boards, direct messaging, and referrals all work if you can scale them.',
      'offer.card3.title': 'Operating stack included',
      'offer.card3.text': 'You receive scripts, CRM visibility, manager support, and a fixed weekly USDT payout cycle.',
      'flow.eyebrow': 'What happens next',
      'flow.title': 'After application, launch follows a clear sequence',
      'flow.lead': 'No confusion: review, onboarding, traffic launch, and payout happen in one operating cycle.',
      'flow.tab1': '1. Register',
      'flow.tab2': '2. Onboard',
      'flow.tab3': '3. Bring candidates',
      'flow.tab4': '4. Get paid',
      'flow.s1.title': 'Short application',
      'flow.s1.text': 'You submit the form and choose the messenger where we can continue the conversation.',
      'flow.s2.title': 'Manager review',
      'flow.s2.text': 'We confirm fit, align expectations, and open the onboarding path.',
      'flow.s3.title': 'Launch pack',
      'flow.s3.text': 'You receive scripts, CRM logic, and the working contact point for daily operations.',
      'flow.s4.title': 'Traffic and payout',
      'flow.s4.text': 'You drive candidates to approved interviews, and volume is paid weekly in USDT.',
      'fit.eyebrow': 'Who it is for',
      'fit.title': 'Apply if your current setup already looks like this',
      'fit.c1': 'You already work with ads, outreach, job boards, or referrals.',
      'fit.c2': 'You can keep traffic running every week, not occasionally.',
      'fit.c3': 'You are comfortable following scripts and CRM statuses.',
      'fit.c4': 'You want a performance deal, not a fixed salary role.',
      'fit.score': 'After approval',
      'fit.resultTitle': 'You get the operating stack',
      'fit.resultLead': 'Scripts, CRM visibility, manager contact, and a fixed weekly payout cycle.',
      'fit.high': 'High fit: you can launch right now.',
      'fit.mid': 'Medium fit: align your process and launch fast.',
      'fit.low': 'Low fit: build a stable acquisition baseline first.',
      'form.eyebrow': 'Start',
      'form.title': 'Start the partner application',
      'form.lead': 'The form takes around two minutes. If there is fit, you continue directly in Telegram or WhatsApp.',
      'form.b1': 'Short form with only the fields needed for review',
      'form.b2': 'One contact path so manager can reach you fast',
      'form.b3': 'After submit you move straight to messenger',
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
      'comp.startLabel': 'Start level',
      'comp.goodLabel': 'Good quality',
      'comp.topLabel': 'Top partners',
      'comp.perInterview': 'per approved interview',
      'comp.kpiStart': 'Start rate per interview',
      'comp.kpiTop': 'Top partner range',
      'comp.kpiBonus': 'Fast-start bonus (50 in month 1)',
      'comp.cta': 'Ready to test your traffic source with weekly payouts?',
      'sticky.text': 'You can launch this week',
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
      'nav.fit': 'Para quem é',
      'nav.geos': 'GEOs prioritários',
      'nav.apply': 'Formulário',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Iniciar inscrição',
      'mobile.menu': 'Menu',
      'mobile.close': 'Fechar',
      'mobile.open': 'Abrir menu',
      'hero.eyebrow': 'Programa B2B para equipes com tráfego',
      'hero.title': 'Oferta CPA: entrevistas aprovadas com pagamentos semanais em USDT.',
      'hero.lead': 'Se você já opera ao menos uma fonte de tráfego ativa, o lançamento é direto: formulário curto, revisão, onboarding e operação.',
      'hero.quick1.title': 'Para quem é',
      'hero.quick1.text': 'Equipes e operadores solo com fontes de tráfego ativas.',
      'hero.quick2.title': 'Como o pagamento funciona',
      'hero.quick2.text': '$20-40 por entrevista aprovada, com pagamento semanal em USDT.',
      'hero.quick3.title': 'O que fazer agora',
      'hero.quick3.text': 'Preencher o formulário curto e continuar no mensageiro.',
      'hero.step1': 'Envie o formulário curto',
      'hero.step2': 'Receba onboarding e scripts',
      'hero.step3': 'Leve para entrevistas e receba',
      'hero.kpi1Value': '$20-40',
      'hero.kpi1': 'por entrevista aprovada',
      'hero.kpi2Value': 'Semanal',
      'hero.kpi2': 'ciclo fixo de pagamento em USDT',
      'hero.kpi3Value': 'Qualquer fonte',
      'hero.kpi3': 'que você consiga escalar',
      'hero.cardKicker': 'Auto-check rápido',
      'hero.cardTitle': 'Verifique o fit antes de enviar',
      'hero.cardGoodTitle': 'Bom fit',
      'hero.cardBadTitle': 'Não é para este cenário',
      'hero.card1': 'Você já roda tráfego via ads, outreach, job boards ou referrals.',
      'hero.card2': 'Você consegue manter aquisição ativa toda semana.',
      'hero.card3': 'Você está pronto para operar com scripts e status no CRM.',
      'hero.card4': 'Você procura um emprego com salário fixo.',
      'hero.card5': 'Você ainda não tem fonte de tráfego ativa.',
      'hero.card6': 'Você não quer seguir processo e reporte.',
      'hero.note': 'Se o bloco Bom fit descreve seu cenário, envie a inscrição e seguimos no mensageiro.',
      'hero.summaryKicker': 'Resumo da oferta',
      'hero.summaryTitle': 'Modelo claro antes do lançamento',
      'hero.summary1': 'Entrevista aprovada -> pagamento.',
      'hero.summary2': '$20 no início, até $35-40 com qualidade.',
      'hero.summary3': 'Pagamentos aos domingos em USDT + bônus de $700 por arranque rápido.',
      'offer.eyebrow': 'Termos da oferta',
      'offer.title': 'Modelo transparente sem condições vagas',
      'offer.lead': 'Um KPI, ritmo fixo de pagamento e processo operacional claro desde o primeiro dia.',
      'offer.card1.title': 'Entrevista aprovada = evento pago',
      'offer.card1.text': 'O pagamento acontece por entrevistas aprovadas, não por volume vago de tráfego ou promessa sem resultado.',
      'offer.card2.title': 'Qualquer fonte que você consiga operar',
      'offer.card2.text': 'Ads, outreach, job boards, mensagens diretas e referrals funcionam se você conseguir escalar.',
      'offer.card3.title': 'Stack operacional incluído',
      'offer.card3.text': 'Você recebe scripts, visibilidade no CRM, suporte do gerente e um ciclo fixo de pagamento semanal em USDT.',
      'flow.eyebrow': 'O que acontece depois',
      'flow.title': 'Após a inscrição, o lançamento segue uma sequência clara',
      'flow.lead': 'Sem dúvida: revisão, onboarding, tráfego e pagamento acontecem em um único ciclo operacional.',
      'flow.tab1': '1. Cadastro',
      'flow.tab2': '2. Onboarding',
      'flow.tab3': '3. Traga candidatos',
      'flow.tab4': '4. Receba',
      'flow.s1.title': 'Inscrição curta',
      'flow.s1.text': 'Você envia o formulário e escolhe o mensageiro para continuar a conversa.',
      'flow.s2.title': 'Revisão do gerente',
      'flow.s2.text': 'Confirmamos o fit, alinhamos expectativa e abrimos o onboarding.',
      'flow.s3.title': 'Pacote de lançamento',
      'flow.s3.text': 'Você recebe scripts, lógica do CRM e o ponto de contato operacional para o dia a dia.',
      'flow.s4.title': 'Tráfego e pagamento',
      'flow.s4.text': 'Você leva candidatos para entrevistas aprovadas, e o volume é pago semanalmente em USDT.',
      'fit.eyebrow': 'Para quem é',
      'fit.title': 'Aplique se sua operação atual já parece com isto',
      'fit.c1': 'Você já trabalha com ads, outreach, job boards ou referrals.',
      'fit.c2': 'Você consegue manter tráfego toda semana, não só ocasionalmente.',
      'fit.c3': 'Você está confortável em seguir scripts e status no CRM.',
      'fit.c4': 'Você procura um acordo por performance, não um cargo com salário fixo.',
      'fit.score': 'Após aprovação',
      'fit.resultTitle': 'Você recebe o stack operacional',
      'fit.resultLead': 'Scripts, visibilidade no CRM, contato do gerente e um ciclo fixo de pagamento semanal.',
      'fit.high': 'Fit alto: pode lançar agora.',
      'fit.mid': 'Fit médio: alinhe processos e inicie rápido.',
      'fit.low': 'Fit baixo: monte primeiro uma base estável de aquisição.',
      'form.eyebrow': 'Início',
      'form.title': 'Inicie a inscrição de parceiro',
      'form.lead': 'O formulário leva cerca de dois minutos. Havendo fit, você continua direto no Telegram ou WhatsApp.',
      'form.b1': 'Formulário curto apenas com os campos necessários para revisão',
      'form.b2': 'Um único canal de contato para o gerente falar rápido com você',
      'form.b3': 'Depois do envio, você segue direto para o mensageiro',
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
      'comp.startLabel': 'Nível inicial',
      'comp.goodLabel': 'Boa qualidade',
      'comp.topLabel': 'Parceiros top',
      'comp.perInterview': 'por entrevista aprovada',
      'comp.kpiStart': 'Taxa inicial por entrevista',
      'comp.kpiTop': 'Faixa dos parceiros top',
      'comp.kpiBonus': 'Bônus de arranque rápido (50 no 1º mês)',
      'comp.cta': 'Pronto para testar sua fonte de tráfego com pagamentos semanais?',
      'sticky.text': 'Você pode lançar ainda esta semana',
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
      'nav.fit': 'Para quién es',
      'nav.geos': 'GEOs prioritarios',
      'nav.apply': 'Solicitud',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Iniciar solicitud',
      'mobile.menu': 'Menú',
      'mobile.close': 'Cerrar',
      'mobile.open': 'Abrir menú',
      'hero.eyebrow': 'Programa B2B para equipos con tráfico',
      'hero.title': 'Oferta CPA: entrevistas aprobadas con pagos semanales en USDT.',
      'hero.lead': 'Si ya operas al menos una fuente de tráfico activa, el arranque es directo: formulario corto, revisión, onboarding y operación.',
      'hero.quick1.title': 'Para quién es',
      'hero.quick1.text': 'Equipos y operadores individuales con fuentes de tráfico activas.',
      'hero.quick2.title': 'Cómo funciona el pago',
      'hero.quick2.text': '$20-40 por entrevista aprobada, con pago semanal en USDT.',
      'hero.quick3.title': 'Qué hacer ahora',
      'hero.quick3.text': 'Completar el formulario corto y seguir en mensajería.',
      'hero.step1': 'Envía el formulario corto',
      'hero.step2': 'Recibe onboarding y scripts',
      'hero.step3': 'Lleva a entrevistas y cobra',
      'hero.kpi1Value': '$20-40',
      'hero.kpi1': 'por entrevista aprobada',
      'hero.kpi2Value': 'Semanal',
      'hero.kpi2': 'ritmo fijo de pago en USDT',
      'hero.kpi3Value': 'Cualquier fuente',
      'hero.kpi3': 'que puedas escalar',
      'hero.cardKicker': 'Auto-check rápido',
      'hero.cardTitle': 'Verifica el fit antes de enviar',
      'hero.cardGoodTitle': 'Buen fit',
      'hero.cardBadTitle': 'No es para este caso',
      'hero.card1': 'Ya operas tráfico por ads, outreach, job boards o referrals.',
      'hero.card2': 'Puedes mantener adquisición activa cada semana.',
      'hero.card3': 'Estás listo para trabajar con scripts y estados en CRM.',
      'hero.card4': 'Buscas un empleo con salario fijo.',
      'hero.card5': 'Todavía no tienes fuente de tráfico activa.',
      'hero.card6': 'No quieres trabajar con proceso y reporte.',
      'hero.note': 'Si el bloque Buen fit coincide con tu situación, envía la solicitud y seguimos en mensajería.',
      'hero.summaryKicker': 'Resumen de oferta',
      'hero.summaryTitle': 'Modelo claro antes de lanzar',
      'hero.summary1': 'Entrevista aprobada -> pago.',
      'hero.summary2': '$20 inicial, hasta $35-40 con calidad.',
      'hero.summary3': 'Pagos los domingos en USDT + bono de $700 por arranque rápido.',
      'offer.eyebrow': 'Términos de oferta',
      'offer.title': 'Modelo transparente sin condiciones difusas',
      'offer.lead': 'Un KPI, ritmo de pago fijo y proceso operativo claro desde el primer día.',
      'offer.card1.title': 'Entrevista aprobada = evento pagado',
      'offer.card1.text': 'Se paga por entrevistas aprobadas, no por volumen difuso de tráfico ni promesas sin resultado.',
      'offer.card2.title': 'Cualquier fuente que puedas operar',
      'offer.card2.text': 'Ads, outreach, job boards, mensajes directos y referrals sirven si puedes escalarlos.',
      'offer.card3.title': 'Stack operativo incluido',
      'offer.card3.text': 'Recibes scripts, visibilidad en CRM, soporte del manager y un ciclo fijo de pago semanal en USDT.',
      'flow.eyebrow': 'Qué pasa después',
      'flow.title': 'Tras la solicitud, el lanzamiento sigue una secuencia clara',
      'flow.lead': 'Sin dudas: revisión, onboarding, tráfico y pago ocurren dentro de un mismo ciclo operativo.',
      'flow.tab1': '1. Registro',
      'flow.tab2': '2. Onboarding',
      'flow.tab3': '3. Trae candidatos',
      'flow.tab4': '4. Cobro',
      'flow.s1.title': 'Solicitud corta',
      'flow.s1.text': 'Envías el formulario y eliges el mensajero para continuar la conversación.',
      'flow.s2.title': 'Revisión del manager',
      'flow.s2.text': 'Confirmamos el fit, alineamos expectativas y abrimos el onboarding.',
      'flow.s3.title': 'Paquete de lanzamiento',
      'flow.s3.text': 'Recibes scripts, lógica del CRM y el punto de contacto operativo para el día a día.',
      'flow.s4.title': 'Tráfico y pago',
      'flow.s4.text': 'Llevas candidatos a entrevistas aprobadas y el volumen se paga semanalmente en USDT.',
      'fit.eyebrow': 'Para quién es',
      'fit.title': 'Aplica si tu operación actual ya se parece a esto',
      'fit.c1': 'Ya trabajas con ads, outreach, job boards o referrals.',
      'fit.c2': 'Puedes mantener tráfico cada semana, no solo de forma ocasional.',
      'fit.c3': 'Te sientes cómodo siguiendo scripts y estados en CRM.',
      'fit.c4': 'Buscas un acuerdo por performance, no un puesto con salario fijo.',
      'fit.score': 'Tras la aprobación',
      'fit.resultTitle': 'Recibes el stack operativo',
      'fit.resultLead': 'Scripts, visibilidad en CRM, contacto del manager y un ciclo fijo de pago semanal.',
      'fit.high': 'Fit alto: puedes lanzar ahora mismo.',
      'fit.mid': 'Fit medio: alinea proceso y lanza rápido.',
      'fit.low': 'Fit bajo: primero construye una base estable de adquisición.',
      'form.eyebrow': 'Inicio',
      'form.title': 'Inicia la solicitud de partner',
      'form.lead': 'El formulario tarda unos dos minutos. Si hay fit, continúas directo en Telegram o WhatsApp.',
      'form.b1': 'Formulario corto solo con los datos necesarios para revisión',
      'form.b2': 'Un único canal de contacto para que el manager te escriba rápido',
      'form.b3': 'Después de enviar, pasas directo al mensajero',
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
      'comp.startLabel': 'Nivel inicial',
      'comp.goodLabel': 'Buena calidad',
      'comp.topLabel': 'Partners top',
      'comp.perInterview': 'por entrevista aprobada',
      'comp.kpiStart': 'Tarifa inicial por entrevista',
      'comp.kpiTop': 'Rango para partners top',
      'comp.kpiBonus': 'Bono de arranque rápido (50 en el mes 1)',
      'comp.cta': '¿Listo para probar tu fuente de tráfico con pagos semanales?',
      'sticky.text': 'Puedes lanzar esta semana',
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

  const EXTRA_I18N = {
    ru: {
      'meta.title': 'Starflow Inc. — Партнёрская программа',
      'meta.description': 'Приводите релевантных кандидатов, получайте $20-40 за подтверждённое интервью и выплаты каждое воскресенье в USDT.',
      'meta.ogDescription': 'Вы приводите кандидатов на подтверждённые интервью и получаете выплаты в USDT каждое воскресенье.',
      'lang.label': 'Язык',
      'comp.meta1.label': 'День выплат:',
      'comp.meta1.value': 'каждое воскресенье',
      'comp.meta2.label': 'Способ:',
      'comp.meta2.value': 'USDT (криптовалюта)',
      'comp.meta3.label': 'Бонус:',
      'comp.meta3.value': '$700 за 50 интервью в первый месяц',
      'comp.meta4.label': 'Лимиты:',
      'comp.meta4.value': 'нет',
      'geo.eyebrow': 'Приоритетные GEO',
      'geo.title': 'Выберите направление: модели или операторы/модераторы',
      'geo.lead': 'Переключайтесь по роли и запускайтесь там, где одобрения быстрее.',
      'geo.tab.models': 'Для моделей',
      'geo.tab.operators': 'Для операторов / модераторов',
      'geo.models.p1.title': '#1 Восточная Европа',
      'geo.models.p1.text': 'Венгрия, Румыния, Чехия, Польша',
      'geo.models.p2.title': '#2 Латинская Америка',
      'geo.models.p2.text': 'Бразилия, Аргентина, Мексика',
      'geo.operators.p1.title': '#1 Восточная Европа',
      'geo.operators.p1.text': 'Венгрия, Румыния, Чехия, Польша',
      'geo.operators.p2.title': '#2 Латинская Америка',
      'geo.operators.p2.text': 'Бразилия, Аргентина, Мексика',
      'geo.operators.p3.title': '#3 Азия',
      'geo.operators.p3.text': 'Филиппины, Индонезия, Таиланд',
      'geo.note': 'Остальные GEO рассматриваем индивидуально. Сильный источник = обсуждаем индивидуальные условия.',
      'persona.eyebrow': 'Кого мы ищем',
      'persona.title': 'Вы можете работать соло или командой',
      'persona.lead': 'Формат не важен: соло, небольшая команда или масштабная структура.',
      'persona.card1.title': 'Арбитражная / affiliate-команда',
      'persona.card1.text': 'Вы уже работаете с воронками, креативами, конверсией и оптимизацией.',
      'persona.card2.title': 'Колл-центр',
      'persona.card2.text': 'Ваша команда может звонить весь день. Нужен рабочий оффер и скрипты.',
      'persona.card3.title': 'Маркетинговое агентство',
      'persona.card3.text': 'У вас уже есть рабочие процессы лидогенерации.',
      'persona.card4.title': 'Фрилансер-одиночка',
      'persona.card4.text': 'Вы ведёте аутрич, DM, рекламу или трафик с job-board самостоятельно.',
      'qual.eyebrow': 'Квалификация',
      'qual.title': 'Зелёные и красные флаги до запуска',
      'qual.lead': 'Используйте это как быстрый операционный фильтр.',
      'qual.good.title': 'Зелёные флаги',
      'qual.good.1': 'Вы понимаете трафик, конверсию и лиды.',
      'qual.good.2': 'Вы можете показать кейсы или примеры.',
      'qual.good.3': 'У вас есть 2-3+ человека и возможность масштабироваться.',
      'qual.good.4': 'Вы работаете с Восточной Европой или LatAm и нужными языками.',
      'qual.good.5': 'Вы быстро отвечаете и готовы работать по скриптам.',
      'qual.good.6': 'Вы понимаете модель pay-per-result и не требуете аванс.',
      'qual.bad.title': 'Красные флаги',
      'qual.bad.1': 'Вы запрашиваете полное финансирование заранее.',
      'qual.bad.2': 'Вы не понимаете базовые термины по трафику.',
      'qual.bad.3': 'Вы обещаете нереальный объём без доказательств.',
      'qual.bad.4': 'Вы работаете только по СНГ/Россия GEO.',
      'qual.bad.5': 'Вы отказываетесь от скриптов и процесса.',
      'qual.bad.6': 'Вы пропадаете или отвечаете слишком медленно.',
      'qual.bad.7': 'Вы фокусируетесь на "гарантиях" до старта.',
      'questions.eyebrow': 'Скрипт интервью',
      'questions.title': '6 ключевых вопросов перед одобрением',
      'questions.lead': 'Эти шесть ответов определяют fit, скорость и потенциал выплат.',
      'questions.q1': 'Какой у вас бэкграунд (колл-центр, affiliate-маркетинг, рекрутинг)?',
      'questions.q2': 'Вы работаете соло или командой? Сколько человек?',
      'questions.q3': 'Какие источники трафика используете (DM, реклама, job-board, cold outreach)?',
      'questions.q4': 'На каких языках работаете?',
      'questions.q5': 'Какие GEO вы покрываете?',
      'questions.q6': 'Какие вопросы у вас есть по офферу?',
      'questions.why.title': 'Зачем это важно',
      'questions.why.1': 'Показывает ваш текущий операционный масштаб.',
      'questions.why.2': 'Быстро подтверждает качество источника и fit по GEO.',
      'questions.why.3': 'Сокращает время онбординга и ускоряет запуск.',
      'obj.eyebrow': 'Работа с возражениями',
      'obj.title': 'Чёткие ответы на два самых частых возражения',
      'obj.exp.title': '«У меня нет опыта»',
      'obj.exp.en': 'EN: We provide CRM and scripts. If you know how to reach people — you will figure it out. The method does not matter, results do.',
      'obj.exp.ru': 'RU: Мы даём CRM и скрипты. Если умеешь находить людей — разберёшься. Способ не важен, важен результат.',
      'obj.exp.1': 'Расскажите, какой у вас опыт: соцсети, аутрич или реклама.',
      'obj.exp.2': 'Подтвердите, что готовы учиться по процессу.',
      'obj.exp.3': 'Укажите, сколько времени готовы выделять в неделю.',
      'obj.mlm.title': '«Это MLM / пирамида?»',
      'obj.mlm.en': 'EN: No. You do not pay to join. There is no multi-level structure. You bring candidates, they complete interviews, you get paid.',
      'obj.mlm.ru': 'RU: Нет. Ты ничего не платишь за вход. Нет многоуровневой структуры. Приводишь кандидатов, они проходят интервью, ты получаешь оплату.',
      'obj.mlm.1': 'MLM = платный вход + многоуровневая структура.',
      'obj.mlm.2': 'Эта модель = ноль входных затрат + один уровень + оплата за результат.',
      'after.eyebrow': 'После регистрации',
      'after.title': 'Сначала вы получаете инструменты, потом запускаете трафик',
      'after.lead': 'После отправки формы нет тупиков: инструменты -> настройка -> первые кандидаты -> первая выплата.',
      'after.receive.title': 'Вы получаете',
      'after.receive.1': 'Доступ к CRM для учёта кандидатов',
      'after.receive.2': 'Скрипты общения с кандидатами',
      'after.receive.3': 'Требования к кандидатам',
      'after.receive.4': 'Telegram-канал поддержки',
      'after.steps.title': 'Ваши первые шаги',
      'after.steps.1': 'Изучить требования к кандидатам',
      'after.steps.2': 'Настроить источник трафика',
      'after.steps.3': 'Привести первых 5-10 кандидатов',
      'after.steps.4': 'Получить первую выплату в воскресенье',
      'faq.eyebrow': 'FAQ',
      'faq.title': 'Всё, что нужно знать перед стартом',
      'faq.q1': 'Сколько можно зарабатывать за одно интервью?',
      'faq.a1': 'Стартовая ставка $20. При стабильном качестве вы переходите на $25-30, а топ-партнёры выходят на $35-40 за подтверждённое интервью.',
      'faq.q2': 'Когда и как происходят выплаты?',
      'faq.a2': 'Выплаты происходят каждое воскресенье в USDT. Лимитов по объёму нет: чем больше подтверждённых интервью, тем выше доход.',
      'faq.q3': 'Какие GEO сейчас приоритетны?',
      'faq.a3': 'Для моделей: Восточная Европа и Латинская Америка. Для операторов/модераторов: Восточная Европа, Латинская Америка и Азия. Остальные GEO обсуждаются индивидуально.',
      'faq.q4': 'Что делать, если у вас нет опыта?',
      'faq.a4': 'Вы получаете CRM и скрипты. Если умеете привлекать людей, вы сможете запуститься. Важнее стабильный результат, а не метод.',
      'faq.q5': 'Это MLM или пирамида?',
      'faq.a5': 'Нет. Нет оплаты за вход и нет многоуровневой структуры. Вы приводите кандидатов, они проходят интервью, вы получаете оплату.',
      'faq.q6': 'Что вы получаете после регистрации?',
      'faq.a6': 'Вы получаете доступ к CRM, скрипты, требования и поддержку в Telegram. После этого запускаете трафик и выходите на первую выплату в воскресенье.',
      'form.contactTelegram': 'Telegram',
      'form.contactWhatsapp': 'WhatsApp',
      'footer.brand': 'Starflow Inc.'
    },
    en: {
      'meta.title': 'Starflow Inc. — Partner Recruiting Program',
      'meta.description': 'Bring qualified candidates, earn $20-40 per approved interview, get paid every Sunday in USDT.',
      'meta.ogDescription': 'You bring candidates to approved interviews. You get paid every Sunday in USDT.',
      'lang.label': 'Language',
      'comp.meta1.label': 'Payout day:',
      'comp.meta1.value': 'every Sunday',
      'comp.meta2.label': 'Method:',
      'comp.meta2.value': 'USDT (crypto)',
      'comp.meta3.label': 'Bonus:',
      'comp.meta3.value': '$700 if you make 50 interviews in the first month',
      'comp.meta4.label': 'Limits:',
      'comp.meta4.value': 'none',
      'geo.eyebrow': 'Priority GEOs',
      'geo.title': 'Choose your lane: Models or Operators/Moderators',
      'geo.lead': 'Switch by role and launch where approvals are fastest.',
      'geo.tab.models': 'For Models',
      'geo.tab.operators': 'For Operators / Moderators',
      'geo.models.p1.title': '#1 Eastern Europe',
      'geo.models.p1.text': 'Hungary, Romania, Czech Republic, Poland',
      'geo.models.p2.title': '#2 Latin America',
      'geo.models.p2.text': 'Brazil, Argentina, Mexico',
      'geo.operators.p1.title': '#1 Eastern Europe',
      'geo.operators.p1.text': 'Hungary, Romania, Czech Republic, Poland',
      'geo.operators.p2.title': '#2 Latin America',
      'geo.operators.p2.text': 'Brazil, Argentina, Mexico',
      'geo.operators.p3.title': '#3 Asia',
      'geo.operators.p3.text': 'Philippines, Indonesia, Thailand',
      'geo.note': 'Other GEOs are reviewed individually. Strong source means custom terms discussion.',
      'persona.eyebrow': 'Who we are looking for',
      'persona.title': 'You can work solo or with a team',
      'persona.lead': 'Format does not matter: solo, small team, or scaled operation.',
      'persona.card1.title': 'Arbitrage / affiliate team',
      'persona.card1.text': 'You already run funnels, creatives, conversion, and optimization.',
      'persona.card2.title': 'Call center',
      'persona.card2.text': 'Your team can call all day. You need a working offer and scripts.',
      'persona.card3.title': 'Marketing agency',
      'persona.card3.text': 'You already operate lead generation processes at scale.',
      'persona.card4.title': 'Solo freelancer',
      'persona.card4.text': 'You run outreach, DMs, ads, or job-board traffic independently.',
      'qual.eyebrow': 'Qualification',
      'qual.title': 'Green flags and red flags before launch',
      'qual.lead': 'Use this as a quick operating filter.',
      'qual.good.title': 'Green flags',
      'qual.good.1': 'You understand traffic, conversion, and leads.',
      'qual.good.2': 'You can show cases or examples.',
      'qual.good.3': 'You have 2-3+ people and can scale process.',
      'qual.good.4': 'You work with Eastern Europe or LatAm and relevant languages.',
      'qual.good.5': 'You respond fast and can follow scripts.',
      'qual.good.6': 'You understand pay-per-result and do not request upfront funding.',
      'qual.bad.title': 'Red flags',
      'qual.bad.1': 'You ask for full upfront financing.',
      'qual.bad.2': 'You do not understand basic traffic terms.',
      'qual.bad.3': 'You promise unrealistic volume without proof.',
      'qual.bad.4': 'You only work with CIS/Russia GEO.',
      'qual.bad.5': 'You refuse scripts and process.',
      'qual.bad.6': 'You disappear or reply too slowly.',
      'qual.bad.7': 'You focus on guarantees before starting work.',
      'questions.eyebrow': 'Discovery script',
      'questions.title': '6 key questions you should answer before approval',
      'questions.lead': 'These six answers define fit, speed, and payout potential.',
      'questions.q1': 'What is your background (call center, affiliate marketing, recruitment)?',
      'questions.q2': 'Do you work solo or with a team? How many people?',
      'questions.q3': 'What traffic sources do you use (DMs, ads, job boards, cold outreach)?',
      'questions.q4': 'What languages do you work with?',
      'questions.q5': 'What GEOs can you cover?',
      'questions.q6': 'What questions do you have about the offer?',
      'questions.why.title': 'Why this matters',
      'questions.why.1': 'You show your current operating scale.',
      'questions.why.2': 'You prove source quality and GEO fit quickly.',
      'questions.why.3': 'You reduce onboarding time and launch faster.',
      'obj.eyebrow': 'Objections handling',
      'obj.title': 'Clear answers to the two most common objections',
      'obj.exp.title': 'I have no experience',
      'obj.exp.en': 'EN: We provide CRM and scripts. If you know how to reach people, you will figure it out. The method does not matter, results do.',
      'obj.exp.ru': 'RU: We provide CRM and scripts. If you know how to find people, you will figure it out. The method does not matter, results do.',
      'obj.exp.1': 'Tell us your current experience: social, outreach, or ads.',
      'obj.exp.2': 'Confirm that you are ready to learn the process.',
      'obj.exp.3': 'Share how much time you can commit each week.',
      'obj.mlm.title': 'Is this MLM / pyramid?',
      'obj.mlm.en': 'EN: No. You do not pay to join. There is no multi-level structure. You bring candidates, they complete interviews, you get paid.',
      'obj.mlm.ru': 'RU: No. You do not pay to join. There is no multi-level structure. You bring candidates, they complete interviews, you get paid.',
      'obj.mlm.1': 'MLM = pay to enter + level structure.',
      'obj.mlm.2': 'This model = zero entry cost + one level + pay per result.',
      'after.eyebrow': 'After registration',
      'after.title': 'You get tools first, then you launch traffic',
      'after.lead': 'No dead ends after submit: tools, setup, first candidates, first payout.',
      'after.receive.title': 'You receive',
      'after.receive.1': 'CRM access to track candidates',
      'after.receive.2': 'Candidate communication scripts',
      'after.receive.3': 'Candidate requirements',
      'after.receive.4': 'Telegram support channel',
      'after.steps.title': 'Your first steps',
      'after.steps.1': 'Study candidate requirements',
      'after.steps.2': 'Set up your traffic source',
      'after.steps.3': 'Bring your first 5-10 candidates',
      'after.steps.4': 'Receive your first Sunday payout',
      'faq.eyebrow': 'FAQ',
      'faq.title': 'Everything you need before you start',
      'faq.q1': 'How much can you earn per interview?',
      'faq.a1': 'You start at $20. With stable quality you move to $25-30, and top partners reach $35-40 per approved interview.',
      'faq.q2': 'When and how do payouts work?',
      'faq.a2': 'Payouts are made every Sunday in USDT. There are no volume limits: the more approved interviews you deliver, the more you earn.',
      'faq.q3': 'Which GEOs are prioritized right now?',
      'faq.a3': 'For models: Eastern Europe and Latin America. For operators/moderators: Eastern Europe, Latin America, and Asia. Other GEOs are discussed individually.',
      'faq.q4': 'What if you have no experience?',
      'faq.a4': 'You get CRM and scripts. If you can attract people, you can launch. Your method matters less than consistent results.',
      'faq.q5': 'Is this MLM or a pyramid model?',
      'faq.a5': 'No. There is no entry payment and no multi-level structure. You bring candidates, they complete interviews, you get paid.',
      'faq.q6': 'What do you receive after registration?',
      'faq.a6': 'You receive CRM access, scripts, requirements, and Telegram support. Then you launch traffic and target your first payout on Sunday.',
      'form.contactTelegram': 'Telegram',
      'form.contactWhatsapp': 'WhatsApp',
      'footer.brand': 'Starflow Inc.'
    },
    pt: {
      'meta.title': 'Starflow Inc. — Programa de Parceria',
      'meta.description': 'Traga candidatos qualificados, ganhe $20-40 por entrevista aprovada e receba todo domingo em USDT.',
      'meta.ogDescription': 'Você traz candidatos para entrevistas aprovadas e recebe em USDT todo domingo.',
      'lang.label': 'Idioma',
      'comp.meta1.label': 'Dia de pagamento:',
      'comp.meta1.value': 'todo domingo',
      'comp.meta2.label': 'Método:',
      'comp.meta2.value': 'USDT (cripto)',
      'comp.meta3.label': 'Bônus:',
      'comp.meta3.value': '$700 se você fizer 50 entrevistas no primeiro mês',
      'comp.meta4.label': 'Limites:',
      'comp.meta4.value': 'não há',
      'geo.eyebrow': 'GEOs prioritários',
      'geo.title': 'Escolha sua faixa: Modelos ou Operadores/Moderadores',
      'geo.lead': 'Alterne por função e lance onde as aprovações são mais rápidas.',
      'geo.tab.models': 'Para Modelos',
      'geo.tab.operators': 'Para Operadores / Moderadores',
      'geo.models.p1.title': '#1 Europa Oriental',
      'geo.models.p1.text': 'Hungria, Romênia, República Tcheca, Polônia',
      'geo.models.p2.title': '#2 América Latina',
      'geo.models.p2.text': 'Brasil, Argentina, México',
      'geo.operators.p1.title': '#1 Europa Oriental',
      'geo.operators.p1.text': 'Hungria, Romênia, República Tcheca, Polônia',
      'geo.operators.p2.title': '#2 América Latina',
      'geo.operators.p2.text': 'Brasil, Argentina, México',
      'geo.operators.p3.title': '#3 Ásia',
      'geo.operators.p3.text': 'Filipinas, Indonésia, Tailândia',
      'geo.note': 'Outros GEOs são avaliados individualmente. Fonte forte significa discussão de termos customizados.',
      'persona.eyebrow': 'Quem buscamos',
      'persona.title': 'Você pode trabalhar solo ou com equipe',
      'persona.lead': 'O formato não importa: solo, equipe pequena ou operação escalada.',
      'persona.card1.title': 'Equipe de arbitragem / afiliados',
      'persona.card1.text': 'Você já opera funis, criativos, conversão e otimização.',
      'persona.card2.title': 'Call center',
      'persona.card2.text': 'Sua equipe liga o dia todo. Você precisa de oferta e scripts prontos.',
      'persona.card3.title': 'Agência de marketing',
      'persona.card3.text': 'Você já opera processos de geração de leads em escala.',
      'persona.card4.title': 'Freelancer solo',
      'persona.card4.text': 'Você opera outreach, DMs, anúncios ou tráfego de job boards de forma independente.',
      'qual.eyebrow': 'Qualificação',
      'qual.title': 'Sinais verdes e vermelhos antes do lançamento',
      'qual.lead': 'Use isso como filtro operacional rápido.',
      'qual.good.title': 'Sinais verdes',
      'qual.good.1': 'Você entende tráfego, conversão e leads.',
      'qual.good.2': 'Você consegue mostrar cases ou exemplos.',
      'qual.good.3': 'Você tem 2-3+ pessoas e consegue escalar processo.',
      'qual.good.4': 'Você trabalha com Europa Oriental ou LatAm e idiomas relevantes.',
      'qual.good.5': 'Você responde rápido e segue scripts.',
      'qual.good.6': 'Você entende pagamento por resultado e não exige adiantamento.',
      'qual.bad.title': 'Sinais vermelhos',
      'qual.bad.1': 'Você pede financiamento total adiantado.',
      'qual.bad.2': 'Você não entende termos básicos de tráfego.',
      'qual.bad.3': 'Você promete volume irreal sem prova.',
      'qual.bad.4': 'Você trabalha apenas com GEO CIS/Rússia.',
      'qual.bad.5': 'Você recusa scripts e processo.',
      'qual.bad.6': 'Você some ou responde muito devagar.',
      'qual.bad.7': 'Você foca em garantias antes de iniciar.',
      'questions.eyebrow': 'Script de descoberta',
      'questions.title': '6 perguntas-chave antes da aprovação',
      'questions.lead': 'Essas respostas definem fit, velocidade e potencial de pagamento.',
      'questions.q1': 'Qual seu background (call center, affiliate marketing, recrutamento)?',
      'questions.q2': 'Você trabalha solo ou em equipe? Quantas pessoas?',
      'questions.q3': 'Quais fontes de tráfego você usa (DM, anúncios, job boards, cold outreach)?',
      'questions.q4': 'Com quais idiomas você trabalha?',
      'questions.q5': 'Quais GEOs você cobre?',
      'questions.q6': 'Que dúvidas você tem sobre a oferta?',
      'questions.why.title': 'Por que isso importa',
      'questions.why.1': 'Mostra sua escala operacional atual.',
      'questions.why.2': 'Comprova rápido a qualidade da fonte e fit de GEO.',
      'questions.why.3': 'Reduz tempo de onboarding e acelera o lançamento.',
      'obj.eyebrow': 'Tratamento de objeções',
      'obj.title': 'Respostas claras para as duas objeções mais comuns',
      'obj.exp.title': 'Não tenho experiência',
      'obj.exp.en': 'EN: We provide CRM and scripts. If you know how to reach people, you will figure it out. The method does not matter, results do.',
      'obj.exp.ru': 'RU: Nós fornecemos CRM e scripts. Se você sabe encontrar pessoas, você consegue. O método não importa, o resultado importa.',
      'obj.exp.1': 'Informe sua experiência atual: social, outreach ou anúncios.',
      'obj.exp.2': 'Confirme que você está pronto para aprender o processo.',
      'obj.exp.3': 'Diga quanto tempo pode dedicar por semana.',
      'obj.mlm.title': 'Isso é MLM / pirâmide?',
      'obj.mlm.en': 'EN: No. You do not pay to join. There is no multi-level structure. You bring candidates, they complete interviews, you get paid.',
      'obj.mlm.ru': 'RU: Não. Você não paga para entrar. Não existe estrutura multinível. Você traz candidatos, eles completam entrevistas, você recebe.',
      'obj.mlm.1': 'MLM = pagar para entrar + estrutura em níveis.',
      'obj.mlm.2': 'Este modelo = custo de entrada zero + um nível + pagamento por resultado.',
      'after.eyebrow': 'Após o registro',
      'after.title': 'Você recebe ferramentas primeiro e depois lança o tráfego',
      'after.lead': 'Sem beco sem saída após envio: ferramentas, setup, primeiros candidatos e primeiro pagamento.',
      'after.receive.title': 'Você recebe',
      'after.receive.1': 'Acesso ao CRM para rastrear candidatos',
      'after.receive.2': 'Scripts de comunicação com candidatos',
      'after.receive.3': 'Requisitos dos candidatos',
      'after.receive.4': 'Canal de suporte no Telegram',
      'after.steps.title': 'Seus primeiros passos',
      'after.steps.1': 'Estudar os requisitos dos candidatos',
      'after.steps.2': 'Configurar sua fonte de tráfego',
      'after.steps.3': 'Trazer os primeiros 5-10 candidatos',
      'after.steps.4': 'Receber o primeiro pagamento no domingo',
      'faq.eyebrow': 'FAQ',
      'faq.title': 'Tudo que você precisa antes de começar',
      'faq.q1': 'Quanto você pode ganhar por entrevista?',
      'faq.a1': 'Você começa em $20. Com qualidade estável, sobe para $25-30 e parceiros top chegam a $35-40 por entrevista aprovada.',
      'faq.q2': 'Quando e como funcionam os pagamentos?',
      'faq.a2': 'Pagamentos são feitos todo domingo em USDT. Não há limite de volume: quanto mais entrevistas aprovadas você entrega, mais ganha.',
      'faq.q3': 'Quais GEOs têm prioridade agora?',
      'faq.a3': 'Para modelos: Europa Oriental e América Latina. Para operadores/moderadores: Europa Oriental, América Latina e Ásia. Outros GEOs são discutidos individualmente.',
      'faq.q4': 'E se você não tiver experiência?',
      'faq.a4': 'Você recebe CRM e scripts. Se consegue atrair pessoas, consegue lançar. O método importa menos que resultado consistente.',
      'faq.q5': 'Isso é MLM ou pirâmide?',
      'faq.a5': 'Não. Não existe pagamento de entrada nem estrutura multinível. Você traz candidatos, eles completam entrevistas e você recebe.',
      'faq.q6': 'O que você recebe após o registro?',
      'faq.a6': 'Você recebe acesso ao CRM, scripts, requisitos e suporte no Telegram. Depois lança tráfego e busca o primeiro pagamento no domingo.',
      'form.contactTelegram': 'Telegram',
      'form.contactWhatsapp': 'WhatsApp',
      'footer.brand': 'Starflow Inc.'
    },
    es: {
      'meta.title': 'Starflow Inc. — Programa de Partners',
      'meta.description': 'Trae candidatos cualificados, gana $20-40 por entrevista aprobada y cobra cada domingo en USDT.',
      'meta.ogDescription': 'Traes candidatos a entrevistas aprobadas y cobras en USDT cada domingo.',
      'lang.label': 'Idioma',
      'comp.meta1.label': 'Día de pago:',
      'comp.meta1.value': 'cada domingo',
      'comp.meta2.label': 'Método:',
      'comp.meta2.value': 'USDT (cripto)',
      'comp.meta3.label': 'Bono:',
      'comp.meta3.value': '$700 si haces 50 entrevistas en el primer mes',
      'comp.meta4.label': 'Límites:',
      'comp.meta4.value': 'no hay',
      'geo.eyebrow': 'GEOs prioritarios',
      'geo.title': 'Elige tu ruta: Modelos u Operadores/Moderadores',
      'geo.lead': 'Cambia por rol y lanza donde las aprobaciones son más rápidas.',
      'geo.tab.models': 'Para Modelos',
      'geo.tab.operators': 'Para Operadores / Moderadores',
      'geo.models.p1.title': '#1 Europa del Este',
      'geo.models.p1.text': 'Hungría, Rumanía, República Checa, Polonia',
      'geo.models.p2.title': '#2 Latinoamérica',
      'geo.models.p2.text': 'Brasil, Argentina, México',
      'geo.operators.p1.title': '#1 Europa del Este',
      'geo.operators.p1.text': 'Hungría, Rumanía, República Checa, Polonia',
      'geo.operators.p2.title': '#2 Latinoamérica',
      'geo.operators.p2.text': 'Brasil, Argentina, México',
      'geo.operators.p3.title': '#3 Asia',
      'geo.operators.p3.text': 'Filipinas, Indonesia, Tailandia',
      'geo.note': 'Otros GEOs se revisan de forma individual. Fuente fuerte significa discusión de términos personalizados.',
      'persona.eyebrow': 'A quién buscamos',
      'persona.title': 'Puedes trabajar en solitario o con equipo',
      'persona.lead': 'El formato no importa: solo, equipo pequeño u operación escalada.',
      'persona.card1.title': 'Equipo de arbitraje / afiliados',
      'persona.card1.text': 'Ya operas funnels, creatividades, conversión y optimización.',
      'persona.card2.title': 'Call center',
      'persona.card2.text': 'Tu equipo puede llamar todo el día. Necesitas una oferta funcional y scripts.',
      'persona.card3.title': 'Agencia de marketing',
      'persona.card3.text': 'Ya operas procesos de generación de leads a escala.',
      'persona.card4.title': 'Freelancer individual',
      'persona.card4.text': 'Gestionas outreach, DMs, anuncios o tráfico de job boards de forma independiente.',
      'qual.eyebrow': 'Calificación',
      'qual.title': 'Señales verdes y rojas antes del lanzamiento',
      'qual.lead': 'Úsalo como filtro operativo rápido.',
      'qual.good.title': 'Señales verdes',
      'qual.good.1': 'Entiendes tráfico, conversión y leads.',
      'qual.good.2': 'Puedes mostrar casos o ejemplos.',
      'qual.good.3': 'Tienes 2-3+ personas y puedes escalar el proceso.',
      'qual.good.4': 'Trabajas con Europa del Este o LatAm y con idiomas relevantes.',
      'qual.good.5': 'Respondes rápido y puedes seguir scripts.',
      'qual.good.6': 'Entiendes el pago por resultado y no pides adelantos.',
      'qual.bad.title': 'Señales rojas',
      'qual.bad.1': 'Pides financiación total por adelantado.',
      'qual.bad.2': 'No entiendes términos básicos de tráfico.',
      'qual.bad.3': 'Prometes volumen irreal sin pruebas.',
      'qual.bad.4': 'Solo trabajas con GEO CIS/Rusia.',
      'qual.bad.5': 'Rechazas scripts y proceso.',
      'qual.bad.6': 'Desapareces o respondes demasiado lento.',
      'qual.bad.7': 'Te enfocas en garantías antes de empezar.',
      'questions.eyebrow': 'Script de discovery',
      'questions.title': '6 preguntas clave antes de la aprobación',
      'questions.lead': 'Estas seis respuestas definen fit, velocidad y potencial de pago.',
      'questions.q1': '¿Cuál es tu background (call center, affiliate marketing, reclutamiento)?',
      'questions.q2': '¿Trabajas solo o con equipo? ¿Cuántas personas?',
      'questions.q3': '¿Qué fuentes de tráfico usas (DM, ads, job boards, cold outreach)?',
      'questions.q4': '¿Con qué idiomas trabajas?',
      'questions.q5': '¿Qué GEOs puedes cubrir?',
      'questions.q6': '¿Qué preguntas tienes sobre la oferta?',
      'questions.why.title': 'Por qué importa',
      'questions.why.1': 'Muestra tu escala operativa actual.',
      'questions.why.2': 'Demuestra rápido calidad de fuente y fit de GEO.',
      'questions.why.3': 'Reduce el tiempo de onboarding y acelera el lanzamiento.',
      'obj.eyebrow': 'Manejo de objeciones',
      'obj.title': 'Respuestas claras a las dos objeciones más comunes',
      'obj.exp.title': 'No tengo experiencia',
      'obj.exp.en': 'EN: We provide CRM and scripts. If you know how to reach people, you will figure it out. The method does not matter, results do.',
      'obj.exp.ru': 'RU: Damos CRM y scripts. Si sabes encontrar personas, podrás arrancar. El método no importa, importa el resultado.',
      'obj.exp.1': 'Cuéntanos tu experiencia actual: social, outreach o ads.',
      'obj.exp.2': 'Confirma que estás listo para aprender el proceso.',
      'obj.exp.3': 'Comparte cuánto tiempo puedes dedicar por semana.',
      'obj.mlm.title': '¿Esto es MLM / pirámide?',
      'obj.mlm.en': 'EN: No. You do not pay to join. There is no multi-level structure. You bring candidates, they complete interviews, you get paid.',
      'obj.mlm.ru': 'RU: No. No pagas por entrar. No hay estructura multinivel. Traes candidatos, completan entrevistas y cobras.',
      'obj.mlm.1': 'MLM = pagar por entrar + estructura por niveles.',
      'obj.mlm.2': 'Este modelo = costo de entrada cero + un nivel + pago por resultado.',
      'after.eyebrow': 'Después del registro',
      'after.title': 'Primero recibes herramientas, luego lanzas tráfico',
      'after.lead': 'Sin callejones sin salida tras enviar: herramientas, configuración, primeros candidatos y primer pago.',
      'after.receive.title': 'Recibes',
      'after.receive.1': 'Acceso al CRM para seguimiento de candidatos',
      'after.receive.2': 'Scripts de comunicación con candidatos',
      'after.receive.3': 'Requisitos de candidatos',
      'after.receive.4': 'Canal de soporte en Telegram',
      'after.steps.title': 'Tus primeros pasos',
      'after.steps.1': 'Estudiar los requisitos de candidatos',
      'after.steps.2': 'Configurar tu fuente de tráfico',
      'after.steps.3': 'Traer tus primeros 5-10 candidatos',
      'after.steps.4': 'Recibir tu primer pago el domingo',
      'faq.eyebrow': 'FAQ',
      'faq.title': 'Todo lo que necesitas antes de empezar',
      'faq.q1': '¿Cuánto puedes ganar por entrevista?',
      'faq.a1': 'Empiezas en $20. Con calidad estable subes a $25-30 y los partners top llegan a $35-40 por entrevista aprobada.',
      'faq.q2': '¿Cuándo y cómo funcionan los pagos?',
      'faq.a2': 'Los pagos se hacen cada domingo en USDT. No hay límites de volumen: cuanto más entrevistas aprobadas entregues, más ganas.',
      'faq.q3': '¿Qué GEOs son prioridad ahora?',
      'faq.a3': 'Para modelos: Europa del Este y Latinoamérica. Para operadores/moderadores: Europa del Este, Latinoamérica y Asia. Otros GEOs se discuten individualmente.',
      'faq.q4': '¿Qué pasa si no tienes experiencia?',
      'faq.a4': 'Recibes CRM y scripts. Si puedes atraer personas, puedes lanzar. El método importa menos que resultados consistentes.',
      'faq.q5': '¿Esto es MLM o pirámide?',
      'faq.a5': 'No. No hay pago de entrada ni estructura multinivel. Traes candidatos, completan entrevistas y cobras.',
      'faq.q6': '¿Qué recibes después del registro?',
      'faq.a6': 'Recibes acceso al CRM, scripts, requisitos y soporte en Telegram. Luego lanzas tráfico y apuntas a tu primer pago del domingo.',
      'form.contactTelegram': 'Telegram',
      'form.contactWhatsapp': 'WhatsApp',
      'footer.brand': 'Starflow Inc.'
    }
  };

  Object.keys(EXTRA_I18N).forEach((lang) => {
    I18N[lang] = Object.assign({}, I18N[lang] || {}, EXTRA_I18N[lang]);
  });

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

    qsa('[data-i18n-meta]').forEach((node) => {
      const key = node.getAttribute('data-i18n-meta');
      const value = t(key, lang);
      if (node.tagName === 'META') {
        node.setAttribute('content', value);
      } else {
        node.textContent = value;
      }
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

  function initStepper() {
    const root = qs('[data-stepper]');
    if (!root) {
      return;
    }

    const tabs = qsa('[data-step-target]', root);
    const panels = qsa('[data-step-panel]', root);
    if (!tabs.length || !panels.length) {
      return;
    }

    const activate = (target, moveFocus) => {
      const stepId = String(target || tabs[0].getAttribute('data-step-target') || '');
      tabs.forEach((tab) => {
        const active = tab.getAttribute('data-step-target') === stepId;
        tab.classList.toggle('is-active', active);
        tab.setAttribute('aria-selected', active ? 'true' : 'false');
        tab.tabIndex = active ? 0 : -1;
        if (active && moveFocus) {
          tab.focus();
        }
      });

      panels.forEach((panel) => {
        const active = panel.getAttribute('data-step-panel') === stepId;
        panel.hidden = !active;
      });
    };

    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => {
        activate(tab.getAttribute('data-step-target'), false);
      });

      tab.addEventListener('keydown', (event) => {
        if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft' && event.key !== 'Home' && event.key !== 'End') {
          return;
        }

        event.preventDefault();
        let nextIndex = index;
        if (event.key === 'ArrowRight') {
          nextIndex = (index + 1) % tabs.length;
        } else if (event.key === 'ArrowLeft') {
          nextIndex = (index - 1 + tabs.length) % tabs.length;
        } else if (event.key === 'Home') {
          nextIndex = 0;
        } else if (event.key === 'End') {
          nextIndex = tabs.length - 1;
        }
        const nextTab = tabs[nextIndex];
        activate(nextTab.getAttribute('data-step-target'), true);
      });
    });

    activate(tabs[0].getAttribute('data-step-target'), false);
  }

  function initGeoSwitcher() {
    const root = qs('[data-geo-switcher]');
    if (!root) {
      return;
    }

    const tabs = qsa('[data-geo-target]', root);
    const panels = qsa('[data-geo-panel]', root);
    if (!tabs.length || !panels.length) {
      return;
    }

    const activate = (target) => {
      const value = String(target || tabs[0].getAttribute('data-geo-target') || '');
      tabs.forEach((tab) => {
        const active = tab.getAttribute('data-geo-target') === value;
        tab.classList.toggle('is-active', active);
        tab.setAttribute('aria-selected', active ? 'true' : 'false');
      });

      panels.forEach((panel) => {
        panel.hidden = panel.getAttribute('data-geo-panel') !== value;
      });
    };

    tabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        activate(tab.getAttribute('data-geo-target'));
      });
    });

    activate(tabs[0].getAttribute('data-geo-target'));
  }

  function initFaqAccordion() {
    const root = qs('[data-faq]');
    if (!root) {
      return;
    }

    const items = qsa('.sfw-faq__item', root);
    if (!items.length) {
      return;
    }

    const updatePanelHeight = (item, open) => {
      const panel = qs('[data-faq-panel]', item);
      if (!panel) {
        return;
      }
      panel.style.maxHeight = open ? panel.scrollHeight + 'px' : '0px';
    };

    const setOpen = (item, open) => {
      const trigger = qs('[data-faq-trigger]', item);
      if (!trigger) {
        return;
      }

      item.classList.toggle('is-open', open);
      trigger.setAttribute('aria-expanded', open ? 'true' : 'false');
      updatePanelHeight(item, open);
    };

    items.forEach((item, index) => {
      const trigger = qs('[data-faq-trigger]', item);
      if (!trigger) {
        return;
      }

      const shouldStartOpen = item.classList.contains('is-open') || index === 0;
      setOpen(item, shouldStartOpen);

      trigger.addEventListener('click', () => {
        const isOpen = item.classList.contains('is-open');
        items.forEach((other) => setOpen(other, false));
        setOpen(item, !isOpen);
      });
    });

    window.addEventListener('resize', () => {
      items.forEach((item) => {
        if (item.classList.contains('is-open')) {
          updatePanelHeight(item, true);
        }
      });
    });
  }

  function initStickyCta() {
    const sticky = qs('.sfw-sticky-cta');
    const hero = qs('.sfw-hero');
    if (!sticky || !hero) {
      return;
    }

    let rafId = 0;
    const update = () => {
      rafId = 0;
      const threshold = Math.max(260, hero.offsetHeight * 0.55);
      const visible = window.scrollY > threshold;
      sticky.classList.toggle('is-visible', visible);
    };

    const onScroll = () => {
      if (!rafId) {
        rafId = window.requestAnimationFrame(update);
      }
    };

    update();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
  }

  function initHeroInteractive() {
    const hero = qs('.sfw-hero__grid');
    if (!hero) {
      return;
    }

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) {
      return;
    }

    let rafId = 0;
    let targetX = 74;
    let targetY = 34;
    let targetShiftX = 0;
    let targetShiftY = 0;

    const apply = () => {
      rafId = 0;
      hero.style.setProperty('--sfw-hero-spot-x', targetX.toFixed(2) + '%');
      hero.style.setProperty('--sfw-hero-spot-y', targetY.toFixed(2) + '%');
      hero.style.setProperty('--sfw-hero-parallax-x', targetShiftX.toFixed(2) + 'px');
      hero.style.setProperty('--sfw-hero-parallax-y', targetShiftY.toFixed(2) + 'px');
    };

    const requestApply = () => {
      if (!rafId) {
        rafId = window.requestAnimationFrame(apply);
      }
    };

    hero.addEventListener('pointermove', (event) => {
      const rect = hero.getBoundingClientRect();
      if (!rect.width || !rect.height) {
        return;
      }

      const relX = (event.clientX - rect.left) / rect.width;
      const relY = (event.clientY - rect.top) / rect.height;

      targetX = 48 + relX * 42;
      targetY = 18 + relY * 56;
      targetShiftX = (relX - 0.5) * 18;
      targetShiftY = (relY - 0.5) * 16;
      requestApply();
    });

    hero.addEventListener('pointerleave', () => {
      targetX = 74;
      targetY = 34;
      targetShiftX = 0;
      targetShiftY = 0;
      requestApply();
    });
  }

  function initScrollProgress() {
    const bar = qs('#sfw-scroll-progress-bar');
    if (!bar) {
      return;
    }

    let rafId = 0;
    const update = () => {
      rafId = 0;
      const doc = document.documentElement;
      const scrollTop = Math.max(0, window.scrollY || doc.scrollTop || 0);
      const max = Math.max(1, doc.scrollHeight - window.innerHeight);
      const ratio = Math.min(1, scrollTop / max);
      bar.style.width = (ratio * 100).toFixed(2) + '%';
    };

    const onScroll = () => {
      if (!rafId) {
        rafId = window.requestAnimationFrame(update);
      }
    };

    update();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
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
      safeStorageSet(STORAGE_KEY, state.lang);
    }
    closeGate();

    onLangChange(state.lang);
  }

  async function syncLinks() {
    if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
      return;
    }

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
    initScrollProgress();
    initReveal();
    initStepper();
    initGeoSwitcher();
    initFaqAccordion();
    initHeroInteractive();
    initStickyCta();
    initMobileMenu();
    initLangGate(state, onLangChange);
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
