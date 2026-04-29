// ════ MOBILE NAV ════
const navToggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelector('.nav-links');
if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    navLinks.classList.toggle('nav-open');
    navToggle.classList.toggle('active');
  });
}

// ════ SMOOTH SCROLL ════
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', e => {
    const href = link.getAttribute('href');
    if (href && href.startsWith('#')) {
      e.preventDefault();
      const target = document.querySelector(href);
      if (target) target.scrollIntoView({ behavior: 'smooth' });
      if (navLinks) navLinks.classList.remove('nav-open');
      if (navToggle) navToggle.classList.remove('active');
    }
  });
});

// ════ STICKY NAV ════
const nav = document.querySelector('#nav');
window.addEventListener('scroll', () => {
  if (nav) nav.classList.toggle('scrolled', window.scrollY > 50);
});

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
  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
}

// ════ PRODUCT FILTER ════
const productCategories = document.querySelectorAll('.product-category');
const productCards = document.querySelectorAll('.product-card');
if (productCategories.length && productCards.length) {
  productCategories.forEach(category => {
    category.addEventListener('click', () => {
      productCategories.forEach(cat => cat.classList.remove('active'));
      category.classList.toggle('active');
      
      const categoryName = category.textContent.toLowerCase();
      productCards.forEach(card => {
        const cardCategory = card.querySelector('.product-category')?.textContent.toLowerCase();
        if (categoryName === 'all' || cardCategory === categoryName) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
}

// ════ CART COUNTER ════
let cartCount = 0;
const addToCartButtons = document.querySelectorAll('.add-to-cart');
const cartCounter = document.querySelector('.cart-counter');
if (addToCartButtons.length) {
  addToCartButtons.forEach(button => {
    button.addEventListener('click', () => {
      cartCount++;
      if (cartCounter) cartCounter.textContent = cartCount;
      
      // Add animation
      button.classList.add('added');
      setTimeout(() => button.classList.remove('added'), 300);
    });
  });
}

// ════ SPECIAL FILTER ════
const specialItems = document.querySelectorAll('.special-item');
if (specialItems.length) {
  specialItems.forEach(item => {
    item.addEventListener('mouseenter', () => {
      item.classList.add('highlighted');
    });
    item.addEventListener('mouseleave', () => {
      item.classList.remove('highlighted');
    });
  });
}

// ════ DELIVERY HOURS ════
const deliveryHours = document.querySelector('.delivery-hours');
const currentDay = new Date().getDay();
const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const hours = {
  1: { open: '9:00 AM', close: '10:00 PM' },
  2: { open: '9:00 AM', close: '10:00 PM' },
  3: { open: '9:00 AM', close: '10:00 PM' },
  4: { open: '9:00 AM', close: '10:00 PM' },
  5: { open: '9:00 AM', close: '10:00 PM' },
  6: { open: '9:00 AM', close: '9:00 PM' },
  0: { open: 'Closed', close: 'Closed' }
};
if (deliveryHours) {
  const dayHours = hours[currentDay];
  deliveryHours.innerHTML = `<strong>${days[currentDay]}:</strong> ${dayHours.open} - ${dayHours.close}`;
}

// ════ ACTIVE NAV HIGHLIGHT ════
if ('IntersectionObserver' in window) {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
  
  const navObserver = new IntersectionObserver(entries => {
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
  }, { threshold: 0.5 });
  
  sections.forEach(section => {
    navObserver.observe(section);
  });
}

// ════ FAQ ACCORDION ════
const faqItems = document.querySelectorAll('.faq-item');
if (faqItems.length) {
  faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    const answer = item.querySelector('.faq-answer');
    
    if (question && answer) {
      question.addEventListener('click', () => {
        const isActive = item.classList.contains('active');
        
        // Close other accordions
        faqItems.forEach(other => {
          if (other !== item) other.classList.remove('active');
        });
        
        // Toggle current accordion
        if (!isActive) {
          item.classList.add('active');
          answer.style.display = 'block';
        } else {
          item.classList.remove('active');
          answer.style.display = 'none';
        }
      });
    }
  });
}

// ════ SEARCH FUNCTIONALITY ════
const searchInput = document.querySelector('.search-input');
const searchResults = document.querySelector('.search-results');
if (searchInput && searchResults) {
  let searchTimeout;
  
  searchInput.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    const query = e.target.value.toLowerCase();
    
    searchTimeout = setTimeout(() => {
      if (query.length > 2) {
        // Filter products based on search query
        productCards.forEach(card => {
          const productName = card.querySelector('.product-name')?.textContent.toLowerCase();
          const productCategory = card.querySelector('.product-category')?.textContent.toLowerCase();
          
          if (productName && (productName.includes(query) || productCategory.includes(query))) {
            card.style.display = 'block';
          } else {
            card.style.display = 'none';
          }
        });
      } else {
        // Reset all products
        productCards.forEach(card => {
          const category = card.querySelector('.product-category')?.textContent.toLowerCase();
          if (category === 'all' || !category) {
            card.style.display = 'block';
          }
        });
      }
    }, 300);
  });
}

// ════ CART ANIMATION ════
const cartIcon = document.querySelector('.cart-icon');
if (cartIcon && cartCount > 0) {
  cartIcon.classList.add('has-items');
  
  // Add pulse animation
  setInterval(() => {
    if (cartCount > 0) {
      cartIcon.classList.add('pulse');
      setTimeout(() => cartIcon.classList.remove('pulse'), 500);
    }
  }, 2000);
}

// ════ PRODUCT QUICK VIEW ════
const quickViewButtons = document.querySelectorAll('.quick-view');
if (quickViewButtons.length) {
  quickViewButtons.forEach(button => {
    button.addEventListener('click', (e) => {
      e.preventDefault();
      const productId = button.dataset.productId;
      const product = productCards.find(card => card.dataset.productId === productId);
      
      if (product) {
        // Create quick view modal
        const modal = document.createElement('div');
        modal.className = 'quick-view-modal';
        modal.innerHTML = `
          <div class="modal-content">
            <span class="close">&times;</span>
            <img src="${product.querySelector('.product-image')?.src}" alt="${product.querySelector('.product-name')?.textContent}">
            <h2>${product.querySelector('.product-name')?.textContent}</h2>
            <p>${product.querySelector('.product-price')?.textContent}</p>
            <button class="add-to-cart-modal">Add to Cart</button>
          </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add modal styles
        modal.style.cssText = `
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0,0,0,0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        `;
        
        // Close modal
        modal.querySelector('.close').addEventListener('click', () => {
          document.body.removeChild(modal);
        });
        
        modal.addEventListener('click', (e) => {
          if (e.target === modal) {
            document.body.removeChild(modal);
          }
        });
        
        // Add to cart in modal
        modal.querySelector('.add-to-cart-modal').addEventListener('click', () => {
          cartCount++;
          if (cartCounter) cartCounter.textContent = cartCount;
          document.body.removeChild(modal);
        });
      }
    });
  });
}

// ════ PRODUCT IMAGE SWAP ════
const productImages = document.querySelectorAll('.product-image');
if (productImages.length) {
  productImages.forEach(img => {
    const thumbnails = img.parentElement?.querySelectorAll('.thumbnail');
    if (thumbnails) {
      thumbnails.forEach(thumb => {
        thumb.addEventListener('click', () => {
          const mainImg = img.querySelector('img');
          const thumbImg = thumb.querySelector('img');
          
          if (mainImg && thumbImg) {
            mainImg.src = thumbImg.src;
            mainImg.classList.add('swapped');
            setTimeout(() => mainImg.classList.remove('swapped'), 300);
          }
        });
      });
    }
  });
}

// ════ DELIVERY STATUS INDICATOR ════
const deliveryStatus = document.querySelector('.delivery-status');
if (deliveryStatus) {
  const isDeliveryTime = (new Date().getHours() >= 9 && new Date().getHours() <= 22);
  deliveryStatus.textContent = isDeliveryTime ? 'Delivery Available Now' : 'Delivery Available 9 AM - 10 PM';
  deliveryStatus.className = isDeliveryTime ? 'delivery-active' : 'delivery-inactive';
}

// ════ PRODUCT RATING ════
const ratings = document.querySelectorAll('.rating-star');
if (ratings.length) {
  ratings.forEach(star => {
    star.addEventListener('click', () => {
      const productId = star.dataset.productId;
      // Store rating in localStorage or send to server
      const currentRating = localStorage.getItem(`rating_${productId}`) || 0;
      localStorage.setItem(`rating_${productId}`, star.dataset.rating);
      
      // Show feedback
      const feedback = document.createElement('div');
      feedback.className = 'rating-feedback';
      feedback.textContent = `Rating: ${star.dataset.rating} stars`;
      star.appendChild(feedback);
      
      setTimeout(() => {
        feedback.remove();
      }, 2000);
    });
  });
}

// ════ PRODUCT COMPARISON ════
const compareButtons = document.querySelectorAll('.compare-button');
if (compareButtons.length) {
  const compareItems = new Set();
  
  compareButtons.forEach(button => {
    button.addEventListener('click', () => {
      const productId = button.dataset.productId;
      
      if (compareItems.has(productId)) {
        compareItems.delete(productId);
        button.classList.remove('comparing');
      } else {
        compareItems.add(productId);
        button.classList.add('comparing');
        
        if (compareItems.size > 2) {
          const firstItem = compareItems.values().next().value;
          const secondItem = compareItems.values().next().value;
          compareItems.delete(firstItem);
          
          // Show comparison modal
          const modal = document.createElement('div');
          modal.className = 'compare-modal';
          modal.innerHTML = `
            <div class="modal-content">
              <span class="close">&times;</span>
              <h2>Compare Products</h2>
              <div class="compare-items">
                <!-- Comparison content -->
              </div>
            </div>
          `;
          
          document.body.appendChild(modal);
        }
      }
    });
  });
}

// ════ PRODUCT RECOMMENDATIONS ════
const recommendationSection = document.querySelector('.recommendations');
if (recommendationSection && productCards.length) {
  // Simple recommendation logic based on product categories
  const popularCategories = {};
  productCards.forEach(card => {
    const category = card.querySelector('.product-category')?.textContent;
    if (category) {
      popularCategories[category] = (popularCategories[category] || 0) + 1;
    }
  });
  
  const sortedCategories = Object.entries(popularCategories)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3);
  
  if (sortedCategories.length > 0) {
    recommendationSection.innerHTML = `
      <h3>Recommended for You</h3>
      <div class="recommendations-grid">
        ${sortedCategories.map(([category]) => `
          <div class="recommendation-card">
            <h4>${category}</h4>
            <p>Popular in this category</p>
          </div>
        `).join('')}
      </div>
    `;
  }
}

// ════ CART REMINDER ════
const cartReminder = document.querySelector('.cart-reminder');
if (cartReminder && cartCount > 0) {
  // Show reminder when cart has items but user is idle
  let idleTime = 0;
  const resetIdleTime = () => { idleTime = 0; };
  
  document.addEventListener('mousemove', resetIdleTime);
  
  setInterval(() => {
    idleTime++;
    if (idleTime > 30 && cartCount > 0) {
      cartReminder.classList.add('show');
      setTimeout(() => {
        cartReminder.classList.remove('show');
      }, 5000);
    }
  }, 1000);
}

// ════ PRODUCT STOCK INDICATOR ════
const stockIndicators = document.querySelectorAll('.stock-indicator');
if (stockIndicators.length) {
  stockIndicators.forEach(indicator => {
    const stock = parseInt(indicator.dataset.stock);
    const maxStock = parseInt(indicator.dataset.maxStock) || 100;
    const percentage = (stock / maxStock) * 100;
    
    indicator.style.width = `${percentage}%`;
    indicator.style.background = percentage > 50 ? '#27AE60' : 
                                 percentage > 20 ? '#F39C12' : 
indicator.style.background = percentage > 50 ? '#27AE60' : 
                                 percentage > 20 ? '#F39C12' : '#E74C3C';
    });
  }


// ════ PRODUCT FILTER ════
const productCategories = document.querySelectorAll('.product-category');
const products = document.querySelectorAll('.product-item');
let currentCategory = 'all';

if (productCategories.length && products.length) {
  productCategories.forEach(category => {
    category.addEventListener('click', () => {
      currentCategory = category.dataset.category;
      products.forEach(product => {
        const productCategory = product.dataset.category;
        product.style.display = currentCategory === 'all' || productCategory === currentCategory ? '' : 'none';
      });
      productCategories.forEach(cat => cat.classList.remove('active'));
      category.classList.add('active');
    });
  });
}

// ════ CART COUNTER ════
const addToCartButtons = document.querySelectorAll('.add-to-cart');
let cartCount = 0;

if (addToCartButtons) {
  addToCartButtons.forEach(button => {
    button.addEventListener('click', () => {
      cartCount++;
      updateCartUI();
    });
  });
}

function updateCartUI() {
  const cartCountElement = document.querySelector('.cart-count');
  if (cartCountElement) {
    cartCountElement.textContent = cartCount;
  }
  
  const cartIcon = document.querySelector('.cart-icon');
  if (cartIcon) {
    cartIcon.classList.add('has-items');
  }
}

// ════ SPECIAL FILTER ════
const specialItems = document.querySelectorAll('.special-item');
if (specialItems.length) {
  specialItems.forEach(item => {
    item.addEventListener('mouseenter', () => {
      item.classList.add('highlighted');
    });
    
    item.addEventListener('mouseleave', () => {
      item.classList.remove('highlighted');
    });
  });
}

// ════ DELIVERY HOURS ════
const deliveryHoursElement = document.querySelector('.delivery-hours');
const deliveryStatus = {
  morning: '7:00 AM - 11:00 AM',
  afternoon: '12:00 PM - 4:00 PM',
  evening: '5:00 PM - 9:00 PM'
};

if (deliveryHoursElement) {
  const currentHour = new Date().getHours();
  let currentStatus = '';
  
  if (currentHour >= 7 && currentHour < 11) {
    currentStatus = deliveryStatus.morning;
  } else if (currentHour >= 12 && currentHour < 16) {
    currentStatus = deliveryStatus.afternoon;
  } else if (currentHour >= 17 && currentHour < 21) {
    currentStatus = deliveryStatus.evening;
  } else {
    currentStatus = 'Closed - Order for next available slot';
  }
  
  deliveryHoursElement.innerHTML = `
    <p>Current Status: <strong>${currentStatus}</strong></p>
    <p>Mon-Sat: ${deliveryStatus.morning} - ${deliveryStatus.evening}</p>
    <p>Sunday: Closed</p>
  `;
}

// ════ CART REMINDER ════
const cartReminder = document.querySelector('.cart-reminder');
if (cartReminder && cartCount > 0) {
  // Show reminder when cart has items but user is idle
  let idleTime = 0;
  const resetIdleTime = () => { idleTime = 0; };
  
  document.addEventListener('mousemove', resetIdleTime);
  
  setInterval(() => {
    idleTime++;
    if (idleTime > 30 && cartCount > 0) {
      cartReminder.classList.add('show');
      setTimeout(() => {
        cartReminder.classList.remove('show');
      }, 5000);
    }
  }, 1000);
}

// ════ PRODUCT STOCK INDICATOR ════
const stockIndicators = document.querySelectorAll('.stock-indicator');
if (stockIndicators.length) {
  stockIndicators.forEach(indicator => {
    const stock = parseInt(indicator.dataset.stock);
    const maxStock = parseInt(indicator.dataset.maxStock) || 100;
    const percentage = (stock / maxStock) * 100;
    
    indicator.style.width = `${percentage}%`;
    indicator.style.background = percentage > 50 ? '#27AE60' : 
                                 percentage > 20 ? '#F39C12' : '#E74C3C';
  });
}