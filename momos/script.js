// ════ MOBILE NAV TOGGLE ════
const navToggleEl = document.querySelector('.nav-toggle');
const navLinksEl = document.querySelector('.nav-links');
if (navToggleEl && navLinksEl) {
    navToggleEl.addEventListener('click', () => {
        navLinksEl.classList.toggle('nav-open');
        navToggleEl.classList.toggle('active');
    });
}

// ════ SMOOTH SCROLL ════
const navLinkEls = document.querySelectorAll('.nav-link');
navLinkEls.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = link.getAttribute('href').substring(1);
        const targetEl = document.getElementById(targetId);
        if (targetEl) {
            targetEl.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// ════ CLOSE MOBILE NAV ON LINK CLICK ════
navLinkEls.forEach(link => {
    link.addEventListener('click', () => {
        navLinksEl.classList.remove('nav-open');
        navToggleEl.classList.remove('active');
    });
});

// ════ SCROLL REVEAL ════
const revealEls = document.querySelectorAll('.reveal');
if (revealEls.length > 0 && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.15
    });
    
    revealEls.forEach(el => observer.observe(el));
}

// ════ STICKY NAV ════
const navEl = document.getElementById('nav');
if (navEl) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navEl.classList.add('scrolled');
        } else {
            navEl.classList.remove('scrolled');
        }
    });
}

// ════ ACTIVE NAV HIGHLIGHTING ════
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
if (sections.length > 0 && navLinks.length > 0 && 'IntersectionObserver' in window) {
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${entry.target.id}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }, {
        threshold: 0.5
    });
    
    sections.forEach(section => sectionObserver.observe(section));
}

// ════ GALLERY CAROUSEL ════
const galleryItems = document.querySelectorAll('.gallery-item');
let currentGalleryIndex = 0;
if (galleryItems.length > 1) {
    const prevBtn = document.createElement('button');
    const nextBtn = document.createElement('button');
    prevBtn.innerHTML = '❮';
    nextBtn.innerHTML = '❯';
    
    const galleryGrid = document.querySelector('.gallery-grid');
    if (galleryGrid) {
        galleryGrid.appendChild(prevBtn);
        galleryGrid.appendChild(nextBtn);
        
        prevBtn.addEventListener('click', () => {
            galleryItems[currentGalleryIndex].classList.remove('active');
            currentGalleryIndex = (currentGalleryIndex - 1 + galleryItems.length) % galleryItems.length;
            galleryItems[currentGalleryIndex].classList.add('active');
        });
        
        nextBtn.addEventListener('click', () => {
            galleryItems[currentGalleryIndex].classList.remove('active');
            currentGalleryIndex = (currentGalleryIndex + 1) % galleryItems.length;
            galleryItems[currentGalleryIndex].classList.add('active');
        });
        
        // Touch support
        let touchStartX = 0;
        let touchEndX = 0;
        
        galleryGrid.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        });
        
        galleryGrid.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        });
        
        function handleSwipe() {
            if (touchEndX < touchStartX - 50) {
                nextBtn.click();
            }
            if (touchEndX > touchStartX + 50) {
                prevBtn.click();
            }
        }
        
        galleryItems[0].classList.add('active');
    }
}

// ════ CONTACT FORM SUBMIT ════
const contactFormEl = document.querySelector('.contact-form');
if (contactFormEl) {
    contactFormEl.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const emailInput = contactFormEl.querySelector('input[type="email"]');
        const nameInput = contactFormEl.querySelector('input[type="text"]');
        const messageInput = contactFormEl.querySelector('textarea');
        
        let isValid = true;
        
        if (emailInput) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(emailInput.value)) {
                emailInput.classList.add('error');
                isValid = false;
            } else {
                emailInput.classList.remove('error');
            }
        }
        
        if (nameInput && nameInput.value.trim() === '') {
            nameInput.classList.add('error');
            isValid = false;
        } else {
            nameInput.classList.remove('error');
        }
        
        if (messageInput && messageInput.value.trim() === '') {
            messageInput.classList.add('error');
            isValid = false;
        } else {
            messageInput.classList.remove('error');
        }
        
        if (isValid) {
            // Simulate form submission
            const submitBtn = contactFormEl.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Sending...';
            submitBtn.disabled = true;
            
            setTimeout(() => {
                submitBtn.textContent = 'Message Sent!';
                contactFormEl.reset();
                setTimeout(() => {
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                }, 3000);
            }, 1500);
        }
    });
}

// ════ ORDER FORM SUBMIT ════
const orderFormEl = document.querySelector('.order-form');
if (orderFormEl) {
    orderFormEl.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const nameInput = orderFormEl.querySelector('input[name="name"]');
        const phoneInput = orderFormEl.querySelector('input[name="phone"]');
        const emailInput = orderFormEl.querySelector('input[name="email"]');
        const itemsInput = orderFormEl.querySelector('select[name="items"]');
        const quantityInput = orderFormEl.querySelector('input[name="quantity"]');
        
        let isValid = true;
        
        if (!nameInput || nameInput.value.trim() === '') {
            nameInput.classList.add('error');
            isValid = false;
        } else {
            nameInput.classList.remove('error');
        }
        
        if (!phoneInput || !/^\d{10}$/.test(phoneInput.value)) {
            phoneInput.classList.add('error');
            isValid = false;
        } else {
            phoneInput.classList.remove('error');
        }
        
        if (!emailInput || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value)) {
            emailInput.classList.add('error');
            isValid = false;
        } else {
            emailInput.classList.remove('error');
        }
        
        if (!itemsInput || itemsInput.value === '') {
            itemsInput.classList.add('error');
            isValid = false;
        } else {
            itemsInput.classList.remove('error');
        }
        
        if (!quantityInput || quantityInput.value < 1) {
            quantityInput.classList.add('error');
            isValid = false;
        } else {
            quantityInput.classList.remove('error');
        }
        
        if (isValid) {
            const orderBtn = orderFormEl.querySelector('.order-button');
            const originalText = orderBtn.textContent;
            orderBtn.textContent = 'Processing Order...';
            orderBtn.disabled = true;
            
            // Update order summary
            const orderSummary = orderFormEl.querySelector('.order-summary');
            if (orderSummary) {
                orderSummary.innerHTML = `
                    <p><strong>Order Summary:</strong></p>
                    <p>Name: ${nameInput.value}</p>
                    <p>Phone: ${phoneInput.value}</p>
                    <p>Email: ${emailInput.value}</p>
                    <p>Items: ${itemsInput.options[itemsInput.selectedIndex].text}</p>
                    <p>Quantity: ${quantityInput.value}</p>
                    <p>Total: $${(50 * quantityInput.value).toFixed(2)}</p>
                `;
            }
            
            setTimeout(() => {
                orderBtn.textContent = 'Order Placed!';
                orderBtn.disabled = false;
                orderFormEl.reset();
                setTimeout(() => {
                    orderBtn.textContent = originalText;
                }, 3000);
            }, 2000);
        }
    });
}

// ════ MAP LOAD ════
const locationMapEl = document.querySelector('.location-map');
if (locationMapEl) {
    // Check if Google Maps API is loaded
    if (typeof google !== 'undefined' && google.maps) {
        const mapContainer = document.createElement('div');
        mapContainer.style.height = '400px';
        mapContainer.style.width = '100%';
        mapContainer.style.borderRadius = '8px';
        mapContainer.style.overflow = 'hidden';
        locationMapEl.appendChild(mapContainer);
        
        const mapOptions = {
            center: { lat: 28.7041, lng: 77.1025 }, // Delhi coordinates
            zoom: 15
        };
        
        const map = new google.maps.Map(mapContainer, mapOptions);
        
        const marker = new google.maps.Marker({
            position: { lat: 28.7041, lng: 77.1025 },
            map: map,
            title: 'Momos Stall Location'
        });
    } else {
        // Fallback: Show a simple map placeholder
        locationMapEl.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 400px; background: #e0e0e0; border-radius: 8px;">
                <p style="color: #666;">Map Loading...</p>
                <p style="color: #999; margin-left: 10px;">Enable Google Maps API for interactive map</p>
            </div>
        `;
    }
}
// ════ MOBILE NAV TOGGLE ════

// ════ SMOOTH SCROLL ════

// ════ SCROLL REVEAL ════
if ('IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                revealObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.15
    });
    
    const revealElements = document.querySelectorAll('.reveal');
    revealElements.forEach(el => {
        revealObserver.observe(el);
    });
}

// ════ STICKY NAV ════
let lastScrollY = window.scrollY;

// ════ GALLERY CAROUSEL ════

// ════ CONTACT FORM SUBMIT ════