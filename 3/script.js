// ════ MOBILE NAV TOGGLE ════
const navToggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelector('.nav-links');

if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    navLinks.classList.toggle('nav-open');
  });
}

// ════ SMOOTH SCROLL ════
const navLinksElements = document.querySelectorAll('.nav-link');
navLinksElements.forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const targetId = link.getAttribute('href');
    if (targetId) {
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth' });
        if (navLinks) {
          navLinks.classList.remove('nav-open');
        }
      }
    }
  });
});

// ════ SCROLL REVEAL ════
if ('IntersectionObserver' in window) {
  const observerOptions = {
    threshold: 0.15
  };
  
  const scrollObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, observerOptions);
  
  const revealElements = document.querySelectorAll('.reveal');
  revealElements.forEach(element => {
    scrollObserver.observe(element);
  });
}

// ════ STICKY NAV ════
const navElement = document.getElementById('nav');
window.addEventListener('scroll', () => {
  if (window.scrollY > 50) {
    if (navElement) {
      navElement.classList.add('scrolled');
    }
  } else {
    if (navElement) {
      navElement.classList.remove('scrolled');
    }
  }
});

// ════ PRODUCT FILTER ════
const productFilter = document.querySelector('.product-filter');
const productCards = document.querySelectorAll('.product-card');
const categoryButtons = document.querySelectorAll('.product-filter-btn');

if (productFilter && productCards && categoryButtons) {
  const filterProducts = (category) => {
    productCards.forEach(card => {
      const cardCategory = card.dataset.category;
      if (category === 'all' || cardCategory === category) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });
  };
  
  categoryButtons.forEach(button => {
    button.addEventListener('click', () => {
      categoryButtons.forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');
      filterProducts(button.dataset.category);
    });
  });
}

// ════ CART COUNTER ════
let cartCount = 0;
const cartItems = document.querySelectorAll('.cart-item');
const cartButtons = document.querySelectorAll('.add-to-cart');

if (cartButtons) {
  cartButtons.forEach(button => {
    button.addEventListener('click', () => {
      cartCount++;
      updateCartCounter();
    });
  });
}

const updateCartCounter = () => {
  const counterElement = document.querySelector('.cart-counter');
  if (counterElement) {
    counterElement.textContent = cartCount;
  }
};

// ════ SEARCH FUNCTIONALITY ════
const searchInput = document.querySelector('.search-input');
const searchResults = document.querySelector('.search-results');

if (searchInput && searchResults) {
  const products = Array.from(document.querySelectorAll('.product-card')).map(card => ({
    name: card.querySelector('.product-name')?.textContent || '',
    category: card.dataset.category || '',
    price: card.querySelector('.product-price')?.textContent || ''
  }));
  
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    const filteredProducts = products.filter(product => 
      product.name.toLowerCase().includes(query) ||
      product.category.toLowerCase().includes(query)
    );
    
    if (filteredProducts.length > 0) {
      displaySearchResults(filteredProducts);
    } else {
      searchResults.innerHTML = '<div class="search-result">No products found</div>';
    }
  });
  
  const displaySearchResults = (results) => {
    searchResults.innerHTML = results.map(product => `
      <div class="search-result">
        <div class="product-name">${product.name}</div>
        <div class="product-price">${product.price}</div>
      </div>
    `).join('');
  };
}

// ════ CATEGORY FILTER ════
const categoryCards = document.querySelectorAll('.category-card');
const categoryGrid = document.querySelector('.category-grid');

if (categoryCards && categoryGrid) {
  const filterByCategory = (selectedCategory) => {
    categoryCards.forEach(card => {
      const cardCategory = card.dataset.category;
      if (cardCategory === selectedCategory) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });
  };
  
  categoryCards.forEach(card => {
    card.addEventListener('click', () => {
      categoryCards.forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      filterByCategory(card.dataset.category);
    });
  });
}

// ════ ACTIVE NAV HIGHLIGHT ════
const sections = document.querySelectorAll('section[id]');
const navLinksForSections = document.querySelectorAll('.nav-link[href^="#"]');

if (sections.length && navLinksForSections.length) {
  const activeObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navLinksForSections.forEach(link => {
          link.classList.remove('active');
        });
        const activeLink = document.querySelector(`.nav-link[href="#${entry.target.id}"]`);
        if (activeLink) {
          activeLink.classList.add('active');
        }
      }
    });
  }, { threshold: 0.5 });
  
  sections.forEach(section => {
    activeObserver.observe(section);
  });
}

// ════ FORM VALIDATION ════
const contactForm = document.querySelector('.contact-form');
const emailInput = document.querySelector('.email-input');

if (contactForm && emailInput) {
  contactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = emailInput.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!emailRegex.test(email)) {
      emailInput.classList.add('error');
      return;
    }
    
    emailInput.classList.remove('error');
    // Form submission logic here
  });
  
  emailInput.addEventListener('blur', () => {
    const email = emailInput.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
      emailInput.classList.add('error');
    } else if (email) {
      emailInput.classList.remove('error');
    }
  });
}

// ════ ACCORDION FOR DELIVERY INFO ════
const accordionHeaders = document.querySelectorAll('.delivery-header');

accordionHeaders.forEach(header => {
  header.addEventListener('click', () => {
    const content = header.nextElementSibling;
    if (content) {
      content.classList.toggle('active');
    }
  });
});

// ════ AUTOCOMPLETE FOR SEARCH ════
if (searchInput) {
  const allProductNames = Array.from(document.querySelectorAll('.product-card')).map(card => 
    card.querySelector('.product-name')?.textContent || ''
  );
  
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    const suggestions = allProductNames.filter(name => 
      name.toLowerCase().startsWith(query)
    ).slice(0, 5);
    
    if (suggestions.length > 0) {
      const suggestionsContainer = document.createElement('div');
      suggestionsContainer.className = 'search-suggestions';
      suggestionsContainer.innerHTML = suggestions.map(suggestion => 
        `<div class="search-suggestion">${suggestion}</div>`
      ).join('');
      
      // Position suggestions near input
      searchInput.parentNode.appendChild(suggestionsContainer);
    }
  });
}

// ════ LAZY LOADING FOR IMAGES ════
const images = document.querySelectorAll('img[data-src]');

if ('IntersectionObserver' in window) {
  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.remove('lazy');
        imageObserver.unobserve(img);
      }
    });
  });
  
  images.forEach(img => imageObserver.observe(img));
}
// ════ MOBILE NAV TOGGLE ════
if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    navLinks.classList.toggle('nav-open');
  });
}

// ════ SMOOTH SCROLL ════
const navLinksSmooth = document.querySelectorAll('.nav-link');

navLinksSmooth.forEach(link => {
  if (link) {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = link.getAttribute('href');
      if (targetId && targetId.startsWith('#')) {
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
          targetElement.scrollIntoView({ behavior: 'smooth' });
        }
      }
    });
  }
});

// ════ SCROLL REVEAL ════
const revealElements = document.querySelectorAll('.reveal');

if ('IntersectionObserver' in window && revealElements.length > 0) {
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });

  revealElements.forEach(element => revealObserver.observe(element));
}

// ════ STICKY NAV ════
window.addEventListener('scroll', () => {
  const navElement = document.querySelector('#nav');
  if (navElement) {
    if (window.scrollY > 50) {
      navElement.classList.add('scrolled');
    } else {
      navElement.classList.remove('scrolled');
    }
  }
});

// ════ PRODUCT FILTER ════
if (productFilter && productCards.length > 0) {
  productFilter.addEventListener('change', (e) => {
    const selectedCategory = e.target.value;
    
    productCards.forEach(card => {
      const cardCategory = card.dataset.category;
      if (selectedCategory === 'all' || cardCategory === selectedCategory) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });
  });
}

// ════ CART COUNTER ════
if (cartCount) {
  let cartCountValue = 0;
  
  const addToCartButtons = document.querySelectorAll('.add-to-cart');
  
  addToCartButtons.forEach(button => {
    if (button) {
      button.addEventListener('click', () => {
        cartCountValue++;
        cartCount.textContent = cartCountValue;
        
        // Add animation effect
        cartCount.classList.add('count-animation');
        setTimeout(() => {
          cartCount.classList.remove('count-animation');
        }, 300);
      });
    }
  });
}

// ════ SEARCH FUNCTIONALITY ════

if (searchInput) {
  const allProducts = Array.from(document.querySelectorAll('.product-card'));
  
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    
    if (query.length === 0) {
      if (searchResultsContainer) {
        searchResultsContainer.innerHTML = '';
      }
      return;
    }
    
    const filteredProducts = allProducts.filter(product => {
      const productName = product.querySelector('.product-name')?.textContent || '';
      const productDescription = product.querySelector('.product-description')?.textContent || '';
      
      return productName.toLowerCase().includes(query) || 
             productDescription.toLowerCase().includes(query);
    });
    
    if (searchResultsContainer) {
      searchResultsContainer.innerHTML = filteredProducts.map(product => `
        <div class="search-result-item">
          ${product.innerHTML}
        </div>
      `).join('');
    }
  });
}

// ════ CATEGORY FILTER ════

if (categoryCards.length > 0) {
  const filterContainer = document.querySelector('.filter-container');
  
  filterButtons.forEach(button => {
    if (button) {
      button.addEventListener('click', () => {
        const category = button.dataset.category;
        
        categoryCards.forEach(card => {
          const cardCategory = card.dataset.category;
          if (category === 'all' || cardCategory === category) {
            card.classList.add('active');
          } else {
            card.classList.remove('active');
          }
        });
        
        // Update button states
        filterButtons.forEach(btn => {
          if (btn.dataset.category === category) {
            btn.classList.add('active');
          } else {
            btn.classList.remove('active');
          }
        });
      });
    }
  });
}