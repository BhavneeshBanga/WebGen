## 1. BUSINESS ANALYSIS
- **Business type:** Neighborhood grocery & essentials store (Kirana). Sells fresh produce, staples, dairy, personal care, and household items.
- **Target customers:** Local residents within a 1-2 km radius, primarily families (age 25-65). Middle-to-lower-middle income, value-conscious, and prioritize freshness and trust. Habitually walk or cycle to the store. Use WhatsApp for communication.
- **Emotion to evoke:** Trust & Familiarity. The feeling of a reliable neighbor who knows your family's preferences and offers credit (`udhaar`) when needed.
- **Primary action wanted:** Initiate a WhatsApp order for home delivery or pickup. Secondary action is to find the store location.
- **USP:** Your Trusted Neighborhood Partner for Daily Needs. Emphasizes personal service, fresh produce, credit facility for regulars, and the convenience of a walk-in store that also delivers.

## 2. BRAND IDENTITY
- **Tone of voice:** Warm, helpful, and familiar. A mix of Hindi-English (Hinglish) that feels like talking to a neighbor (e.g., "Fresh sabzi, ghar tak delivery!"). Avoids corporate jargon.
- **Color palette:**
    - **Deep Green (#135E11):** Represents freshness, nature, and trust. Used for primary text and key icons.
    - **Saffron (#FF9933):** Represents tradition, purity, and energy. Used for accents like buttons and highlights.
    - **Turmeric Gold (#FFC300):** Represents prosperity, health, and warmth. Used for call-to-action buttons and special offers.
    - **Cream (#F5F5DC):** A warm, off-white for the background, conveying cleanliness and a welcoming feel.
- **Typography pair:**
    - **Headings:** Merriweather (Serif) - Evokes tradition, reliability, and a sense of established trust.
    - **Body:** Open Sans (Sans-serif) - Highly legible on mobile screens, ensuring ease of reading for all age groups.
- **Visual metaphors:** A friendly hand holding a basket of fresh vegetables; a simple, clean icon of a mortar and pestle (`sil-batta`); a stylized, warmly-lit storefront.

## 3. WEBSITE SECTIONS
- **nav:**
    - **Purpose:** Provide simple, clear navigation to key information.
    - **CSS class names:** `.main-nav`, `.nav-item`, `.nav-link`
    - **Elements:** Logo (store name), Home, About, Menu, Contact.
    - **Emotional goal:** Clarity and ease of use.
- **hero:**
    - **Purpose:** Make a strong first impression and state the core value proposition immediately.
    - **CSS class names:** `.hero-section`, `.hero-headline`, `.cta-button`
    - **Elements:** High-quality photo of the store's exterior, store name, headline "Your Daily Needs, Delivered," prominent WhatsApp icon with "Order Now" text.
    - **Emotional goal:** Instant trust and a clear call to action.
- **about/story:**
    - **Purpose:** Build a personal connection and humanize the business.
    - **CSS class names:** `.about-section`, `.owner-photo`, `.about-text`
    - **Elements:** "Since 1998" tagline, a short paragraph about the owner's commitment to the community, a photo of the owner or the store's interior.
    - **Emotional goal:** Humanize the business, build deep emotional trust.
- **menu/services:**
    - **Purpose:** Showcase the range of products available in an organized, non-overwhelming way.
    - **CSS class names:** `.menu-section`, `.categories`, `.category-item`
    - **Elements:** Icons and text for categories: "Fresh Sabzi & Fruits," "Pantry Staples (Dal, Atta, Oil)," "Dairy & Bakery," "Personal Care."
    - **Emotional goal:** Show variety, reliability, and that all needs are met.
- **gallery:**
    - **Purpose:** Visually communicate freshness, cleanliness, and the store's atmosphere.
    - **CSS class names:** `.gallery-section`, `.gallery-grid`, `.gallery-item`
    - **Elements:** Grid of photos showing fresh produce, neatly stacked shelves, clean store aisles, and packaged goods.
    - **Emotional goal:** Evoke freshness, quality, and a sense of order.
- **testimonials:**
    - **Purpose:** Provide social proof from the local community.
    - **CSS class names:** `.testimonials-section`, `.testimonial-card`, `.quote-icon`
    - **Elements:** Quotes from local customers (e.g., "Best quality tomatoes in the area! - Ramesh K., Sector 5"), with customer name and locality.
    - **Emotional goal:** Build credibility and reinforce trust.
- **contact:**
    - **Purpose:** Make it effortless for customers to get in touch or place an order.
    - **CSS class names:** `.contact-section`, `.contact-info`, `.contact-button`
    - **Elements:** Large, clickable WhatsApp icon, phone number, full address with a "Get Directions" link, and a simple "WhatsApp for Order" button.
    - **Emotional goal:** Make contact feel direct, personal, and convenient.
- **footer:**
    - **Purpose:** Provide essential information and reinforce key messages.
    - **CSS class names:** `.footer`, `.footer-content`
    - **Elements:** Store hours, address, "Credit available for regular customers," social media icons (primarily WhatsApp), and copyright notice.
    - **Emotional goal:** Reinforce reliability and provide utility.

## 4. USER JOURNEY
- **First impression →** User lands on the homepage. They see a clean, trustworthy design with a photo of the actual store. The headline "Your Daily Needs, Delivered" and the prominent WhatsApp button immediately tell them what this is and what they can do. The emotional goal is "This is a legitimate, local store I can trust."
- **Trust building →** The user scrolls. They see the "About Us" section with the owner's photo and a story. They see the "Gallery" with fresh produce. They read a testimonial from a neighbor. The emotional goal shifts to "This is a real, caring business, not a faceless corporation."
- **Desire →** The user clicks on "Menu/Services." They see well-organized categories with icons for staples, fresh items, etc. They think, "I can get everything I need here, and it looks fresh." The emotional goal is "I want to shop here. They have what I need."
- **Conversion path →** The user sees the "Contact" section. The WhatsApp button is huge and clear. They think, "I'll just send a message for my weekly order." They click the WhatsApp link, which opens their WhatsApp app with a pre-filled message to the store. The path is frictionless. The emotional goal is "This was easy and convenient. I'll do this again."

## 5. IMAGES NEEDED
- friendly_shopkeeper_smile | "Indian kirana store owner smiling at camera" | Hero section, About Us | 1200x630
- fresh_vegetables_display | "colorful Indian vegetables arranged in a basket" | Products section, Banner | 800x600
- clean_kirana_shelf | "well-lit Indian grocery store aisle with organized shelves" | Visit Us page, Background | 1920x1080
- delivery_person_cycle | "Indian man on bicycle with grocery bags delivering" | Delivery Info section, Banner | 600x400
- handing_over_goods | "close-up of hands exchanging money for groceries" | Testimonial section, Icon | 500x500

## 6. INTERACTIVE FEATURES
- **Essential JS features for this business type:**
    - WhatsApp Click-to-Chat: A JavaScript function that constructs the `https://wa.me/91[number]` link for the primary contact button, ensuring the user's default WhatsApp client opens.
    - Google Maps API Integration: A simple, non-intrusive map showing the store's location with a "Get Directions" button that opens the native Google Maps app.
    - Sticky Header: A header that remains visible at the top of the viewport on scroll, ensuring the primary WhatsApp button is always accessible on mobile.
- **Micro-interactions:**
    - WhatsApp CTA Pulse: The main WhatsApp button has a subtle, continuous pulse animation to draw the eye and indicate it's an active, primary action.
    - Product Card Hover: On hovering over product images in a list, a gentle zoom-in (scale 1.05) and a semi-transparent dark overlay appear, improving focus on the product.
    - Smooth Scroll: Anchor links (e.g., "Our Location") trigger a smooth scroll animation to the target section, providing a polished transition.
- **Form behaviors:**
    - No Traditional Forms: The primary interaction is a button, not a form. Clicking "Order on WhatsApp" initiates the chat. This reduces friction and aligns with user behavior.
    - Input Validation (if applicable): If a newsletter signup form is included, it will have simple client-side validation (e.g., "Please enter a valid email address") with inline error messages.
- **Mobile-specific needs:**
    - Touch-Friendly Targets: All interactive elements (buttons, links) have a minimum height and width of 48x48px to accommodate easy tapping with a thumb.
    - Above-the-Fold CTA: The main WhatsApp call-to-action button is placed in the initial viewport without requiring any scrolling on a mobile device.
    - Click-to-Call: The phone number is a clickable `tel:` link, allowing users to call the store directly from their device's dialer.
    - Viewport Meta Tag: `viewport="width=device-width, initial-scale=1.0"` is set to ensure proper rendering and scaling across all mobile devices.

## 7. DESIGN DECISIONS
- **Exact hex colors with reasoning:**
    - `--color-primary: #135E11` (Deep Green): Used for primary text and icons. Evokes feelings of freshness, nature, and trust, reinforcing the store's reliability.
    - `--color-accent-1: #FF9933` (Saffron): Used for secondary buttons, highlights, and small icons. Represents tradition, purity, and energy, adding a vibrant, culturally resonant touch.
    - `--color-accent-2: #FFC300` (Turmeric Gold): Used for the primary Call-to-Action (CTA) button. Symbolizes prosperity, health, and warmth, making it the most prominent and inviting interactive element.
    - `--color-text-dark: #2C3E50` (Neutral Dark): A deep blue-gray for body text, providing excellent readability and a professional, calm feel.
    - `--color-bg-light: #F8F9FA` (Neutral Lighter): A very light gray for main backgrounds, which is softer on the eyes than stark white and creates a modern, clean look.
    - `--color-card-bg: #FFFFFF` (White): Used for cards and distinct content blocks to create visual separation and hierarchy.
- **Google Font pair with import URL:**
    - **Body Font:** Poppins. A clean, geometric sans-serif that is highly readable on screens and has a friendly, modern feel. It works well for both English and Hindi text.
    - **Heading Font:** Rajdhani. A bold, rounded sans-serif that adds personality and a touch of playfulness to headlines, contrasting with the more neutral body font.
    - **Import URL:** `@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&family=Rajdhani:wght@700&display=swap');`
- **Border radius / spacing philosophy:**
    - **Border Radius:** Soft and approachable. A consistent radius of `8px` for buttons, `12px` for cards and input fields, and `16px` for larger containers. This avoids sharp, corporate-looking corners and reinforces the "friendly neighbor" vibe.
    - **Spacing:** A modular spacing system based on an 8px grid. This ensures rhythm and consistency. Base unit is `8px`, with multiples used for padding and margins (e.g., `16px`, `24px`, `32px`, `40px`).
- **CSS variable names and values:**
    ```css
    :root {
      /* Colors */
      --color-primary: #135E11;
      --color-accent-1: #FF9933;
      --color-accent-2: #FFC300;
      --color-text-dark: #2C3E50;
      --color-text-light: #7F8C8D;
      --color-bg-light: #F8F9FA;
      --color-card-bg: #FFFFFF;

      /* Typography */
      --font-body: 'Poppins', sans-serif;
      --font-heading: 'Rajdhani', sans-serif;

      /* Sp