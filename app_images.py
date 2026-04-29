import requests
import re
import sys
import json
import time
import os
import urllib.request
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────
SARVAM_API_KEY  = ""
SERPAPI_KEY     = ""
MODEL           = "sarvam-105b"
API_URL         = "https://api.sarvam.ai/v1/chat/completions"
SERPAPI_URL     = "https://serpapi.com/search"
OUTPUT_DIR      = "."
IMAGES_DIR      = "images"
MAX_TOKENS      = 4096
TEMPERATURE     = 0.10
MAX_RETRIES     = 2
# ─────────────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════════
# SERPAPI — Real Image Downloader
# ═══════════════════════════════════════════════════════════════════════════════

def download_images(queries: list[dict]) -> dict[str, str]:
    if SERPAPI_KEY == "YOUR_SERPAPI_KEY_HERE":
        print("   ⚠️  SERPAPI_KEY set nahi hai — picsum.photos placeholders use honge")
        return _picsum_fallback(queries)

    img_dir = Path(OUTPUT_DIR) / IMAGES_DIR
    img_dir.mkdir(exist_ok=True)

    result = {}
    print(f"\n[IMAGES] SerpAPI se {len(queries)} image sets download ho rahe hain...\n")

    for q in queries:
        key   = q["key"]
        query = q["query"]
        count = q.get("count", 1)

        print(f"   Searching: '{query}'...")
        try:
            params = {
                "engine":  "google_images",
                "q":       query,
                "api_key": SERPAPI_KEY,
                "num":     10,
                "safe":    "active",
                "ijn":     "0",
            }
            resp = requests.get(SERPAPI_URL, params=params, timeout=15)
            data = resp.json()
            images_found = data.get("images_results", [])

            if not images_found:
                print(f"   ⚠️  No results for '{query}' — using placeholder")
                result[key] = _picsum_one(key)
                continue

            downloaded = 0
            for idx, img_info in enumerate(images_found[:15]):
                if downloaded >= count:
                    break
                img_url = img_info.get("original", "")
                if not img_url:
                    continue

                suffix = _get_ext(img_url)
                fname  = f"{key}_{idx}{suffix}" if count > 1 else f"{key}{suffix}"
                fpath  = img_dir / fname
                rel    = f"{IMAGES_DIR}/{fname}"

                try:
                    req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=8) as r:
                        data_bytes = r.read()
                    if len(data_bytes) < 5000:
                        continue
                    fpath.write_bytes(data_bytes)
                    result[key] = rel
                    downloaded += 1
                    print(f"   ✅  {fname} ({len(data_bytes)//1024}KB)")
                except Exception:
                    continue

            if key not in result:
                result[key] = _picsum_one(key)
                print(f"   ⚠️  Download failed — using placeholder for {key}")

        except Exception as e:
            print(f"   ⚠️  SerpAPI error for '{query}': {e}")
            result[key] = _picsum_one(key)

        time.sleep(0.5)

    return result


def _get_ext(url: str) -> str:
    url_clean = url.split("?")[0].lower()
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        if url_clean.endswith(ext):
            return ".jpg" if ext == ".jpeg" else ext
    return ".jpg"


def _picsum_one(key: str) -> str:
    seeds = {"hero": "100/600", "about": "200/400", "product": "300/300",
             "gallery": "400/300", "team": "500/300", "banner": "600/400"}
    for k, v in seeds.items():
        if k in key.lower():
            return f"https://picsum.photos/seed/{key}/{v}"
    return f"https://picsum.photos/seed/{key}/400/300"


def _picsum_fallback(queries: list[dict]) -> dict:
    return {q["key"]: _picsum_one(q["key"]) for q in queries}


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 0 — PLANNING  (Call 1)
# ═══════════════════════════════════════════════════════════════════════════════

PLAN_SYSTEM = """You are a senior web architect creating a detailed blueprint.

OUTPUT FORMAT: Return ONLY a valid JSON object. Zero extra text. Zero markdown fences.

The JSON must have this EXACT structure:
{
  "title": "string",
  "theme": {
    "mood": "dark|light|vibrant|minimal|earthy|professional",
    "primary":    "#hex",
    "secondary":  "#hex",
    "accent":     "#hex",
    "background": "#hex",
    "surface":    "#hex",
    "text":       "#hex",
    "text_muted": "#hex",
    "font_heading": "Google Font Name",
    "font_body":    "Google Font Name",
    "border_radius": "8px"
  },
  "sections": [
    {
      "id": "nav",
      "tag": "nav",
      "name": "Navigation",
      "classes": ["navbar", "nav-container", "nav-logo", "nav-links", "nav-link", "nav-toggle", "nav-toggle-bar"],
      "elements": ["logo text", "5 nav links", "hamburger icon"],
      "needs_image": false,
      "image_query": ""
    }
  ],
  "image_queries": [
    {"key": "hero_bg",   "query": "fresh vegetables colorful market india", "used_in": "hero background"},
    {"key": "about_img", "query": "indian grocery store interior",           "used_in": "about section"}
  ],
  "all_classes": ["flat", "deduplicated", "list", "of", "every", "class"],
  "all_ids":     ["nav", "hero", "about"],
  "js_features": [
    {
      "name": "Mobile Nav Toggle",
      "selector": ".nav-toggle",
      "action": "toggle class 'nav-open' on .nav-links",
      "guard": "null-check before addEventListener"
    },
    {
      "name": "Smooth Scroll",
      "selector": ".nav-link",
      "action": "preventDefault, scrollIntoView({behavior:'smooth'})",
      "guard": "null-check"
    },
    {
      "name": "Scroll Reveal",
      "selector": ".reveal",
      "action": "IntersectionObserver adds class 'visible' when 20% in view",
      "guard": "check IntersectionObserver support"
    },
    {
      "name": "Sticky Nav Shadow",
      "selector": "window scroll",
      "action": "add class 'scrolled' to nav when scrollY > 50",
      "guard": "none needed"
    }
  ],
  "google_fonts_url": "https://fonts.googleapis.com/css2?family=..."
}

RULES:
- all_classes must contain EVERY class from EVERY section's classes array (flat, no duplicates)
- all_ids must contain EVERY section's id
- image_queries: one entry per image needed in the page
- js_features: minimum 4 features, always include nav toggle + smooth scroll + scroll reveal
- font names must be valid Google Fonts"""


def create_plan(user_prompt: str) -> dict:
    print("\n[PHASE 0] Deep planning...\n")

    user_msg = f"""Website request: "{user_prompt}"

Step 1 — Decide what sections this page needs. Think about the USER'S GOAL.
Step 2 — For each section, list every HTML element and its class name.
Step 3 — Decide what images are needed and write good Google Image search queries.
Step 4 — Decide a color palette that fits the mood of "{user_prompt}".
Step 5 — List every JS interaction the user would expect.

Now output the complete JSON blueprint. No text before or after the JSON."""

    print("   [Call 1/8] Generating plan...")
    raw = _api_call(PLAN_SYSTEM, user_msg, label="Plan")
    return _parse_plan_json(raw, user_prompt)


def _parse_plan_json(raw: str, user_prompt: str) -> dict:
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```[a-z]*\n?", "", raw).replace("```", "").strip()
    m = re.search(r"\{[\s\S]*\}", raw)
    if m:
        try:
            plan = json.loads(m.group(0))
            print(f"   ✅ Plan: {len(plan.get('sections',[]))} sections | "
                  f"{len(plan.get('all_classes',[]))} classes | "
                  f"{len(plan.get('image_queries',[]))} images needed")
            return plan
        except Exception as e:
            print(f"   ⚠️  JSON parse error: {e}")
    print("   ⚠️  Using fallback plan")
    return _fallback_plan(user_prompt)


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 0b — PLAN VALIDATION  (Call 2)
# ═══════════════════════════════════════════════════════════════════════════════

VALIDATE_SYSTEM = """You are a code reviewer. Your job: fix inconsistencies in a web blueprint.
Return ONLY valid JSON — the corrected plan. No markdown. No text before/after."""


def validate_plan(plan: dict, user_prompt: str) -> dict:
    print("   [Call 2/8] Self-validating plan...")

    user_msg = f"""Original request: "{user_prompt}"

Current plan:
{json.dumps(plan, indent=2)}

Fix these issues if present:
1. all_classes missing any class from sections[].classes → add them
2. all_ids missing any section id → add them
3. js_features referencing selectors not in all_classes/all_ids → fix selectors
4. image_queries with vague queries → make them specific and visual
5. google_fonts_url not containing both font_heading and font_body → fix URL
6. Missing obvious sections for "{user_prompt}" → add them with classes and image queries

Return the complete corrected JSON."""

    raw = _api_call(VALIDATE_SYSTEM, user_msg, label="Validate")
    result = _parse_plan_json(raw, user_prompt)
    print(f"   ✅ Validated: {len(result.get('all_classes',[]))} classes confirmed")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# PLAN → CONTEXT STRING
# ═══════════════════════════════════════════════════════════════════════════════

def plan_to_context(plan: dict, images: dict) -> str:
    t = plan.get("theme", {})

    sec_lines = []
    for s in plan.get("sections", []):
        classes = " | ".join(f".{c}" for c in s.get("classes", []))
        sec_lines.append(f"  <{s.get('tag','div')} id=\"{s.get('id','')}\">"
                         f"  [{s.get('name','')}]")
        sec_lines.append(f"    classes: {classes}")
        if s.get("needs_image"):
            sec_lines.append(f"    elements: {', '.join(s.get('elements', []))}")

    img_lines = []
    for key, path in images.items():
        used = next((q.get("used_in", "") for q in plan.get("image_queries", [])
                     if q["key"] == key), "")
        img_lines.append(f"  {key}: \"{path}\"  [{used}]")

    js_lines = []
    for f in plan.get("js_features", []):
        js_lines.append(f"  • {f.get('name','')}")
        js_lines.append(f"    selector: {f.get('selector','')}")
        js_lines.append(f"    action:   {f.get('action','')}")
        js_lines.append(f"    guard:    {f.get('guard','')}")

    return f"""╔══════════════════════════════════════════════════════════╗
║                  BLUEPRINT — FOLLOW EXACTLY              ║
╚══════════════════════════════════════════════════════════╝

TITLE:      {plan.get('title','')}
MOOD:       {t.get('mood','')}

THEME COLORS (use in :root variables):
  --primary:    {t.get('primary',   '#333')}
  --secondary:  {t.get('secondary', '#666')}
  --accent:     {t.get('accent',    '#09f')}
  --bg:         {t.get('background','#fff')}
  --surface:    {t.get('surface',   '#f5f5f5')}
  --text:       {t.get('text',      '#222')}
  --text-muted: {t.get('text_muted','#888')}
  --radius:     {t.get('border_radius','8px')}

FONTS:
  Heading: {t.get('font_heading','Poppins')}
  Body:    {t.get('font_body','Open Sans')}
  Google Fonts URL: {plan.get('google_fonts_url','')}

SECTIONS (build ALL, in this order):
{chr(10).join(sec_lines)}

ALL CSS CLASSES — style EVERY one:
  {', '.join('.'+c for c in plan.get('all_classes',[]))}

ALL IDs:
  {', '.join('#'+i for i in plan.get('all_ids',[]))}

IMAGE PATHS — use these EXACT paths as src attributes:
{chr(10).join(img_lines) if img_lines else '  (no images)'}

JS FEATURES — implement ALL:
{chr(10).join(js_lines)}

╔══════════════════════════════════════════════════════════╗
║                     END OF BLUEPRINT                     ║
╚══════════════════════════════════════════════════════════╝"""


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — HTML  (Calls 3 + 4)
# ═══════════════════════════════════════════════════════════════════════════════

HTML_SYSTEM = """You are a senior HTML5 developer. You write semantic, complete, production-ready HTML.

ABSOLUTE RULES — violating any rule makes the output unusable:
[R1]  Return ONLY raw HTML. First character must be '<', last must be '>'.
[R2]  NO markdown fences (```). NO explanation text. NO <think> tags.
[R3]  Start: <!DOCTYPE html>  End: </html>  — both REQUIRED.
[R4]  NO <style> tags. NO <script> tags. External files only.
[R5]  In <head>: <link rel="stylesheet" href="style.css">
[R6]  Before </body>: <script src="script.js" defer></script>
[R7]  Use ONLY class names listed in the blueprint. Do NOT invent new class names.
[R8]  Use ONLY IDs listed in the blueprint. Do NOT invent new IDs.
[R9]  Build EVERY section in the blueprint, in order, complete.
[R10] Add comment above each section: <!-- ═══ SECTION NAME ═══ -->
[R11] Image src: use the EXACT paths from "IMAGE PATHS" in the blueprint.
[R12] Add class="reveal" to every section except nav, for scroll animations.
[R13] If token limit approached, close all open tags cleanly — never partial tags.

GOOD EXAMPLE (follow this pattern):
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page Title</title>
  <link rel="stylesheet" href="style.css">
  <link href="GOOGLE_FONTS_URL" rel="stylesheet">
</head>
<body>
  <!-- ═══ NAVIGATION ═══ -->
  <nav id="nav">
    <div class="navbar">
      <div class="nav-container">
        <div class="nav-logo">Brand</div>
        <ul class="nav-links">
          <li><a href="#hero" class="nav-link">Home</a></li>
        </ul>
        <button class="nav-toggle" aria-label="Menu">
          <span class="nav-toggle-bar"></span>
          <span class="nav-toggle-bar"></span>
          <span class="nav-toggle-bar"></span>
        </button>
      </div>
    </div>
  </nav>
  <!-- ═══ HERO ═══ -->
  <section id="hero" class="reveal">
    ...
  </section>
  <script src="script.js" defer></script>
</body>
</html>"""


def generate_html(user_prompt: str, plan: dict, context: str) -> str:
    print("\n[PHASE 2/4] HTML generate ho raha hai...\n")

    sections_ordered = "\n".join(
        f"  {i+1}. <{s.get('tag','section')} id=\"{s.get('id','')}\">"
        f"  {s.get('name','')}  |  elements: {', '.join(s.get('elements', []))}"
        for i, s in enumerate(plan.get("sections", []))
    )

    user_msg_1 = f"""Build this webpage: "{user_prompt}"

{context}

Build these sections IN ORDER, COMPLETE, no skipping:
{sections_ordered}

Start NOW with <!DOCTYPE html> — output raw HTML only."""

    user_msg_2_tpl = (
        f'You were building: "{user_prompt}"\n\n'
        f"Blueprint (reference):\n{context[:1500]}\n\n"
        "You stopped mid-way. Last lines you wrote:\n```\n{last_lines}\n```\n\n"
        "CONTINUE from exactly where you stopped.\n"
        "- Do NOT restart from <!DOCTYPE html>\n"
        "- Do NOT repeat any lines above\n"
        "- Write remaining HTML to finish the page\n"
        "- End with </body></html>\n"
        "- Raw HTML only"
    )

    return _double_call(
        HTML_SYSTEM, user_msg_1, user_msg_2_tpl, "HTML",
        validator=lambda t: "<!DOCTYPE" in t.upper() and "<body" in t.lower()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — CSS  (Calls 5 + 6)
# ═══════════════════════════════════════════════════════════════════════════════

CSS_SYSTEM = """You are a senior CSS designer. You write modern, beautiful, mobile-first CSS.

ABSOLUTE RULES:
[R1]  Return ONLY raw CSS. No markdown fences. No <style> tags. No HTML. No explanation.
[R2]  NO <think> tags. NO comments like "Here is your CSS".
[R3]  Use ONLY selectors from the blueprint. Do NOT invent new class names.
[R4]  Style EVERY class listed in the blueprint — skip none.
[R5]  File structure order (MANDATORY):
        1. @import Google Fonts
        2. :root { all CSS variables }
        3. * { box-sizing reset }
        4. Section by section, with /* ═══ SECTION ═══ */ comments
        5. @media (max-width: 768px) { mobile overrides }
[R6]  CSS variables to define in :root (use blueprint colors exactly):
        --primary, --secondary, --accent, --bg, --surface,
        --text, --text-muted, --radius, --shadow, --transition
[R7]  Every interactive element needs :hover and :focus styles.
[R8]  Scroll reveal: .reveal { opacity:0; transform:translateY(30px); transition:...}
                     .reveal.visible { opacity:1; transform:none; }
[R9]  Nav scrolled state: nav.scrolled { box-shadow: ...; }
[R10] If stopped early: stop after a complete closing } — NEVER mid-rule.

REQUIRED PATTERNS:
  /* Mobile nav hidden by default */
  .nav-links { display: none; }
  .nav-links.nav-open { display: flex; flex-direction: column; }
  /* Desktop nav */
  @media (min-width: 768px) {
    .nav-links { display: flex; flex-direction: row; }
    .nav-toggle { display: none; }
  }"""


def generate_css(user_prompt: str, plan: dict, context: str) -> str:
    print("\n[PHASE 3/4] CSS generate ho raha hai...\n")

    t = plan.get("theme", {})
    all_classes = " | ".join(f".{c}" for c in plan.get("all_classes", []))

    user_msg_1 = f"""Write complete CSS for: "{user_prompt}"

{context}

MANDATORY :root block (use these EXACT values):
:root {{
  --primary:    {t.get('primary',   '#2d6a4f')};
  --secondary:  {t.get('secondary', '#40916c')};
  --accent:     {t.get('accent',    '#95d5b2')};
  --bg:         {t.get('background','#f8f9fa')};
  --surface:    {t.get('surface',   '#ffffff')};
  --text:       {t.get('text',      '#212529')};
  --text-muted: {t.get('text_muted','#6c757d')};
  --radius:     {t.get('border_radius','8px')};
  --shadow:     0 4px 20px rgba(0,0,0,0.08);
  --transition: all 0.3s ease;
}}

Style ALL these classes (no skipping):
{all_classes}

Output raw CSS starting with @import."""

    user_msg_2_tpl = (
        f'You were writing CSS for: "{user_prompt}"\n\n'
        f"Classes still needing styles:\n{all_classes}\n\n"
        "You stopped here:\n```\n{last_lines}\n```\n\n"
        "Continue EXACTLY. Do NOT repeat selectors already written.\n"
        "Write remaining CSS rules. End with mobile @media block if not done.\n"
        "Raw CSS only."
    )

    return _double_call(
        CSS_SYSTEM, user_msg_1, user_msg_2_tpl, "CSS",
        validator=lambda t: ":root" in t and "{" in t
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — JS  (Calls 7 + 8)
# ═══════════════════════════════════════════════════════════════════════════════

# ── FIX: All literal JS braces are doubled {{ }} so that when the
#    template string is used in an f-string (not .format()), they
#    render as single { }.  The continuation prompt is built with
#    a plain f-string (no .format()) so {behavior:'smooth'} inside
#    the system prompt is never touched by format().
# ────────────────────────────────────────────────────────────────────────────

JS_SYSTEM = """You are a senior JavaScript developer. You write clean, defensive, modern vanilla JS.

ABSOLUTE RULES:
[R1]  Return ONLY raw JavaScript. No <script> tags. No markdown. No HTML. No explanation.
[R2]  Script has `defer` attribute — DOM is fully loaded. No DOMContentLoaded needed.
[R3]  Target ONLY selectors listed in the blueprint. Do NOT invent elements.
[R4]  Implement EVERY feature listed in js_features. Skip none.
[R5]  NULL-CHECK every querySelector before use:
        const el = document.querySelector('.foo');
        if (el) el.addEventListener('click', handler);
[R6]  Add comment above each feature block:
        // ════ FEATURE NAME ════
[R7]  Scroll reveal MUST use IntersectionObserver with threshold 0.15.
[R8]  Mobile nav: toggle class 'nav-open' on .nav-links when .nav-toggle clicked.
[R9]  Smooth scroll: intercept clicks on .nav-link, use scrollIntoView({{behavior:'smooth'}}).
[R10] Sticky nav: add class 'scrolled' to nav element when window.scrollY > 50.
[R11] If stopped early: stop at a clean line end — NEVER mid-statement.

REQUIRED SKELETON (follow this structure):
// ════ MOBILE NAV ════
const navToggle = document.querySelector('.nav-toggle');
const navLinks  = document.querySelector('.nav-links');
if (navToggle && navLinks) {{
  navToggle.addEventListener('click', () => {{
    navLinks.classList.toggle('nav-open');
    navToggle.classList.toggle('active');
  }});
}}

// ════ SMOOTH SCROLL ════
document.querySelectorAll('.nav-link').forEach(link => {{
  link.addEventListener('click', e => {{
    const href = link.getAttribute('href');
    if (href && href.startsWith('#')) {{
      e.preventDefault();
      const target = document.querySelector(href);
      if (target) target.scrollIntoView({{ behavior: 'smooth' }});
    }}
  }});
}});

// ════ STICKY NAV ════
const nav = document.querySelector('#nav');
window.addEventListener('scroll', () => {{
  if (nav) nav.classList.toggle('scrolled', window.scrollY > 50);
}});

// ════ SCROLL REVEAL ════
if ('IntersectionObserver' in window) {{
  const observer = new IntersectionObserver(entries => {{
    entries.forEach(e => {{
      if (e.isIntersecting) {{
        e.target.classList.add('visible');
        observer.unobserve(e.target);
      }}
    }});
  }}, {{ threshold: 0.15 }});
  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
}}"""


def generate_js(user_prompt: str, plan: dict, context: str) -> str:
    print("\n[PHASE 4/4] JavaScript generate ho raha hai...\n")

    features = "\n".join(
        f"  {i+1}. {f.get('name','')}\n"
        f"     selector: {f.get('selector','')}\n"
        f"     action:   {f.get('action','')}\n"
        f"     guard:    {f.get('guard','')}"
        for i, f in enumerate(plan.get("js_features", []))
    )
    classes = ", ".join(f".{c}" for c in plan.get("all_classes", []))
    ids     = ", ".join(f"#{i}" for i in plan.get("all_ids", []))

    user_msg_1 = f"""Write complete JavaScript for: "{user_prompt}"

{context}

Available DOM elements:
  Classes: {classes}
  IDs:     {ids}

Implement ALL these features:
{features}

Also add:
  - Active nav-link highlighting based on scroll position (Intersection Observer)
  - Close mobile nav when a nav-link is clicked
  - Any feature specific to "{user_prompt}" (e.g. product filter, counter animation, accordion FAQ)

Raw JavaScript only. Start with the nav toggle."""

    # ── KEY FIX: continuation prompt built as plain f-string, NOT via
    #    msg2_tpl.format(...).  This means {{ }} in JS_SYSTEM is never
    #    processed here, and {behavior:'smooth'} never causes a KeyError.
    # ────────────────────────────────────────────────────────────────────

    return _double_call_js(
        JS_SYSTEM, user_msg_1, user_prompt, features, "JS",
        validator=lambda t: "querySelector" in t or "addEventListener" in t
    )


def _double_call_js(system: str, msg1: str, user_prompt: str,
                    features: str, label: str, validator=None) -> str:
    """JS-specific double-call that avoids .format() on the continuation prompt."""
    for attempt in range(MAX_RETRIES + 1):
        if attempt:
            print(f"   [{label}] Retry {attempt}...")
        print(f"   [{label} 1/2] Part 1 generating...")
        part1 = _api_call(system, msg1, label=f"{label}-1")
        if validator and not validator(part1) and attempt < MAX_RETRIES:
            print(f"   [{label}] Validation failed — retrying part 1")
            continue
        break

    lines      = part1.strip().splitlines()
    last_lines = "\n".join(lines[-45:]) if len(lines) > 45 else part1.strip()

    # Plain f-string — no .format(), no KeyError risk
    msg2 = (
        f'You were writing JS for: "{user_prompt}"\n\n'
        f"Features blueprint:\n{features}\n\n"
        f"You stopped here:\n```\n{last_lines}\n```\n\n"
        "Continue EXACTLY. Do NOT repeat already-written functions.\n"
        "Write remaining JS features. Use null-checks on all selectors.\n"
        "Raw JavaScript only."
    )

    print(f"   [{label} 2/2] Part 2 generating (continuation)...")
    part2 = _api_call(system, msg2, label=f"{label}-2")
    part2 = _remove_overlap(part1, part2)

    return part1.strip() + "\n" + part2.strip()


# ═══════════════════════════════════════════════════════════════════════════════
# Generic Double-call engine (HTML + CSS)
# ═══════════════════════════════════════════════════════════════════════════════

def _double_call(system: str, msg1: str, msg2_tpl: str,
                 label: str, validator=None) -> str:
    for attempt in range(MAX_RETRIES + 1):
        if attempt:
            print(f"   [{label}] Retry {attempt}...")
        print(f"   [{label} 1/2] Part 1 generating...")
        part1 = _api_call(system, msg1, label=f"{label}-1")
        if validator and not validator(part1) and attempt < MAX_RETRIES:
            print(f"   [{label}] Validation failed — retrying part 1")
            continue
        break

    lines      = part1.strip().splitlines()
    last_lines = "\n".join(lines[-45:]) if len(lines) > 45 else part1.strip()

    print(f"   [{label} 2/2] Part 2 generating (continuation)...")
    part2 = _api_call(system, msg2_tpl.format(last_lines=last_lines), label=f"{label}-2")
    part2 = _remove_overlap(part1, part2)

    return part1.strip() + "\n" + part2.strip()


def _remove_overlap(p1: str, p2: str) -> str:
    l1, l2 = p1.strip().splitlines(), p2.strip().splitlines()
    anchor  = l1[-12:] if len(l1) >= 12 else l1
    for i in range(len(anchor), 0, -1):
        if l2[:i] == anchor[-i:]:
            return "\n".join(l2[i:])
    return p2


# ═══════════════════════════════════════════════════════════════════════════════
# API caller
# ═══════════════════════════════════════════════════════════════════════════════

def _api_call(system: str, user: str, label: str = "") -> str:
    payload = {
        "model":       MODEL,
        "temperature": TEMPERATURE,
        "max_tokens":  MAX_TOKENS,
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
                print(f"   Timeout ({label}) — retry in 5s...")
                time.sleep(5)
                continue
            sys.exit("Persistent timeout. Check internet.")
        except requests.exceptions.ConnectionError:
            sys.exit("Connection error. Check internet.")

        if r.status_code == 429:
            wait = 15 + attempt * 15
            print(f"   Rate limited — waiting {wait}s...")
            time.sleep(wait)
            continue
        if r.status_code == 401:
            sys.exit("API Key invalid!")
        if r.status_code != 200:
            print(f"   API error {r.status_code}: {r.text[:200]}")
            if attempt < 3:
                time.sleep(5)
                continue
            sys.exit("API repeatedly failed.")

        return r.json()["choices"][0]["message"]["content"]

    sys.exit("API gave up.")


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
# Quality Check
# ═══════════════════════════════════════════════════════════════════════════════

def quality_check(html: str, css: str, js: str, plan: dict) -> None:
    print("\n── Quality Check ───────────────────────────────────────────")
    issues = 0

    checks = [
        ("<!DOCTYPE html>" in html.upper(),           "HTML has DOCTYPE"),
        ("</html>" in html.lower(),                   "HTML closed properly"),
        ("style.css" in html,                         "HTML links style.css"),
        ("script.js" in html,                         "HTML links script.js"),
        (":root" in css,                              "CSS has :root variables"),
        ("@media" in css,                             "CSS has responsive breakpoint"),
        (".reveal" in css,                            "CSS has scroll reveal styles"),
        ("nav-open" in js or "nav-links" in js,       "JS has nav toggle"),
        ("scrollIntoView" in js,                      "JS has smooth scroll"),
        ("IntersectionObserver" in js,                "JS has scroll reveal observer"),
    ]

    for ok, label in checks:
        icon = "✅" if ok else "❌"
        if not ok:
            issues += 1
        print(f"   {icon}  {label}")

    missing_html = [c for c in plan.get("all_classes", []) if c not in html]
    missing_css  = [c for c in plan.get("all_classes", []) if f".{c}" not in css]
    if missing_html:
        print(f"   ⚠️  {len(missing_html)} classes missing from HTML: "
              f"{', '.join(missing_html[:6])}")
        issues += 1
    if missing_css:
        print(f"   ⚠️  {len(missing_css)} classes unstyled in CSS: "
              f"{', '.join(missing_css[:6])}")
        issues += 1

    status = "✅ All good!" if issues == 0 else f"⚠️  {issues} issue(s) — files saved anyway"
    print(f"\n   {status}")
    print("────────────────────────────────────────────────────────────")


# ═══════════════════════════════════════════════════════════════════════════════
# Save
# ═══════════════════════════════════════════════════════════════════════════════

def save(content: str, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content, encoding="utf-8")
    kb = len(content.encode()) / 1024
    print(f"   ✅  {path}  ({kb:.1f} KB)")


# ═══════════════════════════════════════════════════════════════════════════════
# Fallback plan
# ═══════════════════════════════════════════════════════════════════════════════

def _fallback_plan(user_prompt: str) -> dict:
    return {
        "title": user_prompt.title(),
        "theme": {
            "mood": "modern", "primary": "#2d6a4f", "secondary": "#40916c",
            "accent": "#95d5b2", "background": "#f8f9fa", "surface": "#ffffff",
            "text": "#212529", "text_muted": "#6c757d", "border_radius": "8px",
            "font_heading": "Poppins", "font_body": "Open Sans"
        },
        "sections": [
            {"id": "nav",    "tag": "nav",     "name": "Navigation",
             "elements": ["logo", "nav links", "toggle"],
             "needs_image": False, "image_query": "",
             "classes": ["navbar", "nav-container", "nav-logo", "nav-links",
                         "nav-link", "nav-toggle", "nav-toggle-bar"]},
            {"id": "hero",   "tag": "section", "name": "Hero",
             "elements": ["heading", "subtext", "CTA button"],
             "needs_image": True,  "image_query": user_prompt + " hero background",
             "classes": ["hero", "hero-content", "hero-title", "hero-subtitle", "hero-cta"]},
            {"id": "about",  "tag": "section", "name": "About",
             "elements": ["text", "image"],
             "needs_image": True,  "image_query": user_prompt + " interior",
             "classes": ["about", "about-container", "about-text", "about-image"]},
            {"id": "footer", "tag": "footer",  "name": "Footer",
             "elements": ["copyright"],
             "needs_image": False, "image_query": "",
             "classes": ["footer", "footer-copy"]},
        ],
        "image_queries": [
            {"key": "hero_bg",   "query": user_prompt + " hero",     "used_in": "hero background"},
            {"key": "about_img", "query": user_prompt + " interior",  "used_in": "about section"},
        ],
        "all_classes": [
            "navbar", "nav-container", "nav-logo", "nav-links", "nav-link",
            "nav-toggle", "nav-toggle-bar", "hero", "hero-content", "hero-title",
            "hero-subtitle", "hero-cta", "about", "about-container", "about-text",
            "about-image", "footer", "footer-copy"
        ],
        "all_ids": ["nav", "hero", "about", "footer"],
        "js_features": [
            {"name": "Mobile Nav Toggle", "selector": ".nav-toggle",
             "action": "toggle 'nav-open' on .nav-links", "guard": "null-check"},
            {"name": "Smooth Scroll",     "selector": ".nav-link",
             "action": "scrollIntoView smooth",            "guard": "null-check"},
            {"name": "Scroll Reveal",     "selector": ".reveal",
             "action": "IntersectionObserver adds .visible", "guard": "feature detect"},
            {"name": "Sticky Nav",        "selector": "window",
             "action": "add .scrolled to #nav on scroll > 50px", "guard": "none"},
        ],
        "google_fonts_url": (
            "https://fonts.googleapis.com/css2?"
            "family=Poppins:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap"
        )
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("   WebGen v2 — Deep Reasoning + Real Images")
    print("   8 API calls: Plan → Validate → HTML×2 → CSS×2 → JS×2")
    print("=" * 65)
    print("\nKya banana hai? (e.g. 'dark theme restaurant landing page with menu')\n")
    user_prompt = input(">>> ").strip()
    if not user_prompt:
        sys.exit("Kuch toh batao!")

    # Phase 0: Plan
    plan = create_plan(user_prompt)

    # Phase 0b: Validate
    plan = validate_plan(plan, user_prompt)

    # Save plan
    save(json.dumps(plan, indent=2), f"{OUTPUT_DIR}/plan.json")

    # Download images via SerpAPI
    image_queries = plan.get("image_queries", [])
    images = download_images(image_queries) if image_queries else {}

    # Build context
    context = plan_to_context(plan, images)
    print("\n   Context preview (first 20 lines):")
    for line in context.splitlines()[:20]:
        print("      " + line)
    print()

    # Generate files
    raw_html = generate_html(user_prompt, plan, context)
    html     = clean_html(raw_html)
    save(html, f"{OUTPUT_DIR}/index.html")

    raw_css = generate_css(user_prompt, plan, context)
    css     = clean_css(raw_css)
    save(css, f"{OUTPUT_DIR}/style.css")

    raw_js = generate_js(user_prompt, plan, context)
    js     = clean_js(raw_js)
    save(js, f"{OUTPUT_DIR}/script.js")

    # Quality check
    quality_check(html, css, js, plan)

    print(f"""
{'='*65}
  Done!  (8 API calls + {len(images)} images downloaded)
  index.html  →  open in browser
  style.css
  script.js
  images/     →  {len(images)} real images
  plan.json   →  full blueprint
{'='*65}
  open index.html
""")


if __name__ == "__main__":
    main()