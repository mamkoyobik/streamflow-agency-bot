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

const navToggle = document.querySelector('.nav-toggle');
const mobileNav = document.querySelector('.mobile-nav');
const closeButtons = document.querySelectorAll('[data-nav-close]');

function closeNav() {
  document.body.classList.remove('nav-open');
  if (navToggle) navToggle.setAttribute('aria-expanded', 'false');
  if (mobileNav) mobileNav.setAttribute('aria-hidden', 'true');
}

if (navToggle && mobileNav) {
  navToggle.addEventListener('click', () => {
    const isOpen = document.body.classList.toggle('nav-open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
    mobileNav.setAttribute('aria-hidden', String(!isOpen));
  });

  closeButtons.forEach((btn) => btn.addEventListener('click', closeNav));
  mobileNav.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeNav));
}

const form = document.getElementById('application-form');
const formStatus = document.getElementById('form-status');
const formNext = document.getElementById('form-next');
const formNextLink = formNext ? formNext.querySelector('a') : null;
const telegramLink = document.getElementById('telegram-link');

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

if (form) {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (formStatus) {
      formStatus.textContent = 'Отправка...';
      formStatus.classList.remove('is-error');
      formStatus.classList.remove('is-success');
    }

    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) submitButton.disabled = true;

    try {
      const formData = new FormData(form);
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
        form.reset();
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
  });
}
