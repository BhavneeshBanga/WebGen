// ════ MOBILE NAV TOGGLE ════
const navToggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelector('.nav-links');
if(navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
        navLinks.classList.toggle('nav-open');
        navToggle.classList.toggle('nav-toggle-active');
    });
}

// ════ SMOOTH SCROLL ════
const navLinksArray = document.querySelectorAll('.nav-link');
navLinksArray.forEach(link => {
    if(link) {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if(targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
                if(navLinks) navLinks.classList.remove('nav-open');
                navToggle.classList.remove('nav-toggle-active');
            }
        });
    }
});

// ════ SCROLL REVEAL ════
if('IntersectionObserver' in window) {
    const revealElements = document.querySelectorAll('.reveal');
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if(entry.isIntersecting) {
                entry.target.classList.add('visible');
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });

    revealElements.forEach(element => {
        revealObserver.observe(element);
    });
}

// ════ STICKY NAV ════
const navbar = document.getElementById('nav');
if(navbar) {
    window.addEventListener('scroll', () => {
        if(window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// ════ PRODUCT QUICK VIEW ════
const productCards = document.querySelectorAll('.product-card');
let quickViewModal = null;
let quickViewContent = null;

productCards.forEach(card => {
    if(card) {
        card.addEventListener('click', () => {
            initializeQuickView();
            if(quickViewModal) {
                quickViewModal.style.display = 'block';
            }
            if(quickViewContent) {
                quickViewContent.innerHTML = `
                    <img src="${card.querySelector('.product-image')?.src || 'https://picsum.photos/seed/product_items/400/400'}" alt="Product" style="width: 100%; border-radius: 8px; margin-bottom: 15px;">
                    <h3 style="margin-bottom: 10px;">${card.querySelector('.product-info h4')?.textContent || 'Product Name'}</h3>
                    <p style="color: #6B4423; margin-bottom: 10px;">${card.querySelector('.product-price')?.textContent || '₹0.00'}</p>
                    <button class="product-add-btn" onclick="addToCartFromModal('${card.querySelector('.product-info h4')?.textContent || 'Product'}');">Add to Cart</button>
                    <button onclick="closeQuickView()" style="margin-top: 10px; padding: 8px 16px; background: #D2691E; color: white; border: none; border-radius: 4px; cursor: pointer;">Close</button>
                `;
            }
        });
    }
});

function initializeQuickView() {
    if(!quickViewModal) {
        quickViewModal = document.createElement('div');
        quickViewModal.className = 'quick-view-modal';
        quickViewModal.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5); display: none; z-index: 1000;
            align-items: center; justify-content: center;
        `;
        document.body.appendChild(quickViewModal);
    }
    if(!quickViewContent) {
        quickViewContent = document.createElement('div');
        quickViewContent.style.cssText = `
            background: white; padding: 30px; border-radius: 8px;
            max-width: 500px; width: 90%; max-height: 80vh;
            overflow-y: auto;
        `;
        quickViewModal.appendChild(quickViewContent);
    }
}

function closeQuickView() {
    if(quickViewModal) {
        quickViewModal.style.display = 'none';
    }
}

// ════ CART COUNTER ════
let cartCount = 0;
const cartIcon = document.querySelector('.cart-icon');
const cartCountElement = document.querySelector('.cart-count');

function addToCart(productName) {
    cartCount++;
    updateCartDisplay();
    showNotification(`${productName} added to cart!`);
}

function addToCartFromModal(productName) {
    addToCart(productName);
    closeQuickView();
}

function updateCartDisplay() {
    if(cartCountElement) {
        cartCountElement.textContent = cartCount;
    }
    if(cartIcon) {
        cartIcon.style.display = 'flex';
        const countDot = document.querySelector('.count-dot');
        if(countDot) {
            countDot.style.display = 'block';
        }
    }
}

// ════ CLOSE MOBILE NAV ON LINK CLICK ════
navLinksArray.forEach(link => {
    if(link) {
        link.addEventListener('click', () => {
            if(navLinks) navLinks.classList.remove('nav-open');
            navToggle.classList.remove('nav-toggle-active');
        });
    }
});

// ════ ACTIVE NAV LINK HIGHLIGHTING ════
const sections = document.querySelectorAll('section[id]');
const activeLinkObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if(entry.isIntersecting) {
            navLinksArray.forEach(link => {
                link.classList.remove('active');
                const href = link.getAttribute('href');
                if(href === `#${entry.target.id}`) {
                    link.classList.add('active');
                }
            });
        }
    });
}, { threshold: 0.5 });

sections.forEach(section => {
    if(section) {
        activeLinkObserver.observe(section);
    }
});

// ════ FORM VALIDATION ════
const contactForm = document.querySelector('.contact-form');
if(contactForm) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(contactForm);
        const name = formData.get('name');
        const email = formData.get('email');
        const message = formData.get('message');

        if(!name || !email || !message) {
            showNotification('Please fill all fields', 'error');
            return;
        }

        if(!validateEmail(email)) {
            showNotification('Please enter a valid email', 'error');
            return;
        }

        showNotification('Message sent successfully!', 'success');
        contactForm.reset();
    });
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// ════ PRODUCT FILTER ════
const filterButtons = document.querySelectorAll('.filter-btn');
const productsGrid = document.querySelector('.products-grid');
if(filterButtons && productsGrid) {
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.getAttribute('data-filter');
            if(filter === 'all') {
                productsGrid.style.display = 'grid';
            } else {
                productsGrid.querySelectorAll('.product-card').forEach(card => {
                    card.style.display = card.classList.contains(filter) ? 'block' : 'none';
                });
            }
        });
    });
}

// ════ DELIVERY INFO ACCORDION ════
const deliveryDetails = document.querySelectorAll('.delivery-details-item');
deliveryDetails.forEach(item => {
    if(item) {
        item.addEventListener('click', () => {
            item.classList.toggle('active');
        });
    }
});

// ════ CART NOTIFICATION ════
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed; bottom: 20px; right: 20px; padding: 15px 25px;
        background: ${type === 'error' ? '#FF6B6B' : '#4CAF50'}; color: white;
        border-radius: 4px; z-index: 2000; animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ════ CART COUNT RESET ON PAGE LOAD ════
window.addEventListener('load', () => {
    const savedCount = localStorage.getItem('cartCount');
    if(savedCount) {
        cartCount = parseInt(savedCount);
        updateCartDisplay();
    }
});

window.addEventListener('beforeunload', () => {
    localStorage.setItem('cartCount', cartCount);
});

// ════ SCROLL TO TOP BUTTON ════
const scrollToTopBtn = document.querySelector('.scroll-to-top');
if(scrollToTopBtn) {
    scrollToTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    window.addEventListener('scroll', () => {
        if(window.scrollY > 300) {
            scrollToTopBtn.style.display = 'block';
        } else {
            scrollToTopBtn.style.display = 'none';
        }
    });
}

// ════ LAZY LOAD IMAGES ════
const images = document.querySelectorAll('img[data-src]');
const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if(entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.classList.remove('lazy');
            imageObserver.unobserve(img);
        }
    });
});

images.forEach(img => {
    if(img) {
        img.classList.add('lazy');
        imageObserver.observe(img);
    }
});

// ════ RESIZE HANDLER ════
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        if(window.innerWidth > 768 && navLinks) {
            navLinks.classList.remove('nav-open');
            navToggle.classList.remove('nav-toggle-active');
        }
    }, 250);
});
// ════ MOBILE NAV TOGGLE ════

// ════ SMOOTH SCROLL ════

// ════ SCROLL REVEAL ════
const revealElements = document.querySelectorAll('.reveal');
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if(entry.isIntersecting) {
            entry.target.classList.add('visible');
            revealObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.15 });

revealElements.forEach(element => {
    if(element) {
        revealObserver.observe(element);
    }
});

// ════ STICKY NAV ════
const navElement = document.querySelector('#nav');
if(navElement) {
    window.addEventListener('scroll', () => {
        if(window.scrollY > 50) {
            navElement.classList.add('scrolled');
        } else {
            navElement.classList.remove('scrolled');
        }
    });
}

// ════ PRODUCT QUICK VIEW ════

function showQuickViewModal(id, name, price) {
    const modal = document.createElement('div');
    modal.className = 'quick-view-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <h2>${name}</h2>
            <p class="price">$${price}</p>
            <p>${id}</p>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const closeModalBtn = modal.querySelector('.close-modal');
    closeModalBtn.addEventListener('click', () => {
        modal.remove();
    });
    
    modal.addEventListener('click', (e) => {
        if(e.target === modal) {
            modal.remove();
        }
    });
}

// ════ CART COUNTER ════

function updateCartCount() {
    if(cartCount) {
        cartCount.textContent = cartItems;
        cartCount.style.display = cartItems > 0 ? 'block' : 'none';
    }
}

function addToCart(productId) {
    cartItems++;
    updateCartCount();
}

// Example: Add to cart functionality for product cards
productCards.forEach(card => {
    if(card) {
        const addToCartBtn = card.querySelector('.add-to-cart');
        if(addToCartBtn) {
            addToCartBtn.addEventListener('click', () => {
                const productId = card.dataset.productId;
                addToCart(productId);
            });
        }
    }
});