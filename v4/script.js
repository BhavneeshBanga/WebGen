// ════ FEATURE: Mobile Nav Toggle ════
const navToggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelector('.nav-links');
const navOverlay = document.querySelector('.nav-overlay');

if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    navLinks.classList.toggle('nav-open');
    navOverlay.classList.toggle('nav-open');
  });
}

if (navLinks) {
  navLinks.addEventListener('click', (e) => {
    if (e.target.classList.contains('nav-link')) {
      navLinks.classList.remove('nav-open');
      navOverlay.classList.remove('nav-open');
    }
  });
}

// ════ FEATURE: Smooth Scroll ════
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    e.preventDefault();
    const targetId = anchor.getAttribute('href').substring(1);
    const targetEl = document.getElementById(targetId);
    if (targetEl) {
      targetEl.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

// ════ FEATURE: Scroll Reveal ════
const scrollRevealElements = document.querySelectorAll('.scroll-reveal');

const scrollRevealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      scrollRevealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.15 });

scrollRevealElements.forEach(el => {
  scrollRevealObserver.observe(el);
});

// ════ FEATURE: Sticky Nav ════
const navEl = document.getElementById('nav');

window.addEventListener('scroll', () => {
  if (navEl) {
    if (window.scrollY > 60) {
      navEl.classList.add('scrolled');
    } else {
      navEl.classList.remove('scrolled');
    }
  }
});

// ════ FEATURE: Active Nav Highlight ════
const sections = document.querySelectorAll('section[id]');
const navItems = document.querySelectorAll('.nav-link[href^="#"]');

const navHighlightObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const activeId = '#' + entry.target.id;
      navItems.forEach(item => {
        if (item.getAttribute('href') === activeId) {
          item.classList.add('active');
        } else {
          item.classList.remove('active');
        }
      });
    }
  });
}, { threshold: 0.5 });

sections.forEach(section => {
  navHighlightObserver.observe(section);
});

// ════ FEATURE: Order Quantity Controls ════
const quantityIncrease = document.querySelectorAll('.quantity-increase');
const quantityDecrease = document.querySelectorAll('.quantity-decrease');

quantityIncrease.forEach(btn => {
  btn.addEventListener('click', () => {
    const input = btn.parentElement.querySelector('.quantity-input');
    if (input) {
      const currentValue = parseInt(input.value) || 1;
      if (currentValue < 99) {
        input.value = currentValue + 1;
      }
    }
  });
});

quantityDecrease.forEach(btn => {
  btn.addEventListener('click', () => {
    const input = btn.parentElement.querySelector('.quantity-input');
    if (input) {
      const currentValue = parseInt(input.value) || 1;
      if (currentValue > 1) {
        input.value = currentValue - 1;
      }
    }
  });
});

// ════ FEATURE: Form Submissions ════
const orderForm = document.querySelector('.order-form');
const contactForm = document.querySelector('.contact-form');

function handleFormSubmission(form, successMessage) {
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const formInputs = form.querySelectorAll('input, textarea');
    let isValid = true;

    formInputs.forEach(input => {
      if (!input.value.trim()) {
        input.classList.add('error');
        isValid = false;
      } else {
        input.classList.remove('error');
      }
    });

    if (isValid) {
      const successEl = document.createElement('div');
      successEl.className = 'form-success';
      successEl.textContent = successMessage;
      form.appendChild(successEl);

      setTimeout(() => {
        successEl.remove();
        form.reset();
      }, 2000);
    }
  });
}

handleFormSubmission(orderForm, 'Order placed successfully! We will contact you soon.');
handleFormSubmission(contactForm, 'Message sent successfully! We will get back to you shortly.');

// ════ FEATURE: Gallery Lightbox ════
const galleryImages = document.querySelectorAll('.gallery-item img');

galleryImages.forEach(img => {
  img.addEventListener('click', () => {
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
      <img src="${img.src}" alt="${img.alt}">
      <button class="lightbox-close">&times;</button>
    `;
    
    document.body.appendChild(lightbox);
    
    lightbox.querySelector('.lightbox-close').addEventListener('click', () => {
      lightbox.remove();
    });
    
    lightbox.addEventListener('click', (e) => {
      if (e.target === lightbox) {
        lightbox.remove();
      }
    });
  });
});

// ════ FEATURE: WhatsApp CTA ════
const whatsappBtn = document.querySelector('.whatsapp-btn');
if (whatsappBtn) {
  whatsappBtn.addEventListener('click', (e) => {
    e.preventDefault();
    window.open('https://wa.me/919876543210', '_blank');
  });
}

// ════ FEATURE: Mobile Navigation ════

// ════ FEATURE: Smooth Scrolling ════
const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
smoothScrollLinks.forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const targetId = link.getAttribute('href');
    const targetElement = document.querySelector(targetId);
    if (targetElement) {
      targetElement.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

// ════ FEATURE: Scroll Reveal ════

// ════ FEATURE: Sticky Navigation ════
const navElement = document.getElementById('nav');
if (navElement) {
  window.addEventListener('scroll', () => {
    if (window.scrollY > 60) {
      navElement.classList.add('scrolled');
    } else {
      navElement.classList.remove('scrolled');
    }
  });
}

// ════ FEATURE: Active Navigation Highlight ════

if (sections.length > 0 && navMenuLinks.length > 0) {
  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const activeSectionId = entry.target.id;
        navMenuLinks.forEach(link => {
          link.classList.remove('active');
          if (link.getAttribute('href') === `#${activeSectionId}`) {
            link.classList.add('active');
          }
        });
      }
    });
  }, {
    threshold: 0.5
  });
  
  sections.forEach(section => {
    sectionObserver.observe(section);
  });
  
  // Set initial active link based on current scroll position
  const currentSection = Array.from(sections).find(section => {
    const rect = section.getBoundingClientRect();
    return rect.top <= 100 && rect.bottom >= 100;
  });
  
  if (currentSection) {
    const activeSectionId = currentSection.id;
    navMenuLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${activeSectionId}`) {
        link.classList.add('active');
      }
    });
  }
}

// ════ FEATURE: Order Quantity Controls ════
const quantityControls = document.querySelectorAll('.quantity-control');
quantityControls.forEach(control => {
  const input = control.querySelector('input[type="number"]');
  const incrementBtn = control.querySelector('.increment');
  const decrementBtn = control.querySelector('.decrement');
  
  if (input && incrementBtn && decrementBtn) {
    incrementBtn.addEventListener('click', () => {
      const currentValue = parseInt(input.value) || 0;
      if (currentValue < 99) {
        input.value = currentValue + 1;
      }
    });
    
    decrementBtn.addEventListener('click', () => {
      const currentValue = parseInt(input.value) || 0;
      if (currentValue > 1) {
        input.value = currentValue - 1;
      }
    });
    
    // Ensure minimum value
    input.addEventListener('blur', () => {
      const value = parseInt(input.value) || 0;
      if (value < 1) {
        input.value = 1;
      }
    });
    
    // Ensure maximum value
    input.addEventListener('change', () => {
      const value = parseInt(input.value) || 0;
      if (value > 99) {
        input.value = 99;
      }
    });
  }
});

// ════ FEATURE: Form Validation and Submission ════
function handleFormSubmission(form, successMessage) {
  if (!form) return;
  
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    
    // Basic validation
    const formData = new FormData(form);
    const name = formData.get('name');
    const email = formData.get('email');
    const phone = formData.get('phone');
    const message = formData.get('message');
    
    if (!name || !email || !phone || !message) {
      showNotification(form, 'Please fill in all required fields.', 'error');
      return;
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      showNotification(form, 'Please enter a valid email address.', 'error');
      return;
    }
    
    // Phone validation (basic Indian phone number)
    const phoneRegex = /^[6-9]\d{9}$/;
    if (!phoneRegex.test(phone)) {
      showNotification(form, 'Please enter a valid 10-digit phone number.', 'error');
      return;
    }
    
    // Show success message
    showNotification(form, successMessage, 'success');
    
    // Reset form after 2 seconds
    setTimeout(() => {
      form.reset();
    }, 2000);
  });
}

function showNotification(form, message, type) {
  // Remove existing notifications
  const existingNotification = form.parentElement.querySelector('.notification');
  if (existingNotification) {
    existingNotification.remove();
  }
  
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  
  // Insert after form
  form.parentElement.insertBefore(notification, form.nextSibling);
  
  // Remove after 5 seconds
  setTimeout(() => {
    if (notification.parentElement) {
      notification.remove();
    }
  }, 5000);
}

// Initialize form handling
handleFormSubmission(orderForm, 'Order placed successfully! We will contact you soon.');
handleFormSubmission(contactForm, 'Message sent successfully! We will get back to you shortly.');

// ════ FEATURE: WhatsApp CTA ════

// ════ FEATURE: Gallery Lightbox ════

// ════ FEATURE: Price Calculator ════
const productInputs = document.querySelectorAll('.product-input');
productInputs.forEach(input => {
  input.addEventListener('input', (e) => {
    const productRow = e.target.closest('.product-row');
    const quantityInput = productRow.querySelector('.quantity-input');
    const priceInput = productRow.querySelector('.price-input');
    const subtotalInput = productRow.querySelector('.subtotal-input');
    
    if (quantityInput && priceInput && subtotalInput) {
      const quantity = parseFloat(quantityInput.value) || 0;
      const price = parseFloat(priceInput.value) || 0;
      const subtotal = quantity * price;
      
      subtotalInput.value = subtotal.toFixed(2);
    }
  });
});

// ════ FEATURE: Cart Summary Update ════
function updateCartSummary() {
  const cartItems = document.querySelectorAll('.cart-item');
  let totalAmount = 0;
  let totalItems = 0;
  
  cartItems.forEach(item => {
    const quantityInput = item.querySelector('.quantity-input');
    const priceInput = item.querySelector('.price-input');
    const subtotalInput = item.querySelector('.subtotal-input');
    
    if (quantityInput && priceInput && subtotalInput) {
      const quantity = parseFloat(quantityInput.value) || 0;
      const price = parseFloat(priceInput.value) || 0;
      const subtotal = parseFloat(subtotalInput.value) || 0;
      
      totalAmount += subtotal;
      totalItems += quantity;
    }
  });
  
  const totalElement = document.querySelector('.cart-total-amount');
  const itemsElement = document.querySelector('.cart-total-items');
  
  if (totalElement) {
    totalElement.textContent = `₹${totalAmount.toFixed(2)}`;
  }
  
  if (itemsElement) {
    itemsElement.textContent = totalItems;
  }
}

// Add event listeners to update cart summary
document.addEventListener('input', (e) => {
  if (e.target.classList.contains('quantity-input') || 
      e.target.classList.contains('price-input') ||
      e.target.classList.contains('subtotal-input')) {
    updateCartSummary();
  }
});

// ════ FEATURE: Search Functionality ════
const searchInput = document.querySelector('.search-input');
const searchResults = document.querySelector('.search-results');
const searchProducts = document.querySelectorAll('.product-item');

if (searchInput && searchResults) {
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    
    if (query.length < 2) {
      searchResults.innerHTML = '';
      return;
    }
    
    const filteredProducts = Array.from(searchProducts).filter(product => {
      const productName = product.textContent.toLowerCase();
      return productName.includes(query);
    });
    
    if (filteredProducts.length > 0) {
      searchResults.innerHTML = `
        <div class="search-result-header">
          ${filteredProducts.length} products found
        </div>
        ${filteredProducts.map(product => `
          <div class="search-result-item">
            <div class="product-item-content">
              ${product.innerHTML}
            </div>
          </div>
        `).join('')}
      `;
    } else {
      searchResults.innerHTML = '<div class="no-results">No products found</div>';
    }
  });
  
  // Close search results when clicking outside
  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
      searchResults.innerHTML = '';
    }
  });
}

// ════ FEATURE: Product Quick View ════
const quickViewButtons = document.querySelectorAll('.quick-view-btn');
quickViewButtons.forEach(btn => {
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    
    const productId = btn.dataset.productId;
    const product = document.getElementById(`product-${productId}`);
    
    if (product) {
      const quickViewModal = document.createElement('div');
      quickViewModal.className = 'quick-view-modal';
      quickViewModal.innerHTML = `
        <div class="quick-view-content">
          <button class="quick-view-close">&times;</button>
          ${product.innerHTML}
        </div>
      `;
      
      document.body.appendChild(quickViewModal);
      
      quickViewModal.querySelector('.quick-view-close').addEventListener('click', () => {
        quickViewModal.remove();
      });
      
      quickViewModal.addEventListener('click', (e) => {
        if (e.target === quickViewModal) {
          quickViewModal.remove();
        }
      });
    }
  });
});

// ════ FEATURE: Newsletter Subscription ════
const newsletterForm = document.querySelector('.newsletter-form');
const newsletterInput = document.querySelector('.newsletter-input');
const newsletterSuccess = document.querySelector('.newsletter-success');

if (newsletterForm && newsletterInput) {
  newsletterForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const email = newsletterInput.value.trim();
    
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newsletterSuccess.textContent = 'Please enter a valid email address.';
      newsletterSuccess.style.display = 'block';
      return;
    }
    
    newsletterSuccess.textContent = 'Thank you for subscribing!';
    newsletterSuccess.style.display = 'block';
    newsletterForm.reset();
    
    // Hide success message after 5 seconds
    setTimeout(() => {
      newsletterSuccess.style.display = 'none';
    }, 5000);
  });
}

// ════ FEATURE: Product Image Gallery ════
const productGallery = document.querySelectorAll('.product-gallery img');
const galleryNav = document.querySelector('.gallery-nav');

productGallery.forEach((img, index) => {
  img.addEventListener('click', () => {
    const mainImage = document.querySelector('.main-product-image');
    if (mainImage) {
      mainImage.src = img.src;
      mainImage.alt = img.alt;
      
      // Update active state
      productGallery.forEach(galleryImg => {
        galleryImg.classList.remove('active');
      });
      img.classList.add('active');
    }
  });
});

if (galleryNav) {
  const galleryItems = galleryNav.querySelectorAll('.gallery-item');
  galleryItems.forEach((item, index) => {
    item.addEventListener('click', () => {
      const mainImage = document.querySelector('.main-product-image');
      if (mainImage) {
        mainImage.src = item.querySelector('img').src;
        mainImage.alt = item.querySelector('img').alt;
        
        // Update active state
        galleryItems.forEach(galleryItem => {
          galleryItem.classList.remove('active');
        });
        item.classList.add('active');
      }
    });
  });
}

// ════ FEATURE: Wishlist Toggle ════
const wishlistButtons = document.querySelectorAll('.wishlist-btn');
wishlistButtons.forEach(btn => {
  btn.addEventListener('click', (e) => {
    e.preventDefault();