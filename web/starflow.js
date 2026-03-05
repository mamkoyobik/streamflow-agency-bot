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
      'nav.apply': 'Анкета',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Начать заявку',
      'mobile.menu': 'Меню',
      'mobile.close': 'Закрыть',
      'hero.eyebrow': 'Партнёрская программа для команд с трафиком',
      'hero.title': 'Приводите кандидатов на интервью. Получайте еженедельные выплаты в USDT.',
      'hero.lead': 'Starflow — партнёрская сеть для команд и соло-операторов, у которых уже есть источники трафика. Вы приводите кандидатов. Мы даём скрипты, CRM и менеджерскую поддержку.',
      'hero.step1': 'Отправляете короткую форму',
      'hero.step2': 'Получаете онбординг и скрипты',
      'hero.step3': 'Доводите до интервью и получаете оплату',
      'hero.kpi1Value': '$20-40',
      'hero.kpi1': 'за подтверждённое интервью',
      'hero.kpi2Value': 'Еженедельно',
      'hero.kpi2': 'фиксированный цикл выплат в USDT',
      'hero.kpi3Value': 'Любой источник',
      'hero.kpi3': 'который вы умеете масштабировать',
      'hero.cardKicker': 'По сути',
      'hero.cardTitle': 'Как реально устроен оффер',
      'hero.card1': 'Вы приводите кандидатов из рекламы, аутрича, job boards, DM или рефералов.',
      'hero.card2': 'Мы даём рабочую систему: скрипты, CRM-логику и связь с менеджером.',
      'hero.card3': 'Один KPI, один цикл выплат, без размытой партнёрской схемы.',
      'hero.note': 'Лучше всего подходит партнёрам, у которых уже есть хотя бы один рабочий канал привлечения.',
      'offer.eyebrow': 'Условия оффера',
      'offer.title': 'Всё завязано на один понятный бизнес-результат',
      'offer.lead': 'Это прямой партнёрский оффер: подтверждённые интервью, еженедельные выплаты и единый рабочий стек с первого дня.',
      'offer.card1.title': 'Подтверждённое интервью = оплачиваемое событие',
      'offer.card1.text': 'Оплата идёт за подтверждённые интервью, а не за размытый трафик или обещания без результата.',
      'offer.card2.title': 'Любой источник, который вы умеете вести',
      'offer.card2.text': 'Реклама, аутрич, job boards, прямые сообщения и рефералы подходят, если вы умеете держать объём.',
      'offer.card3.title': 'Операционный стек включён',
      'offer.card3.text': 'Вы получаете скрипты, видимость в CRM, поддержку менеджера и фиксированный цикл выплат в USDT.',
      'flow.eyebrow': 'Что дальше',
      'flow.title': 'После формы путь запуска максимально прямой',
      'flow.lead': 'Никакой неопределённости. Проверка, онбординг, запуск трафика и выплата идут по одной простой схеме.',
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
      'form.lead': 'Форма занимает около двух минут. Если есть fit, вы сразу переходите в Telegram или WhatsApp.',
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
      'nav.apply': 'Apply',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Start application',
      'mobile.menu': 'Menu',
      'mobile.close': 'Close',
      'hero.eyebrow': 'Partner program for acquisition teams',
      'hero.title': 'Bring qualified candidates to interviews. Get paid weekly in USDT.',
      'hero.lead': 'Starflow is a partner network for teams and solo operators who already have traffic sources. You drive acquisition. We provide scripts, CRM, and manager support.',
      'hero.step1': 'Send the short form',
      'hero.step2': 'Get onboarding and scripts',
      'hero.step3': 'Drive interviews and get paid',
      'hero.kpi1Value': '$20-40',
      'hero.kpi1': 'per approved interview',
      'hero.kpi2Value': 'Weekly',
      'hero.kpi2': 'USDT payout rhythm',
      'hero.kpi3Value': 'Any source',
      'hero.kpi3': 'that you can scale',
      'hero.cardKicker': 'Straight to the point',
      'hero.cardTitle': 'What the deal actually looks like',
      'hero.card1': 'You bring candidates from ads, outreach, job boards, direct messaging, or referrals.',
      'hero.card2': 'We provide the operating system: scripts, CRM workflow, and manager support.',
      'hero.card3': 'One KPI, one payout rhythm, no vague affiliate logic.',
      'hero.note': 'Best fit for partners with at least one working traffic source.',
      'offer.eyebrow': 'Offer terms',
      'offer.title': 'Everything is tied to one clear business result',
      'offer.lead': 'This is a direct partner deal: approved interviews, weekly payouts, and one operating stack from day one.',
      'offer.card1.title': 'Approved interview = paid event',
      'offer.card1.text': 'You get paid for approved interviews, not vague traffic volume or passive-income promises.',
      'offer.card2.title': 'Any source you can operate',
      'offer.card2.text': 'Ads, outreach, job boards, direct messaging, and referrals all work if you can scale them.',
      'offer.card3.title': 'Operating stack included',
      'offer.card3.text': 'You receive scripts, CRM visibility, manager support, and a fixed weekly USDT payout cycle.',
      'flow.eyebrow': 'What happens next',
      'flow.title': 'After the form, the launch path is straightforward',
      'flow.lead': 'You are not left guessing. Review, onboarding, traffic launch, and payout follow one simple sequence.',
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
      'form.lead': 'The form takes about two minutes. If there is fit, you continue directly in Telegram or WhatsApp.',
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
      'nav.apply': 'Formulário',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Iniciar inscrição',
      'mobile.menu': 'Menu',
      'mobile.close': 'Fechar',
      'hero.eyebrow': 'Programa de parceria para equipes com tráfego',
      'hero.title': 'Leve candidatos qualificados para entrevistas. Receba pagamentos semanais em USDT.',
      'hero.lead': 'Starflow é uma rede de parceiros para equipes e operadores solo que já possuem fontes de tráfego. Você traz os candidatos. Nós entregamos scripts, CRM e suporte do gerente.',
      'hero.step1': 'Envie o formulário curto',
      'hero.step2': 'Receba onboarding e scripts',
      'hero.step3': 'Leve para entrevistas e receba',
      'hero.kpi1Value': '$20-40',
      'hero.kpi1': 'por entrevista aprovada',
      'hero.kpi2Value': 'Semanal',
      'hero.kpi2': 'ciclo fixo de pagamento em USDT',
      'hero.kpi3Value': 'Qualquer fonte',
      'hero.kpi3': 'que você consiga escalar',
      'hero.cardKicker': 'Direto ao ponto',
      'hero.cardTitle': 'Como a parceria funciona na prática',
      'hero.card1': 'Você traz candidatos de ads, outreach, job boards, mensagens diretas ou referrals.',
      'hero.card2': 'Nós entregamos o sistema operacional: scripts, fluxo no CRM e suporte do gerente.',
      'hero.card3': 'Um KPI, um ritmo de pagamento, sem lógica vaga de afiliado.',
      'hero.note': 'Melhor encaixe para parceiros que já têm ao menos uma fonte de tráfego funcionando.',
      'offer.eyebrow': 'Termos da oferta',
      'offer.title': 'Tudo está ligado a um resultado de negócio claro',
      'offer.lead': 'É uma parceria direta: entrevistas aprovadas, pagamentos semanais e um stack operacional único desde o primeiro dia.',
      'offer.card1.title': 'Entrevista aprovada = evento pago',
      'offer.card1.text': 'O pagamento acontece por entrevistas aprovadas, não por volume vago de tráfego ou promessa sem resultado.',
      'offer.card2.title': 'Qualquer fonte que você consiga operar',
      'offer.card2.text': 'Ads, outreach, job boards, mensagens diretas e referrals funcionam se você conseguir escalar.',
      'offer.card3.title': 'Stack operacional incluído',
      'offer.card3.text': 'Você recebe scripts, visibilidade no CRM, suporte do gerente e um ciclo fixo de pagamento semanal em USDT.',
      'flow.eyebrow': 'O que acontece depois',
      'flow.title': 'Depois do formulário, o caminho de lançamento é simples',
      'flow.lead': 'Sem adivinhação. Revisão, onboarding, lançamento de tráfego e pagamento seguem uma única sequência.',
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
      'form.lead': 'O formulário leva cerca de dois minutos. Se houver fit, você continua direto no Telegram ou WhatsApp.',
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
      'nav.apply': 'Solicitud',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Iniciar solicitud',
      'mobile.menu': 'Menú',
      'mobile.close': 'Cerrar',
      'hero.eyebrow': 'Programa de partners para equipos con tráfico',
      'hero.title': 'Lleva candidatos calificados a entrevistas. Cobra pagos semanales en USDT.',
      'hero.lead': 'Starflow es una red de partners para equipos y operadores individuales que ya tienen fuentes de tráfico. Tú atraes candidatos. Nosotros entregamos scripts, CRM y soporte del manager.',
      'hero.step1': 'Envía el formulario corto',
      'hero.step2': 'Recibe onboarding y scripts',
      'hero.step3': 'Lleva a entrevistas y cobra',
      'hero.kpi1Value': '$20-40',
      'hero.kpi1': 'por entrevista aprobada',
      'hero.kpi2Value': 'Semanal',
      'hero.kpi2': 'ritmo fijo de pago en USDT',
      'hero.kpi3Value': 'Cualquier fuente',
      'hero.kpi3': 'que puedas escalar',
      'hero.cardKicker': 'Directo al punto',
      'hero.cardTitle': 'Cómo funciona realmente el acuerdo',
      'hero.card1': 'Tú llevas candidatos desde ads, outreach, job boards, mensajes directos o referrals.',
      'hero.card2': 'Nosotros entregamos el sistema operativo: scripts, flujo en CRM y soporte del manager.',
      'hero.card3': 'Un KPI, un ritmo de pago, sin lógica difusa de afiliado.',
      'hero.note': 'Encaja mejor con partners que ya tienen al menos una fuente de tráfico funcionando.',
      'offer.eyebrow': 'Términos de oferta',
      'offer.title': 'Todo está conectado a un resultado de negocio claro',
      'offer.lead': 'Es un acuerdo directo de partnership: entrevistas aprobadas, pagos semanales y un stack operativo único desde el primer día.',
      'offer.card1.title': 'Entrevista aprobada = evento pagado',
      'offer.card1.text': 'Se paga por entrevistas aprobadas, no por volumen difuso de tráfico ni promesas sin resultado.',
      'offer.card2.title': 'Cualquier fuente que puedas operar',
      'offer.card2.text': 'Ads, outreach, job boards, mensajes directos y referrals sirven si puedes escalarlos.',
      'offer.card3.title': 'Stack operativo incluido',
      'offer.card3.text': 'Recibes scripts, visibilidad en CRM, soporte del manager y un ciclo fijo de pago semanal en USDT.',
      'flow.eyebrow': 'Qué pasa después',
      'flow.title': 'Después del formulario, la ruta de lanzamiento es directa',
      'flow.lead': 'Sin adivinar. Revisión, onboarding, lanzamiento de tráfico y pago siguen una sola secuencia clara.',
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
    initReveal();
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
