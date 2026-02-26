(function () {
  'use strict';

  const LANG_STORAGE_KEY = 'starflow_lang_v2';
  const SUPPORTED_LANGS = ['en', 'pt', 'es'];
  const DEFAULT_LANG = 'en';
  const PROJECT_KEY = 'starflow_corp';

  const I18N = {
    en: {
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
      'faq.exp.l1': 'What experience do you have (social, outreach, ads)?',
      'faq.exp.l2': 'Are you ready to learn from our materials?',
      'faq.exp.l3': 'How much time can you dedicate?',
      'faq.mlm.q': 'Is this MLM / pyramid?',
      'faq.mlm.a': 'No. You pay nothing to join. No multi-level structure. You bring candidates, they pass interviews, you get paid.',
      'faq.mlm.l1': 'MLM: pay to join + build multi-level hierarchy.',
      'faq.mlm.l2': 'Here: zero investment, one level, payment for result.',
      'apply.overline': 'Application',
      'apply.title': 'Start as a partner',
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
      'faq.exp.l1': 'Qual experiência você já tem (social, outreach, ads)?',
      'faq.exp.l2': 'Está pronto para aprender com nossos materiais?',
      'faq.exp.l3': 'Quanto tempo pode dedicar?',
      'faq.mlm.q': 'Isso é MLM / pirâmide?',
      'faq.mlm.a': 'Não. Você não paga para entrar. Não há estrutura multinível. Você traz candidatos, eles passam entrevista, você recebe.',
      'faq.mlm.l1': 'MLM: paga entrada + constrói níveis.',
      'faq.mlm.l2': 'Aqui: zero investimento, um nível, pagamento por resultado.',
      'apply.overline': 'Aplicação',
      'apply.title': 'Comece como parceiro',
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
      'faq.exp.l1': '¿Qué experiencia tienes (social, outreach, ads)?',
      'faq.exp.l2': '¿Listo para aprender con nuestros materiales?',
      'faq.exp.l3': '¿Cuánto tiempo puedes dedicar?',
      'faq.mlm.q': '¿Es MLM / pirámide?',
      'faq.mlm.a': 'No. No pagas para entrar. No hay estructura multinivel. Traes candidatos, pasan entrevistas, cobras.',
      'faq.mlm.l1': 'MLM: pagas entrada + construyes niveles.',
      'faq.mlm.l2': 'Aquí: cero inversión, un nivel, pago por resultado.',
      'apply.overline': 'Aplicación',
      'apply.title': 'Empieza como partner',
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

  const state = {
    lang: getInitialLang(),
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
    preferred: document.getElementById('preferred-contact'),
    contactValue: document.getElementById('contact-value'),
    nextBox: document.getElementById('next-actions'),
    nextTelegram: document.getElementById('next-telegram'),
    nextWhatsapp: document.getElementById('next-whatsapp'),
  };

  function getInitialLang() {
    try {
      const stored = localStorage.getItem(LANG_STORAGE_KEY);
      if (SUPPORTED_LANGS.includes(stored)) {
        return stored;
      }
    } catch (err) {
      // ignore
    }
    return DEFAULT_LANG;
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

  function initStarfield() {
    const canvas = document.getElementById('star-canvas');
    if (!canvas || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let w = 0;
    let h = 0;
    let raf = null;
    const stars = [];
    const STAR_COUNT = 100;

    function resize() {
      w = window.innerWidth;
      h = window.innerHeight;
      canvas.width = Math.max(1, Math.floor(w * window.devicePixelRatio));
      canvas.height = Math.max(1, Math.floor(h * window.devicePixelRatio));
      canvas.style.width = `${w}px`;
      canvas.style.height = `${h}px`;
      ctx.setTransform(window.devicePixelRatio, 0, 0, window.devicePixelRatio, 0, 0);

      stars.length = 0;
      for (let i = 0; i < STAR_COUNT; i += 1) {
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h,
          z: 0.2 + Math.random() * 0.8,
          vx: -0.08 + Math.random() * 0.16,
          vy: 0.04 + Math.random() * 0.2,
          r: 0.4 + Math.random() * 1.8,
        });
      }
    }

    function draw() {
      ctx.clearRect(0, 0, w, h);

      for (const star of stars) {
        star.x += star.vx * star.z;
        star.y += star.vy * star.z;

        if (star.x < -5) star.x = w + 5;
        if (star.x > w + 5) star.x = -5;
        if (star.y < -5) star.y = h + 5;
        if (star.y > h + 5) star.y = -5;

        ctx.beginPath();
        ctx.fillStyle = `rgba(170, 205, 255, ${0.25 + star.z * 0.55})`;
        ctx.arc(star.x, star.y, star.r * star.z, 0, Math.PI * 2);
        ctx.fill();
      }

      raf = requestAnimationFrame(draw);
    }

    window.addEventListener('resize', resize);
    resize();
    draw();

    window.addEventListener('beforeunload', () => {
      if (raf) cancelAnimationFrame(raf);
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
      dom.lang.value = state.lang;
      dom.lang.addEventListener('change', () => {
        const value = SUPPORTED_LANGS.includes(dom.lang.value) ? dom.lang.value : DEFAULT_LANG;
        state.lang = value;
        persistLang(value);
        applyI18n();
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

    applyI18n();
    bindEvents();
    revealOnScroll();
    bindTilt();
    initCursorGlow();
    initHeroParallax();
    animateCounters();
    initStarfield();
    loadConfig();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
