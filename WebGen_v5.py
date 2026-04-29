"""
WebGen v5 — Lean & Beautiful
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Philosophy: 5 sections, each done PERFECTLY.
  Nav → Hero → Menu/Services → About+Contact → Footer

Architecture:
  Call 1  — Brand Plan (JSON, compressed prompt, no fluff)
  Call 2  — HTML  (single pass, tight prompt)
  Call 3  — CSS   (single pass, design-system driven)
  Call 4  — JS    (single pass, only what's needed)
  
Total: 4 API calls × 4096 tokens = razor sharp output.

Fixes vs v4:
  ✅ _api_call: safe .get() + strips <think> before returning
  ✅ _parse_json: isinstance guard + truncation repair
  ✅ No brainstorm phase (saves 2 calls, quality preserved via richer plan prompt)
  ✅ Single-pass generation (4096 is enough for 5 tight sections)
  ✅ Plan prompt tells model: THINK BRIEFLY, output immediately
  ✅ CSS design system: tokens baked into prompt, not re-generated
"""

import requests, re, sys, json, time, os, hashlib
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
SARVAM_API_KEY = "sk_9mq4tMzACqmABwkMG"
MODEL          = "sarvam-105b"
API_URL        = "https://api.sarvam.ai/v1/chat/completions"
MAX_TOKENS     = 4096
TEMPERATURE    = 0.10
OUTPUT_DIR     = "."
# ─────────────────────────────────────────────────────────────────────────────


# ══════════════════════════════════════════════════════════════════════════════
# API CALLER — safe, think-stripped
# ══════════════════════════════════════════════════════════════════════════════

def _api_call(system: str, user: str, label: str = "") -> str:
    payload = {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    }
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type":  "application/json",
    }

    for attempt in range(4):
        try:
            r = requests.post(API_URL, json=payload, headers=headers, timeout=200)
        except requests.exceptions.Timeout:
            if attempt < 3:
                print(f"   Timeout ({label}) — retry in 5s..."); time.sleep(5); continue
            sys.exit("Persistent timeout.")
        except requests.exceptions.ConnectionError:
            sys.exit("Connection error.")

        if r.status_code == 429:
            wait = 15 + attempt * 15
            print(f"   Rate-limited — waiting {wait}s..."); time.sleep(wait); continue
        if r.status_code == 401:
            sys.exit("Invalid API key.")
        if r.status_code != 200:
            print(f"   API {r.status_code}: {r.text[:200]}")
            if attempt < 3: time.sleep(5); continue
            sys.exit("API repeatedly failed.")

        data    = r.json()
        choices = data.get("choices", [])
        if not choices:
            print(f"   ⚠️  No choices ({label}): {str(data)[:200]}")
            return "{}"
        content = choices[0].get("message", {}).get("content", "")
        if not content:
            print(f"   ⚠️  Empty content ({label})")
            return "{}"

        # Strip thinking block BEFORE returning — reclaim those tokens
        content = re.sub(r"<think>[\s\S]*?</think>", "", content, flags=re.IGNORECASE).strip()
        return content

    sys.exit("API gave up.")


# ══════════════════════════════════════════════════════════════════════════════
# JSON PARSER — with truncation repair
# ══════════════════════════════════════════════════════════════════════════════

def _repair_truncated_json(text: str) -> str:
    """Close unclosed braces/brackets from a truncated JSON string."""
    text = text.strip()
    # If last char is inside a string, close it
    lines = text.splitlines()
    if lines:
        last = lines[-1]
        # Count unescaped quotes to detect open string
        unescaped_quotes = len(re.findall(r'(?<!\\)"', last))
        if unescaped_quotes % 2 == 1:
            text += '"'
    # Close arrays and objects
    text += ']' * max(0, text.count('[') - text.count(']'))
    text += '}' * max(0, text.count('{') - text.count('}'))
    return text


def _parse_json(raw: str, user_prompt: str) -> dict:
    # Guard: non-string or empty
    if not isinstance(raw, str) or not raw.strip():
        print("   ⚠️  Empty/non-string response — using fallback plan")
        return _fallback_plan(user_prompt)

    # Strip think blocks and fences
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```[a-z]*\n?", "", raw).replace("```", "").strip()

    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        print("   ⚠️  No JSON object found — using fallback plan")
        return _fallback_plan(user_prompt)

    candidate = m.group(0)

    # Try 1: raw parse
    try:
        return json.loads(candidate)
    except Exception:
        pass

    # Try 2: trailing comma fix
    c2 = re.sub(r',\s*([}\]])', r'\1', candidate)
    try:
        return json.loads(c2)
    except Exception:
        pass

    # Try 3: truncation repair
    c3 = _repair_truncated_json(c2)
    try:
        result = json.loads(c3)
        print("   ⚠️  JSON was truncated — auto-repaired ✅")
        return result
    except Exception as e:
        print(f"   ⚠️  JSON unrecoverable ({e}) — using fallback plan")
        return _fallback_plan(user_prompt)


# ══════════════════════════════════════════════════════════════════════════════
# CALL 1 — BRAND PLAN
# ══════════════════════════════════════════════════════════════════════════════

PLAN_SYSTEM = """You are a senior brand strategist and web architect for Indian local businesses.
THINK BRIEFLY then output JSON immediately — keep thinking under 200 words.

Output ONLY valid JSON. Zero text before or after. Zero markdown fences.

JSON structure:
{
  "title": "page <title> tag text",
  "business_name": "display name",
  "tagline": "one punchy line",
  "whatsapp": "91XXXXXXXXXX",
  "phone": "+91 XXXXX XXXXX",
  "address": "full street address, city",
  "hours": "Mon-Sun 10AM – 11PM",
  "theme": {
    "primary":   "#hex",
    "secondary": "#hex",
    "accent":    "#hex",
    "bg":        "#hex",
    "surface":   "#hex",
    "text":      "#hex",
    "muted":     "#hex",
    "on_primary":"#hex",
    "overlay":   "rgba(0,0,0,0.55)",
    "radius":    "12px",
    "font_head": "Google Font name",
    "font_body": "Google Font name",
    "fonts_url": "https://fonts.googleapis.com/css2?family=..."
  },
  "hero": {
    "heading": "bold headline, max 8 words",
    "subheading": "supporting line, max 15 words",
    "cta_text": "button label",
    "cta_href": "#contact",
    "bg_query": "specific photo description for picsum seed"
  },
  "menu": {
    "section_title": "Our Menu" or "Services" or relevant,
    "items": [
      {"name":"...", "desc":"short mouth-watering description", "price":"₹XX", "emoji":"🫓"},
      {"name":"...", "desc":"...", "price":"₹XX", "emoji":"🧅"},
      {"name":"...", "desc":"...", "price":"₹XX", "emoji":"🌶️"},
      {"name":"...", "desc":"...", "price":"₹XX", "emoji":"🥗"}
    ]
  },
  "about": {
    "heading": "Our Story" or similar,
    "para1": "2-sentence authentic backstory",
    "para2": "2-sentence why-us / quality promise",
    "stats": [
      {"number":"15+",  "label":"Years of Taste"},
      {"number":"500+", "label":"Happy Customers Daily"},
      {"number":"10+",  "label":"Menu Items"}
    ]
  },
  "gallery_seeds": ["kulcha1","kulcha2","kulcha3"],
  "schema_type": "FoodEstablishment",
  "meta_desc": "SEO meta description under 160 chars"
}

Design rules:
- Indian business: saffron/turmeric/deep-green palette works well
- Prices in ₹
- WhatsApp is primary CTA
- Warm, trustworthy, appetite-stimulating mood
- Pick distinctive Google Fonts (NOT Inter, NOT Roboto)"""


def get_plan(user_prompt: str) -> dict:
    print("\n[CALL 1/4] Building brand plan...")
    raw = _api_call(
        PLAN_SYSTEM,
        f'Business: "{user_prompt}"\n\nCreate the JSON plan. Think briefly, then output JSON:',
        label="Plan"
    )
    plan = _parse_json(raw, user_prompt)

    # Ensure gallery seeds exist
    if not plan.get("gallery_seeds"):
        plan["gallery_seeds"] = ["food1", "food2", "food3"]

    print(f"   ✅ Plan: {plan.get('business_name','?')} | "
          f"theme: {plan.get('theme',{}).get('primary','?')} | "
          f"fonts: {plan.get('theme',{}).get('font_head','?')}")
    return plan


# ══════════════════════════════════════════════════════════════════════════════
# IMAGE HELPER — picsum with unique seeds
# ══════════════════════════════════════════════════════════════════════════════

def picsum(seed: str, w: int, h: int) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", seed)
    uhash = hashlib.md5(seed.encode()).hexdigest()[:6]
    return f"https://picsum.photos/seed/{safe}_{uhash}/{w}/{h}"


# ══════════════════════════════════════════════════════════════════════════════
# CALL 2 — HTML
# ══════════════════════════════════════════════════════════════════════════════

HTML_SYSTEM = """You are a senior HTML5 engineer. Write complete, semantic, production HTML.

RULES:
1. Output ONLY raw HTML. Start: <!DOCTYPE html>  End: </html>
2. NO inline <style> or <script> — link style.css and script.js
3. Use EXACTLY the classes/IDs listed in the blueprint
4. Every section (not nav) gets class="reveal"
5. Hero MUST have <div class="hero-overlay"></div> as first child
6. Nav: sticky, logo left, links center/right, WhatsApp CTA button
7. Include JSON-LD schema in <head>
8. Include viewport, charset, OG meta tags
9. Footer: copyright, quick links, social icons, WhatsApp
10. Keep HTML lean — no unnecessary wrappers"""


def build_html(plan: dict) -> str:
    t  = plan.get("theme", {})
    h  = plan.get("hero", {})
    m  = plan.get("menu", {})
    a  = plan.get("about", {})
    gs = plan.get("gallery_seeds", ["s1","s2","s3"])
    seo = plan.get("meta_desc", "")

    menu_items_html = "\n".join(
        f"""      <div class="menu-card reveal">
        <div class="menu-card-emoji">{item.get('emoji','🍽️')}</div>
        <h3 class="menu-card-name">{item.get('name','Item')}</h3>
        <p class="menu-card-desc">{item.get('desc','')}</p>
        <span class="menu-card-price">{item.get('price','₹??')}</span>
      </div>"""
        for item in m.get("items", [])
    )

    stats_html = "\n".join(
        f"""      <div class="stat-item">
        <span class="stat-number">{s.get('number','')}</span>
        <span class="stat-label">{s.get('label','')}</span>
      </div>"""
        for s in a.get("stats", [])
    )

    hero_bg = picsum(h.get("bg_query", "food"), 1920, 1080)
    g1 = picsum(gs[0] if len(gs)>0 else "g1", 600, 450)
    g2 = picsum(gs[1] if len(gs)>1 else "g2", 600, 450)
    g3 = picsum(gs[2] if len(gs)>2 else "g3", 600, 450)
    wa  = plan.get("whatsapp", "919876543210")
    phone = plan.get("phone", "+91 98765 43210")
    addr  = plan.get("address", "")
    hours = plan.get("hours", "")

    schema = {
        "@context": "https://schema.org",
        "@type": plan.get("schema_type", "FoodEstablishment"),
        "name": plan.get("business_name", ""),
        "description": seo,
        "telephone": phone,
        "address": {"@type": "PostalAddress", "streetAddress": addr},
        "openingHours": hours,
    }

    blueprint = f"""
╔═ HTML BLUEPRINT ══════════════════════════════════════╗
IDs:      #nav #hero #menu #about #contact #footer
Classes:  .navbar .nav-logo .nav-links .nav-link .nav-cta .nav-toggle .nav-toggle-bar
          .hero .hero-overlay .hero-content .hero-title .hero-sub .hero-btn
          .menu-section .menu-grid .menu-card .menu-card-emoji .menu-card-name .menu-card-desc .menu-card-price
          .about-section .about-grid .about-text .about-heading .about-para .about-stats .stat-item .stat-number .stat-label
          .gallery-grid .gallery-img
          .contact-section .contact-grid .contact-info .contact-map .whatsapp-btn .info-item .info-icon
          .footer .footer-inner .footer-logo .footer-links .footer-link .footer-copy .social-row .social-btn
          .reveal .container .section-title .section-sub .btn .btn-primary .btn-outline
╚═══════════════════════════════════════════════════════╝

IMAGES (use these exact URLs):
  Hero BG:   {hero_bg}
  Gallery 1: {g1}
  Gallery 2: {g2}
  Gallery 3: {g3}

DATA:
  Business:  {plan.get('business_name','')}
  Tagline:   {plan.get('tagline','')}
  Phone:     {phone}
  WhatsApp:  https://wa.me/{wa}
  Address:   {addr}
  Hours:     {hours}
  Fonts URL: {t.get('fonts_url','')}
"""

    prompt = f"""Build complete HTML for this website.

{blueprint}

Hero section content:
  heading: "{h.get('heading','')}"
  subheading: "{h.get('subheading','')}"
  CTA button: "{h.get('cta_text','Order Now')}" linking to "{h.get('cta_href','#contact')}"

Menu section title: "{m.get('section_title','Our Menu')}"
Menu cards (pre-built below — copy exactly):
{menu_items_html}

About heading: "{a.get('heading','Our Story')}"
About para 1: "{a.get('para1','')}"
About para 2: "{a.get('para2','')}"
Stats (pre-built — copy exactly):
{stats_html}

Gallery: 3 images using the exact URLs above

JSON-LD schema to put in <head>:
{json.dumps(schema, indent=2)}

Meta description: "{seo}"
OG title: "{plan.get('title','')}"

CRITICAL REMINDERS:
- Hero: first child must be <div class="hero-overlay"></div>
- Nav: <a href="https://wa.me/{wa}" class="nav-cta btn btn-primary" target="_blank">WhatsApp Us</a>
- Every section except nav: add class="reveal"
- Link: <link rel="stylesheet" href="style.css">
- Script: <script src="script.js" defer></script>
- Footer is MANDATORY

Start with <!DOCTYPE html>:"""

    print("\n[CALL 2/4] Generating HTML...")
    raw = _api_call(HTML_SYSTEM, prompt, label="HTML")

    # Clean
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```[a-z]*\n?", "", raw).replace("```", "").strip()
    m2 = re.search(r"(<!DOCTYPE\s*html[\s\S]*?</html>)", raw, re.IGNORECASE)
    html = m2.group(1).strip() if m2 else raw

    # Auto-inject hero overlay if missing
    if "hero-overlay" not in html:
        html = re.sub(
            r'(id="hero"[^>]*>)',
            r'\1\n  <div class="hero-overlay"></div>',
            html
        )

    print(f"   ✅ HTML: {len(html)//1024}KB")
    return html


# ══════════════════════════════════════════════════════════════════════════════
# CALL 3 — CSS
# ══════════════════════════════════════════════════════════════════════════════

CSS_SYSTEM = """You are a senior CSS designer. Write modern, mobile-first CSS.

RULES:
1. Output ONLY raw CSS — no markdown, no <style> tags
2. File order: @import → :root → reset → base → sections → components → @media
3. Style EVERY class listed. Skip none.
4. :root must have ALL variables listed
5. Every interactive element: BOTH :hover AND :focus states
6. .reveal { opacity:0; transform:translateY(28px); transition:opacity .6s ease,transform .6s ease }
   .reveal.visible { opacity:1; transform:translateY(0) }
7. .hero-overlay { position:absolute; inset:0; background:var(--overlay); z-index:1 }
   .hero-content { position:relative; z-index:2 }
8. nav.scrolled { box-shadow: 0 2px 20px rgba(0,0,0,.12) }
9. Mobile nav: .nav-links{display:none} .nav-links.nav-open{display:flex;flex-direction:column}
10. @media(min-width:768px): .nav-links{display:flex;flex-direction:row} .nav-toggle{display:none}
11. VALID media queries ONLY: @media (min-width:768px) — NEVER @media mobile
12. Two breakpoints: 768px and 480px
13. Design must be BEAUTIFUL — use gradients, shadows, smooth hover lifts on cards"""


def build_css(plan: dict) -> str:
    t   = plan.get("theme", {})
    pri = t.get("primary",    "#E65100")
    sec = t.get("secondary",  "#FFF3E0")
    acc = t.get("accent",     "#2E7D32")
    bg  = t.get("bg",         "#FFFDE7")
    sur = t.get("surface",    "#FFFFFF")
    txt = t.get("text",       "#212121")
    mut = t.get("muted",      "#757575")
    onp = t.get("on_primary", "#FFFFFF")
    ove = t.get("overlay",    "rgba(0,0,0,0.55)")
    rad = t.get("radius",     "12px")
    fh  = t.get("font_head",  "Poppins")
    fb  = t.get("font_body",  "Open Sans")
    fu  = t.get("fonts_url",  "")

    all_classes = """
navbar nav-logo nav-links nav-link nav-cta nav-toggle nav-toggle-bar
hero hero-overlay hero-content hero-title hero-sub hero-btn
menu-section menu-grid menu-card menu-card-emoji menu-card-name menu-card-desc menu-card-price
about-section about-grid about-text about-heading about-para about-stats stat-item stat-number stat-label
gallery-grid gallery-img
contact-section contact-grid contact-info contact-map whatsapp-btn info-item info-icon
footer footer-inner footer-logo footer-links footer-link footer-copy social-row social-btn
reveal container section-title section-sub btn btn-primary btn-outline
""".strip()

    prompt = f""":root variables to use EXACTLY:
  --primary:    {pri}
  --secondary:  {sec}
  --accent:     {acc}
  --bg:         {bg}
  --surface:    {sur}
  --text:       {txt}
  --muted:      {mut}
  --on-primary: {onp}
  --overlay:    {ove}
  --radius:     {rad}
  --shadow:     0 4px 20px rgba(0,0,0,.08)
  --shadow-lg:  0 12px 40px rgba(0,0,0,.16)
  --nav-h:      68px
  --transition: all .3s ease
  --pad:        5rem 0
  --max-w:      1160px
  font-heading: "{fh}"
  font-body:    "{fb}"
  fonts-import: {fu}

Classes to style (ALL of them):
{all_classes}

Design requirements:
- Hero: full-screen (100vh), bg image cover, overlay, centered text
- Menu cards: hover lift (translateY(-6px) + shadow-lg), emoji large & centered on top
- About: 2-col grid (text | stats), stats are big numbers with label below
- Gallery: 3-col CSS grid, images fill squares with object-fit:cover, hover zoom
- Contact: 2-col (info | map placeholder), whatsapp-btn is big green pill button
- Footer: dark background (primary color), light text
- .btn: padding .75rem 2rem, border-radius var(--radius), font-weight 600, transition
- .btn-primary: bg var(--primary), color var(--on-primary)
- .btn-outline: border 2px solid var(--primary), bg transparent
- section-title: large, bold, centered, decorated with colored underline pseudo-element
- Nav: fixed top, glass/frosted or solid, height var(--nav-h), z-index 1000

Write complete CSS now, start with @import:"""

    print("\n[CALL 3/4] Generating CSS...")
    raw = _api_call(CSS_SYSTEM, prompt, label="CSS")

    # Clean
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"</?style[^>]*>", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```[a-z]*\n?", "", raw).replace("```", "").strip()
    m = re.search(r"(@import|:root|\*\s*\{|[.#\w]+\s*\{)", raw)
    css = raw[m.start():].strip() if m else raw

    # Auto-repairs
    css = re.sub(r'justify-\s*\n\s*content\s*:', 'justify-content:', css)
    css = re.sub(r'@media\s+mobile\b', '@media (max-width:767px)', css)

    if ".hero-overlay" not in css:
        css += "\n.hero-overlay{position:absolute;inset:0;background:var(--overlay);z-index:1}\n.hero-content{position:relative;z-index:2}\n"
    if ".nav-links.nav-open" not in css:
        css += "\n.nav-links{display:none}\n.nav-links.nav-open{display:flex;flex-direction:column;padding:1rem}\n@media(min-width:768px){.nav-links{display:flex;flex-direction:row;gap:1.5rem}.nav-toggle{display:none}}\n"
    if "nav.scrolled" not in css and ".navbar.scrolled" not in css:
        css += "\n.navbar.scrolled,#nav.scrolled{box-shadow:0 2px 20px rgba(0,0,0,.15)}\n"

    # Dedup selectors (keep last)
    css = _dedup_css(css)
    print(f"   ✅ CSS: {len(css)//1024}KB")
    return css


def _dedup_css(css: str) -> str:
    """Keep last occurrence of each selector block."""
    # Split into blocks at top-level selector boundaries
    # Simple approach: track selector → block, keep last
    blocks = re.split(r'\n(?=[.#*@a-zA-Z\[])', css)
    seen: dict = {}
    order: list = []
    for block in blocks:
        key_m = re.match(r'([^{]+)\{', block.strip())
        key = key_m.group(1).strip() if key_m else block[:40]
        if key not in seen:
            order.append(key)
        seen[key] = block
    removed = len(blocks) - len(order)
    if removed:
        print(f"   [CSS] Removed {removed} duplicate selectors ✅")
    return "\n".join(seen[k] for k in order)


# ══════════════════════════════════════════════════════════════════════════════
# CALL 4 — JS
# ══════════════════════════════════════════════════════════════════════════════

JS_SYSTEM = """You are a senior JavaScript developer. Write clean, defensive vanilla JS.

RULES:
1. Output ONLY raw JS — no <script> tags, no markdown
2. Script has defer attr — no DOMContentLoaded wrapper needed
3. NULL-CHECK every querySelector before use: const el = document.querySelector('.x'); if(el){...}
4. NEVER declare the same const/let/var name twice
5. Add // ── FEATURE: Name ── comment above each block
6. Keep it lean — only implement what's listed below"""


def build_js(plan: dict) -> str:
    wa = plan.get("whatsapp", "919876543210")

    prompt = f"""Implement these 5 features for the website. Use exact variable names shown.

// ── FEATURE: Mobile Nav Toggle ──
const navToggle = document.querySelector('.nav-toggle');
const navLinks  = document.querySelector('.nav-links');
// Click navToggle → toggle class 'nav-open' on navLinks
// Click any .nav-link → remove 'nav-open' from navLinks

// ── FEATURE: Sticky Nav ──
const navbar = document.querySelector('.navbar');
// window scroll → if scrollY > 60 add class 'scrolled' to navbar else remove it

// ── FEATURE: Smooth Scroll ──
// All .nav-link with href starting '#' → preventDefault, querySelector(href), scrollIntoView({{behavior:'smooth',block:'start'}})

// ── FEATURE: Scroll Reveal ──
const revealEls = document.querySelectorAll('.reveal');
// IntersectionObserver threshold 0.12 → add class 'visible' → unobserve
// Feature-detect: if (!window.IntersectionObserver) add 'visible' to all directly

// ── FEATURE: WhatsApp Float Button ──
// After page loads 3 seconds, inject a floating WhatsApp button bottom-right:
// <a href="https://wa.me/{wa}" class="wa-float" target="_blank" aria-label="Chat on WhatsApp">
//   <svg ...WhatsApp icon...></svg>
// </a>
// Style it inline: position fixed, bottom 24px, right 24px, bg #25D366, 
//   border-radius 50%, width 56px, height 56px, display flex, align/justify center,
//   box-shadow 0 4px 16px rgba(0,0,0,.25), z-index 9999, transition all .3s ease
// Add hover: scale(1.1)

Write complete JS now. Null-check everything. No duplicate declarations."""

    print("\n[CALL 4/4] Generating JS...")
    raw = _api_call(JS_SYSTEM, prompt, label="JS")

    # Clean
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"</?script[^>]*>", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```[a-z]*\n?", "", raw).replace("```", "").strip()
    m = re.search(r"(//|const |let |var |document|window|function )", raw)
    js = raw[m.start():].strip() if m else raw

    # Remove duplicate const declarations (keep first)
    js = _dedup_js(js)
    print(f"   ✅ JS: {len(js)//1024}KB")
    return js


def _dedup_js(js: str) -> str:
    """Remove re-declarations of same const/let/var name."""
    declared: set = set()
    out: list = []
    skip = False
    depth = 0

    for line in js.splitlines():
        depth += line.count('{') - line.count('}')
        m = re.match(r'\s*(const|let|var)\s+(\w+)', line)
        if m and depth <= 1:
            name = m.group(2)
            if name in declared:
                skip = True
                out.append(f"// [dedup removed re-declaration of {name}]")
                continue
            declared.add(name)
            skip = False
        elif skip and (line.strip().startswith('//') or depth <= 0):
            skip = False
        if not skip:
            out.append(line)

    return "\n".join(out)


# ══════════════════════════════════════════════════════════════════════════════
# QUALITY CHECK
# ══════════════════════════════════════════════════════════════════════════════

def quality_check(html: str, css: str, js: str) -> dict:
    print("\n── Quality Check ─────────────────────────────────────────")
    checks = [
        ("<!DOCTYPE"      in html.upper(),              "HTML DOCTYPE"),
        ("</html>"        in html.lower(),              "HTML closed"),
        ("style.css"      in html,                      "Links style.css"),
        ("script.js"      in html,                      "Links script.js"),
        ("hero-overlay"   in html,                      "Hero overlay present"),
        ("wa.me"          in html,                      "WhatsApp CTA"),
        ("ld+json"        in html,                      "JSON-LD schema"),
        ("</footer>"      in html,                      "Footer present"),
        (":root"          in css,                       "CSS :root vars"),
        ("@media"         in css,                       "CSS responsive"),
        (".reveal.visible" in css,                      "CSS reveal.visible"),
        ("hero-overlay"   in css,                       "CSS hero overlay"),
        ("nav-open"       in js,                        "JS mobile nav"),
        ("scrollIntoView" in js,                        "JS smooth scroll"),
        ("IntersectionObserver" in js,                  "JS scroll reveal"),
        ("scrolled"       in js,                        "JS sticky nav"),
        ("wa-float"       in js,                        "JS WhatsApp float"),
        ("@media mobile"  not in css,                   "No invalid @media"),
    ]

    issues = []
    for ok, label in checks:
        print(f"   {'✅' if ok else '❌'}  {label}")
        if not ok:
            issues.append(label)

    # JS duplicate check
    consts = re.findall(r'\bconst\s+(\w+)', js)
    dupes  = [n for n in set(consts) if consts.count(n) > 1]
    if dupes:
        print(f"   ⚠️  JS duplicate consts: {', '.join(dupes[:5])}")
        issues.append("JS duplicates")
    else:
        print("   ✅  No JS duplicate declarations")

    score = max(0, 100 - len(issues) * 5)
    print(f"\n   Score: {score}/100  {'🏆 Perfect!' if not issues else f'⚠️ {len(issues)} issue(s)'}")
    if issues:
        print(f"   Issues: {' | '.join(issues)}")
    print("──────────────────────────────────────────────────────────")
    return {"score": score, "issues": issues}


# ══════════════════════════════════════════════════════════════════════════════
# FALLBACK PLAN
# ══════════════════════════════════════════════════════════════════════════════

def _fallback_plan(user_prompt: str) -> dict:
    name = user_prompt.title()
    return {
        "title": f"{name} | Authentic Indian Food",
        "business_name": name,
        "tagline": f"Fresh, Hot & Delicious {name}",
        "whatsapp": "919876543210",
        "phone": "+91 98765 43210",
        "address": "Shop No. 1, Main Market, Your City",
        "hours": "Mon–Sun: 10:00 AM – 11:00 PM",
        "theme": {
            "primary":    "#E65100",
            "secondary":  "#FFF3E0",
            "accent":     "#2E7D32",
            "bg":         "#FFFDE7",
            "surface":    "#FFFFFF",
            "text":       "#1A1A1A",
            "muted":      "#6B6B6B",
            "on_primary": "#FFFFFF",
            "overlay":    "rgba(0,0,0,0.58)",
            "radius":     "12px",
            "font_head":  "Playfair Display",
            "font_body":  "Lato",
            "fonts_url":  "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Lato:wght@400;600&display=swap",
        },
        "hero": {
            "heading":    f"Taste the Real {name}",
            "subheading": "Made fresh daily with authentic spices and love",
            "cta_text":   "Order on WhatsApp",
            "cta_href":   "https://wa.me/919876543210",
            "bg_query":   f"indian {user_prompt.lower()} food stall",
        },
        "menu": {
            "section_title": "Our Menu",
            "items": [
                {"name": f"Classic {name}",   "desc": "Original recipe, crispy & fluffy",   "price": "₹60",  "emoji": "🫓"},
                {"name": f"Paneer {name}",    "desc": "Rich cottage cheese stuffing",        "price": "₹80",  "emoji": "🧀"},
                {"name": f"Aloo {name}",      "desc": "Spiced potato filling, fan favorite", "price": "₹60",  "emoji": "🥔"},
                {"name": f"Special {name}",   "desc": "Chef's secret masala blend",          "price": "₹100", "emoji": "⭐"},
            ],
        },
        "about": {
            "heading": "Our Story",
            "para1":   "Started from a single tawa and a family recipe, we have been serving the neighbourhood for over 15 years.",
            "para2":   "Every kulcha is hand-made fresh daily. We use pure desi ghee and never compromise on quality.",
            "stats": [
                {"number": "15+",  "label": "Years of Taste"},
                {"number": "500+", "label": "Happy Customers Daily"},
                {"number": "8",    "label": "Menu Items"},
            ],
        },
        "gallery_seeds": ["kulcha_golden", "kulcha_paneer", "kulcha_crowd"],
        "schema_type": "FoodEstablishment",
        "meta_desc":   f"Best {name} in town. Authentic taste, fresh daily. Order on WhatsApp.",
    }


# ══════════════════════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════════════════════

def save(content: str, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content, encoding="utf-8")
    print(f"   💾 Saved: {path}  ({len(content.encode())//1024}KB)")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("   WebGen v5 — Lean & Beautiful")
    print("   4 API calls · 5 perfect sections · Zero bloat")
    print("=" * 60)

    user_prompt = input("\nKya banana hai?\n>>> ").strip()
    if not user_prompt:
        sys.exit("Kuch toh batao!")

    # Call 1: Plan
    plan = get_plan(user_prompt)
    save(json.dumps(plan, indent=2), f"{OUTPUT_DIR}/plan.json")

    # Call 2: HTML
    html = build_html(plan)
    save(html, f"{OUTPUT_DIR}/index.html")

    # Call 3: CSS
    css = build_css(plan)
    save(css, f"{OUTPUT_DIR}/style.css")

    # Call 4: JS
    js = build_js(plan)
    save(js, f"{OUTPUT_DIR}/script.js")

    # Quality check
    report = quality_check(html, css, js)

    t = plan.get("theme", {})
    print(f"""
{'='*60}
  ✅ WebGen v5 — Done!

  Files:
    index.html  —  {len(html)//1024}KB
    style.css   —  {len(css)//1024}KB
    script.js   —  {len(js)//1024}KB
    plan.json   —  blueprint

  Brand:
    Name:    {plan.get('business_name','')}
    Tagline: {plan.get('tagline','')}
    Colors:  {t.get('primary','')} / {t.get('accent','')}
    Fonts:   {t.get('font_head','')} + {t.get('font_body','')}

  Quality: {report['score']}/100
  {'Issues: ' + ' | '.join(report['issues']) if report['issues'] else '  No issues found 🏆'}

  Next steps:
    1. Open index.html in browser
    2. Replace WhatsApp number in plan.json → re-run
    3. Update address/hours in plan.json → re-run
    4. Swap picsum images with real photos
{'='*60}
""")


if __name__ == "__main__":
    main()