(function () {
  'use strict';

  const LANG_STORAGE_KEY = 'starflow_lang_v2';
  const SUPPORTED_LANGS = ['ru', 'en', 'pt', 'es'];
  const DEFAULT_LANG = 'ru';
  const PROJECT_KEY = 'starflow_corp';

  const I18N = {
    ru: {
      'langGate.title': 'Выберите язык',
      'langGate.subtitle': 'Выберите язык интерфейса перед началом работы',
      'nav.partners': 'Типы партнёров',
      'nav.terms': 'Условия',
      'nav.flow': 'Партнёрский флоу',
      'nav.faq': 'FAQ',
      'nav.apply': 'Заявка',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Оставить заявку',
      'hero.overline': 'Партнёрская сеть для стриминговых компаний',
      'hero.title': 'Приводи людей.<br>Остальное закрываем мы.',
      'hero.lead': 'Арбитражные команды, колл-центры, агентства и соло-фрилансеры. Размер команды не важен. Важен только ваш результат в привлечении кандидатов.',
      'hero.signal': 'Активный оффер',
      'hero.signalMeta': 'Выплаты каждое воскресенье в USDT',
      'hero.bar1': 'Качество интервью',
      'hero.bar2': 'Поток операторов',
      'hero.bar3': 'Поток моделей',
      'hero.cardA.title': 'Еженедельное исполнение',
      'hero.cardA.text': 'Выплаты каждое воскресенье в USDT.',
      'hero.cardB.title': 'Работает любой источник',
      'hero.cardB.text': 'DM, outreach, boards, ads - KPI только результат.',
      'hero.line1': 'Таргет',
      'hero.line2': 'Job boards',
      'hero.line3': 'Рассылки',
      'hero.line4': 'Холодный outreach',
      'hero.line5': 'Direct DM',
      'hero.line6': 'Без лимитов по источникам',
      'kpi.years': 'лет в трафике',
      'kpi.max': 'максимум CPA за интервью',
      'kpi.weekly': 'цикл выплат',
      'partners.overline': 'Кого ищем',
      'partners.title': 'Портрет партнёра',
      'partners.arb.title': 'Арбитражная команда',
      'partners.arb.text': 'Умеют работать с креативами, воронками, конверсией и оптимизацией.',
      'partners.call.title': 'Колл-центр',
      'partners.call.text': 'Есть операторы на звонках весь день. Нужен только оффер и скрипт.',
      'partners.agency.title': 'Маркетинговое агентство',
      'partners.agency.text': 'Процессы лидогенерации уже выстроены и работают.',
      'partners.solo.title': 'Соло-фрилансер',
      'partners.solo.text': 'Самостоятельно запускает рекламу/аутрич и дает результат.',
      'partners.notice1': 'Формат не важен: команда из 50 человек или один специалист с ноутбуком.',
      'partners.notice2': 'Важно одно: вы умеете привлекать людей.',
      'terms.overline': 'Детали оффера',
      'terms.title': 'Как работает это предложение',
      'terms.whatWeDo.title': 'Что делаем мы',
      'terms.whatWeDo.text': 'Ищем девушек 18-27 на позиции стримерш и парней 18-30 на позиции модераторов. Компании платят нам за квалифицированные интервью.',
      'terms.partnerDoes.title': 'Что делает партнёр',
      'terms.partnerDoes.text': 'Вы приводите кандидатов на интервью любым источником: таргет, объявления, DM, рассылки, job boards, холодный outreach.',
      'terms.conditions.title': 'Условия',
      'terms.conditions.cpa': 'CPA модель: $20-40 за каждое успешное интервью',
      'terms.conditions.payout': 'Выплаты каждое воскресенье в USDT',
      'terms.conditions.limit': 'Без лимитов: больше кандидатов - больше доход',
      'terms.conditions.assets': 'Даём CRM, скрипты и материалы',
      'terms.geo.title': 'GEO',
      'terms.geo.text': 'Модели: Европа, LatAm. Операторы: Европа, LatAm, Азия.',
      'flow.overline': 'Партнёрский флоу',
      'flow.title': 'От трафика до выплаты',
      'flow.step1': 'Запускаете трафик из любого источника.',
      'flow.step2': 'Кандидаты доходят до этапа интервью.',
      'flow.step3': 'Квалифицированные интервью фиксируются в CRM.',
      'flow.step4': 'Получаете еженедельную выплату в USDT.',
      'faq.title': 'Частые вопросы',
      'faq.exp.q': 'У меня нет опыта',
      'faq.exp.a': 'Мы даём CRM и скрипты. Если умеете находить людей, разберётесь. Метод не важен, важен результат.',
      'faq.exp.follow': 'Уточните у партнёра:',
      'faq.exp.l1': 'Какой у вас опыт (соцсети, outreach, реклама)?',
      'faq.exp.l2': 'Готовы учиться по нашим материалам?',
      'faq.exp.l3': 'Сколько времени готовы уделять?',
      'faq.mlm.q': 'Это MLM / пирамида?',
      'faq.mlm.a': 'Нет. Вход бесплатный. Нет многоуровневой структуры. Вы приводите кандидатов, они проходят интервью, вы получаете оплату.',
      'faq.mlm.follow': 'Разница:',
      'faq.mlm.l1': 'MLM: оплата за вход + построение уровней.',
      'faq.mlm.l2': 'Здесь: ноль вложений, один уровень, оплата за результат.',
      'faq.team.q': 'Нужна большая команда?',
      'faq.team.a': 'Нет. Размер команды не важен: подойдёт как агентство из 50 человек, так и один специалист.',
      'faq.team.l1': 'Ключевое требование: умеете привлекать людей.',
      'faq.team.l2': 'Важен результат, а не количество людей в штате.',
      'faq.sources.q': 'Какие источники трафика разрешены?',
      'faq.sources.a': 'Любые, если приводят квалифицированных кандидатов на интервью.',
      'faq.sources.l1': 'Таргет, job boards, рассылки, DM, холодный outreach.',
      'faq.sources.l2': 'Метод не ограничен, KPI - качество и доходимость до интервью.',
      'faq.pay.q': 'Как устроены выплаты и поддержка?',
      'faq.pay.a': 'Вы получаете оплату по CPA за успешные интервью, а мы даём операционную поддержку с первого дня.',
      'faq.pay.l1': '$20-40 за каждое успешное интервью.',
      'faq.pay.l2': 'Выплаты каждое воскресенье в USDT.',
      'faq.pay.l3': 'Без лимитов по объёму.',
      'faq.pay.l4': 'Предоставляем CRM, скрипты и материалы.',
      'faq.geo.q': 'Какие GEO и типы кандидатов нужны?',
      'faq.geo.a': 'Работаем по чётким возрастным и региональным профилям.',
      'faq.geo.l1': 'Девушки 18-27 для стримерских ролей.',
      'faq.geo.l2': 'Парни 18-30 для ролей модерации.',
      'faq.geo.l3': 'Модели: Европа и LatAm. Операторы: Европа, LatAm и Азия.',
      'apply.overline': 'Заявка',
      'apply.title': 'Старт как партнёр',
      'apply.copy': 'Заполните короткую форму и продолжите в удобном мессенджере.',
      'apply.hint1': 'Без бюрократии',
      'apply.hint2': 'Прямой контакт с менеджером',
      'apply.hint3': 'Быстрый запуск со скриптами',
      'form.name': 'ФИО',
      'form.contact': 'Контактные данные',
      'form.contactPlaceholderTelegram': '@username',
      'form.contactPlaceholderWhatsapp': '+7 900 000 00 00',
      'form.email': 'Email для регистрации',
      'form.birth': 'Дата рождения',
      'form.phone': 'Номер телефона',
      'form.submit': 'Отправить заявку',
      'form.next': 'Продолжить в мессенджере',
      'form.telegram': 'Открыть Telegram',
      'form.whatsapp': 'Открыть WhatsApp',
      'msg.sending': 'Отправляем заявку...',
      'msg.success': 'Заявка успешно отправлена.',
      'msg.required': 'Заполните все обязательные поля.',
      'msg.name': 'Введите корректное ФИО.',
      'msg.email': 'Введите корректный email.',
      'msg.phone': 'Телефон должен быть в международном формате.',
      'msg.birth': 'Формат даты: ДД.ММ.ГГГГ и возраст 18+.',
      'msg.telegram': 'Формат Telegram: @username',
      'msg.whatsapp': 'WhatsApp должен быть в международном формате.',
      'msg.error': 'Не удалось отправить заявку. Попробуйте ещё раз.',
      'msg.nextMissing': 'Ссылки пока не настроены. Свяжитесь с менеджером в Telegram.',
    },
    en: {
      'langGate.title': 'Choose language',
      'langGate.subtitle': 'Select interface language before you continue',
      'nav.partners': 'Partner Types',
      'nav.terms': 'Terms',
      'nav.flow': 'Partner Flow',
      'nav.faq': 'FAQ',
      'nav.apply': 'Apply',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Apply',
      'hero.overline': 'Partner Network For Streaming Companies',
      'hero.title': 'Bring people.<br>We handle the rest.',
      'hero.lead': 'Media buyers, call-centers, agencies, solo freelancers. Team size does not matter. The only thing that matters is your ability to attract candidates.',
      'hero.signal': 'Live Offer Signal',
      'hero.signalMeta': 'Weekly payouts in USDT',
      'hero.bar1': 'Interview quality',
      'hero.bar2': 'Operator flow',
      'hero.bar3': 'Model flow',
      'hero.cardA.title': 'Weekly execution',
      'hero.cardA.text': 'Payout cycle every Sunday in USDT.',
      'hero.cardB.title': 'Any source works',
      'hero.cardB.text': 'DM, outreach, boards, ads - result is KPI.',
      'hero.line1': 'Target Ads',
      'hero.line2': 'Job Boards',
      'hero.line3': 'Mailing Lists',
      'hero.line4': 'Cold Outreach',
      'hero.line5': 'Direct DM',
      'hero.line6': 'No Source Limits',
      'kpi.years': 'years in traffic',
      'kpi.max': 'max CPA per interview',
      'kpi.weekly': 'payout cycle',
      'partners.overline': 'Who We Need',
      'partners.title': 'Partner profile',
      'partners.arb.title': 'Arbitrage Team',
      'partners.arb.text': 'Already knows creatives, funnels, conversion and optimization.',
      'partners.call.title': 'Call-Center',
      'partners.call.text': 'Has managers on calls all day. Needs only offer + script.',
      'partners.agency.title': 'Marketing Agency',
      'partners.agency.text': 'Leadgen processes are already built and running.',
      'partners.solo.title': 'Solo Freelancer',
      'partners.solo.text': 'Runs ads/outreach independently and ships results.',
      'partners.notice1': 'Format does not matter: 50 people team or one person with a laptop.',
      'partners.notice2': 'Only one thing matters: you can attract people.',
      'terms.overline': 'Offer Details',
      'terms.title': 'How this offer works',
      'terms.whatWeDo.title': 'What we do',
      'terms.whatWeDo.text': 'We find female candidates 18-27 for streamer positions and male candidates 18-30 for moderation roles. Streaming companies pay us for qualified interviews.',
      'terms.partnerDoes.title': 'What partner does',
      'terms.partnerDoes.text': 'You drive candidates to interviews by any source: ads, broadcasts, DM, mailing lists, job boards, cold outreach.',
      'terms.conditions.title': 'Conditions',
      'terms.conditions.cpa': 'CPA model: $20-40 per successful interview',
      'terms.conditions.payout': 'Payouts every Sunday in USDT',
      'terms.conditions.limit': 'No limits: bring more, earn more',
      'terms.conditions.assets': 'We provide CRM, scripts and materials',
      'terms.geo.title': 'GEO',
      'terms.geo.text': 'Models: Europe, LatAm. Operators: Europe, LatAm, Asia.',
      'flow.overline': 'Partner Flow',
      'flow.title': 'From traffic to payout',
      'flow.step1': 'You launch traffic from any source.',
      'flow.step2': 'Candidates reach interview stage.',
      'flow.step3': 'Qualified interviews are counted in CRM.',
      'flow.step4': 'You receive weekly payout in USDT.',
      'faq.title': 'Common objections',
      'faq.exp.q': 'I have no experience',
      'faq.exp.a': 'We provide CRM and scripts. If you know how to reach people, you will figure it out. Method does not matter, results do.',
      'faq.exp.follow': 'Clarify with partner:',
      'faq.exp.l1': 'What experience do you have (social, outreach, ads)?',
      'faq.exp.l2': 'Are you ready to learn from our materials?',
      'faq.exp.l3': 'How much time can you dedicate?',
      'faq.mlm.q': 'Is this MLM / pyramid?',
      'faq.mlm.a': 'No. You pay nothing to join. No multi-level structure. You bring candidates, they pass interviews, you get paid.',
      'faq.mlm.follow': 'Difference:',
      'faq.mlm.l1': 'MLM: pay to join + build multi-level hierarchy.',
      'faq.mlm.l2': 'Here: zero investment, one level, payment for result.',
      'faq.team.q': 'Do I need a big team?',
      'faq.team.a': 'No. Team size does not matter. A 50-person team and one freelancer are both valid formats.',
      'faq.team.l1': 'Key requirement: ability to attract people.',
      'faq.team.l2': 'Performance matters, not headcount.',
      'faq.sources.q': 'Which traffic sources are allowed?',
      'faq.sources.a': 'Any source is allowed if it brings qualified candidates to interviews.',
      'faq.sources.l1': 'Target ads, job boards, mailing lists, DM, cold outreach.',
      'faq.sources.l2': 'Method is flexible, final interview quality is the KPI.',
      'faq.pay.q': 'How do payout and support work?',
      'faq.pay.a': 'You get paid under CPA model for successful interviews, and we give operational support from day one.',
      'faq.pay.l1': '$20-40 per successful interview.',
      'faq.pay.l2': 'Payouts every Sunday in USDT.',
      'faq.pay.l3': 'No limits on volume.',
      'faq.pay.l4': 'CRM, scripts and materials are provided.',
      'faq.geo.q': 'What GEO and candidate types do you need?',
      'faq.geo.a': 'We operate with clear candidate profiles and regional focus.',
      'faq.geo.l1': 'Female candidates 18-27 for streamer roles.',
      'faq.geo.l2': 'Male candidates 18-30 for moderation roles.',
      'faq.geo.l3': 'Models: Europe + LatAm. Operators: Europe + LatAm + Asia.',
      'apply.overline': 'Application',
      'apply.title': 'Start as a partner',
      'apply.copy': 'Fill the short form and continue directly in messenger.',
      'apply.hint1': 'No bureaucracy',
      'apply.hint2': 'Direct manager contact',
      'apply.hint3': 'Fast launch with scripts',
      'form.name': 'Full name',
      'form.contact': 'Contact details',
      'form.contactPlaceholderTelegram': '@username',
      'form.contactPlaceholderWhatsapp': '+34 600 000 000',
      'form.email': 'Email for registration',
      'form.birth': 'Date of birth',
      'form.phone': 'Phone number',
      'form.submit': 'Send application',
      'form.next': 'Continue in messenger',
      'form.telegram': 'Open Telegram',
      'form.whatsapp': 'Open WhatsApp',
      'msg.sending': 'Sending application...',
      'msg.success': 'Application sent successfully.',
      'msg.required': 'Please fill in all required fields.',
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
      'nav.partners': 'Tipos de Parceiro',
      'nav.terms': 'Condições',
      'nav.flow': 'Fluxo do Parceiro',
      'nav.faq': 'FAQ',
      'nav.apply': 'Aplicar',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Aplicar',
      'hero.overline': 'Rede de Parceiros para Empresas de Streaming',
      'hero.title': 'Traga pessoas.<br>Nos cuidamos do resto.',
      'hero.lead': 'Mídia buyers, call-centers, agências e freelancers solo. Tamanho da equipe não importa. O que importa é sua capacidade de atrair candidatos.',
      'hero.signal': 'Sinal da Oferta',
      'hero.signalMeta': 'Pagamentos semanais em USDT',
      'hero.bar1': 'Qualidade da entrevista',
      'hero.bar2': 'Fluxo de operadores',
      'hero.bar3': 'Fluxo de modelos',
      'hero.cardA.title': 'Execução semanal',
      'hero.cardA.text': 'Pagamentos todo domingo em USDT.',
      'hero.cardB.title': 'Qualquer fonte funciona',
      'hero.cardB.text': 'DM, outreach, boards, ads - KPI é o resultado.',
      'hero.line1': 'Tráfego pago',
      'hero.line2': 'Job boards',
      'hero.line3': 'Listas de envio',
      'hero.line4': 'Outreach frio',
      'hero.line5': 'DM direto',
      'hero.line6': 'Sem limite de fontes',
      'kpi.years': 'anos com tráfego',
      'kpi.max': 'CPA máximo por entrevista',
      'kpi.weekly': 'ciclo de pagamento',
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
      'nav.partners': 'Tipos de Partner',
      'nav.terms': 'Condiciones',
      'nav.flow': 'Flujo del Partner',
      'nav.faq': 'FAQ',
      'nav.apply': 'Aplicar',
      'cta.telegram': 'Telegram',
      'cta.apply': 'Aplicar',
      'hero.overline': 'Red de Partners para Empresas de Streaming',
      'hero.title': 'Trae gente.<br>Nosotros hacemos el resto.',
      'hero.lead': 'Media buyers, call-centers, agencias y freelancers. El tamaño del equipo no importa. Lo único importante es atraer candidatos.',
      'hero.signal': 'Señal de Oferta',
      'hero.signalMeta': 'Pagos semanales en USDT',
      'hero.bar1': 'Calidad de entrevistas',
      'hero.bar2': 'Flujo de operadores',
      'hero.bar3': 'Flujo de modelos',
      'hero.cardA.title': 'Ejecución semanal',
      'hero.cardA.text': 'Pagos cada domingo en USDT.',
      'hero.cardB.title': 'Cualquier fuente funciona',
      'hero.cardB.text': 'DM, outreach, boards, ads - KPI es el resultado.',
      'hero.line1': 'Ads',
      'hero.line2': 'Job boards',
      'hero.line3': 'Mailings',
      'hero.line4': 'Outreach en frío',
      'hero.line5': 'DM directo',
      'hero.line6': 'Sin límite de fuentes',
      'kpi.years': 'años en tráfico',
      'kpi.max': 'CPA máximo por entrevista',
      'kpi.weekly': 'ciclo de pago',
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
    sourceChips: document.querySelectorAll('.source-ribbon span'),
    timelineItems: document.querySelectorAll('.timeline li'),
  };

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

  function applyI18n() {
    document.documentElement.lang = state.lang;
    if (dom.lang) {
      dom.lang.value = state.lang;
    }

    document.querySelectorAll('[data-i18n]').forEach((node) => {
      const key = node.getAttribute('data-i18n');
      const value = t(key);
      if (value.includes('<br>')) {
        node.innerHTML = value;
      } else {
        node.textContent = value;
      }
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach((node) => {
      const key = node.getAttribute('data-i18n-placeholder');
      node.setAttribute('placeholder', t(key));
    });

    if (dom.form) {
      const langInput = dom.form.querySelector('input[name="site_lang"]');
      if (langInput) {
        langInput.value = state.lang;
      }
    }

    updateContactPlaceholder();
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
    dom.langGate.hidden = false;
    document.body.classList.add('lang-gate-open');
  }

  function closeLangGate() {
    if (!dom.langGate) {
      return;
    }
    dom.langGate.hidden = true;
    document.body.classList.remove('lang-gate-open');
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

    if (!state.hasStoredLang) {
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

  function bindTilt() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return;
    }
    const cards = document.querySelectorAll('[data-tilt]');
    cards.forEach((card) => {
      card.addEventListener('pointermove', (event) => {
        const rect = card.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width;
        const y = (event.clientY - rect.top) / rect.height;
        const rotateY = (x - 0.5) * 12;
        const rotateX = (0.5 - y) * 10;
        card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
      });
      card.addEventListener('pointerleave', () => {
        card.style.transform = 'perspective(800px) rotateX(0deg) rotateY(0deg)';
      });
    });
  }

  function initCursorGlow() {
    const glow = document.getElementById('cursor-glow');
    if (!glow || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return;
    }
    let frameRequested = false;
    let targetX = window.innerWidth * 0.5;
    let targetY = window.innerHeight * 0.45;

    function apply() {
      frameRequested = false;
      const x = Math.max(0, Math.min(window.innerWidth, targetX));
      const y = Math.max(0, Math.min(window.innerHeight, targetY));
      document.documentElement.style.setProperty('--mx', `${x}px`);
      document.documentElement.style.setProperty('--my', `${y}px`);
    }

    function onMove(event) {
      targetX = event.clientX;
      targetY = event.clientY;
      if (!frameRequested) {
        frameRequested = true;
        requestAnimationFrame(apply);
      }
    }

    window.addEventListener('pointermove', onMove, { passive: true });
    apply();
  }

  function initHeroParallax() {
    const stage = document.querySelector('.hero-stage');
    if (!stage || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return;
    }
    const copy = document.querySelector('.hero-copy');

    stage.addEventListener('pointermove', (event) => {
      const rect = stage.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;
      stage.style.transform = `perspective(1000px) rotateY(${x * 5}deg) rotateX(${y * -4}deg)`;
      if (copy) {
        copy.style.transform = `translate3d(${x * 8}px, ${y * 8}px, 0)`;
      }
    });

    stage.addEventListener('pointerleave', () => {
      stage.style.transform = 'perspective(1000px) rotateY(0deg) rotateX(0deg)';
      if (copy) {
        copy.style.transform = 'translate3d(0,0,0)';
      }
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

  function initHeroLabParallax() {
    const lab = dom.heroLab;
    if (!lab || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return;
    }
    const panel = lab.querySelector('.signal-card');
    const cards = Array.from(lab.querySelectorAll('.mini-stat'));
    if (!panel && !cards.length) {
      return;
    }

    lab.addEventListener('pointermove', (event) => {
      const rect = lab.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;
      if (panel) {
        panel.style.transform = `translate3d(${x * 14}px, ${y * 14}px, 0)`;
      }
      cards.forEach((card, index) => {
        const scale = index === 0 ? 1 : -1;
        card.style.transform = `translate3d(${x * 11 * scale}px, ${y * 11 * scale}px, 0)`;
      });
    });

    lab.addEventListener('pointerleave', () => {
      if (panel) {
        panel.style.transform = '';
      }
      cards.forEach((card) => {
        card.style.transform = '';
      });
    });
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

  function initMagneticTargets() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return;
    }
    const targets = [
      ...Array.from(document.querySelectorAll('.hero .btn, .header-tools .btn')),
      ...Array.from(dom.sourceChips || []),
    ];
    targets.forEach((target) => {
      target.addEventListener('pointermove', (event) => {
        const rect = target.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - 0.5;
        const y = (event.clientY - rect.top) / rect.height - 0.5;
        target.style.transform = `translate3d(${x * 7}px, ${y * 7}px, 0)`;
      });
      target.addEventListener('pointerleave', () => {
        target.style.transform = '';
      });
    });
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
        setStatus(json.message || t('msg.error'), 'error');
        return;
      }

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
      } else {
        dom.nextTelegram.hidden = true;
      }

      if (whatsappLink) {
        dom.nextWhatsapp.href = whatsappLink;
        dom.nextWhatsapp.hidden = false;
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
    applyI18n();
    bindEvents();
    initLanguageGate();
    revealOnScroll();
    initFaqAccordion();
    animateCounters();
    initScrollProgress();
    initHeroBars();
    initTimelineFocus();
    loadConfig();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
