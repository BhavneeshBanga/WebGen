document.addEventListener('DOMContentLoaded', () => {
    // MOBILE NAV
    const navbarToggle = document.querySelector('.navbar-toggle');
    const navbarMenu = document.querySelector('.navbar-menu');
    if (navbarToggle !== null && navbarMenu !== null) {
        navbarToggle.addEventListener('click', () => {
            navbarMenu.classList.toggle('active');
        });
    }

    // SMOOTH SCROLL
    const navbarItems = document.querySelectorAll('.navbar-item');
    navbarItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = item.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            if (targetSection !== null) {
                targetSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // CATEGORY FILTER
    const categoryFilters = document.querySelectorAll('.category-filter');
    const productCards = document.querySelectorAll('.product-card');
    if (categoryFilters.length > 0 && productCards.length > 0) {
        categoryFilters.forEach(filter => {
            filter.addEventListener('click', () => {
                const filterCategory = filter.getAttribute('data-filter');
                productCards.forEach(card => {
                    const cardCategory = card.getAttribute('data-category');
                    if (filterCategory === 'all' || cardCategory === filterCategory) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
                categoryFilters.forEach(f => f.classList.remove('active'));
                filter.classList.add('active');
            });
        });
    }

    // CONTACT FORM SUBMISSION
    const contactForm = document.querySelector('.contact-form');
    const formInputs = document.querySelectorAll('.form-input');
    if (contactForm !== null && formInputs.length > 0) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(contactForm);
            const isValid = Array.from(formInputs).every(input => input.value.trim() !== '');
            if (isValid) {
                const successMessage = document.createElement('div');
                successMessage.className = 'success-message';
                successMessage.textContent = 'Thank you for your message! We will get back to you soon.';
                contactForm.appendChild(successMessage);
                contactForm.reset();
                setTimeout(() => successMessage.remove(), 5000);
            }
        });
    }

    // ACTIVE NAV HIGHLIGHTING
    const sections = document.querySelectorAll('section[id]');
    const navbarItems = document.querySelectorAll('.navbar-item');
    if (sections.length > 0 && navbarItems.length > 0) {
        const observerOptions = {
            root: null,
            rootMargin: '-50% 0px -50% 0px',
            threshold: 0
        };
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const targetId = entry.target.id;
                    navbarItems.forEach(item => {
                        if (item.getAttribute('href').substring(1) === targetId) {
                            navbarItems.forEach(i => i.classList.remove('active'));
                            item.classList.add('active');
                        }
                    });
                }
            });
        }, observerOptions);
        sections.forEach(section => observer.observe(section));
    }

    // SCROLL REVEAL
    const revealElements = document.querySelectorAll('.reveal');
    if (revealElements.length > 0) {
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                }
            });
        }, { threshold: 0.1 });
        revealElements.forEach(el => revealObserver.observe(el));
    }
});
// MOBILE NAV
const navbarToggle = document.querySelector('.navbar-toggle');
const navbarMenu = document.querySelector('.navbar-menu');
if (navbarToggle !== null && navbarMenu !== null) {
    navbarToggle.addEventListener('click', () => {
        navbarMenu.classList.toggle('active');
    });
}

// SMOOTH SCROLL
const navbarItems = document.querySelectorAll('.navbar-item');
navbarItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = item.getAttribute('href').substring(1);
        const targetSection = document.getElementById(targetId);
        if (targetSection !== null) {
            targetSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// CATEGORY FILTER
const categoryFilters = document.querySelectorAll('.category-filter');
const products = document.querySelectorAll('.product');
if (categoryFilters.length > 0 && products.length > 0) {
    categoryFilters.forEach(filter => {
        filter.addEventListener('click', () => {
            const filterClass = filter.getAttribute('data-filter');
            products.forEach(product => {
                if (filterClass === 'all' || product.classList.contains(filterClass)) {
                    product.style.display = 'block';
                } else {
                    product.style.display = 'none';
                }
            });
        });
    });
}