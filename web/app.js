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
    const target = positions[index] ?? slides[index].offsetLeft;
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

const forms = document.querySelectorAll('[data-application-form]');
const telegramLink = document.getElementById('telegram-link');
const formNextLinks = document.querySelectorAll('[data-form-next] a');

async function loadConfig() {
  try {
    const response = await fetch('/api/config');
    if (!response.ok) return;
    const data = await response.json();
    if (data.telegram_link && telegramLink) {
      telegramLink.href = data.telegram_link;
    }
    if (data.bot_link && formNextLinks.length) {
      formNextLinks.forEach((link) => {
        link.href = data.bot_link;
        const parent = link.closest('[data-form-next]');
        if (parent) parent.classList.remove('hidden');
      });
    }
  } catch (err) {
    // ignore
  }
}

loadConfig();

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

  form.setAttribute('novalidate', 'novalidate');

  if (progressTotal) progressTotal.textContent = String(total);

  const validators = {
    name: (value) => (value.trim().length >= 2 ? '' : 'Введите имя полностью.'),
    city: (value) => (value.trim().length >= 2 ? '' : 'Укажи город и страну.'),
    phone: (value) => (isValidPhone(value) ? '' : 'Введите телефон в формате +7 900 000 00 00.'),
    age: (value) => (isValidBirthdate(value) ? '' : 'Дата рождения в формате 01.01.2000.'),
    living: (value) => (normalizeYesNo(value) ? '' : 'Ответь «да» или «нет».'),
    devices: (value) => (value.trim().length >= 2 ? '' : 'Уточни, какие устройства есть.'),
    device_model: (value) => (value.trim().length >= 2 ? '' : 'Напиши модель устройства.'),
    work_time: (value) => (/\d/.test(value) ? '' : 'Укажи количество часов цифрами.'),
    headphones: (value) => (value.trim().length >= 2 ? '' : 'Ответь про наушники с микрофоном.'),
    telegram: (value) => (normalizeTelegram(value) ? '' : 'Укажи Telegram в формате @username.'),
    experience: (value) => (value.trim().length >= 1 ? '' : 'Напиши, есть ли опыт.'),
    photo_face: (_value, field) => (field.files && field.files.length ? '' : 'Загрузи фото анфас.'),
    photo_full: (_value, field) => (field.files && field.files.length ? '' : 'Загрузи фото в полный рост.'),
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
        message = field.files && field.files.length ? '' : 'Поле обязательно.';
      } else {
        message = value.trim() ? '' : 'Поле обязательно.';
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
    current = nextIndex;
    update();
    const nextStep = steps[current];
    if (nextStep) {
      const focusField = nextStep.querySelector('input, textarea, select');
      if (focusField) focusField.focus();
    }
  }

  btnPrev?.addEventListener('click', () => goTo(current - 1));
  btnNext?.addEventListener('click', () => {
    if (validateStep(current)) {
      goTo(current + 1);
    }
  });

  steps.forEach((step, idx) => {
    step.querySelectorAll('input, textarea, select').forEach((field) => {
      field.addEventListener('input', () => {
        if (field.closest('.field')?.classList.contains('is-error')) {
          validateField(field);
        }
      });
      field.addEventListener('change', () => {
        if (idx === current && validateField(field) && current < total - 1) {
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
  const { pendingMessage = 'Отправка...', resetForm = false } = options;
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
    const payload = await response.json();
    if (response.ok && payload.ok) {
      if (formStatus) {
        formStatus.classList.add('is-success');
        formStatus.innerHTML = payload.message || 'Готово.';
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
            stepper.setFieldError(field, payload.message || 'Поле заполнено неверно.');
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
          formStatus.innerHTML = payload.message || 'Ошибка отправки.';
        }
      }
    }
  } catch (err) {
    if (formStatus) {
      formStatus.classList.add('is-error');
      formStatus.textContent = 'Ошибка отправки.';
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
  const yesRe = /\b(да|ага|есть|имеется|конечно|yes|y|da|ок|ok)\b/;
  const noRe = /\b(нет|нету|неа|no|n)\b/;
  if (yesRe.test(v)) return 'Да';
  if (noRe.test(v)) return 'Нет';
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
