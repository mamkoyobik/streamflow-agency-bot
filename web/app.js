document.body.classList.add('preload');
window.addEventListener('DOMContentLoaded', () => {
  requestAnimationFrame(() => {
    document.body.classList.add('is-ready');
    document.body.classList.remove('preload');
  });
});

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

const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (!prefersReduced) {
  document.querySelectorAll('a[href]').forEach((link) => {
    const href = link.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('mailto:') || href.startsWith('tel:')) return;
    if (link.target === '_blank' || link.hasAttribute('download')) return;
    if (href.startsWith('http')) return;
    link.addEventListener('click', (event) => {
      event.preventDefault();
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

const videoModal = document.getElementById('video-modal');
const pdfModal = document.getElementById('pdf-modal');
const modalVideo = videoModal ? videoModal.querySelector('video') : null;
const pdfIframe = pdfModal ? pdfModal.querySelector('iframe') : null;

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

const pdfButtons = document.querySelectorAll('[data-pdf]');
if (pdfModal && pdfIframe) {
  pdfButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const src = button.getAttribute('data-pdf');
      if (!src) return;
      pdfIframe.src = src;
      openModal(pdfModal);
    });
  });
}

[videoModal, pdfModal].forEach((modal) => {
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
    if (pdfModal && pdfModal.classList.contains('open')) {
      closeModal(pdfModal);
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
  menuTextNodes.forEach((node) => {
    node.textContent = isOpen ? 'Закрыть' : 'Меню';
  });
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

const carousels = document.querySelectorAll('[data-carousel]');
carousels.forEach((carousel) => {
  const track = carousel.querySelector('.carousel-track');
  const slides = Array.from(carousel.querySelectorAll('.carousel-slide'));
  const dots = Array.from(carousel.querySelectorAll('.carousel-dot'));
  if (!track || slides.length === 0) return;

  let positions = slides.map((slide) => slide.offsetLeft);

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
    setActive(closestIndex);
  }

  let scrollTimer;
  track.addEventListener('scroll', () => {
    window.clearTimeout(scrollTimer);
    scrollTimer = window.setTimeout(updateActive, 80);
  });

  dots.forEach((dot, idx) => {
    dot.addEventListener('click', () => {
      const target = positions[idx] ?? slides[idx].offsetLeft;
      track.scrollTo({ left: target, behavior: 'smooth' });
      setActive(idx);
    });
  });

  window.addEventListener('resize', () => {
    positions = slides.map((slide) => slide.offsetLeft);
    updateActive();
  });

  updateActive();
});

const form = document.getElementById('application-form');
const formStatus = document.getElementById('form-status');
const formNext = document.getElementById('form-next');
const formNextLink = formNext ? formNext.querySelector('a') : null;
const telegramLink = document.getElementById('telegram-link');
const submitButton = form ? form.querySelector('button[type="submit"]') : null;
const testButton = form ? form.querySelector('[data-test-submit]') : null;

async function loadConfig() {
  try {
    const response = await fetch('/api/config');
    if (!response.ok) return;
    const data = await response.json();
    if (data.telegram_link && telegramLink) {
      telegramLink.href = data.telegram_link;
    }
    if (data.bot_link && formNext && formNextLink) {
      formNextLink.href = data.bot_link;
      formNext.classList.remove('hidden');
    }
  } catch (err) {
    // ignore
  }
}

loadConfig();

async function sendApplication(formData, options = {}) {
  const { pendingMessage = 'Отправка...', resetForm = false } = options;
  if (formStatus) {
    formStatus.textContent = pendingMessage;
    formStatus.classList.remove('is-error');
    formStatus.classList.remove('is-success');
  }

  if (submitButton) submitButton.disabled = true;
  if (testButton) testButton.disabled = true;

  try {
    const response = await fetch('/api/apply', {
      method: 'POST',
      body: formData,
    });
    const payload = await response.json();
    if (response.ok && payload.ok) {
      if (formStatus) {
        formStatus.classList.add('is-success');
        formStatus.innerHTML = payload.message || 'Готово.';
      }
      if (resetForm && form) form.reset();
      if (payload.bot_link && formNext && formNextLink) {
        formNextLink.href = payload.bot_link;
        formNext.classList.remove('hidden');
      }
    } else if (formStatus) {
      formStatus.classList.add('is-error');
      formStatus.innerHTML = payload.message || 'Ошибка отправки.';
    }
  } catch (err) {
    if (formStatus) {
      formStatus.classList.add('is-error');
      formStatus.textContent = 'Ошибка отправки.';
    }
  } finally {
    if (submitButton) submitButton.disabled = false;
    if (testButton) testButton.disabled = false;
  }
}

async function buildTestFormData() {
  const formData = new FormData();
  formData.set('name', 'Тестовая заявка Streamflow');
  formData.set('city', 'Москва, Россия');
  formData.set('phone', '+79990000000');
  formData.set('age', '01.01.2000');
  formData.set('living', 'да');
  formData.set('devices', 'телефон');
  formData.set('device_model', 'iPhone 14');
  formData.set('work_time', '6');
  formData.set('headphones', 'да');
  formData.set('telegram', '@streamflow_test');
  formData.set('experience', 'тест');

  const [faceBlob, fullBlob] = await Promise.all([
    fetch('assets/reviews/review-1.jpg').then((response) => response.blob()),
    fetch('assets/reviews/review-2.jpg').then((response) => response.blob()),
  ]);

  formData.set('photo_face', new File([faceBlob], 'face.jpg', { type: faceBlob.type || 'image/jpeg' }));
  formData.set('photo_full', new File([fullBlob], 'full.jpg', { type: fullBlob.type || 'image/jpeg' }));

  return formData;
}

if (form) {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    await sendApplication(formData, { resetForm: true });
  });

  if (testButton) {
    testButton.addEventListener('click', async () => {
      const formData = await buildTestFormData();
      await sendApplication(formData, { pendingMessage: 'Отправка тестовой заявки...', resetForm: false });
    });
  }
}
