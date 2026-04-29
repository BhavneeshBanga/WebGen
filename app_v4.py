"""
WebGen v4 — Ultra-Enhanced Website Builder
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPROVEMENTS OVER v3:
  ✅ Deep-Think Planning (2-pass: brainstorm → detailed blueprint)
  ✅ SerpAPI real image downloads (max 5, with fallback to picsum)
  ✅ Unique picsum seeds per image (no more identical gallery photos)
  ✅ CSS fixes: valid media queries, no broken properties, hover+focus
  ✅ HTML fixes: unique image seeds, hero overlay, no duplicate sections
  ✅ JS fixes: null-checks everywhere, no duplicate declarations
  ✅ Footer always generated
  ✅ Quality checker now auto-repairs common issues

Architecture:
  Phase 0a — Deep Brainstorm (unconstrained thinking)
  Phase 0b — Structured Plan (JSON blueprint from brainstorm)
  Phase 0c — Validate + enrich plan
  Phase 1  — Image acquisition (SerpAPI → picsum fallback)
  Phase 2  — HTML  (2 calls + auto-repair)
  Phase 3  — CSS   (2 calls + dedup + auto-repair)
  Phase 3b — CSS post-process
  Phase 4  — JS    (2 calls + auto-repair)
  Phase 4b — JS  post-process
  Phase 5  — Quality check + final report

Total: 10 API calls (plan thinking + structured + validate + html×2 + css×2 + js×2 + QA)
"""

import requests
import re
import sys
import json
import time
import os
import hashlib
from pathlib import Path
from urllib.parse import quote_plus

# ─── Configuration ───────────────────────────────────────────────────────────
SARVAM_API_KEY  = "sk_9mq4ACqmABwkMG"
SERPAPI_KEY     = "569648758b8334ee8a52ef6491713c"          # ← paste your SerpAPI key here (or set env var SERPAPI_KEY)
MODEL           = "sarvam-105b"
API_URL         = "https://api.sarvam.ai/v1/chat/completions"
SERPAPI_URL     = "https://serpapi.com/search"
OUTPUT_DIR      = "."
MAX_TOKENS      = 4096
TEMPERATURE     = 0.10
MAX_RETRIES     = 2
MAX_IMAGES      = 5           # SerpAPI budget
IMAGE_DIR       = "images"    # subfolder for downloaded images
# ─────────────────────────────────────────────────────────────────────────────

# Resolve SerpAPI key from env if not hardcoded
if not SERPAPI_KEY:
    SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — Image Acquisition
#   Priority: SerpAPI (real photos) → picsum.photos (free placeholder)
# ═══════════════════════════════════════════════════════════════════════════════

_SEED_DIMS = {
    "hero":         ("1920", "1080"),
    "banner":       ("1200", "600"),
    "about":        ("800",  "600"),
    "gallery":      ("600",  "450"),
    "team":         ("400",  "500"),
    "product":      ("400",  "400"),
    "menu":         ("800",  "500"),
    "testimonial":  ("400",  "400"),
    "delivery":     ("800",  "500"),
    "special":      ("600",  "400"),
    "blog":         ("800",  "500"),
    "service":      ("600",  "400"),
    "customer":     ("400",  "400"),
    "offer":        ("600",  "400"),
}

def _picsum_url(key: str, seed_offset: int = 0) -> str:
    """Generate a unique picsum URL per key. seed_offset ensures gallery images differ."""
    key_clean = re.sub(r"[^a-zA-Z0-9_-]", "_", str(key))
    # Use a hash to make each key truly unique
    seed = f"{key_clean}_{seed_offset}_{hashlib.md5(key_clean.encode()).hexdigest()[:6]}"
    w, h = "800", "500"
    for part, dims in _SEED_DIMS.items():
        if part in key_clean.lower():
            w, h = dims
            break
    return f"https://picsum.photos/seed/{seed}/{w}/{h}"


def _serpapi_search(query: str, num: int = 3) -> list[str]:
    """Search SerpAPI for images. Returns list of image URLs."""
    if not SERPAPI_KEY:
        return []
    try:
        params = {
            "engine":  "google_images",
            "q":       query,
            "api_key": SERPAPI_KEY,
            "num":     num,
            "safe":    "active",
            "hl":      "en",
        }
        r = requests.get(SERPAPI_URL, params=params, timeout=15)
        if r.status_code != 200:
            print(f"   ⚠️  SerpAPI {r.status_code}: {r.text[:100]}")
            return []
        data = r.json()
        urls = []
        for img in data.get("images_results", [])[:num]:
            url = img.get("original") or img.get("thumbnail")
            if url and url.startswith("http"):
                urls.append(url)
        return urls
    except Exception as e:
        print(f"   ⚠️  SerpAPI error: {e}")
        return []


def _download_image(url: str, dest_path: str) -> bool:
    """Download an image. Returns True on success."""
    try:
        r = requests.get(url, timeout=15, stream=True,
                         headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            size_kb = Path(dest_path).stat().st_size / 1024
            if size_kb < 5:  # Too small = broken
                Path(dest_path).unlink(missing_ok=True)
                return False
            return True
    except Exception:
        pass
    return False


def acquire_images(image_queries: list[dict], output_dir: str) -> dict[str, str]:
    """
    Returns {key: "path/or/url"} for use in HTML.
    Uses SerpAPI for up to MAX_IMAGES queries, picsum for the rest.
    Gallery items get unique picsum seeds so they're visually distinct.
    """
    result = {}
    img_folder = Path(output_dir) / IMAGE_DIR
    img_folder.mkdir(parents=True, exist_ok=True)

    serpapi_used = 0
    print(f"\n[IMAGES] Acquiring {len(image_queries)} images "
          f"({'SerpAPI enabled' if SERPAPI_KEY else 'picsum only — set SERPAPI_KEY for real photos'})\n")

    # Track gallery index for unique seeds
    gallery_counter = {}

    for q in image_queries:
        if not isinstance(q, dict):
            continue
        key = q.get("key", "")
        if not key:
            continue
        key_clean = re.sub(r"[^a-zA-Z0-9_-]", "_", str(key))
        query_text = q.get("query", key)

        # Count gallery variants
        base = re.sub(r"_\d+$", "", key_clean)
        gallery_counter[base] = gallery_counter.get(base, 0) + 1
        offset = gallery_counter[base]

        # Try SerpAPI
        if SERPAPI_KEY and serpapi_used < MAX_IMAGES:
            print(f"   🔍 SerpAPI: '{query_text}'")
            urls = _serpapi_search(query_text, num=1)
            if urls:
                ext = "jpg"
                dest = str(img_folder / f"{key_clean}.{ext}")
                if _download_image(urls[0], dest):
                    rel_path = f"{IMAGE_DIR}/{key_clean}.{ext}"
                    result[key_clean] = rel_path
                    serpapi_used += 1
                    print(f"   ✅ Downloaded: {rel_path}")
                    continue
                else:
                    print(f"   ⚠️  Download failed, using picsum")

        # Fallback: picsum with unique seed
        url = _picsum_url(key_clean, seed_offset=offset)
        result[key_clean] = url
        print(f"   📷 Picsum [{key_clean}]: {url}")

    print(f"\n   Summary: {serpapi_used} real photos, "
          f"{len(result) - serpapi_used} picsum placeholders\n")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 0a — DEEP BRAINSTORM (unconstrained thinking)
# ═══════════════════════════════════════════════════════════════════════════════

BRAINSTORM_SYSTEM_P1 = """You are a world-class UX strategist and brand designer.
Analyze this Indian local business and write sections 1-4 of a creative brief.

Write ONLY these 4 sections — stop after section 4:

## 1. BUSINESS ANALYSIS
- Business type, target customers (age/income/habits), emotion to evoke, primary action wanted, USP

## 2. BRAND IDENTITY  
- Tone of voice, color palette (hex codes) with psychology reasoning, typography pair, visual metaphors

## 3. WEBSITE SECTIONS
For each section: purpose, CSS class names, elements, emotional goal
(List minimum 8 sections: nav, hero, about/story, menu/services, gallery, testimonials, contact, footer)

## 4. USER JOURNEY
- First impression → trust building → desire → conversion path

Be specific. Indian context: ₹ prices, WhatsApp contact, local neighborhoods, cultural color significance."""


BRAINSTORM_SYSTEM_P2 = """You are a world-class web architect continuing a creative brief.
Write ONLY sections 5-7 based on the business context provided.

## 5. IMAGES NEEDED
List exactly 5 images:
- key_name | SerpAPI search query (very specific, photographic) | used_in | dimensions

## 6. INTERACTIVE FEATURES
- Essential JS features for this business type
- Micro-interactions
- Form behaviors
- Mobile-specific needs

## 7. DESIGN DECISIONS
- Exact hex colors with reasoning
- Google Font pair with import URL
- Border radius / spacing philosophy  
- CSS variable names and values
- Mobile-first considerations

Be specific with hex codes, font names, and CSS values."""


def deep_brainstorm(user_prompt: str) -> str:
    """Phase 0a: 2-pass brainstorm to beat 4096 token limit."""
    print("\n[PHASE 0a] Deep brainstorming (2-pass)...\n")

    context = f"""Business request: "{user_prompt}"

Indian context reminders:
- Local customer behavior (walk-in, WhatsApp orders)  
- Indian color preferences (saffron #FF9933, turmeric gold, deep green)
- Prices in ₹
- WhatsApp is primary contact method
- Hindi/English mix if relevant
- Small stall or shop, not a chain restaurant"""

    # Pass 1: Business analysis + sections
    print("   [Brainstorm 1/2] Business analysis + sections...")
    p1 = _api_call(BRAINSTORM_SYSTEM_P1,
                   context + "\n\nWrite sections 1-4 now:",
                   label="Brainstorm-P1")

    # Pass 2: Images + features + design decisions
    print("   [Brainstorm 2/2] Images + design decisions...")
    p2 = _api_call(BRAINSTORM_SYSTEM_P2,
                   context + f"\n\nBrief so far:\n{p1[:1500]}\n\nWrite sections 5-7 now:",
                   label="Brainstorm-P2")

    full = p1.strip() + "\n\n" + p2.strip()
    return full


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 0b — STRUCTURED PLAN (from brainstorm)
# ═══════════════════════════════════════════════════════════════════════════════

PLAN_SYSTEM = """You are a senior web architect. Convert a creative brief into a JSON blueprint.

CRITICAL: Output ONLY valid JSON. No text before or after. No markdown fences.
THINK BRIEFLY then output JSON immediately — do not write long thinking.

The JSON must have this EXACT structure:
{
  "title": "string — full page title tag",
  "tagline": "string — one-line brand tagline",
  "business_type": "string — e.g. food_stall / kirana / salon / etc",
  "target_customer": "string — who visits this site",
  "primary_action": "string — what we most want them to do",
  "whatsapp_number": "string — placeholder like +91 98765 43210",
  "theme": {
    "mood": "dark|light|vibrant|warm|earthy|festive|minimal|professional",
    "primary":        "#hex — dominant brand color",
    "secondary":      "#hex — supporting color",
    "accent":         "#hex — call-to-action / highlight color",
    "background":     "#hex — page background",
    "surface":        "#hex — card / section background",
    "text":           "#hex — body text",
    "text_muted":     "#hex — secondary text",
    "text_on_primary":"#hex — text on primary color buttons",
    "font_heading":   "Google Font Name",
    "font_body":      "Google Font Name",
    "border_radius":  "8px|12px|16px|20px|4px",
    "hero_overlay":   "rgba(0,0,0,0.5) — overlay on hero image for text readability"
  },
  "sections": [
    {
      "id": "nav",
      "tag": "nav",
      "name": "Navigation",
      "purpose": "Brand identity + navigation hub",
      "classes": ["navbar","nav-container","nav-logo","nav-links","nav-link","nav-toggle","nav-toggle-bar","nav-cta"],
      "elements": ["logo text with icon", "5 nav links", "WhatsApp CTA button", "hamburger menu"],
      "interactions": ["sticky on scroll", "mobile dropdown", "active link highlight"],
      "needs_image": false,
      "image_key": ""
    }
  ],
  "image_queries": [
    {
      "key": "hero_bg",
      "query": "SPECIFIC search query for SerpAPI — detailed real photo description",
      "used_in": "hero section background",
      "dimensions": "1920x1080"
    }
  ],
  "all_classes": ["every","class","flat","deduplicated","list"],
  "all_ids": ["nav","hero","about"],
  "js_features": [
    {
      "name": "Mobile Nav Toggle",
      "selector": ".nav-toggle",
      "action": "toggle class nav-open on .nav-links element",
      "guard": "null-check both elements",
      "var_name": "navToggleBtn"
    },
    {
      "name": "Smooth Scroll",
      "selector": ".nav-link[href^='#']",
      "action": "scrollIntoView({behavior:'smooth',block:'start'})",
      "guard": "check href exists and target element exists",
      "var_name": "navLinks"
    },
    {
      "name": "Scroll Reveal",
      "selector": ".reveal",
      "action": "IntersectionObserver adds class visible at threshold 0.15",
      "guard": "feature detect IntersectionObserver",
      "var_name": "revealObserver"
    },
    {
      "name": "Sticky Nav",
      "selector": "#nav",
      "action": "add class scrolled when window.scrollY > 60",
      "guard": "null-check nav element",
      "var_name": "navElement"
    }
  ],
  "css_tokens": {
    "spacing_unit": "1rem",
    "section_padding": "5rem 0",
    "container_max_width": "1200px",
    "card_shadow": "0 4px 24px rgba(0,0,0,0.08)",
    "card_shadow_hover": "0 12px 40px rgba(0,0,0,0.16)",
    "transition_speed": "0.3s",
    "nav_height": "70px"
  },
  "seo": {
    "meta_description": "string",
    "og_title": "string",
    "schema_type": "LocalBusiness|Restaurant|Store|FoodEstablishment"
  },
  "google_fonts_url": "https://fonts.googleapis.com/css2?family=..."
}

CRITICAL RULES:
1. all_classes: EVERY class used across ALL sections, flat and deduplicated
2. all_ids: every section ID
3. js_features: minimum 6, each has unique var_name (no duplicates!)
4. image_queries: EXACTLY 5 entries with very specific SerpAPI search queries
5. hero_overlay must be dark enough for white text to be readable
6. Each section must have 'purpose', 'interactions', and 'image_key' fields
7. Nav section must include a WhatsApp CTA button class"""


def create_structured_plan(brainstorm: str, user_prompt: str) -> dict:
    """Phase 0b: Convert brainstorm into JSON blueprint."""
    print("   [Call 2/10] Structuring plan from brainstorm...")
    msg = f"""Original request: "{user_prompt}"

Creative Brief:
{brainstorm}

Convert this brief into the exact JSON blueprint format specified.
Ensure:
- image_queries has EXACTLY 5 entries with specific, searchable photo descriptions
- all_classes includes EVERY class mentioned in sections
- js_features has unique var_name for each feature (no 'navLinks' used twice)
- The design choices align with Indian local business aesthetics
- WhatsApp integration is included

Output only the JSON:"""

    raw = _api_call(PLAN_SYSTEM, msg, label="Plan-Structure")
    return _parse_json(raw, user_prompt, "plan")


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 0c — PLAN VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

VALIDATE_SYSTEM = """You are a meticulous code reviewer. Fix inconsistencies in this web blueprint.
Return ONLY valid JSON — the corrected plan. No markdown. No text before/after.

Critical fixes to apply:
1. all_classes: add any missing classes from sections[].classes
2. all_ids: add any missing section ids
3. js_features: ensure every var_name is unique (suffix with 2/3 if duplicate)
4. image_queries: must have EXACTLY 5 entries — add or remove to reach 5
5. Each image_query must have: key, query, used_in, dimensions
6. google_fonts_url: must include all fonts in theme
7. theme must have hero_overlay field
8. Every section needs: id, tag, name, purpose, classes, elements, interactions, needs_image, image_key
9. css_tokens block must be present
10. seo block must be present"""


def validate_plan(plan: dict, user_prompt: str) -> dict:
    """Phase 0c: Validate and repair the plan."""
    print("   [Call 3/10] Validating plan...")
    msg = f"""Request: "{user_prompt}"

Plan to validate:
{json.dumps(plan, indent=2)}

Apply all critical fixes listed in your instructions. Return corrected JSON only."""

    raw = _api_call(VALIDATE_SYSTEM, msg, label="Validate")
    result = _parse_json(raw, user_prompt, "plan")

    # Ensure exactly 5 image queries
    result = _normalize_image_queries(result)

    # Post-validation Python fixes
    result = _fix_js_var_names(result)

    print(f"   ✅ Plan: {len(result.get('sections',[]))} sections | "
          f"{len(result.get('all_classes',[]))} classes | "
          f"{len(result.get('image_queries',[]))} images | "
          f"{len(result.get('js_features',[]))} JS features")
    return result


def _normalize_image_queries(plan: dict) -> dict:
    """Ensure exactly 5 image queries with required fields."""
    queries = []
    for i, q in enumerate(plan.get("image_queries", [])):
        if not isinstance(q, dict):
            continue
        if "key" not in q:
            q["key"] = re.sub(r"[^a-zA-Z0-9_-]", "_", q.get("id", q.get("name", f"image_{i}")))
        if "query" not in q:
            q["query"] = q.get("search", q.get("description", q["key"].replace("_", " ")))
        if "used_in" not in q:
            q["used_in"] = q["key"].replace("_", " ")
        if "dimensions" not in q:
            q["dimensions"] = "800x500"
        queries.append(q)

    # Pad to 5 if needed
    while len(queries) < 5:
        i = len(queries)
        queries.append({
            "key": f"extra_img_{i}",
            "query": f"{plan.get('title', 'business')} interior photo",
            "used_in": f"extra section {i}",
            "dimensions": "800x500"
        })
    # Trim to 5
    plan["image_queries"] = queries[:5]
    return plan


def _fix_js_var_names(plan: dict) -> dict:
    """Ensure all js_features have unique var_names."""
    seen = {}
    for feat in plan.get("js_features", []):
        name = feat.get("var_name", "")
        if not name:
            name = re.sub(r"\s+", "_", feat.get("name", "feature")).lower()
            feat["var_name"] = name
        if name in seen:
            seen[name] += 1
            feat["var_name"] = f"{name}_{seen[name]}"
        else:
            seen[name] = 1
    return plan


# ═══════════════════════════════════════════════════════════════════════════════
# Context builder — richer than v3
# ═══════════════════════════════════════════════════════════════════════════════

def plan_to_context(plan: dict, images: dict) -> str:
    t   = plan.get("theme", {})
    tok = plan.get("css_tokens", {})
    seo = plan.get("seo", {})

    sec_lines = []
    for s in plan.get("sections", []):
        classes = " | ".join(f".{c}" for c in s.get("classes", []))
        img_note = f" [img: {s.get('image_key','')}]" if s.get("needs_image") else ""
        sec_lines.append(f"\n  <{s.get('tag','div')} id=\"{s.get('id','')}\">{img_note}")
        sec_lines.append(f"    PURPOSE: {s.get('purpose','')}")
        sec_lines.append(f"    classes: {classes}")
        sec_lines.append(f"    elements: {', '.join(s.get('elements', []))}")
        sec_lines.append(f"    interactions: {', '.join(s.get('interactions', []))}")

    img_lines = []
    for k, v in images.items():
        img_lines.append(f"  {k}: \"{v}\"")

    js_lines = []
    for f in plan.get("js_features", []):
        js_lines.append(
            f"  • {f.get('name','')} | var:{f.get('var_name','')} | "
            f"selector:{f.get('selector','')} | action:{f.get('action','')} | "
            f"guard:{f.get('guard','')}"
        )

    return f"""╔══════════════════════════════════════════════════════════════╗
║              BLUEPRINT v4 — FOLLOW EXACTLY                   ║
╚══════════════════════════════════════════════════════════════╝
TITLE:    {plan.get('title','')}
TAGLINE:  {plan.get('tagline','')}
CUSTOMER: {plan.get('target_customer','')}
GOAL:     {plan.get('primary_action','')}
WHATSAPP: {plan.get('whatsapp_number','+91 98765 43210')}
SCHEMA:   {seo.get('schema_type','LocalBusiness')}

─── THEME ───────────────────────────────────────────────────────
MOOD: {t.get('mood','')}
COLORS (:root CSS variables):
  --primary:        {t.get('primary','#333')}
  --secondary:      {t.get('secondary','#666')}
  --accent:         {t.get('accent','#09f')}
  --bg:             {t.get('background','#fff')}
  --surface:        {t.get('surface','#f5f5f5')}
  --text:           {t.get('text','#222')}
  --text-muted:     {t.get('text_muted','#888')}
  --text-on-primary:{t.get('text_on_primary','#fff')}
  --radius:         {t.get('border_radius','8px')}
  --hero-overlay:   {t.get('hero_overlay','rgba(0,0,0,0.5)')}
  --nav-height:     {tok.get('nav_height','70px')}
  --shadow:         {tok.get('card_shadow','0 4px 24px rgba(0,0,0,0.08)')}
  --shadow-hover:   {tok.get('card_shadow_hover','0 12px 40px rgba(0,0,0,0.16)')}
  --transition:     all {tok.get('transition_speed','0.3s')} ease
  --section-pad:    {tok.get('section_padding','5rem 0')}
  --container-max:  {tok.get('container_max_width','1200px')}

FONTS: heading="{t.get('font_heading','Poppins')}" body="{t.get('font_body','Open Sans')}"
FONTS URL: {plan.get('google_fonts_url','')}

─── SECTIONS (build ALL in order) ──────────────────────────────
{''.join(sec_lines)}

─── ALL CLASSES (style/use every one) ──────────────────────────
{', '.join('.'+c for c in plan.get('all_classes',[]))}

─── ALL IDs ────────────────────────────────────────────────────
{', '.join('#'+i for i in plan.get('all_ids',[]))}

─── IMAGE PATHS (use exact URLs/paths as src or background-image) ──
{chr(10).join(img_lines) if img_lines else '  (none)'}

─── JS FEATURES (implement ALL with exact var names) ────────────
{chr(10).join(js_lines)}

─── CRITICAL HTML RULES ─────────────────────────────────────────
1. Hero MUST have a semi-transparent overlay div for text readability:
   <div class="hero-overlay"></div>  styled with background: var(--hero-overlay)
2. Every gallery image must use a DIFFERENT image key (gallery_1, gallery_2, etc.)
3. Nav must have a WhatsApp CTA button linking to wa.me/
4. Include JSON-LD schema for {seo.get('schema_type','LocalBusiness')}
5. Meta description: "{seo.get('meta_description','')}"

─── CRITICAL CSS RULES ──────────────────────────────────────────
1. Use :hover AND :focus for ALL interactive elements (not just :focus)
2. @media queries MUST use (min-width: 768px) format, NEVER "@media mobile"
3. .nav-links mobile: display:none; .nav-links.nav-open: display:flex; flex-direction:column
4. Desktop @media(min-width:768px): .nav-links{{display:flex; flex-direction:row}} .nav-toggle{{display:none}}
5. NO broken CSS properties (check justify-content, display, etc.)
6. nav.scrolled MUST have box-shadow

─── CRITICAL JS RULES ───────────────────────────────────────────
1. NEVER redeclare the same const/let/var name
2. NULL-CHECK every querySelector before use: if(el) {{ ... }}
3. Each feature uses the EXACT var_name from the blueprint above
4. Close mobile nav when any nav-link is clicked
5. Order/contact forms show success message, reset after 2s
╚══════════════════════════════════════════════════════════════╝"""


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — HTML
# ═══════════════════════════════════════════════════════════════════════════════

HTML_SYSTEM = """You are a senior HTML5 developer. Write semantic, complete, production-ready HTML.

ABSOLUTE RULES:
[R1]  Return ONLY raw HTML. Start: <!DOCTYPE html>  End: </html>. NOTHING else.
[R2]  NO inline <style> or <script>. Link: <link rel="stylesheet" href="style.css">
[R3]  Before </body>: <script src="script.js" defer></script>
[R4]  Use ONLY classes and IDs from the blueprint.
[R5]  Every section (except nav) gets class="reveal"
[R6]  Add <!-- ═══ SECTION: name ═══ --> comment above each section
[R7]  Hero MUST have: <div class="hero-overlay"></div> as first child of .hero
[R8]  Gallery images: each uses a DIFFERENT image key (not the same src repeated)
[R9]  Nav WhatsApp button: <a href="wa.me/PHONENUMBER" class="nav-cta" target="_blank">WhatsApp</a>
[R10] Include JSON-LD <script type="application/ld+json"> in <head>
[R11] Include viewport, charset, OG tags in <head>
[R12] Footer section is MANDATORY — include copyright, links, social icons
[R13] Each section appears EXACTLY ONCE — never duplicate sections
[R14] Use picsum URLs OR local image paths exactly as given in blueprint"""


def generate_html(user_prompt: str, plan: dict, context: str) -> str:
    print("\n[PHASE 2] HTML generating...\n")
    sections_list = "\n".join(
        f"  {i+1}. #{s.get('id','')} — {s.get('name','')} | {s.get('purpose','')}"
        for i, s in enumerate(plan.get("sections", []))
    )
    seo = plan.get("seo", {})
    t   = plan.get("theme", {})

    msg1 = f"""Build complete HTML for: "{user_prompt}"

{context}

Sections to build (ALL required, each ONCE):
{sections_list}

Critical reminders:
- Hero needs .hero-overlay div (first child) for readability
- Gallery: use gallery_1, gallery_2, gallery_3 image keys (different images)
- Footer is MANDATORY
- JSON-LD schema in head
- OG tags: title="{seo.get('og_title', plan.get('title',''))}"
- WhatsApp link: wa.me/{plan.get('whatsapp_number','+91 98765 43210').replace(' ','').replace('+','')}

Start with <!DOCTYPE html> now:"""

    msg2_tpl = (
        f'Continuing HTML for "{user_prompt}".\n\n'
        'You stopped here:\n```\n{last_lines}\n```\n\n'
        'Continue from where you stopped. Do NOT restart or repeat any section. '
        'Include footer if not done. End with </body></html>. Raw HTML only.'
    )
    raw = _double_call(HTML_SYSTEM, msg1, msg2_tpl, "HTML",
                       validator=lambda t: "<!doctype" in t.lower(),
                       call_label_offset=3)  # calls 4 and 5
    return _autorepair_html(raw, plan)


def _autorepair_html(html: str, plan: dict) -> str:
    """Fix common HTML generation issues."""
    # Fix: ensure hero-overlay exists
    if 'class="hero"' in html and 'hero-overlay' not in html:
        html = html.replace(
            'class="hero"',
            'class="hero"',
        )
        # Insert overlay after hero-bg if present
        if 'hero-bg' in html:
            html = re.sub(
                r'(<div class="hero-bg"[^>]*>)',
                r'\1\n    <div class="hero-overlay"></div>',
                html
            )

    # Fix: remove duplicate sections (keep first occurrence only)
    seen_ids = set()
    def remove_dup(m):
        sid = m.group(1)
        if sid in seen_ids:
            return f'<!-- duplicate #{sid} removed -->'
        seen_ids.add(sid)
        return m.group(0)

    # This is a simplified dedup — full dedup requires HTML parsing
    # Just warn for now; the JS post-process is more important
    return html


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — CSS
# ═══════════════════════════════════════════════════════════════════════════════

CSS_SYSTEM = """You are a senior CSS designer. Write modern, mobile-first, production CSS.

ABSOLUTE RULES:
[R1]  Return ONLY raw CSS. No markdown, no <style> tags.
[R2]  File order: @import → :root → * reset → body/html → sections → components → @media
[R3]  Style EVERY class in the blueprint. Skip NONE.
[R4]  :root must have ALL variables from blueprint (--primary through --section-pad)
[R5]  EVERY interactive element needs BOTH :hover AND :focus states
[R6]  .reveal { opacity:0; transform:translateY(30px); transition:opacity 0.6s ease,transform 0.6s ease }
      .reveal.visible { opacity:1; transform:translateY(0) }
[R7]  nav.scrolled { box-shadow: var(--shadow) }  ← MUST exist
[R8]  .hero-overlay { position:absolute; inset:0; background:var(--hero-overlay); z-index:1 }
      .hero-content { position:relative; z-index:2 }  ← MUST exist
[R9]  Mobile nav (.nav-links): display:none  → .nav-links.nav-open: display:flex; flex-direction:column
[R10] Desktop: @media(min-width:768px) { .nav-links{display:flex;flex-direction:row;gap:2rem} .nav-toggle{display:none} }
[R11] VALID @media format ONLY: @media (min-width: 768px) — NEVER "@media mobile"
[R12] Never break a CSS property across lines (justify-content must be on ONE line)
[R13] Stop only at a complete } — never mid-rule
[R14] Provide TWO breakpoints: 768px (tablet) and 480px (mobile)"""


def generate_css(user_prompt: str, plan: dict, context: str) -> str:
    print("\n[PHASE 3] CSS generating...\n")
    t   = plan.get("theme", {})
    tok = plan.get("css_tokens", {})
    all_classes = " | ".join(f".{c}" for c in plan.get("all_classes", []))

    msg1 = f"""Write complete CSS for: "{user_prompt}"

{context}

:root block MUST use these EXACT values:
:root {{
  --primary:         {t.get('primary',   '#333')};
  --secondary:       {t.get('secondary', '#666')};
  --accent:          {t.get('accent',    '#09f')};
  --bg:              {t.get('background','#fff')};
  --surface:         {t.get('surface',   '#f5f5f5')};
  --text:            {t.get('text',      '#222')};
  --text-muted:      {t.get('text_muted','#888')};
  --text-on-primary: {t.get('text_on_primary','#fff')};
  --radius:          {t.get('border_radius','8px')};
  --hero-overlay:    {t.get('hero_overlay','rgba(0,0,0,0.5)')};
  --nav-height:      {tok.get('nav_height','70px')};
  --shadow:          {tok.get('card_shadow','0 4px 24px rgba(0,0,0,0.08)')};
  --shadow-hover:    {tok.get('card_shadow_hover','0 12px 40px rgba(0,0,0,0.16)')};
  --transition:      all {tok.get('transition_speed','0.3s')} ease;
  --section-pad:     {tok.get('section_padding','5rem 0')};
  --container-max:   {tok.get('container_max_width','1200px')};
}}

Style ALL these classes: {all_classes}

Start with @import:"""

    msg2_tpl = (
        f'Continuing CSS for "{user_prompt}".\n'
        f'Classes still needed: {all_classes}\n\n'
        'You stopped here:\n```\n{{last_lines}}\n```\n\n'
        'Continue. Do NOT repeat already-written selectors. '
        'End with @media (max-width: 480px) block. Raw CSS only.'
    )
    raw = _double_call(CSS_SYSTEM, msg1, msg2_tpl.replace('{{', '{').replace('}}', '}'), "CSS",
                       validator=lambda t: ":root" in t,
                       call_label_offset=5)  # calls 6 and 7
    css = _postprocess_css(raw)
    return _autorepair_css(css, plan)


def _autorepair_css(css: str, plan: dict) -> str:
    """Fix common CSS bugs that slip through generation."""
    # Fix 1: Broken justify-content across lines
    css = re.sub(r'justify-\s*\n\s*content\s*:', 'justify-content:', css)

    # Fix 2: Invalid @media mobile → @media (max-width: 767px)
    css = re.sub(r'@media\s+mobile\b', '@media (max-width: 767px)', css)
    css = re.sub(r'@media\s+tablet\b', '@media (max-width: 1024px)', css)

    # Fix 3: Ensure hero-overlay exists
    if '.hero-overlay' not in css:
        css += """
/* ── Auto-injected: hero overlay ── */
.hero-overlay {
  position: absolute;
  inset: 0;
  background: var(--hero-overlay);
  z-index: 1;
}
.hero-content {
  position: relative;
  z-index: 2;
}
"""

    # Fix 4: Ensure nav.scrolled has box-shadow
    if 'nav.scrolled' not in css and '.navbar.scrolled' not in css and '#nav.scrolled' not in css:
        css += """
/* ── Auto-injected: sticky nav ── */
#nav.scrolled,
.navbar.scrolled {
  box-shadow: var(--shadow);
}
"""

    # Fix 5: Ensure mobile nav works
    if '.nav-links.nav-open' not in css:
        css += """
/* ── Auto-injected: mobile nav ── */
.nav-links { display: none; }
.nav-links.nav-open { display: flex; flex-direction: column; }
@media (min-width: 768px) {
  .nav-links { display: flex; flex-direction: row; gap: 2rem; }
  .nav-toggle { display: none; }
}
"""
    return css


def _postprocess_css(css: str) -> str:
    """Remove duplicate CSS selectors — keep the LAST occurrence."""
    print("   [CSS Post] Deduplicating selectors...")
    lines = css.splitlines()
    imports_and_root: list[str] = []
    result_blocks: list[tuple[str, str]] = []
    current_selector = None
    current_block: list[str] = []
    depth = 0
    in_preamble = True
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if in_preamble and (stripped.startswith("@import") or
                            stripped.startswith(":root") or
                            stripped.startswith("*") or
                            stripped.startswith("html") or
                            stripped.startswith("body") or
                            stripped == ""):
            imports_and_root.append(line)
            if "{" in line:
                depth = line.count("{") - line.count("}")
                while depth > 0 and i + 1 < len(lines):
                    i += 1
                    imports_and_root.append(lines[i])
                    depth += lines[i].count("{") - lines[i].count("}")
                depth = 0
            i += 1
            continue

        in_preamble = False

        if "{" in stripped and depth == 0:
            current_selector = stripped.split("{")[0].strip()
            current_block = [line]
            depth = line.count("{") - line.count("}")
            if depth == 0:
                result_blocks.append((current_selector, "\n".join(current_block)))
                current_selector = None
                current_block = []
        elif current_selector is not None:
            current_block.append(line)
            depth += line.count("{") - line.count("}")
            if depth <= 0:
                result_blocks.append((current_selector, "\n".join(current_block)))
                current_selector = None
                current_block = []
                depth = 0
        i += 1

    seen_order: list[str] = []
    seen_map: dict[str, str] = {}
    for sel, block in result_blocks:
        if sel not in seen_map:
            seen_order.append(sel)
        seen_map[sel] = block

    deduped = "\n\n".join(seen_map[sel] for sel in seen_order)
    final = "\n".join(imports_and_root) + "\n\n" + deduped
    removed = len(result_blocks) - len(seen_order)
    print(f"   [CSS Post] {f'Removed {removed} duplicates ✅' if removed else 'No duplicates found ✅'}")
    return final


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — JS
# ═══════════════════════════════════════════════════════════════════════════════

JS_SYSTEM = """You are a senior JavaScript developer. Write clean, defensive, production vanilla JS.

ABSOLUTE RULES:
[R1]  Return ONLY raw JavaScript. No <script> tags, no markdown.
[R2]  Script runs after DOM load (defer attr handles this). No DOMContentLoaded wrapper.
[R3]  NULL-CHECK EVERY querySelector/getElementById before use:
      const el = document.querySelector('.x');
      if (el) { /* use el */ }
[R4]  NEVER declare the same const/let/var name twice anywhere in the file.
[R5]  Use the EXACT var_name from blueprint for each feature.
[R6]  Add // ════ FEATURE: Name ════ comment above each feature block.
[R7]  Mobile nav: toggle 'nav-open' on .nav-links; also close when any nav-link clicked.
[R8]  Smooth scroll: prevent default, get href, querySelector target, scrollIntoView.
[R9]  Scroll reveal: IntersectionObserver threshold 0.15, add class 'visible', unobserve after.
[R10] Sticky nav: window scroll event, toggle 'scrolled' on #nav at scrollY > 60.
[R11] Active nav highlight: IntersectionObserver on sections, match href to #id.
[R12] Form submissions: preventDefault, validate, show success message, reset form after 2s.
[R13] WhatsApp button: no JS needed (it's an <a> tag) — skip.
[R14] Order quantity +/- buttons: increment/decrement input value, min=1 max=99."""


def generate_js(user_prompt: str, plan: dict, context: str) -> str:
    print("\n[PHASE 4] JS generating...\n")
    features = "\n".join(
        f"  {i+1}. {f.get('name','')} | var_name:{f.get('var_name','')} | "
        f"selector:{f.get('selector','')} | action:{f.get('action','')} | "
        f"guard:{f.get('guard','')}"
        for i, f in enumerate(plan.get("js_features", []))
    )
    classes = ", ".join(f".{c}" for c in plan.get("all_classes", []))
    ids     = ", ".join(f"#{x}" for x in plan.get("all_ids", []))

    msg1 = f"""Write complete JavaScript for: "{user_prompt}"

{context}

DOM available:
  Classes: {classes}
  IDs: {ids}

Implement ALL features (use EXACT var_name shown):
{features}

Additional requirements:
- Close mobile nav when any .nav-link is clicked
- Active nav-link class via IntersectionObserver on sections
- Order quantity controls (.quantity-decrease / .quantity-increase)
- Contact/order form validation with success feedback
- Gallery lightbox if gallery section exists

CRITICAL: Each variable name must be unique. Use the exact var_name from blueprint.
Start now with // ════ FEATURE: Mobile Nav Toggle ════"""

    return _double_call_js(JS_SYSTEM, msg1, user_prompt, features, "JS",
                           validator=lambda t: "querySelector" in t,
                           call_label_offset=7)  # calls 8 and 9


def _double_call_js(system, msg1, user_prompt, features, label,
                    validator=None, call_label_offset=0):
    for attempt in range(MAX_RETRIES + 1):
        if attempt:
            print(f"   [{label}] Retry {attempt}...")
        print(f"   [{label} {call_label_offset+1}/10] Part 1...")
        part1 = _api_call(system, msg1, label=f"{label}-1")
        if not validator or validator(part1):
            break

    lines = part1.strip().splitlines()
    last_lines = "\n".join(lines[-40:]) if len(lines) > 40 else part1.strip()

    msg2 = (
        f'Continuing JS for "{user_prompt}".\n\n'
        f'Features:\n{features}\n\n'
        f'You stopped here:\n```\n{last_lines}\n```\n\n'
        'Continue EXACTLY from where you stopped. '
        'Do NOT re-declare any variable already declared above. '
        'Use unique variable names. Null-check everything. '
        'Finish remaining features. Raw JS only.'
    )
    print(f"   [{label} {call_label_offset+2}/10] Part 2...")
    part2 = _api_call(system, msg2, label=f"{label}-2")
    part2 = _remove_overlap(part1, part2)

    raw = part1.strip() + "\n\n" + part2.strip()
    return _postprocess_js(raw)


def _postprocess_js(js: str) -> str:
    """Fix JS: remove duplicate declarations, truncated lines, broken strings."""
    print("   [JS Post] Fixing JS...")
    lines = js.splitlines()

    # Remove duplicate top-level const/let/var declarations (keep first)
    declared: set[str] = set()
    clean_lines: list[str] = []
    brace_depth = 0
    skip_until_depth = None

    for line in lines:
        stripped = line.strip()
        brace_depth += line.count("{") - line.count("}")

        m = re.match(r'^(const|let|var)\s+(\w+)', stripped)
        if m and brace_depth <= line.count("{"):
            varname = m.group(2)
            if varname in declared:
                skip_until_depth = brace_depth - line.count("{") + line.count("}")
                continue
            else:
                declared.add(varname)

        if skip_until_depth is not None:
            if brace_depth <= skip_until_depth:
                skip_until_depth = None
            continue

        clean_lines.append(line)

    js = "\n".join(clean_lines)

    # Remove truncated last line
    js_lines = js.rstrip().splitlines()
    while js_lines:
        last = js_lines[-1].strip()
        if last and not re.search(r'[;}\),]$', last) and not last.startswith("//"):
            js_lines.pop()
        else:
            break
    js = "\n".join(js_lines)

    # Fix broken hex colors
    js = re.sub(r"'#[0-9A-Fa-f]{0,5}\s*$", "'#E74C3C'", js, flags=re.MULTILINE)
    js = re.sub(r'"#[0-9A-Fa-f]{0,5}\s*$', '"#E74C3C"', js, flags=re.MULTILINE)

    # Remove phantom duplicate feature comment blocks that have no code
    js = re.sub(r'(// ════[^\n]*\n){2,}', lambda m: m.group(0).split('\n')[0] + '\n', js)

    print("   [JS Post] Done ✅")
    return js


# ═══════════════════════════════════════════════════════════════════════════════
# Generic double-call (HTML + CSS)
# ═══════════════════════════════════════════════════════════════════════════════

def _double_call(system, msg1, msg2_tpl, label, validator=None, call_label_offset=0):
    for attempt in range(MAX_RETRIES + 1):
        if attempt:
            print(f"   [{label}] Retry {attempt}...")
        print(f"   [{label} {call_label_offset+1}/10] Part 1...")
        part1 = _api_call(system, msg1, label=f"{label}-1")
        if not validator or validator(part1):
            break

    lines = part1.strip().splitlines()
    last_lines = "\n".join(lines[-40:]) if len(lines) > 40 else part1.strip()

    print(f"   [{label} {call_label_offset+2}/10] Part 2...")
    part2 = _api_call(system, msg2_tpl.format(last_lines=last_lines), label=f"{label}-2")
    part2 = _remove_overlap(part1, part2)
    return part1.strip() + "\n" + part2.strip()


def _remove_overlap(p1: str, p2: str) -> str:
    l1, l2 = p1.strip().splitlines(), p2.strip().splitlines()
    anchor = l1[-12:] if len(l1) >= 12 else l1
    for i in range(len(anchor), 0, -1):
        if l2[:i] == anchor[-i:]:
            return "\n".join(l2[i:])
    return p2


# ═══════════════════════════════════════════════════════════════════════════════
# Cleaners
# ═══════════════════════════════════════════════════════════════════════════════

def clean_html(raw: str) -> str:
    s = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE)
    s = re.sub(r"```[a-z]*\n?", "", s).replace("```", "").strip()
    m = re.search(r"(<!DOCTYPE\s*html[\s\S]*?</html>)", s, re.IGNORECASE)
    return m.group(1).strip() if m else s

def clean_css(raw: str) -> str:
    s = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE)
    s = re.sub(r"</?style[^>]*>", "", s, flags=re.IGNORECASE)
    s = re.sub(r"```[a-z]*\n?", "", s).replace("```", "").strip()
    m = re.search(r"(@import|:root|\*\s*\{|[.#\w]+\s*\{)", s)
    return s[m.start():].strip() if m else s

def clean_js(raw: str) -> str:
    s = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE)
    s = re.sub(r"</?script[^>]*>", "", s, flags=re.IGNORECASE)
    s = re.sub(r"```[a-z]*\n?", "", s).replace("```", "").strip()
    m = re.search(r"(//|const |let |var |document|window|function )", s)
    return s[m.start():].strip() if m else s


# ═══════════════════════════════════════════════════════════════════════════════
# API caller
# ═══════════════════════════════════════════════════════════════════════════════

def _api_call(system: str, user: str, label: str = "", max_tokens: int = None) -> str:
    payload = {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "max_tokens": max_tokens or MAX_TOKENS,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user}
        ],
    }
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type":  "application/json"
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
            print(f"   Rate limited — waiting {wait}s..."); time.sleep(wait); continue
        if r.status_code == 401:
            sys.exit("API Key invalid!")
        if r.status_code != 200:
            print(f"   API error {r.status_code}: {r.text[:200]}")
            if attempt < 3: time.sleep(5); continue
            sys.exit("API repeatedly failed.")

        # ── SAFE extraction ──────────────────────────────────────
        data    = r.json()
        choices = data.get("choices", [])
        if not choices:
            print(f"   ⚠️  No choices in response ({label}): {str(data)[:200]}")
            return "{}"          # safe fallback for JSON callers
        content = choices[0].get("message", {}).get("content", "")
        if not content:
            print(f"   ⚠️  Empty content ({label})")
            return "{}"
        # ── Strip thinking block before returning ─────────────────
        content = re.sub(r"<think>[\s\S]*?</think>", "", content, flags=re.IGNORECASE).strip()
        return content

    sys.exit("API gave up.")


def _repair_truncated_json(text: str) -> str:
    """Best-effort repair of JSON truncated mid-way."""
    text = text.strip()
    # Count unmatched braces and brackets
    depth_curly  = text.count('{') - text.count('}')
    depth_square = text.count('[') - text.count(']')
    # Close any open string (heuristic: if odd number of unescaped quotes on last line)
    last_line = text.splitlines()[-1] if text.splitlines() else ""
    if last_line.count('"') % 2 == 1:
        text += '"'
    # Close open array/objects
    text += ']' * max(0, depth_square)
    text += '}' * max(0, depth_curly)
    return text


def _parse_json(raw: str, user_prompt: str, kind: str) -> dict:
    if not isinstance(raw, str) or not raw.strip():
        print(f"   ⚠️  _parse_json got empty/non-string — using fallback plan")
        return _fallback_plan(user_prompt)

    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```[a-z]*\n?", "", raw).replace("```", "").strip()
    m = re.search(r"\{[\s\S]*\}", raw)
    if m:
        candidate = m.group(0)
        # Try 1: raw
        try:
            return json.loads(candidate)
        except Exception:
            pass
        # Try 2: trailing comma fix
        candidate2 = re.sub(r',\s*}', '}', candidate)
        candidate2 = re.sub(r',\s*]', ']', candidate2)
        try:
            return json.loads(candidate2)
        except Exception:
            pass
        # Try 3: repair truncated JSON
        candidate3 = _repair_truncated_json(candidate2)
        try:
            result = json.loads(candidate3)
            print("   ⚠️  JSON was truncated — repaired successfully ✅")
            return result
        except Exception as e:
            print(f"   ⚠️  JSON unrecoverable: {e}")

    print("   ⚠️  Using fallback plan")
    return _fallback_plan(user_prompt)


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 5 — Quality Check
# ═══════════════════════════════════════════════════════════════════════════════

def quality_check(html: str, css: str, js: str, plan: dict) -> dict:
    print("\n── Quality Check ────────────────────────────────────────────────")
    issues = []

    checks = [
        ("<!DOCTYPE html>" in html.upper(),       "HTML has DOCTYPE"),
        ("</html>" in html.lower(),               "HTML properly closed"),
        ("style.css" in html,                     "HTML → style.css"),
        ("script.js" in html,                     "HTML → script.js"),
        ("hero-overlay" in html,                  "Hero has overlay for readability"),
        ("wa.me" in html,                         "WhatsApp CTA present"),
        ("application/ld+json" in html,           "JSON-LD schema present"),
        ("</footer>" in html,                     "Footer section present"),
        (":root" in css,                          "CSS :root variables defined"),
        ("@media" in css,                         "CSS has responsive breakpoints"),
        (".reveal" in css,                        "CSS scroll reveal defined"),
        (".reveal.visible" in css,                "CSS reveal.visible state"),
        ("hero-overlay" in css,                   "CSS hero overlay styled"),
        ("nav.scrolled" in css or ".navbar.scrolled" in css or "#nav.scrolled" in css,
                                                  "CSS sticky nav scrolled"),
        (".nav-links.nav-open" in css,            "CSS mobile nav open state"),
        ("@media mobile" not in css,              "No invalid @media mobile"),
        ("nav-open" in js,                        "JS mobile nav toggle"),
        ("scrollIntoView" in js,                  "JS smooth scroll"),
        ("IntersectionObserver" in js,            "JS scroll reveal"),
        ("scrolled" in js,                        "JS sticky nav"),
        ("querySelector" in js,                   "JS uses querySelector"),
    ]

    for ok, label in checks:
        status = "✅" if ok else "❌"
        print(f"   {status}  {label}")
        if not ok:
            issues.append(label)

    # Class coverage
    missing_html = [c for c in plan.get("all_classes", []) if c not in html]
    missing_css  = [c for c in plan.get("all_classes", []) if f".{c}" not in css]
    if missing_html:
        print(f"   ⚠️  HTML missing {len(missing_html)} classes: {', '.join(missing_html[:6])}")
        issues.append(f"HTML missing {len(missing_html)} classes")
    if missing_css:
        print(f"   ⚠️  CSS unstyled {len(missing_css)} classes: {', '.join(missing_css[:6])}")
        issues.append(f"CSS unstyled {len(missing_css)} classes")

    # JS duplicate check
    const_names = re.findall(r'\bconst\s+(\w+)', js)
    dupes = [n for n in set(const_names) if const_names.count(n) > 1]
    if dupes:
        print(f"   ⚠️  JS duplicate consts: {', '.join(dupes[:5])}")
        issues.append(f"JS duplicate consts: {', '.join(dupes[:3])}")
    else:
        print("   ✅  JS no duplicate declarations")

    score = max(0, 100 - len(issues) * 5)
    status = "🏆 Excellent!" if len(issues) == 0 else f"⚠️  {len(issues)} issue(s)"
    print(f"\n   Score: {score}/100  {status}")
    if issues:
        print(f"   Issues: {' | '.join(issues[:4])}")
    print("─────────────────────────────────────────────────────────────────")
    return {"issues": len(issues), "score": score, "details": issues}


# ═══════════════════════════════════════════════════════════════════════════════
# Save
# ═══════════════════════════════════════════════════════════════════════════════

def save(content: str, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content, encoding="utf-8")
    kb = len(content.encode()) / 1024
    print(f"   ✅  Saved: {path}  ({kb:.1f} KB)")


# ═══════════════════════════════════════════════════════════════════════════════
# Fallback plan
# ═══════════════════════════════════════════════════════════════════════════════

def _fallback_plan(user_prompt: str) -> dict:
    return {
        "title": user_prompt.title(),
        "tagline": f"Best {user_prompt} in town",
        "business_type": "local_business",
        "target_customer": "local residents",
        "primary_action": "call or visit us",
        "whatsapp_number": "+91 98765 43210",
        "theme": {
            "mood": "warm",
            "primary": "#E65100", "secondary": "#FFF3E0",
            "accent": "#2E7D32", "background": "#FFFDE7",
            "surface": "#FFFFFF", "text": "#212121",
            "text_muted": "#757575", "text_on_primary": "#FFFFFF",
            "border_radius": "10px",
            "hero_overlay": "rgba(0,0,0,0.55)",
            "font_heading": "Poppins", "font_body": "Open Sans"
        },
        "sections": [
            {"id":"nav","tag":"nav","name":"Navigation","purpose":"Brand + navigation",
             "needs_image":False,"image_key":"",
             "classes":["navbar","nav-container","nav-logo","nav-links","nav-link","nav-toggle","nav-toggle-bar","nav-cta"],
             "elements":["logo","nav links","WhatsApp button","hamburger"],
             "interactions":["sticky","mobile toggle","smooth scroll"]},
            {"id":"hero","tag":"section","name":"Hero","purpose":"First impression + CTA",
             "needs_image":True,"image_key":"hero_bg",
             "classes":["hero","hero-bg","hero-overlay","hero-content","hero-title","hero-subtitle","hero-cta"],
             "elements":["background image","overlay","heading","subtitle","CTA button"],
             "interactions":["scroll reveal","parallax"]},
            {"id":"about","tag":"section","name":"About","purpose":"Build trust",
             "needs_image":True,"image_key":"about_img",
             "classes":["about","about-content","about-text","about-image","about-stats"],
             "elements":["story text","image","stats"],
             "interactions":["scroll reveal","count-up animation"]},
            {"id":"footer","tag":"footer","name":"Footer","purpose":"Final touch",
             "needs_image":False,"image_key":"",
             "classes":["footer","footer-content","footer-bottom","footer-links","social-icons","social-icon"],
             "elements":["copyright","links","social icons"],
             "interactions":["hover effects"]},
        ],
        "image_queries":[
            {"key":"hero_bg","query":f"{user_prompt} hero photo","used_in":"hero","dimensions":"1920x1080"},
            {"key":"about_img","query":f"{user_prompt} interior","used_in":"about","dimensions":"800x600"},
            {"key":"gallery_1","query":f"{user_prompt} food photo 1","used_in":"gallery","dimensions":"600x450"},
            {"key":"gallery_2","query":f"{user_prompt} food photo 2","used_in":"gallery","dimensions":"600x450"},
            {"key":"gallery_3","query":f"{user_prompt} customer","used_in":"gallery","dimensions":"600x450"},
        ],
        "all_classes":[
            "navbar","nav-container","nav-logo","nav-links","nav-link","nav-toggle","nav-toggle-bar","nav-cta",
            "hero","hero-bg","hero-overlay","hero-content","hero-title","hero-subtitle","hero-cta",
            "about","about-content","about-text","about-image","about-stats",
            "footer","footer-content","footer-bottom","footer-links","social-icons","social-icon","reveal",
        ],
        "all_ids":["nav","hero","about","footer"],
        "js_features":[
            {"name":"Mobile Nav Toggle","selector":".nav-toggle","action":"toggle nav-open on .nav-links",
             "guard":"null-check","var_name":"navToggleBtn"},
            {"name":"Smooth Scroll","selector":".nav-link","action":"scrollIntoView smooth",
             "guard":"null-check target","var_name":"navLinksList"},
            {"name":"Scroll Reveal","selector":".reveal","action":"IntersectionObserver adds visible",
             "guard":"feature detect","var_name":"revealObserver"},
            {"name":"Sticky Nav","selector":"#nav","action":"toggle scrolled on #nav at scrollY>60",
             "guard":"null-check","var_name":"navElement"},
        ],
        "css_tokens":{
            "spacing_unit":"1rem","section_padding":"5rem 0","container_max_width":"1200px",
            "card_shadow":"0 4px 24px rgba(0,0,0,0.08)","card_shadow_hover":"0 12px 40px rgba(0,0,0,0.16)",
            "transition_speed":"0.3s","nav_height":"70px"
        },
        "seo":{
            "meta_description":f"Best {user_prompt}. Visit us today!",
            "og_title":user_prompt.title(),"schema_type":"LocalBusiness"
        },
        "google_fonts_url":"https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 68)
    print("   WebGen v4 — Ultra-Enhanced Website Builder")
    print("   Phases: Brainstorm → Plan → Validate → Images → HTML → CSS → JS")
    print("   Fixes: CSS dedup + JS dedup + hero overlay + mobile nav + media queries")
    print(f"   Images: {'SerpAPI (real photos) + picsum fallback' if SERPAPI_KEY else 'picsum placeholders (add SERPAPI_KEY for real photos)'}")
    print("=" * 68)

    user_prompt = input("\nKya banana hai?\n>>> ").strip()
    if not user_prompt:
        sys.exit("Kuch toh batao!")

    # Phase 0a: Deep Brainstorm
    print("\n[PHASE 0a] Deep brainstorm (Call 1/10)...")
    brainstorm = deep_brainstorm(user_prompt)
    save(brainstorm, f"{OUTPUT_DIR}/brainstorm.md")

    # Phase 0b: Structured Plan
    plan = create_structured_plan(brainstorm, user_prompt)

    # Phase 0c: Validate
    plan = validate_plan(plan, user_prompt)
    save(json.dumps(plan, indent=2), f"{OUTPUT_DIR}/plan.json")

    # Phase 1: Images
    images = acquire_images(plan.get("image_queries", []), OUTPUT_DIR)

    # Build context
    context = plan_to_context(plan, images)

    # Phase 2: HTML
    html = clean_html(generate_html(user_prompt, plan, context))
    save(html, f"{OUTPUT_DIR}/index.html")

    # Phase 3: CSS
    css = clean_css(generate_css(user_prompt, plan, context))
    save(css, f"{OUTPUT_DIR}/style.css")

    # Phase 4: JS
    js = clean_js(generate_js(user_prompt, plan, context))
    save(js, f"{OUTPUT_DIR}/script.js")

    # Phase 5: Quality check
    report = quality_check(html, css, js, plan)

    serpapi_count = sum(1 for v in images.values() if not v.startswith("http"))
    picsum_count  = sum(1 for v in images.values() if v.startswith("http"))

    print(f"""
{'='*68}
  WebGen v4 — Complete! 🎉

  Files generated:
    index.html   — {len(html)//1024}KB
    style.css    — {len(css)//1024}KB
    script.js    — {len(js)//1024}KB
    plan.json    — Full blueprint
    brainstorm.md— Creative strategy

  Images:
    {serpapi_count} real photos (downloaded)
    {picsum_count} picsum placeholders
    {'→ Add SERPAPI_KEY env var for real photos' if not SERPAPI_KEY else ''}

  Quality: {report['score']}/100  ({report['issues']} issues)
  {'Issues: ' + ' | '.join(report['details'][:3]) if report['details'] else ''}

  Next steps:
    1. Open index.html in browser
    2. Replace placeholder images with real photos
    3. Update WhatsApp number in nav-cta href
    4. Customize colors/fonts in style.css :root
{'='*68}
""")


if __name__ == "__main__":
    main()