// ════ FEATURE NAME ════ Mobile Nav Toggle
const navToggleEl = document.querySelector('.nav-toggle');
const navLinksEl = document.querySelector('.nav-links');
if (navToggleEl && navLinksEl) {
  navToggleEl.addEventListener('click', () => {
    navLinksEl.classList.toggle('nav-open');
  });
}

// ════ FEATURE NAME ════ Smooth Scroll
const navLinkEls = document.querySelectorAll('.nav-link');
navLinkEls.forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const targetId = link.getAttribute('href');
    const targetEl = document.querySelector(targetId);
    if (targetEl) {
      targetEl.scrollIntoView({ behavior: 'smooth' });
    }
    if (navLinksEl) {
      navLinksEl.classList.remove('nav-open');
    }
  });
});

// ════ FEATURE NAME ════ Scroll Reveal
const revealEls = document.querySelectorAll('.reveal');
if (typeof IntersectionObserver !== 'undefined') {
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });
  revealEls.forEach(el => revealObserver.observe(el));
}

// ════ FEATURE NAME ════ Sticky Nav
const navEl = document.querySelector('#nav');
if (navEl) {
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      navEl.classList.add('scrolled');
    } else {
      navEl.classList.remove('scrolled');
    }
  });
}

// ════ FEATURE NAME ════ Gallery Lightbox
const galleryItemEls = document.querySelectorAll('.gallery-item');
let currentLightboxIndex = 0;
const lightboxContainerEl = document.createElement('div');
lightboxContainerEl.className = 'lightbox-container';
document.body.appendChild(lightboxContainerEl);

galleryItemEls.forEach((item, index) => {
  item.addEventListener('click', () => {
    const imgEl = item.querySelector('img');
    if (imgEl) {
      lightboxContainerEl.innerHTML = `
        <img src="${imgEl.src}" alt="" class="lightbox-image">
        <button class="lightbox-close">×</button>
      `;
      currentLightboxIndex = index;
      lightboxContainerEl.classList.add('active');
      document.body.style.overflow = 'hidden';
      lightboxContainerEl.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
      lightboxContainerEl.addEventListener('click', (e) => {
        if (e.target === lightboxContainerEl) closeLightbox();
        else handleLightboxNav(e);
      });
      document.addEventListener('keydown', handleKeydown);
    }
  });
});

function closeLightbox() {
  lightboxContainerEl.classList.remove('active');
  document.body.style.overflow = '';
  document.removeEventListener('keydown', handleKeydown);
  lightboxContainerEl.innerHTML = '';
}

function handleLightboxNav(e) {
  if (e.target === lightboxContainerEl.querySelector('.lightbox-close')) return;
  const navBtn = e.target;
  if (navBtn.textContent === '❮') {
    currentLightboxIndex = (currentLightboxIndex - 1 + galleryItemEls.length) % galleryItemEls.length;
  } else if (navBtn.textContent === '❯') {
    currentLightboxIndex = (currentLightboxIndex + 1) % galleryItemEls.length;
  }
  updateLightboxImage();
}

function handleKeydown(e) {
  if (e.key === 'Escape') closeLightbox();
}

function updateLightboxImage() {
  const imgEl = lightboxContainerEl.querySelector('.lightbox-image');
  const navBtns = lightboxContainerEl.querySelectorAll('.lightbox-nav');
  const galleryItem = galleryItemEls[currentLightboxIndex];
  if (galleryItem && imgEl) {
    const src = galleryItem.querySelector('img').src;
    imgEl.src = src;
    navBtns[0].onclick = () => { currentLightboxIndex = (currentLightboxIndex - 1 + galleryItemEls.length) % galleryItemEls.length; updateLightboxImage(); };
    navBtns[1].onclick = () => { currentLightboxIndex = (currentLightboxIndex + 1) % galleryItemEls.length; updateLightboxImage(); };
  }
}

// ════ FEATURE NAME ════ Menu Filter
const filterBtns = document.querySelectorAll('.filter-button');
const menuItems = document.querySelectorAll('.menu-item');

filterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const filterType = btn.dataset.filter;
    menuItems.forEach(item => {
      const itemType = item.dataset.type;
      if (filterType === 'all' || itemType === filterType) {
        item.style.display = 'block';
      } else {
        item.style.display = 'none';
      }
    });
    filterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  });
});

// ════ FEATURE NAME ════ Order Form Submit
const orderFormEl = document.querySelector('.order-form');
const orderSubmitBtn = document.querySelector('.order-submit');

if (orderFormEl && orderSubmitBtn) {
  orderFormEl.addEventListener('submit', (e) => {
    e.preventDefault();
    const formData = new FormData(orderFormEl);
    const items = Array.from(orderFormEl.querySelectorAll('.order-item'));
    let isValid = true;
    items.forEach(item => {
      const quantityEl = item.querySelector('.order-quantity');
      const quantity = parseInt(quantityEl.value, 10);
      if (quantity <= 0) {
        isValid = false;
        quantityEl.classList.add('error');
      } else {
        quantityEl.classList.remove('error');
      }
    });
    if (isValid) {
      const orderData = {
        ...Object.fromEntries(formData.entries()),
        items: items.map(item => ({
          name: item.dataset.name,
          quantity: parseInt(item.querySelector('.order-quantity').value, 10)
        }))
      };
      console.log('Order submitted:', orderData);
      alert('Order submitted successfully! We will contact you soon.');
      orderFormEl.reset();
    }
  });
}

// ════ FEATURE NAME ════ Active Nav Link Highlighting
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-link');

const activeLinkObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      navLinks.forEach(link => link.classList.remove('active'));
      const activeLink = document.querySelector(`.nav-link[href="${entry.target.id}"]`);
      if (activeLink) activeLink.classList.add('active');
    }
  });
}, { threshold: 0.5 });

sections.forEach(section => activeLinkObserver.observe(section));

// ════ FEATURE NAME ════ Page-Specific Feature: Order Counter
const orderQuantityEls = document.querySelectorAll('.order-quantity');
orderQuantityEls.forEach(input => {
  input.addEventListener('input', () => {
    const counterEl = input.parentElement.querySelector('.order-counter');
    if (counterEl) {
      const value = parseInt(input.value, 10) || 0;
      counterEl.textContent = value;
    }
  });
});

// ════ FEATURE NAME ════ Page-Specific Feature: Accordion for About Stats
const statItems = document.querySelectorAll('.about-stats .stat-item');
statItems.forEach(item => {
  const header = item.querySelector('.stat-header');
  const content = item.querySelector('.stat-content');
  if (header && content) {
    header.addEventListener('click', () => {
      content.classList.toggle('active');
      header.classList.toggle('active');
    });
  }
});

// ════ FEATURE NAME ════ Page-Specific Feature: Social Media Link Opening
const socialLinks = document.querySelectorAll('.social-link');
socialLinks.forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const url = link.getAttribute('href');
    if (url && url.startsWith('http')) {
      window.open(url, '_blank');
    }
  });
});
// ════ FEATURE NAME ════ Mobile Nav Toggle

// ════ FEATURE NAME ════ Smooth Scroll

// ════ FEATURE NAME ════ Scroll Reveal

// ════ FEATURE NAME ════ Sticky Nav

// ════ FEATURE NAME ════ Gallery Lightbox
const galleryItems = document.querySelectorAll('.gallery-item');
if (galleryItems.length > 0) {
  const lightboxEl = document.createElement('div');
  lightboxEl.className = 'lightbox';
  lightboxEl.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.9);
    display: none;
    z-index: 1000;
    align-items: center;
    justify-content: center;
  `;
  
  const lightboxImg = document.createElement('img');
  lightboxImg.style.cssText = `
    max-width: 90%;
    max-height: 90%;
    border-radius: 8px;
  `;
  
  lightboxEl.appendChild(lightboxImg);
  document.body.appendChild(lightboxEl);
  
  galleryItems.forEach(item => {
    if (item) {
      const img = item.querySelector('img');
      if (img) {
        item.addEventListener('click', () => {
          lightboxImg.src = img.src;
          lightboxEl.style.display = 'flex';
          document.body.style.overflow = 'hidden';
        });
      }
    }
  });
  
  const closeLightbox = () => {
    lightboxEl.style.display = 'none';
    document.body.style.overflow = '';
  };
  
  lightboxEl.addEventListener('click', closeLightbox);
  
  const escapeHandler = (e) => {
    if (e.key === 'Escape') closeLightbox();
  };
  
  document.addEventListener('keydown', escapeHandler);
}

// ════ FEATURE NAME ════ Menu Filter
const filterButtons = document.querySelectorAll('.filter-button');

// ════ FEATURE NAME ════ Order Form Submit
if (orderSubmitBtn && orderForm) {
  orderSubmitBtn.addEventListener('click', (e) => {
    e.preventDefault();
    
    const formData = new FormData(orderForm);
    const name = formData.get('name');
    const phone = formData.get('phone');
    const email = formData.get('email');
    const items = formData.querySelectorAll('input[type="checkbox"]:checked');
    
    if (!name || !phone) {
      alert('Please fill in your name and phone number');
      return;
    }
    
    if (!/^[\d\s\-\+\(\)]+$/.test(phone)) {
      alert('Please enter a valid phone number');
      return;
    }
    
    const orderData = {
      name,
      phone,
      email: email || '',
      items: Array.from(items).map(item => ({
        name: item.dataset.itemName,
        quantity: item.value || 1
      }))
    };
    
    const orderSummary = document.querySelector('.order-summary');
    if (orderSummary) {
      orderSummary.innerHTML = `
        <h3>Order Summary</h3>
        <p><strong>Name:</strong> ${name}</p>
        <p><strong>Phone:</strong> ${phone}</p>
        ${email ? `<p><strong>Email:</strong> ${email}</p>` : ''}
        <p><strong>Items:</strong></p>
        <ul>
          ${orderData.items.map(item => `
            <li>${item.name} - ${item.quantity}</li>
          `).join('')}
        </ul>
        <p><strong>Total:</strong> $${(orderData.items.length * 20).toFixed(2)}</p>
      `;
      
      orderSummary.style.display = 'block';
      orderForm.reset();
      
      // Simulate form submission
      fetch('/api/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData)
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          alert('Order placed successfully! Confirmation sent to your email.');
          orderSummary.innerHTML = '<p>Thank you for your order! We will contact you shortly.</p>';
        } else {
          alert('Order failed. Please try again.');
        }
      })
      .catch(error => {
        console.error('Order submission error:', error);
        alert('Order failed. Please try again.');
      });
    }
  });
}