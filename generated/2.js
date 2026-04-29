// ════ MOBILE NAV ════
const navToggle = document.querySelector('.navbar-toggle');
const navLinks  = document.querySelector('.navbar-menu');
if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    navLinks.classList.toggle('nav-open');
    navToggle.classList.toggle('active');
  });
}

// ════ SMOOTH SCROLL ════
document.querySelectorAll('.navbar-item').forEach(link => {
  link.addEventListener('click', e => {
    const href = link.getAttribute('href');
    if (href && href.startsWith('#')) {
      e.preventDefault();
      const target = document.querySelector(href);
      if (target) target.scrollIntoView({ behavior: 'smooth' });
      navLinks.classList.remove('nav-open');
      navToggle.classList.remove('active');
    }
  });
});

// ════ STICKY NAV ════
const nav = document.querySelector('#nav');
window.addEventListener('scroll', () => {
  if (nav) nav.classList.toggle('scrolled', window.scrollY > 50);
});

// ════ ACTIVE NAV HIGHLIGHTING ════
if ('IntersectionObserver' in window) {
  const navObserver = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        document.querySelectorAll('.navbar-item').forEach(item => {
          item.classList.remove('active');
        });
        const activeItem = document.querySelector(`.navbar-item[href="${e.target.getAttribute('href')}"]`);
        if (activeItem) activeItem.classList.add('active');
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('section[id]').forEach(section => {
    navObserver.observe(section);
  });
}

// ════ CATEGORY FILTER ════
const categoryFilter = document.querySelector('.category-filter');
const productsGrid = document.querySelector('.products-grid');
if (categoryFilter && productsGrid) {
  categoryFilter.addEventListener('change', (e) => {
    const selectedCategory = e.target.value;
    if (selectedCategory === 'all') {
      productsGrid.style.display = 'grid';
    } else {
      productsGrid.querySelectorAll('.product-card').forEach(card => {
        if (card.dataset.category === selectedCategory) {
          productsGrid.style.display = 'grid';
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    }
  });
}

// ════ CONTACT FORM SUBMISSION ════
const contactForm = document.querySelector('.contact-form');
if (contactForm) {
  contactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const formData = new FormData(contactForm);
    const name = contactForm.querySelector('.form-input[name="name"]');
    const email = contactForm.querySelector('.form-input[name="email"]');
    const message = contactForm.querySelector('.form-input[name="message"]');
    
    if (name && email && message) {
      const formDetails = {
        name: name.value.trim(),
        email: email.value.trim(),
        message: message.value.trim()
      };
      
      if (formDetails.name && formDetails.email && formDetails.message) {
        // Simulate form submission
        const submitBtn = contactForm.querySelector('.form-button');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Sending...';
        submitBtn.disabled = true;
        
        setTimeout(() => {
          submitBtn.textContent = 'Message Sent!';
          contactForm.reset();
          submitBtn.disabled = false;
          submitBtn.textContent = originalText;
          
          // Show success message
          const successMsg = document.createElement('div');
          successMsg.className = 'success-message';
          successMsg.textContent = 'Thank you for contacting Fresh Kirana Store! We\'ll get back to you soon.';
          contactForm.appendChild(successMsg);
          
          setTimeout(() => {
            successMsg.remove();
          }, 5000);
        }, 1500);
      } else {
        alert('Please fill in all fields correctly.');
      }
    }
  });
}

// ════ SCROLL REVEAL ════
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.15 });
  
  document.querySelectorAll('.hero-content, .about-container, .products-grid, .service-card, .contact-container').forEach(el => {
    observer.observe(el);
  });
}

// ════ FRESH KIRANA STORE FEATURES ════
// Auto-rotate featured products
const featuredProducts = document.querySelectorAll('.product-card');
if (featuredProducts.length > 0) {
  let currentIndex = 0;
  const autoRotateInterval = setInterval(() => {
    featuredProducts.forEach(product => {
      product.classList.remove('featured');
    });
    featuredProducts[currentIndex].classList.add('featured');
    currentIndex = (currentIndex + 1) % featuredProducts.length;
  }, 5000);
  
  // Pause rotation on hover
  const productsSection = document.querySelector('.products');
  if (productsSection) {
    productsSection.addEventListener('mouseenter', () => clearInterval(autoRotateInterval));
    productsSection.addEventListener('mouseleave', () => {
      currentIndex = 0;
      featuredProducts.forEach(product => {
        product.classList.remove('featured');
      });
      featuredProducts[currentIndex].classList.add('featured');
      setInterval(() => {
        featuredProducts.forEach(product => {
          product.classList.remove('featured');
        });
        featuredProducts[currentIndex].classList.add('featured');
        currentIndex = (currentIndex + 1) % featuredProducts.length;
      }, 5000);
    });
  }
}

// Add to cart functionality for products
document.querySelectorAll('.product-card').forEach(card => {
  const addToCartBtn = card.querySelector('.add-to-cart');
  if (addToCartBtn) {
    addToCartBtn.addEventListener('click', () => {
      const productTitle = card.querySelector('.product-title').textContent;
      const productPrice = card.querySelector('.product-price').textContent;
      
      // Create cart notification
      const cartNotification = document.createElement('div');
      cartNotification.className = 'cart-notification';
      cartNotification.textContent = `${productTitle} added to cart!`;
      cartNotification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #4CAF50;
        color: white;
        padding: 15px 25px;
        border-radius: 5px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease;
      `;
      
      document.body.appendChild(cartNotification);
      
      setTimeout(() => {
        cartNotification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => cartNotification.remove(), 300);
      }, 2000);
    });
  }
});

// Service counter animation
document.querySelectorAll('.service-card').forEach(card => {
  const counter = card.querySelector('.service-counter');
  if (counter) {
    const target = parseInt(counter.dataset.target);
    const duration = 2000;
    const increment = target / (duration / 16);
    let current = 0;
    
    const updateCounter = () => {
      current += increment;
      if (current < target) {
        counter.textContent = Math.floor(current);
        requestAnimationFrame(updateCounter);
      } else {
        counter.textContent = target;
      }
    };
    
    updateCounter();
  }
});

// Newsletter subscription for footer
const newsletterForm = document.querySelector('.newsletter-form');
if (newsletterForm) {
  newsletterForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const emailInput = newsletterForm.querySelector('.newsletter-input');
    const email = emailInput.value.trim();
    
    if (email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      const successMsg = document.createElement('div');
      successMsg.className = 'newsletter-success';
      successMsg.textContent = 'Thank you for subscribing!';
      emailInput.parentElement.appendChild(successMsg);
      
      emailInput.value = '';
      
      setTimeout(() => {
        successMsg.remove();
      }, 3000);
    } else {
      alert('Please enter a valid email address.');
    }
  });
}

// Add CSS animations dynamically
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  @keyframes slideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
  }
  .success-message {
    background: #4CAF50;
    color: white;
    padding: 15px;
    border-radius: 5px;
    margin-top: 15px;
    animation: slideIn 0.3s ease;
  }
  .cart-notification {
    animation: slideIn 0.3s ease;
  }
  .newsletter-success {
    color: #4CAF50;
    margin-top: 10px;
    animation: slideIn 0.3s ease;
  }
  .product-card.featured {
    box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    transform: scale(1.02);
    transition: transform 0.3s ease;
  }
  .navbar.scrolled {
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  }
  .navbar-item.active {
    color: #4CAF50 !important;
  }
  .service-card .service-counter {
    font-size: 2em;
    font-weight: bold;
    color: #4CAF50;
  }
  .form-input {
    width: 100%;
    padding: 10px;
    margin: 8px 0;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: inherit;
  }
  .form-button {
    background: #4CAF50;
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    transition: background 0.3s ease;
  }
  .form-button:hover {
    background: #45a049;
  }
  .form-button:disabled {
    background: #cccccc;
    cursor: not-allowed;
  }
  .product-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }
  .product-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  }
  .category-filter {
    margin-bottom: 20px;
  }
  .category-filter select {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
  }
  .visible {
    opacity: 1 !important;
    transform: translateY(0) !important;
  }
  .reveal {
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.6s ease;
  }
`;
document.head.appendChild(style);
// ════ CATEGORY FILTER ════
const categoryFilter = document.querySelector('.category-filter select');
const productCards = document.querySelectorAll('.product-card');
if (categoryFilter) {
  categoryFilter.addEventListener('change', (e) => {
    const selectedCategory = e.target.value;
    if (selectedCategory === 'all' || selectedCategory === '') {
      productCards.forEach(card => card.style.display = 'block');
    } else {
      productCards.forEach(card => {
        const category = card.dataset.category;
        card.style.display = category === selectedCategory ? 'block' : 'none';
      });
    }
  });
}

// ════ CONTACT FORM SUBMISSION ════
const contactForm = document.querySelector('.contact-form');
if (contactForm) {
  contactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const formData = new FormData(contactForm);
    const submitButton = contactForm.querySelector('.form-button');
    if (submitButton) submitButton.disabled = true;
    fetch('/api/contact', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        contactForm.reset();
        const successMessage = document.createElement('p');
        successMessage.className = 'success-message';
        successMessage.textContent = 'Thank you for your message!';
        contactForm.appendChild(successMessage);
        setTimeout(() => successMessage.remove(), 5000);
      } else {
        const errorMessage = document.createElement('p');
        errorMessage.className = 'error-message';
        errorMessage.textContent = data.message || 'Something went wrong.';
        contactForm.appendChild(errorMessage);
        setTimeout(() => errorMessage.remove(), 5000);
      }
    })
    .catch(error => {
      const errorMessage = document.createElement('p');
      errorMessage.className = 'error-message';
      errorMessage.textContent = 'Network error. Please try again.';
      contactForm.appendChild(errorMessage);
      setTimeout(() => errorMessage.remove(), 5000);
    })
    .finally(() => {
      if (submitButton) submitButton.disabled = false;
    });
  });
}

// ════ ACTIVE NAV HIGHLIGHTING ════
const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
const sections = document.querySelectorAll('section[id]');
if (navLinks.length && sections.length) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navLinks.forEach(link => link.classList.remove('active'));
        const id = entry.target.id;
        const activeLink = document.querySelector(`.nav-link[href="#${id}"]`);
        if (activeLink) activeLink.classList.add('active');
      }
    });
  }, { threshold: 0.5 });
  sections.forEach(section => observer.observe(section));
}