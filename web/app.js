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

  if (progressTotal) progressTotal.textContent = String(total);

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
    for (const field of fields) {
      if (!field.checkValidity()) {
        field.reportValidity();
        return false;
      }
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
      field.addEventListener('change', () => {
        if (idx === current && field.checkValidity() && current < total - 1) {
          goTo(current + 1);
        }
      });
      field.addEventListener('keydown', (event) => {
        if (event.key !== 'Enter') return;
        if (field.tagName === 'TEXTAREA') return;
        if (current < total - 1) {
          event.preventDefault();
          if (field.checkValidity()) {
            goTo(current + 1);
          }
        }
      });
    });
  });

  form.addEventListener('form:reset-steps', () => goTo(0));
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
    const formData = new FormData(form);
    await sendApplication(formData, elements, { resetForm: true });
  });
});
