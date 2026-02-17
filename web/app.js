document.body.classList.add('preload');
window.addEventListener('DOMContentLoaded', () => {
  requestAnimationFrame(() => {
    document.body.classList.add('is-ready');
    document.body.classList.remove('preload');
  });
});

function normalizeInitialScrollPosition() {
  if ('scrollRestoration' in history) {
    history.scrollRestoration = 'manual';
  }
  if (window.location.hash) {
    history.replaceState(null, '', `${window.location.pathname}${window.location.search}`);
  }
  const resetToTop = () => {
    window.scrollTo(0, 0);
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
    requestAnimationFrame(() => {
      window.scrollTo(0, 0);
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
    });
  };
  window.addEventListener('load', () => {
    resetToTop();
    if ('scrollRestoration' in history) {
      history.scrollRestoration = 'auto';
    }
  });
  window.addEventListener('DOMContentLoaded', () => {
    resetToTop();
  });
  window.addEventListener('pageshow', () => {
    resetToTop();
  });
}

normalizeInitialScrollPosition();

function initScrollProgress() {
  const update = () => {
    const doc = document.documentElement;
    const scrollTop = doc.scrollTop || document.body.scrollTop;
    const scrollHeight = doc.scrollHeight - doc.clientHeight;
    const progress = scrollHeight > 0 ? Math.min(100, Math.max(0, (scrollTop / scrollHeight) * 100)) : 0;
    document.body.style.setProperty('--scroll-progress', `${progress}%`);
  };

  let ticking = false;
  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      update();
      ticking = false;
    });
  };

  update();
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
}

initScrollProgress();

const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const SITE_LANG_STORAGE_KEY = 'streamflow_site_lang';
const SITE_LANGS = ['ru', 'en', 'pt', 'es'];
const DEFAULT_SITE_LANG = 'ru';
let CURRENT_SITE_LANG = DEFAULT_SITE_LANG;

function safeStorageGet(storage, key) {
  try {
    return storage.getItem(key);
  } catch (err) {
    return null;
  }
}

function safeStorageSet(storage, key, value) {
  try {
    storage.setItem(key, value);
  } catch (err) {
    // ignore storage write issues (private mode/restrictions)
  }
}

const I18N = {
  ru: {
    'brand.name': 'Streamflow',
    'brand.subtitle': 'Model Agency',
    'langGate.title': 'Выберите язык',
    'langGate.subtitle': 'Select your language to continue',
    'langGate.ru': 'Русский',
    'langGate.en': 'English',
    'langGate.pt': 'Português',
    'langGate.es': 'Español',
    'nav.home': 'Главная',
    'nav.about': 'О работе',
    'nav.conditions': 'Условия',
    'nav.income': 'Доходы',
    'nav.steps': 'Этапы',
    'nav.streams': 'Видеопримеры',
    'nav.portfolio': 'Портфолио',
    'nav.apply': 'Заявка',
    'nav.telegram': 'Telegram',
    'cta.apply': 'Оставить заявку',
    'cta.telegram': 'Telegram канал',
    'cta.watchExamples': 'Смотреть примеры',
    'mobile.menu': 'Меню',
    'mobile.close': 'Закрыть',
    'hero.eyebrow': 'Model Agency',
    'hero.title': 'Агентство стриминговых моделей',
    'hero.lead': 'Спокойный старт, ясные шаги и поддержка команды на каждом этапе. Без спешки, без давления, с понятной коммуникацией.',
    'hero.card1Title': 'Старт',
    'hero.card1Text': 'Спокойный старт и понятные шаги без давления.',
    'hero.card2Title': 'Образ',
    'hero.card2Text': 'Образ остаётся в твоих руках.',
    'hero.card3Title': 'Поддержка',
    'hero.card3Text': 'Команда рядом на каждом шаге.',
    'hero.card4Title': 'Уверенность',
    'hero.card4Text': 'Спокойный рост без давления и стресса.',
    'trust.supportTitle': 'Персональная поддержка старта',
    'trust.supportText': 'Каждую анкету ведёт менеджер и даёт обратную связь по шагам.',
    'trust.communicationTitle': 'Прозрачная коммуникация',
    'trust.communicationText': 'Ответ и обратная связь приходят в Telegram.',
    'trust.channelTitle': 'Канал Streamflow',
    'trust.channelLink': 'Перейти в канал',
    'about.eyebrow': 'О работе',
    'about.title': 'Комфортный формат для моделей, которые ценят спокойствие.',
    'about.text': 'Streamflow помогает начать уверенно: сопровождение, поддержка и прозрачные правила работы.',
    'about.cta': 'Условия и преимущества',
    'offer.eyebrow': 'Условия и преимущества',
    'offer.title': 'Всё по шагам и без лишнего стресса.',
    'offer.subtitle': 'Три базовых фокуса, которые дают уверенность на старте и стабильность в работе.',
    'offer.item1Title': 'Комфортный вход',
    'offer.item1Text': 'Объясняем, настраиваем, показываем, как выглядит работа изнутри.',
    'offer.item2Title': 'Визуал и безопасность',
    'offer.item2Text': 'Только аккуратный визуал и спокойный формат без давления.',
    'offer.item3Title': 'Стабильный рост',
    'offer.item3Text': 'Поддержка и рекомендации, чтобы результат рос плавно.',
    'offer.ctaSecondary': 'Смотреть этапы',
    'income.eyebrow': 'Примеры дохода',
    'income.title': 'Примеры дохода',
    'income.subtitle': 'Это реальные цифры моделей, которые работают с нами несколько месяцев.',
    'income.note': 'Рост дохода',
    'streams.eyebrow': 'Видеопримеры',
    'streams.title': 'Смотри атмосферу и ритм стримов.',
    'streams.subtitle': 'Фрагменты реальных стримов, снятых моделями дома.',
    'steps.eyebrow': 'Этапы',
    'steps.title': 'Три шага до уверенного старта.',
    'steps.subtitle': 'Прозрачный путь без давления и хаоса — всё по шагам.',
    'steps.item1Title': 'Заявка',
    'steps.item1Text': 'Заполняешь анкету, мы аккуратно проверяем и возвращаемся с ответом.',
    'steps.item2Title': 'Подготовка',
    'steps.item2Text': 'Подготовка профиля, образа и понятный план первого эфира.',
    'steps.item3Title': 'Старт',
    'steps.item3Text': 'Запуск с поддержкой команды и понятной обратной связью.',
    'portfolio.eyebrow': 'Портфолио',
    'portfolio.title': 'Портфолио моделей Streamflow.',
    'portfolio.hint': 'Листай фото влево/вправо или нажимай стрелки.',
    'form.eyebrow': 'Заявка',
    'form.title': 'Анкета Streamflow',
    'form.subtitle': 'Этап 1 из 2: короткая заявка за 1 минуту.',
    'form.mini1': 'Оставляешь базовые данные.',
    'form.mini2': 'Переходишь в Telegram на обязательный этап 2.',
    'form.mini3': 'После этапа 2 заявка уходит в работу.',
    'form.progressTitle': 'Этап 1: короткая заявка',
    'form.side1': 'Имя',
    'form.side2': 'Телефон',
    'form.side3': 'Дата рождения',
    'form.side4': 'Модель устройства',
    'form.side5': 'Telegram',
    'form.side6': '—',
    'form.side7': '—',
    'form.side8': '—',
    'form.side9': '—',
    'form.side10': '—',
    'form.side11': '—',
    'form.side12': '—',
    'form.side13': '—',
    'form.q1': '1️⃣ Как тебя зовут?<br><br>Напиши имя полностью:',
    'form.q2': '2️⃣ Контактный телефон (+код):',
    'form.q3': '3️⃣ Дата рождения<br><br>Пример: 01.01.2000',
    'form.q4': '4️⃣ Модель устройства:',
    'form.q5': '5️⃣ Telegram (@username):',
    'form.q6': '6️⃣ Устройства:',
    'form.q6Placeholder': 'Например: смартфон, ноутбук',
    'form.q7': '7️⃣ Модель устройства:',
    'form.q8': '8️⃣ Время работы (часов в день):',
    'form.q9': '9️⃣ Есть ли наушники с микрофоном:',
    'form.q10': '🔟 Telegram (@username):',
    'form.q11': '1️⃣1️⃣ Опыт (если нет — напиши «нет»):',
    'form.q12': '1️⃣2️⃣ Фото анфас:',
    'form.q13': '1️⃣3️⃣ Фото в полный рост:',
    'form.prev': 'Назад',
    'form.next': 'Далее',
    'form.submit': 'Сохранить этап 1',
    'form.openTelegram': 'Открыть Telegram',
    'form.sending': 'Отправка...',
    'form.success': 'Этап 1 сохранён. Переходи в Telegram для обязательного этапа 2.',
    'form.sendError': 'Ошибка отправки.',
    'form.invalid': 'Поле заполнено неверно.',
    'footer.channel': 'Канал Streamflow',
    'footer.rights': '© Streamflow. Все права защищены.',
    'validation.name': 'Введите имя полностью.',
    'validation.city': 'Укажи страну.',
    'validation.phone': 'Введите телефон в формате +7 900 000 00 00.',
    'validation.age': 'Дата рождения в формате 01.01.2000.',
    'validation.yesNo': 'Ответь «да» или «нет».',
    'validation.devices': 'Уточни, какие устройства есть.',
    'validation.deviceModel': 'Напиши модель устройства.',
    'validation.workTime': 'Укажи количество часов цифрами.',
    'validation.telegram': 'Укажи Telegram в формате @username.',
    'validation.experience': 'Напиши, есть ли опыт.',
    'validation.photoFace': 'Загрузи фото анфас.',
    'validation.photoFull': 'Загрузи фото в полный рост.',
    'validation.required': 'Поле обязательно.',
  },
  en: {
    'brand.name': 'Streamflow',
    'brand.subtitle': 'Model Agency',
    'langGate.title': 'Choose language',
    'langGate.subtitle': 'Select your language to continue',
    'langGate.ru': 'Russian',
    'langGate.en': 'English',
    'langGate.pt': 'Portuguese',
    'langGate.es': 'Spanish',
    'nav.home': 'Home',
    'nav.about': 'About',
    'nav.conditions': 'Conditions',
    'nav.income': 'Income',
    'nav.steps': 'Steps',
    'nav.streams': 'Stream samples',
    'nav.portfolio': 'Portfolio',
    'nav.apply': 'Apply',
    'nav.telegram': 'Telegram',
    'cta.apply': 'Apply now',
    'cta.telegram': 'Telegram channel',
    'cta.watchExamples': 'View samples',
    'mobile.menu': 'Menu',
    'mobile.close': 'Close',
    'hero.eyebrow': 'Model Agency',
    'hero.title': 'Streaming model agency',
    'hero.lead': 'Calm start, clear steps and team support on every stage. No pressure, no rush, clear communication.',
    'hero.card1Title': 'Start',
    'hero.card1Text': 'Calm launch and clear steps without pressure.',
    'hero.card2Title': 'Style',
    'hero.card2Text': 'Your image stays under your control.',
    'hero.card3Title': 'Support',
    'hero.card3Text': 'The team is near on every step.',
    'hero.card4Title': 'Confidence',
    'hero.card4Text': 'Steady growth without stress.',
    'trust.supportTitle': 'Personal launch support',
    'trust.supportText': 'Every profile is handled by a manager with clear feedback.',
    'trust.communicationTitle': 'Transparent communication',
    'trust.communicationText': 'Response and updates are sent via Telegram.',
    'trust.channelTitle': 'Streamflow channel',
    'trust.channelLink': 'Open channel',
    'about.eyebrow': 'About work',
    'about.title': 'A comfortable format for models who value calm growth.',
    'about.text': 'Streamflow helps you start confidently with guidance, support and transparent rules.',
    'about.cta': 'Conditions and benefits',
    'offer.eyebrow': 'Conditions and benefits',
    'offer.title': 'Everything step by step without stress.',
    'offer.subtitle': 'Three key focus points that build confidence at launch and stable growth.',
    'offer.item1Title': 'Comfortable onboarding',
    'offer.item1Text': 'We explain, set up and show how work looks in practice.',
    'offer.item2Title': 'Visual and safety',
    'offer.item2Text': 'Only clean visual style and calm workflow without pressure.',
    'offer.item3Title': 'Stable growth',
    'offer.item3Text': 'Support and recommendations for steady results.',
    'offer.ctaSecondary': 'View steps',
    'income.eyebrow': 'Income examples',
    'income.title': 'Income examples',
    'income.subtitle': 'Real numbers from models working with us for several months.',
    'income.note': 'Income growth',
    'streams.eyebrow': 'Stream examples',
    'streams.title': 'See the atmosphere and stream rhythm.',
    'streams.subtitle': 'Real stream fragments recorded by models at home.',
    'steps.eyebrow': 'Steps',
    'steps.title': 'Three steps to a confident start.',
    'steps.subtitle': 'A clear path without chaos or pressure.',
    'steps.item1Title': 'Application',
    'steps.item1Text': 'You complete the form, we review it carefully and reply.',
    'steps.item2Title': 'Preparation',
    'steps.item2Text': 'Profile prep, visual prep and a clear first-stream plan.',
    'steps.item3Title': 'Start',
    'steps.item3Text': 'Launch with team support and clear feedback.',
    'portfolio.eyebrow': 'Portfolio',
    'portfolio.title': 'Streamflow model portfolio.',
    'portfolio.hint': 'Swipe left or right, or use the arrows.',
    'form.eyebrow': 'Application',
    'form.title': 'Streamflow form',
    'form.subtitle': 'Step 1 of 2: a quick 1-minute application.',
    'form.mini1': 'Leave your basic contact details.',
    'form.mini2': 'Move to Telegram for required Step 2.',
    'form.mini3': 'After Step 2 your application goes to review.',
    'form.progressTitle': 'Step 1: quick application',
    'form.side1': 'Name',
    'form.side2': 'Phone',
    'form.side3': 'Birth date',
    'form.side4': 'Device model',
    'form.side5': 'Telegram',
    'form.side6': '—',
    'form.side7': '—',
    'form.side8': '—',
    'form.side9': '—',
    'form.side10': '—',
    'form.side11': '—',
    'form.side12': '—',
    'form.side13': '—',
    'form.q1': '1️⃣ What is your full name?',
    'form.q2': '2️⃣ Contact phone (+code):',
    'form.q3': '3️⃣ Birth date<br><br>Example: 01.01.2000',
    'form.q4': '4️⃣ Device model:',
    'form.q5': '5️⃣ Telegram (@username):',
    'form.q6': '6️⃣ Devices:',
    'form.q6Placeholder': 'Example: smartphone, laptop',
    'form.q7': '7️⃣ Device model:',
    'form.q8': '8️⃣ Work time (hours per day):',
    'form.q9': '9️⃣ Do you have headphones with microphone?',
    'form.q10': '🔟 Telegram (@username):',
    'form.q11': '1️⃣1️⃣ Experience (if none, write "none"):',
    'form.q12': '1️⃣2️⃣ Front photo:',
    'form.q13': '1️⃣3️⃣ Full-body photo:',
    'form.prev': 'Back',
    'form.next': 'Next',
    'form.submit': 'Save Step 1',
    'form.openTelegram': 'Open Telegram',
    'form.sending': 'Sending...',
    'form.success': 'Step 1 saved. Open Telegram and complete required Step 2.',
    'form.sendError': 'Sending error.',
    'form.invalid': 'Invalid field value.',
    'footer.channel': 'Streamflow channel',
    'footer.rights': '© Streamflow. All rights reserved.',
    'validation.name': 'Enter full name.',
    'validation.city': 'Enter your country.',
    'validation.phone': 'Enter phone like +1 555 123 4567.',
    'validation.age': 'Birth date format: 01.01.2000.',
    'validation.yesNo': 'Answer "yes" or "no".',
    'validation.devices': 'Specify available devices.',
    'validation.deviceModel': 'Enter your device model.',
    'validation.workTime': 'Enter work hours using digits.',
    'validation.telegram': 'Enter Telegram as @username.',
    'validation.experience': 'Tell us if you have experience.',
    'validation.photoFace': 'Upload front-face photo.',
    'validation.photoFull': 'Upload full-body photo.',
    'validation.required': 'This field is required.',
  },
  pt: {
    'brand.name': 'Streamflow',
    'brand.subtitle': 'Model Agency',
    'langGate.title': 'Escolha o idioma',
    'langGate.subtitle': 'Selecione seu idioma para continuar',
    'langGate.ru': 'Russo',
    'langGate.en': 'Inglês',
    'langGate.pt': 'Português',
    'langGate.es': 'Espanhol',
    'nav.home': 'Início',
    'nav.about': 'Sobre',
    'nav.conditions': 'Condições',
    'nav.income': 'Renda',
    'nav.steps': 'Etapas',
    'nav.streams': 'Exemplos',
    'nav.portfolio': 'Portfólio',
    'nav.apply': 'Candidatura',
    'nav.telegram': 'Telegram',
    'cta.apply': 'Enviar candidatura',
    'cta.telegram': 'Canal Telegram',
    'cta.watchExamples': 'Ver exemplos',
    'mobile.menu': 'Menu',
    'mobile.close': 'Fechar',
    'hero.eyebrow': 'Model Agency',
    'hero.title': 'Agência de modelos de streaming',
    'hero.lead': 'Começo tranquilo, passos claros e suporte da equipe em cada etapa. Sem pressão, sem correria.',
    'hero.card1Title': 'Início',
    'hero.card1Text': 'Começo tranquilo com passos claros.',
    'hero.card2Title': 'Imagem',
    'hero.card2Text': 'Sua imagem permanece sob seu controle.',
    'hero.card3Title': 'Suporte',
    'hero.card3Text': 'A equipe está ao seu lado em cada etapa.',
    'hero.card4Title': 'Confiança',
    'hero.card4Text': 'Crescimento estável sem estresse.',
    'trust.supportTitle': 'Suporte pessoal no início',
    'trust.supportText': 'Cada candidatura é acompanhada por um gerente.',
    'trust.communicationTitle': 'Comunicação transparente',
    'trust.communicationText': 'Resposta e acompanhamento via Telegram.',
    'trust.channelTitle': 'Canal Streamflow',
    'trust.channelLink': 'Abrir canal',
    'about.eyebrow': 'Sobre o trabalho',
    'about.title': 'Formato confortável para modelos que valorizam tranquilidade.',
    'about.text': 'A Streamflow ajuda você a começar com orientação, suporte e regras claras.',
    'about.cta': 'Condições e benefícios',
    'offer.eyebrow': 'Condições e benefícios',
    'offer.title': 'Tudo por etapas, sem estresse.',
    'offer.subtitle': 'Três focos que dão confiança no começo e estabilidade no trabalho.',
    'offer.item1Title': 'Entrada confortável',
    'offer.item1Text': 'Explicamos, configuramos e mostramos o processo por dentro.',
    'offer.item2Title': 'Visual e segurança',
    'offer.item2Text': 'Somente visual limpo e formato tranquilo, sem pressão.',
    'offer.item3Title': 'Crescimento estável',
    'offer.item3Text': 'Suporte e recomendações para resultados consistentes.',
    'offer.ctaSecondary': 'Ver etapas',
    'income.eyebrow': 'Exemplos de renda',
    'income.title': 'Exemplos de renda',
    'income.subtitle': 'Números reais de modelos que trabalham conosco há alguns meses.',
    'income.note': 'Crescimento da renda',
    'streams.eyebrow': 'Exemplos de stream',
    'streams.title': 'Veja o ritmo e a atmosfera das lives.',
    'streams.subtitle': 'Trechos reais de streams gravados pelas modelos em casa.',
    'steps.eyebrow': 'Etapas',
    'steps.title': 'Três passos para um início confiante.',
    'steps.subtitle': 'Caminho claro, sem pressão e sem caos.',
    'steps.item1Title': 'Candidatura',
    'steps.item1Text': 'Você preenche o formulário e retornamos com resposta.',
    'steps.item2Title': 'Preparação',
    'steps.item2Text': 'Preparação do perfil, imagem e plano do primeiro stream.',
    'steps.item3Title': 'Início',
    'steps.item3Text': 'Lançamento com suporte da equipe e feedback claro.',
    'portfolio.eyebrow': 'Portfólio',
    'portfolio.title': 'Portfólio de modelos Streamflow.',
    'portfolio.hint': 'Deslize para a esquerda/direita ou use as setas.',
    'form.eyebrow': 'Candidatura',
    'form.title': 'Formulário Streamflow',
    'form.subtitle': 'Etapa 1 de 2: cadastro rápido em 1 minuto.',
    'form.mini1': 'Você envia seus dados básicos.',
    'form.mini2': 'Segue para o Telegram para a Etapa 2 obrigatória.',
    'form.mini3': 'Após a Etapa 2, a candidatura entra em análise.',
    'form.progressTitle': 'Etapa 1: cadastro rápido',
    'form.side1': 'Nome',
    'form.side2': 'Telefone',
    'form.side3': 'Data de nascimento',
    'form.side4': 'Modelo do dispositivo',
    'form.side5': 'Telegram',
    'form.side6': '—',
    'form.side7': '—',
    'form.side8': '—',
    'form.side9': '—',
    'form.side10': '—',
    'form.side11': '—',
    'form.side12': '—',
    'form.side13': '—',
    'form.q1': '1️⃣ Qual é o seu nome completo?',
    'form.q2': '2️⃣ Telefone de contato (+código):',
    'form.q3': '3️⃣ Data de nascimento<br><br>Exemplo: 01.01.2000',
    'form.q4': '4️⃣ Modelo do dispositivo:',
    'form.q5': '5️⃣ Telegram (@username):',
    'form.q6': '6️⃣ Dispositivos:',
    'form.q6Placeholder': 'Exemplo: smartphone, notebook',
    'form.q7': '7️⃣ Modelo do dispositivo:',
    'form.q8': '8️⃣ Tempo de trabalho (horas por dia):',
    'form.q9': '9️⃣ Você tem fones com microfone?',
    'form.q10': '🔟 Telegram (@username):',
    'form.q11': '1️⃣1️⃣ Experiência (se não tiver, escreva "não"):',
    'form.q12': '1️⃣2️⃣ Foto frontal:',
    'form.q13': '1️⃣3️⃣ Foto de corpo inteiro:',
    'form.prev': 'Voltar',
    'form.next': 'Avançar',
    'form.submit': 'Salvar Etapa 1',
    'form.openTelegram': 'Abrir Telegram',
    'form.sending': 'Enviando...',
    'form.success': 'Etapa 1 salva. Abra o Telegram e conclua a Etapa 2 obrigatória.',
    'form.sendError': 'Erro ao enviar.',
    'form.invalid': 'Campo preenchido incorretamente.',
    'footer.channel': 'Canal Streamflow',
    'footer.rights': '© Streamflow. Todos os direitos reservados.',
    'validation.name': 'Digite o nome completo.',
    'validation.city': 'Informe o país.',
    'validation.phone': 'Digite telefone no formato +55 11 99999 9999.',
    'validation.age': 'Data no formato 01.01.2000.',
    'validation.yesNo': 'Responda "sim" ou "não".',
    'validation.devices': 'Informe quais dispositivos você tem.',
    'validation.deviceModel': 'Informe o modelo do dispositivo.',
    'validation.workTime': 'Informe as horas com números.',
    'validation.telegram': 'Informe o Telegram no formato @username.',
    'validation.experience': 'Escreva se você tem experiência.',
    'validation.photoFace': 'Envie a foto frontal.',
    'validation.photoFull': 'Envie a foto de corpo inteiro.',
    'validation.required': 'Campo obrigatório.',
  },
  es: {
    'brand.name': 'Streamflow',
    'brand.subtitle': 'Model Agency',
    'langGate.title': 'Elige idioma',
    'langGate.subtitle': 'Selecciona tu idioma para continuar',
    'langGate.ru': 'Ruso',
    'langGate.en': 'Inglés',
    'langGate.pt': 'Portugués',
    'langGate.es': 'Español',
    'nav.home': 'Inicio',
    'nav.about': 'Sobre',
    'nav.conditions': 'Condiciones',
    'nav.income': 'Ingresos',
    'nav.steps': 'Etapas',
    'nav.streams': 'Ejemplos',
    'nav.portfolio': 'Portafolio',
    'nav.apply': 'Solicitud',
    'nav.telegram': 'Telegram',
    'cta.apply': 'Enviar solicitud',
    'cta.telegram': 'Canal Telegram',
    'cta.watchExamples': 'Ver ejemplos',
    'mobile.menu': 'Menú',
    'mobile.close': 'Cerrar',
    'hero.eyebrow': 'Model Agency',
    'hero.title': 'Agencia de modelos de streaming',
    'hero.lead': 'Inicio tranquilo, pasos claros y apoyo del equipo en cada etapa. Sin presión, sin prisa.',
    'hero.card1Title': 'Inicio',
    'hero.card1Text': 'Inicio tranquilo y pasos claros sin presión.',
    'hero.card2Title': 'Imagen',
    'hero.card2Text': 'Tu imagen queda en tus manos.',
    'hero.card3Title': 'Apoyo',
    'hero.card3Text': 'El equipo está contigo en cada paso.',
    'hero.card4Title': 'Confianza',
    'hero.card4Text': 'Crecimiento estable sin estrés.',
    'trust.supportTitle': 'Soporte personal de inicio',
    'trust.supportText': 'Cada solicitud la revisa un manager con feedback claro.',
    'trust.communicationTitle': 'Comunicación transparente',
    'trust.communicationText': 'Respuesta y seguimiento por Telegram.',
    'trust.channelTitle': 'Canal Streamflow',
    'trust.channelLink': 'Abrir canal',
    'about.eyebrow': 'Sobre el trabajo',
    'about.title': 'Formato cómodo para modelos que valoran la calma.',
    'about.text': 'Streamflow te ayuda a empezar con acompañamiento, soporte y reglas claras.',
    'about.cta': 'Condiciones y beneficios',
    'offer.eyebrow': 'Condiciones y beneficios',
    'offer.title': 'Todo por pasos, sin estrés.',
    'offer.subtitle': 'Tres focos clave para un inicio seguro y crecimiento estable.',
    'offer.item1Title': 'Entrada cómoda',
    'offer.item1Text': 'Explicamos, configuramos y mostramos cómo funciona el trabajo.',
    'offer.item2Title': 'Visual y seguridad',
    'offer.item2Text': 'Solo visual limpio y formato tranquilo, sin presión.',
    'offer.item3Title': 'Crecimiento estable',
    'offer.item3Text': 'Soporte y recomendaciones para resultados constantes.',
    'offer.ctaSecondary': 'Ver etapas',
    'income.eyebrow': 'Ejemplos de ingresos',
    'income.title': 'Ejemplos de ingresos',
    'income.subtitle': 'Cifras reales de modelos que trabajan con nosotros hace meses.',
    'income.note': 'Crecimiento de ingresos',
    'streams.eyebrow': 'Ejemplos de stream',
    'streams.title': 'Mira el ritmo y la atmósfera de los streams.',
    'streams.subtitle': 'Fragmentos reales grabados por modelos desde casa.',
    'steps.eyebrow': 'Etapas',
    'steps.title': 'Tres pasos para empezar con confianza.',
    'steps.subtitle': 'Un camino claro sin presión ni caos.',
    'steps.item1Title': 'Solicitud',
    'steps.item1Text': 'Rellenas el formulario y te respondemos con cuidado.',
    'steps.item2Title': 'Preparación',
    'steps.item2Text': 'Preparación del perfil, imagen y plan del primer stream.',
    'steps.item3Title': 'Inicio',
    'steps.item3Text': 'Lanzamiento con apoyo del equipo y feedback claro.',
    'portfolio.eyebrow': 'Portafolio',
    'portfolio.title': 'Portafolio de modelos Streamflow.',
    'portfolio.hint': 'Desliza a izquierda/derecha o usa las flechas.',
    'form.eyebrow': 'Solicitud',
    'form.title': 'Formulario Streamflow',
    'form.subtitle': 'Etapa 1 de 2: solicitud rápida en 1 minuto.',
    'form.mini1': 'Dejas tus datos básicos.',
    'form.mini2': 'Vas a Telegram para la Etapa 2 obligatoria.',
    'form.mini3': 'Después de la Etapa 2 tu solicitud entra en revisión.',
    'form.progressTitle': 'Etapa 1: solicitud rápida',
    'form.side1': 'Nombre',
    'form.side2': 'Teléfono',
    'form.side3': 'Fecha de nacimiento',
    'form.side4': 'Modelo del dispositivo',
    'form.side5': 'Telegram',
    'form.side6': '—',
    'form.side7': '—',
    'form.side8': '—',
    'form.side9': '—',
    'form.side10': '—',
    'form.side11': '—',
    'form.side12': '—',
    'form.side13': '—',
    'form.q1': '1️⃣ ¿Cuál es tu nombre completo?',
    'form.q2': '2️⃣ Teléfono de contacto (+código):',
    'form.q3': '3️⃣ Fecha de nacimiento<br><br>Ejemplo: 01.01.2000',
    'form.q4': '4️⃣ Modelo del dispositivo:',
    'form.q5': '5️⃣ Telegram (@username):',
    'form.q6': '6️⃣ Dispositivos:',
    'form.q6Placeholder': 'Ejemplo: smartphone, portátil',
    'form.q7': '7️⃣ Modelo del dispositivo:',
    'form.q8': '8️⃣ Tiempo de trabajo (horas por día):',
    'form.q9': '9️⃣ ¿Tienes auriculares con micrófono?',
    'form.q10': '🔟 Telegram (@username):',
    'form.q11': '1️⃣1️⃣ Experiencia (si no tienes, escribe "no"):',
    'form.q12': '1️⃣2️⃣ Foto frontal:',
    'form.q13': '1️⃣3️⃣ Foto cuerpo completo:',
    'form.prev': 'Atrás',
    'form.next': 'Siguiente',
    'form.submit': 'Guardar Etapa 1',
    'form.openTelegram': 'Abrir Telegram',
    'form.sending': 'Enviando...',
    'form.success': 'Etapa 1 guardada. Abre Telegram y completa la Etapa 2 obligatoria.',
    'form.sendError': 'Error al enviar.',
    'form.invalid': 'Campo inválido.',
    'footer.channel': 'Canal Streamflow',
    'footer.rights': '© Streamflow. Todos los derechos reservados.',
    'validation.name': 'Escribe el nombre completo.',
    'validation.city': 'Indica el país.',
    'validation.phone': 'Escribe teléfono en formato internacional.',
    'validation.age': 'Fecha en formato 01.01.2000.',
    'validation.yesNo': 'Responde "sí" o "no".',
    'validation.devices': 'Indica qué dispositivos tienes.',
    'validation.deviceModel': 'Escribe el modelo del dispositivo.',
    'validation.workTime': 'Indica las horas con números.',
    'validation.telegram': 'Indica Telegram en formato @username.',
    'validation.experience': 'Escribe si tienes experiencia.',
    'validation.photoFace': 'Sube una foto frontal.',
    'validation.photoFull': 'Sube una foto de cuerpo completo.',
    'validation.required': 'Campo obligatorio.',
  },
};

function normalizeSiteLang(lang) {
  const value = String(lang || '').trim().toLowerCase();
  return SITE_LANGS.includes(value) ? value : DEFAULT_SITE_LANG;
}

function siteText(key, lang = CURRENT_SITE_LANG) {
  const locale = normalizeSiteLang(lang);
  return I18N[locale][key] || I18N[DEFAULT_SITE_LANG][key] || '';
}

const INCOME_CURRENCY_BY_LANG = {
  ru: { locale: 'ru-RU', currency: 'RUB', rateFromRub: 1, roundStep: 1000 },
  en: { locale: 'en-US', currency: 'USD', rateFromRub: 0.011, roundStep: 50 },
  pt: { locale: 'pt-BR', currency: 'BRL', rateFromRub: 0.056, roundStep: 100 },
  es: { locale: 'es-ES', currency: 'EUR', rateFromRub: 0.01, roundStep: 50 },
};

function formatIncomeAmount(rubValue, lang = CURRENT_SITE_LANG) {
  const locale = normalizeSiteLang(lang);
  const config = INCOME_CURRENCY_BY_LANG[locale] || INCOME_CURRENCY_BY_LANG[DEFAULT_SITE_LANG];
  const raw = Math.max(0, Number(rubValue) || 0) * config.rateFromRub;
  const rounded = config.roundStep > 1
    ? Math.max(config.roundStep, Math.round(raw / config.roundStep) * config.roundStep)
    : raw;
  return new Intl.NumberFormat(config.locale, {
    style: 'currency',
    currency: config.currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(rounded);
}

function updateIncomeAmounts(lang = CURRENT_SITE_LANG) {
  document.querySelectorAll('.income-amount[data-income-rub]').forEach((element) => {
    const rubValue = Number(element.getAttribute('data-income-rub'));
    if (!Number.isFinite(rubValue) || rubValue <= 0) return;
    element.textContent = formatIncomeAmount(rubValue, lang);
  });
}

function updateMenuToggleText() {
  const isOpen = document.body.classList.contains('nav-open');
  const text = isOpen ? siteText('mobile.close') : siteText('mobile.menu');
  document.querySelectorAll('[data-menu-text]').forEach((node) => {
    node.textContent = text;
  });
}

function applySiteTranslations(lang) {
  CURRENT_SITE_LANG = normalizeSiteLang(lang);
  document.documentElement.lang = CURRENT_SITE_LANG;
  document.querySelectorAll('[data-i18n]').forEach((element) => {
    const key = element.getAttribute('data-i18n');
    const value = siteText(key, CURRENT_SITE_LANG);
    if (!value) return;
    element.innerHTML = value;
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach((element) => {
    const key = element.getAttribute('data-i18n-placeholder');
    const value = siteText(key, CURRENT_SITE_LANG);
    if (value) element.setAttribute('placeholder', value);
  });
  document.querySelectorAll('input[name="site_lang"]').forEach((langField) => {
    langField.value = CURRENT_SITE_LANG;
  });
  const desktopSelect = document.getElementById('site-lang-select');
  const mobileSelect = document.getElementById('site-lang-select-mobile');
  if (desktopSelect) desktopSelect.value = CURRENT_SITE_LANG;
  if (mobileSelect) mobileSelect.value = CURRENT_SITE_LANG;
  updateIncomeAmounts(CURRENT_SITE_LANG);
  updateMenuToggleText();
  document.dispatchEvent(new CustomEvent('site-language-changed', { detail: { lang: CURRENT_SITE_LANG } }));
}

function setSiteLanguage(lang, options = {}) {
  const locale = normalizeSiteLang(lang);
  if (options.persist !== false) {
    safeStorageSet(localStorage, SITE_LANG_STORAGE_KEY, locale);
  }
  applySiteTranslations(locale);
}

function hideLanguageGate() {
  const gate = document.getElementById('language-gate');
  if (!gate) return;
  gate.classList.remove('is-visible');
  gate.setAttribute('aria-hidden', 'true');
  document.body.classList.remove('lang-locked');
}

function showLanguageGate() {
  const gate = document.getElementById('language-gate');
  if (!gate) return;
  gate.classList.add('is-visible');
  gate.setAttribute('aria-hidden', 'false');
  document.body.classList.add('lang-locked');
}

function initSiteLanguage() {
  const savedRaw = safeStorageGet(localStorage, SITE_LANG_STORAGE_KEY);
  const hasSaved = !!savedRaw && SITE_LANGS.includes(savedRaw.toLowerCase());
  const initialLang = hasSaved ? savedRaw : DEFAULT_SITE_LANG;
  applySiteTranslations(initialLang);

  const desktopSelect = document.getElementById('site-lang-select');
  const mobileSelect = document.getElementById('site-lang-select-mobile');
  [desktopSelect, mobileSelect].forEach((select) => {
    if (!select) return;
    select.addEventListener('change', () => {
      setSiteLanguage(select.value, { persist: true });
    });
  });

  document.querySelectorAll('[data-language-option]').forEach((button) => {
    button.addEventListener('click', () => {
      const locale = button.getAttribute('data-language-option') || DEFAULT_SITE_LANG;
      setSiteLanguage(locale, { persist: true });
      hideLanguageGate();
    });
  });

  showLanguageGate();
}

initSiteLanguage();

function initHeroParallax() {
  if (prefersReduced) return;
  if (window.matchMedia('(max-width: 1100px)').matches) return;
  const hero = document.querySelector('.hero');
  if (!hero) return;

  let targetX = 0;
  let targetY = 0;
  let currentX = 0;
  let currentY = 0;
  const maxShift = 14;

  function render() {
    currentX += (targetX - currentX) * 0.1;
    currentY += (targetY - currentY) * 0.1;
    hero.style.setProperty('--hero-parallax-x', `${currentX}px`);
    hero.style.setProperty('--hero-parallax-y', `${currentY}px`);
    hero.style.setProperty('--hero-parallax-x2', `${-currentX * 0.55}px`);
    hero.style.setProperty('--hero-parallax-y2', `${-currentY * 0.55}px`);
    requestAnimationFrame(render);
  }

  hero.addEventListener('pointermove', (event) => {
    const rect = hero.getBoundingClientRect();
    const nx = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    const ny = ((event.clientY - rect.top) / rect.height) * 2 - 1;
    targetX = nx * maxShift;
    targetY = ny * maxShift;
  });

  hero.addEventListener('pointerleave', () => {
    targetX = 0;
    targetY = 0;
  });

  render();
}

initHeroParallax();

function initLiquidEtherBackground() {
  const layer = document.querySelector('.liquid-ether-bg');
  const hero = document.querySelector('.hero');
  if (!layer || !hero || prefersReduced) return;

  let targetX = 0;
  let targetY = 0;
  let currentX = 0;
  let currentY = 0;
  const maxShift = 20;

  const update = () => {
    currentX += (targetX - currentX) * 0.08;
    currentY += (targetY - currentY) * 0.08;
    layer.style.setProperty('--ether-x', `${currentX}px`);
    layer.style.setProperty('--ether-y', `${currentY}px`);
    requestAnimationFrame(update);
  };

  hero.addEventListener('pointermove', (event) => {
    const rect = hero.getBoundingClientRect();
    const nx = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    const ny = ((event.clientY - rect.top) / rect.height) * 2 - 1;
    targetX = nx * maxShift;
    targetY = ny * maxShift;
  });

  hero.addEventListener('pointerleave', () => {
    targetX = 0;
    targetY = 0;
  });

  update();
}

initLiquidEtherBackground();

function initGradualBlur() {
  const blurBlocks = Array.from(document.querySelectorAll('.gradual-blur'));
  if (!blurBlocks.length) return;

  blurBlocks.forEach((block) => {
    if (!block.querySelector('.gradual-blur-inner')) {
      const inner = document.createElement('div');
      inner.className = 'gradual-blur-inner';
      for (let i = 0; i < 5; i += 1) {
        const layer = document.createElement('div');
        layer.className = 'gradual-blur-layer';
        inner.appendChild(layer);
      }
      block.appendChild(inner);
    }
  });

  const hero = document.querySelector('.hero');
  if (!hero) return;

  let ticking = false;
  const update = () => {
    const rect = hero.getBoundingClientRect();
    const viewport = Math.max(window.innerHeight || 1, 1);
    const offset = Math.max(0, -rect.top);
    const travel = Math.max(rect.height - viewport, 1);
    const progress = Math.min(1, Math.max(0, offset / travel));

    blurBlocks.forEach((block) => {
      const isTop = block.classList.contains('gradual-blur-top');
      const baseOpacity = isTop ? 0.52 : 0.68;
      const extraOpacity = isTop ? 0.24 : 0.28;
      const blurStrength = isTop ? 0.9 + progress * 0.85 : 1 + progress * 1.1;
      block.style.setProperty('--blur-opacity', String((baseOpacity + extraOpacity * progress).toFixed(3)));
      block.style.setProperty('--blur-strength', String(blurStrength.toFixed(3)));
    });
  };

  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      update();
      ticking = false;
    });
  };

  update();
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
}

initGradualBlur();

function initSpotlightCards() {
  const cards = document.querySelectorAll(
    '.card-spotlight, .offer-item, .steps-item, .income-card, .video-card, .portfolio-block, .trust-item'
  );
  if (!cards.length) return;

  cards.forEach((card) => {
    card.addEventListener('pointermove', (event) => {
      const rect = card.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      card.style.setProperty('--mouse-x', `${x}px`);
      card.style.setProperty('--mouse-y', `${y}px`);
      card.classList.add('is-spotlight-active');
    });

    card.addEventListener('pointerleave', () => {
      card.classList.remove('is-spotlight-active');
    });
  });
}

initSpotlightCards();

const revealElements = document.querySelectorAll('.reveal');
if (revealElements.length) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.18 });

  revealElements.forEach((el) => observer.observe(el));
}

if (!prefersReduced) {
  document.querySelectorAll('a[href]').forEach((link) => {
    const href = link.getAttribute('href');
    if (!href || href.startsWith('mailto:') || href.startsWith('tel:')) return;
    if (href.startsWith('#')) {
      link.addEventListener('click', () => {
        safeStorageSet(sessionStorage, 'allow_hash_scroll_ts', String(Date.now()));
      });
      return;
    }
    if (link.target === '_blank' || link.hasAttribute('download')) return;
    if (href.startsWith('http')) return;
    link.addEventListener('click', (event) => {
      event.preventDefault();
      if (href.includes('#')) {
        safeStorageSet(sessionStorage, 'allow_hash_scroll_ts', String(Date.now()));
      }
      document.body.classList.add('is-transitioning');
      setTimeout(() => {
        window.location.href = href;
      }, 200);
    });
  });
}

const videoCards = document.querySelectorAll('.video-card');
videoCards.forEach((card) => {
  const preview = card.querySelector('video');
  if (preview) {
    preview.addEventListener('loadedmetadata', () => {
      try {
        preview.currentTime = 0.2;
      } catch (err) {
        // ignore
      }
    });
    card.addEventListener('pointerenter', async () => {
      try {
        await preview.play();
      } catch (err) {
        // ignore autoplay restrictions
      }
    });
    card.addEventListener('pointerleave', () => {
      preview.pause();
      try {
        preview.currentTime = 0.2;
      } catch (err) {
        // ignore
      }
    });
  }
});

const ambientVideos = Array.from(document.querySelectorAll('video[autoplay][muted][loop]'));
if (ambientVideos.length) {
  const ambientObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      const video = entry.target;
      if (!(video instanceof HTMLVideoElement)) return;
      if (entry.isIntersecting && entry.intersectionRatio > 0.35) {
        video.play().catch(() => {});
      } else {
        video.pause();
      }
    });
  }, { threshold: [0, 0.35, 0.7] });

  ambientVideos.forEach((video) => {
    video.pause();
    ambientObserver.observe(video);
  });
}

const videoModal = document.getElementById('video-modal');
const modalVideo = videoModal ? videoModal.querySelector('video') : null;

function openModal(modal) {
  modal.classList.add('open');
  modal.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
}

function closeModal(modal) {
  modal.classList.remove('open');
  modal.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
}

if (videoModal && modalVideo) {
  videoCards.forEach((card) => {
    card.addEventListener('click', () => {
      const src = card.getAttribute('data-video');
      if (!src) return;
      modalVideo.src = src;
      modalVideo.currentTime = 0;
      openModal(videoModal);
      modalVideo.play().catch(() => {});
    });
  });
}

[videoModal].forEach((modal) => {
  if (!modal) return;
  modal.addEventListener('click', (event) => {
    if (event.target.hasAttribute('data-close')) {
      if (modal === videoModal && modalVideo) {
        modalVideo.pause();
        modalVideo.removeAttribute('src');
      }
      closeModal(modal);
    }
  });
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    if (videoModal && videoModal.classList.contains('open')) {
      if (modalVideo) {
        modalVideo.pause();
        modalVideo.removeAttribute('src');
      }
      closeModal(videoModal);
    }
  }
});

const navOpenButtons = document.querySelectorAll('[data-nav-open]');
const mobileNav = document.querySelector('.mobile-nav');
const navCloseButtons = document.querySelectorAll('[data-nav-close]');
const menuTextNodes = document.querySelectorAll('[data-menu-text]');

function setNavState(isOpen) {
  document.body.classList.toggle('nav-open', isOpen);
  navOpenButtons.forEach((btn) => btn.setAttribute('aria-expanded', String(isOpen)));
  updateMenuToggleText();
  if (mobileNav) {
    mobileNav.setAttribute('aria-hidden', String(!isOpen));
  }
}

if (mobileNav) {
  navOpenButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      setNavState(!document.body.classList.contains('nav-open'));
    });
  });

  navCloseButtons.forEach((btn) => btn.addEventListener('click', () => setNavState(false)));
  mobileNav.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => setNavState(false)));
}

function initFloatingMenuVisibility() {
  const floatingBtn = document.querySelector('.floating-menu-btn');
  const footer = document.querySelector('.site-footer');
  if (!floatingBtn || !footer) return;

  const observer = new IntersectionObserver(
    (entries) => {
      const isFooterVisible = entries.some((entry) => entry.isIntersecting);
      floatingBtn.classList.toggle('is-hidden', isFooterVisible);
    },
    { threshold: 0.1 }
  );

  observer.observe(footer);
}

initFloatingMenuVisibility();

const carousels = document.querySelectorAll('[data-carousel]');
carousels.forEach((carousel) => {
  const track = carousel.querySelector('.carousel-track');
  const slides = Array.from(carousel.querySelectorAll('.carousel-slide'));
  const dots = Array.from(carousel.querySelectorAll('.carousel-dot'));
  if (!track || slides.length === 0) return;

  let positions = slides.map((slide) => slide.offsetLeft);
  let activeIndex = 0;
  let autoTimer;
  let isDragging = false;
  let startX = 0;
  let startScrollLeft = 0;

  function setActive(index) {
    if (!dots.length) return;
    dots.forEach((dot, idx) => dot.classList.toggle('is-active', idx === index));
  }

  function updateActive() {
    const scrollLeft = track.scrollLeft;
    let closestIndex = 0;
    let minDiff = Infinity;
    positions.forEach((pos, idx) => {
      const diff = Math.abs(scrollLeft - pos);
      if (diff < minDiff) {
        minDiff = diff;
        closestIndex = idx;
      }
    });
    activeIndex = closestIndex;
    setActive(closestIndex);
  }

  function stopAuto() {
    if (autoTimer) {
      window.clearInterval(autoTimer);
      autoTimer = null;
    }
  }

  function goTo(index) {
    const target =
      typeof positions[index] === 'number'
        ? positions[index]
        : slides[index].offsetLeft;
    track.scrollTo({ left: target, behavior: 'smooth' });
    activeIndex = index;
    setActive(index);
  }

  function startAuto() {
    stopAuto();
    autoTimer = window.setInterval(() => {
      const next = (activeIndex + 1) % slides.length;
      goTo(next);
    }, 4000);
  }

  let scrollTimer;
  track.addEventListener('scroll', () => {
    window.clearTimeout(scrollTimer);
    scrollTimer = window.setTimeout(updateActive, 80);
  });

  dots.forEach((dot, idx) => {
    dot.addEventListener('click', () => {
      goTo(idx);
    });
  });

  track.addEventListener('pointerdown', (event) => {
    isDragging = true;
    startX = event.clientX;
    startScrollLeft = track.scrollLeft;
    stopAuto();
    track.setPointerCapture(event.pointerId);
  });

  track.addEventListener('pointermove', (event) => {
    if (!isDragging) return;
    const delta = startX - event.clientX;
    track.scrollLeft = startScrollLeft + delta;
  });

  function endDrag(event) {
    if (!isDragging) return;
    isDragging = false;
    if (event.pointerId !== undefined) {
      try {
        track.releasePointerCapture(event.pointerId);
      } catch (err) {
        // ignore
      }
    }
    updateActive();
    startAuto();
  }

  track.addEventListener('pointerup', endDrag);
  track.addEventListener('pointerleave', endDrag);
  track.addEventListener('pointercancel', endDrag);

  window.addEventListener('resize', () => {
    positions = slides.map((slide) => slide.offsetLeft);
    updateActive();
  });

  updateActive();
  startAuto();
});

const portfolioSliders = document.querySelectorAll('[data-portfolio]');
portfolioSliders.forEach((slider) => {
  const track = slider.querySelector('.portfolio-track');
  const slides = Array.from(slider.querySelectorAll('.portfolio-slide'));
  const dots = Array.from(slider.querySelectorAll('.portfolio-dot'));
  const prev = slider.querySelector('.portfolio-btn.prev');
  const next = slider.querySelector('.portfolio-btn.next');
  if (!track || slides.length === 0) return;

  const getClosestIndex = () => {
    const scrollLeft = track.scrollLeft;
    let closestIndex = 0;
    let minDiff = Infinity;
    slides.forEach((slide, idx) => {
      const diff = Math.abs(scrollLeft - slide.offsetLeft);
      if (diff < minDiff) {
        minDiff = diff;
        closestIndex = idx;
      }
    });
    return closestIndex;
  };

  const updateDots = (index) => {
    if (!dots.length) return;
    dots.forEach((dot, idx) => dot.classList.toggle('is-active', idx === index));
  };

  const goTo = (index) => {
    const slide = slides[index];
    const target = slide ? slide.offsetLeft : 0;
    track.scrollTo({ left: target, behavior: 'smooth' });
    updateDots(index);
  };

  let scrollTimer;
  track.addEventListener('scroll', () => {
    window.clearTimeout(scrollTimer);
    scrollTimer = window.setTimeout(() => updateDots(getClosestIndex()), 80);
  });

  if (prev) {
    prev.addEventListener('click', () => {
      const nextIndex = Math.max(0, getClosestIndex() - 1);
      goTo(nextIndex);
    });
  }

  if (next) {
    next.addEventListener('click', () => {
      const nextIndex = Math.min(slides.length - 1, getClosestIndex() + 1);
      goTo(nextIndex);
    });
  }

  dots.forEach((dot, idx) => dot.addEventListener('click', () => goTo(idx)));
  updateDots(0);
});

const forms = document.querySelectorAll('[data-application-form]');
const telegramLinks = document.querySelectorAll('[data-telegram-link]');
const formNextLinks = document.querySelectorAll('[data-form-next] a');

async function loadConfig() {
  try {
    const response = await fetch('/api/config');
    if (!response.ok) return;
    const data = await response.json();
    if (data.telegram_link && telegramLinks.length) {
      telegramLinks.forEach((link) => {
        link.href = data.telegram_link;
      });
    }
    if (data.bot_link && formNextLinks.length) {
      formNextLinks.forEach((link) => {
        link.href = data.bot_link;
      });
    }
  } catch (err) {
    // ignore
  }
}

function initSmartCta() {
  const ctas = Array.from(document.querySelectorAll('[data-smart-cta]'));
  if (!ctas.length) return;

  ctas.forEach((cta) => {
    cta.dataset.defaultText = cta.textContent.trim();
    cta.dataset.defaultHref = cta.getAttribute('href') || '#apply';
  });

  function getTelegramHref() {
    const link = document.querySelector('[data-telegram-link]');
    return link ? link.getAttribute('href') || '#apply' : '#apply';
  }

  function detectSection() {
    const sections = ['apply', 'portfolio', 'streams'];
    const marker = window.scrollY + window.innerHeight * 0.42;
    for (const id of sections) {
      const section = document.getElementById(id);
      if (!section) continue;
      const top = section.offsetTop;
      const bottom = top + section.offsetHeight;
      if (marker >= top && marker < bottom) return id;
    }
    return null;
  }

  function applyState(sectionId) {
    const firstCta = ctas.length ? ctas[0] : null;
    let text = (firstCta && firstCta.dataset.defaultText) || 'Оставить заявку';
    let href = (firstCta && firstCta.dataset.defaultHref) || '#apply';
    if (sectionId === 'streams' || sectionId === 'portfolio') {
      text = 'Смотреть примеры';
      href = '#streams';
    } else if (sectionId === 'apply') {
      text = 'Telegram канал';
      href = getTelegramHref();
    }
    ctas.forEach((cta) => {
      cta.textContent = text;
      cta.setAttribute('href', href);
    });
  }

  let ticking = false;
  const onChange = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      applyState(detectSection());
      ticking = false;
    });
  };

  onChange();
  window.addEventListener('scroll', onChange, { passive: true });
  window.addEventListener('resize', onChange);
}

loadConfig().finally(() => {
  initSmartCta();
});

function initMultiStep(form) {
  const steps = Array.from(form.querySelectorAll('.form-step'));
  if (!steps.length) return;

  let current = 0;
  const total = steps.length;
  const progressCurrent = form.querySelector('[data-step-current]');
  const progressTotal = form.querySelector('[data-step-total]');
  const progressBar = form.querySelector('[data-step-bar]');
  const btnPrev = form.querySelector('[data-step-prev]');
  const btnNext = form.querySelector('[data-step-next]');
  const btnSubmit = form.querySelector('[data-step-submit]');
  const progressCurrentSide = form.querySelector('[data-step-current-side]');
  const progressTotalSide = form.querySelector('[data-step-total-side]');
  const progressBarSide = form.querySelector('[data-step-bar-side]');
  const sidePoints = Array.from(form.querySelectorAll('[data-step-point]'));
  let userNavigated = false;

  form.setAttribute('novalidate', 'novalidate');

  if (progressTotal) progressTotal.textContent = String(total);
  if (progressTotalSide) progressTotalSide.textContent = String(total);

  const validators = {
    name: (value) => (value.trim().length >= 2 ? '' : siteText('validation.name')),
    city: (value) => (value.trim().length >= 2 ? '' : siteText('validation.city')),
    phone: (value) => (isValidPhone(value) ? '' : siteText('validation.phone')),
    age: (value) => (isValidBirthdate(value) ? '' : siteText('validation.age')),
    living: (value) => (normalizeYesNo(value) ? '' : siteText('validation.yesNo')),
    devices: (value) => (value.trim().length >= 2 ? '' : siteText('validation.devices')),
    device_model: (value) => (value.trim().length >= 2 ? '' : siteText('validation.deviceModel')),
    work_time: (value) => (/\d/.test(value) ? '' : siteText('validation.workTime')),
    headphones: (value) => (normalizeYesNo(value) ? '' : siteText('validation.yesNo')),
    telegram: (value) => (normalizeTelegram(value) ? '' : siteText('validation.telegram')),
    experience: (value) => (value.trim().length >= 1 ? '' : siteText('validation.experience')),
    photo_face: (_value, field) => (field.files && field.files.length ? '' : siteText('validation.photoFace')),
    photo_full: (_value, field) => (field.files && field.files.length ? '' : siteText('validation.photoFull')),
  };

  function ensureFieldError(field) {
    const wrapper = field.closest('.field');
    if (!wrapper) return null;
    let error = wrapper.querySelector('.field-error');
    if (!error) {
      error = document.createElement('div');
      error.className = 'field-error';
      error.setAttribute('role', 'alert');
      error.setAttribute('aria-live', 'polite');
      wrapper.appendChild(error);
    }
    return error;
  }

  function setFieldError(field, message) {
    const wrapper = field.closest('.field');
    const error = ensureFieldError(field);
    if (wrapper) wrapper.classList.add('is-error');
    if (error) error.textContent = message;
    field.setAttribute('aria-invalid', 'true');
  }

  function clearFieldError(field) {
    const wrapper = field.closest('.field');
    const error = wrapper ? wrapper.querySelector('.field-error') : null;
    if (wrapper) wrapper.classList.remove('is-error');
    if (error) error.textContent = '';
    field.removeAttribute('aria-invalid');
  }

  function validateField(field) {
    if (!field) return true;
    const value = field.type === 'file' ? '' : field.value || '';
    const rule = validators[field.name];
    let message = '';
    if (rule) {
      message = rule(value, field) || '';
    } else if (field.required) {
      if (field.type === 'file') {
        message = field.files && field.files.length ? '' : siteText('validation.required');
      } else {
        message = value.trim() ? '' : siteText('validation.required');
      }
    }

    if (message) {
      setFieldError(field, message);
      return false;
    }
    clearFieldError(field);
    return true;
  }

  function update() {
    steps.forEach((step, idx) => step.classList.toggle('is-active', idx === current));
    if (progressCurrent) progressCurrent.textContent = String(current + 1);
    if (progressBar) progressBar.style.width = `${((current + 1) / total) * 100}%`;
    if (progressCurrentSide) progressCurrentSide.textContent = String(current + 1);
    if (progressBarSide) progressBarSide.style.width = `${((current + 1) / total) * 100}%`;
    if (sidePoints.length) {
      sidePoints.forEach((point, idx) => {
        point.classList.toggle('is-active', idx === current);
        point.classList.toggle('is-done', idx < current);
      });
      const active = sidePoints[current];
      if (active && userNavigated) {
        active.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      }
    }
    if (btnPrev) btnPrev.classList.toggle('hidden', current === 0);
    if (btnNext) btnNext.classList.toggle('hidden', current >= total - 1);
    if (btnSubmit) btnSubmit.classList.toggle('hidden', current < total - 1);
  }

  function validateStep(index) {
    const step = steps[index];
    if (!step) return true;
    const fields = step.querySelectorAll('input, textarea, select');
    let firstInvalid = null;
    fields.forEach((field) => {
      const valid = validateField(field);
      if (!valid && !firstInvalid) firstInvalid = field;
    });
    if (firstInvalid) {
      firstInvalid.focus();
      firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return false;
    }
    return true;
  }

  function goTo(index) {
    const nextIndex = Math.max(0, Math.min(total - 1, index));
    if (nextIndex !== current) userNavigated = true;
    current = nextIndex;
    update();
    const nextStep = steps[current];
    if (nextStep) {
      const focusField = nextStep.querySelector('input, textarea, select');
      if (focusField) focusField.focus();
    }
  }

  if (btnPrev) {
    btnPrev.addEventListener('click', () => goTo(current - 1));
  }
  if (btnNext) {
    btnNext.addEventListener('click', () => {
      if (validateStep(current)) {
        goTo(current + 1);
      }
    });
  }

  steps.forEach((step, idx) => {
    step.querySelectorAll('input, textarea, select').forEach((field) => {
      field.addEventListener('input', () => {
        const fieldWrap = field.closest('.field');
        if (fieldWrap && fieldWrap.classList.contains('is-error')) {
          validateField(field);
        }
      });
      field.addEventListener('change', () => {
        const isAutoStepField =
          field.hasAttribute('data-autonext') ||
          field.tagName === 'SELECT' ||
          field.type === 'file';
        if (idx === current && isAutoStepField && validateField(field) && current < total - 1) {
          goTo(current + 1);
        }
      });
      field.addEventListener('keydown', (event) => {
        if (event.key !== 'Enter') return;
        if (field.tagName === 'TEXTAREA') return;
        if (current < total - 1) {
          event.preventDefault();
          if (validateField(field)) {
            goTo(current + 1);
          }
        }
      });
    });
  });

  form.addEventListener('form:reset-steps', () => goTo(0));
  form.__stepper = { steps, goTo, validateField, validateStep, setFieldError };
  update();
}

async function sendApplication(formData, elements, options = {}) {
  const { pendingMessage = siteText('form.sending'), resetForm = false } = options;
  const { form, formStatus, formNext, formNextLink, submitButton } = elements;
  if (formStatus) {
    formStatus.textContent = pendingMessage;
    formStatus.classList.remove('is-error');
    formStatus.classList.remove('is-success');
  }

  if (submitButton) submitButton.disabled = true;

  try {
    const response = await fetch('/api/apply', {
      method: 'POST',
      body: formData,
    });
    let payload = {};
    try {
      payload = await response.json();
    } catch (err) {
      payload = {};
    }
    if (response.ok && payload.ok) {
      if (formStatus) {
        formStatus.classList.add('is-success');
        formStatus.innerHTML = payload.message || siteText('form.success');
      }
      if (resetForm && form) {
        form.reset();
        form.dispatchEvent(new Event('form:reset-steps'));
      }
      if (payload.bot_link && formNext && formNextLink) {
        formNextLink.href = payload.bot_link;
        formNext.classList.remove('hidden');
      }
    } else {
      const fieldName = payload.field;
      const stepper = form ? form.__stepper : null;
      let handledInline = false;
      if (fieldName && form) {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (field) {
          if (stepper) {
            const step = field.closest('.form-step');
            if (step) {
              const stepIndex = stepper.steps.indexOf(step);
              if (stepIndex >= 0) {
                stepper.goTo(stepIndex);
              }
            }
            stepper.setFieldError(field, payload.message || siteText('form.invalid'));
          }
          field.focus();
          field.scrollIntoView({ behavior: 'smooth', block: 'center' });
          handledInline = true;
        }
      }
      if (formStatus) {
        if (handledInline) {
          formStatus.textContent = '';
          formStatus.classList.remove('is-error');
        } else {
          formStatus.classList.add('is-error');
          formStatus.innerHTML = payload.message || siteText('form.sendError');
        }
      }
    }
  } catch (err) {
    if (formStatus) {
      formStatus.classList.add('is-error');
      formStatus.textContent = siteText('form.sendError');
    }
  } finally {
    if (submitButton) submitButton.disabled = false;
  }
}

forms.forEach((form) => {
  const formStatus = form.querySelector('[data-form-status]');
  const formNext = form.querySelector('[data-form-next]');
  const formNextLink = formNext ? formNext.querySelector('a') : null;
  const submitButton = form.querySelector('button[type="submit"]');
  const elements = { form, formStatus, formNext, formNextLink, submitButton };

  initMultiStep(form);

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const stepper = form.__stepper;
    if (stepper) {
      for (let i = 0; i < stepper.steps.length; i += 1) {
        const ok = stepper.validateStep(i);
        if (!ok) {
          stepper.goTo(i);
          return;
        }
      }
    }
    const formData = new FormData(form);
    await sendApplication(formData, elements, { resetForm: true });
  });
});

function normalizeTelegram(value) {
  let v = (value || '').trim();
  if (!v) return null;
  if (v.startsWith('https://t.me/')) v = v.split('/').pop() || '';
  if (v.startsWith('http://t.me/')) v = v.split('/').pop() || '';
  if (v.startsWith('t.me/')) v = v.split('/')[1] || '';
  if (v.startsWith('@')) v = v.slice(1);
  if (/^[A-Za-z0-9_]{5,32}$/.test(v)) return `@${v}`;
  return null;
}

function normalizePhone(value) {
  const v = (value || '').replace(/[()\s-]+/g, '');
  if (!v) return null;
  if (v.startsWith('+')) {
    const digits = v.slice(1);
    if (!/^\d+$/.test(digits)) return null;
    return `+${digits}`;
  }
  if (/^\d+$/.test(v)) return v;
  return null;
}

function isValidPhone(value) {
  const normalized = normalizePhone(value);
  if (!normalized) return false;
  const digits = normalized.replace(/\D/g, '');
  return digits.length >= 10 && digits.length <= 15;
}

function normalizeYesNo(value) {
  const v = (value || '').trim().toLowerCase();
  if (!v) return null;
  const tokens = v.match(/[a-zA-Zа-яА-ЯёЁ]+/g) || [v];
  const yes = new Set(['да', 'ага', 'есть', 'имеется', 'конечно', 'yes', 'y', 'da', 'ок', 'ok', 'si', 'sí', 'sim']);
  const no = new Set(['нет', 'нету', 'неа', 'no', 'n', 'nao', 'não']);
  for (const raw of tokens) {
    const token = raw.toLowerCase();
    if (yes.has(token)) return 'Да';
    if (no.has(token)) return 'Нет';
  }
  return null;
}

function isValidBirthdate(value) {
  const v = (value || '').trim();
  let day;
  let month;
  let year;
  let match = v.match(/^(\d{2})[./](\d{2})[./](\d{4})$/);
  if (match) {
    day = Number(match[1]);
    month = Number(match[2]);
    year = Number(match[3]);
  } else {
    match = v.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (!match) return false;
    year = Number(match[1]);
    month = Number(match[2]);
    day = Number(match[3]);
  }
  if (year < 1900) return false;
  const date = new Date(year, month - 1, day);
  if (Number.isNaN(date.getTime())) return false;
  if (date.getFullYear() !== year || date.getMonth() !== month - 1 || date.getDate() !== day) return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return date <= today;
}
