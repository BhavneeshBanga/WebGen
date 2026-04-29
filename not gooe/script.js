// ── FEATURE: Mobile Nav Toggle ──
const navToggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelector('.nav-links');
if(navToggle && navLinks){
  navToggle.addEventListener('click', () => {
    navLinks.classList.toggle('nav-open');
  });
  
  const navLinkItems = document.querySelectorAll('.nav-link');
  if(navLinkItems) {
    navLinkItems.forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('nav-open');
      });
    });
  }
}

// ── FEATURE: Sticky Nav ──
const navbar = document.querySelector('.navbar');
if(navbar){
  window.addEventListener('scroll', () => {
    if(window.scrollY > 60){
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });
}

// ── FEATURE: Smooth Scroll ──
const smoothScrollLinks = document.querySelectorAll('.nav-link[href^="#"]');
if(smoothScrollLinks){
  smoothScrollLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = link.getAttribute('href').substring(1);
      const targetEl = document.getElementById(targetId);
      if(targetEl){
        targetEl.scrollIntoView({behavior: 'smooth', block: 'start'});
      }
    });
  });
}

// ── FEATURE: Scroll Reveal ──
const revealEls = document.querySelectorAll('.reveal');
if(revealEls){
  if(window.IntersectionObserver){
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if(entry.isIntersecting){
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, {threshold: 0.12});
    
    revealEls.forEach(el => observer.observe(el));
  } else {
    revealEls.forEach(el => el.classList.add('visible'));
  }
}

// ── FEATURE: WhatsApp Float Button ──
setTimeout(() => {
  const waFloat = document.createElement('a');
  waFloat.href = 'https://wa.me/919876543210';
  waFloat.className = 'wa-float';
  waFloat.target = '_blank';
  waFloat.setAttribute('aria-label', 'Chat on WhatsApp');
  waFloat.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff">
      <path d="M17.47 15.48c-.28-.22-1.23-.86-1.52-.69-.29.17-.47.44-.47.73 0 .29.18.56.46.68.28.13 1.23.5 1.52.21.29-.29.47-.66.47-.97 0-.29-.18-.56-.46-.68zM20 8.69c1.02.14 1.97.41 2.82.78.32.15.53.42.53.71 0 .29-.18.56-.46.68-.28.13-1.23.5-1.52.21-.29-.29-.47-.66-.47-.97 0-.29.18-.56.46-.68zM13.89 16.17c0-.29-.18-.56-.46-.68-.28-.13-1.23-.5-1.52-.21-.29.29-.47.66-.47.97 0 .29.18.56.46.68.28.13 1.23.5 1.52-.21zM3.53 10.75c-.28-.22-1.23-.86-1.52-.69-.29.17-.47.44-.47.73 0 .29.18.56.46.68.28.13 1.23.5 1.52.21.29-.29.47-.66.47-.97 0-.29-.18-.56-.46-.68zM10.46 16.17c0-.29-.18-.56-.46-.68-.28-.13-1.23-.5-1.52-.21-.29.29-.47.66-.47.97 0 .29.18.56.46.68.28.13 1.23.5 1.52-.21.29-.29.47-.66.47-.97zM4.57 12.92c-.28-.22-1.23-.86-1.52-.69-.29.17-.47.44-.47.73 0 .29.18.56.46.68.28.13 1.23.5 1.52.21.29-.29.47-.66.47-.97 0-.29-.18-.56-.46-.68zM16.38 16.17c0-.29-.18-.56-.46-.68-.28-.13-1.23-.5-1.52-.21-.29.29-.47.66-.47.97 0 .29.18.56.46.68.28.13 1.23.5 1.52-.21.29-.29.47-.66.47-.97z"/>
    </svg>
  `;
  waFloat.style.cssText = `
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: #25D366;
    border-radius: 50%;
    width: 56px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 16px rgba(0,0,0,.25);
    z-index: 9999;
    transition: all .3s ease;
  `;
  waFloat.addEventListener('mouseenter', () => {
    waFloat.style.transform = 'scale(1.1)';
  });
  waFloat.addEventListener('mouseleave', () => {
    waFloat.style.transform = 'scale(1)';
  });
  document.body.appendChild(waFloat);
}, 3000);