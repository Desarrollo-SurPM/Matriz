// ============================================
// PREVENCIONISTA OS - JAVASCRIPT PRINCIPAL
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    initLoginModal();
    initNavbar();
    initAnimations();
    initParticles();
    initSmoothScroll();
});

// ============================================
// MODAL DE LOGIN
// ============================================

function initLoginModal() {
    const loginBtn = document.getElementById('loginBtn');
    const loginModal = document.getElementById('loginModal');
    const closeModal = document.getElementById('closeModal');

    if (loginBtn && loginModal) {
        loginBtn.addEventListener('click', function(e) {
            e.preventDefault();
            loginModal.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }

    if (closeModal && loginModal) {
        closeModal.addEventListener('click', function() {
            loginModal.classList.remove('active');
            document.body.style.overflow = 'auto';
        });

        // Cerrar al hacer click fuera del modal
        loginModal.addEventListener('click', function(e) {
            if (e.target === loginModal) {
                loginModal.classList.remove('active');
                document.body.style.overflow = 'auto';
            }
        });
    }

    // Cerrar con tecla ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && loginModal && loginModal.classList.contains('active')) {
            loginModal.classList.remove('active');
            document.body.style.overflow = 'auto';
        }
    });
}

// ============================================
// NAVBAR INTERACTIVO
// ============================================

function initNavbar() {
    const navbar = document.querySelector('.navbar-modern');
    let lastScroll = 0;

    if (!navbar) return;

    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;

        // Agregar sombra al navbar al hacer scroll
        if (currentScroll > 50) {
            navbar.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.5)';
        } else {
            navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.4)';
        }

        lastScroll = currentScroll;
    });

    // Marcar link activo
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// ============================================
// ANIMACIONES DE ENTRADA
// ============================================

function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.8s ease-out forwards';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observar elementos con clase 'animate-on-scroll'
    const animatedElements = document.querySelectorAll('.feature-card, .card-modern');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });
}

// ============================================
// PARTÍCULAS ANIMADAS
// ============================================

function initParticles() {
    const particlesContainer = document.querySelector('.hero-particles');

    if (!particlesContainer) return;

    const particleCount = 20;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';

        // Posición aleatoria
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';

        // Tamaño aleatorio
        const size = Math.random() * 4 + 2;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';

        // Duración de animación aleatoria
        const duration = Math.random() * 20 + 10;
        particle.style.animationDuration = duration + 's';

        // Delay aleatorio
        const delay = Math.random() * 5;
        particle.style.animationDelay = `-${delay}s`;

        particlesContainer.appendChild(particle);
    }
}

// ============================================
// SCROLL SUAVE
// ============================================

function initSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            if (href === '#') return;

            e.preventDefault();

            const target = document.querySelector(href);

            if (target) {
                const offsetTop = target.offsetTop - 80;

                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// ============================================
// EFECTOS DE HOVER EN CARDS
// ============================================

function initCardEffects() {
    const cards = document.querySelectorAll('.card-modern, .feature-card');

    cards.forEach(card => {
        card.addEventListener('mouseenter', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            this.style.setProperty('--mouse-x', x + 'px');
            this.style.setProperty('--mouse-y', y + 'px');
        });
    });
}

// ============================================
// VALIDACIÓN DE FORMULARIOS
// ============================================

function initFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = this.querySelectorAll('input[required], select[required], textarea[required]');
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('is-invalid');

                    // Crear mensaje de error si no existe
                    if (!input.nextElementSibling || !input.nextElementSibling.classList.contains('error-message')) {
                        const error = document.createElement('div');
                        error.className = 'error-message';
                        error.style.color = 'var(--danger)';
                        error.style.fontSize = '0.85rem';
                        error.style.marginTop = '0.25rem';
                        error.textContent = 'Este campo es requerido';
                        input.parentNode.insertBefore(error, input.nextSibling);
                    }
                } else {
                    input.classList.remove('is-invalid');
                    const errorMsg = input.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('error-message')) {
                        errorMsg.remove();
                    }
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });

        // Limpiar errores al escribir
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                this.classList.remove('is-invalid');
                const errorMsg = this.nextElementSibling;
                if (errorMsg && errorMsg.classList.contains('error-message')) {
                    errorMsg.remove();
                }
            });
        });
    });
}

// ============================================
// TOOLTIPS PERSONALIZADOS
// ============================================

function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');

    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            tooltip.style.cssText = `
                position: absolute;
                background: var(--bg-card);
                color: var(--text-primary);
                padding: 0.5rem 1rem;
                border-radius: var(--radius-md);
                font-size: 0.85rem;
                box-shadow: var(--shadow-lg);
                pointer-events: none;
                z-index: 10000;
                white-space: nowrap;
                border: 1px solid var(--border-color);
            `;

            document.body.appendChild(tooltip);

            const rect = this.getBoundingClientRect();
            const tooltipRect = tooltip.getBoundingClientRect();

            tooltip.style.left = (rect.left + rect.width / 2 - tooltipRect.width / 2) + 'px';
            tooltip.style.top = (rect.top - tooltipRect.height - 10) + 'px';

            this._tooltip = tooltip;
        });

        element.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                this._tooltip.remove();
                this._tooltip = null;
            }
        });
    });
}

// ============================================
// NOTIFICACIONES TOAST
// ============================================

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--bg-card);
        color: var(--text-primary);
        padding: 1rem 1.5rem;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-xl);
        border-left: 4px solid ${type === 'success' ? 'var(--success)' : type === 'error' ? 'var(--danger)' : 'var(--info)'};
        z-index: 10000;
        animation: slideInRight 0.3s ease-out;
        max-width: 350px;
    `;

    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================
// CONTADOR ANIMADO
// ============================================

function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// ============================================
// LAZY LOADING DE IMÁGENES
// ============================================

function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');

    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.getAttribute('data-src');
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// ============================================
// MODO OSCURO/CLARO (FUTURO)
// ============================================

function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');

    if (!themeToggle) return;

    const currentTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', currentTheme);

    themeToggle.addEventListener('click', function() {
        const theme = document.documentElement.getAttribute('data-theme');
        const newTheme = theme === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });
}

// ============================================
// COPIAR AL PORTAPAPELES
// ============================================

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copiado al portapapeles', 'success');
    }).catch(() => {
        showToast('Error al copiar', 'error');
    });
}

// ============================================
// EXPORTAR FUNCIONES GLOBALES
// ============================================

window.PrevencionistOS = {
    showToast,
    animateCounter,
    copyToClipboard
};

// ============================================
// ANIMACIONES CSS ADICIONALES
// ============================================

const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
