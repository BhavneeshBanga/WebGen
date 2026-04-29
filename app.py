"""
WebGen v3 — Advanced Website Builder
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Architecture:
  Phase 0  — Plan (JSON blueprint)
  Phase 0b — Validate plan
  Phase 1  — Image placeholders (picsum.photos, FREE, no API key)
  Phase 2  — HTML  (2 calls: generate + continue)
  Phase 3  — CSS   (2 calls: generate + continue)
  Phase 3b — CSS post-process: deduplicate selectors
  Phase 4  — JS    (2 calls: generate + continue)
  Phase 4b — JS  post-process: fix duplicate consts, broken strings
  Phase 5  — Quality check + report

Total: 8 API calls, 0 external image APIs.
"""

import requests
import re
import sys
import json
import time
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────
SARVAM_API_KEY = "sk_9mqGOMzACqmABwkMG"
MODEL          = "sarvam-105b"
API_URL        = "https://api.sarvam.ai/v1/chat/completions"
OUTPUT_DIR     = "grocrie"
MAX_TOKENS     = 4096
TEMPERATURE    = 0.10
MAX_RETRIES    = 2
# ─────────────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — Image placeholders (picsum.photos, completely free)
# ═══════════════════════════════════════════════════════════════════════════════

# Curated picsum seeds that look relevant for common website types
_SEED_MAP = {
    "hero":     ("1920", "1080"),
    "about":    ("800",  "600"),
    "product":  ("400",  "400"),
    "gallery":  ("600",  "400"),
    "team":     ("400",  "500"),
    "banner":   ("1200", "400"),
    "delivery": ("800",  "500"),
    "special":  ("600",  "400"),
    "blog":     ("800",  "500"),
    "service":  ("600",  "400"),
}

def generate_placeholders(image_queries: list[dict]) -> dict[str, str]:
    """
    Returns {"hero_bg": "https://picsum.photos/...", ...}
    Uses picsum.photos with semantic seeds so images are consistent
    across reloads but vary per key.
    """
    result = {}
    print(f"\n[IMAGES] Picsum placeholders generating for {len(image_queries)} images...\n")
    for q in image_queries:
        # Safely handle missing or malformed entries
        if not isinstance(q, dict):
            continue
        key = q.get("key") or q.get("id") or q.get("name")
        if not key:
            # Try first string value in the dict
            key = next((v for v in q.values() if isinstance(v, str) and v), None)
        if not key:
            continue
        # Sanitize key for use as picsum seed (no spaces/special chars)
        key = re.sub(r"[^a-zA-Z0-9_-]", "_", str(key))
        # Pick dimensions based on key name
        w, h = "800", "500"
        for part, dims in _SEED_MAP.items():
            if part in key.lower():
                w, h = dims
                break
        url = f"https://picsum.photos/seed/{key}/{w}/{h}"
        result[key] = url
        print(f"   ✅  {key}: {url}")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 0 — PLANNING
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
      "classes": ["navbar","nav-container","nav-logo","nav-links","nav-link","nav-toggle","nav-toggle-bar"],
      "elements": ["logo text","5 nav links","hamburger icon"],
      "needs_image": false,
      "image_query": ""
    }
  ],
  "image_queries": [
    {"key": "hero_bg",   "query": "hero background", "used_in": "hero section"},
    {"key": "about_img", "query": "about image",     "used_in": "about section"}
  ],
  "all_classes": ["every","class","flat","deduplicated"],
  "all_ids":     ["nav","hero","about"],
  "js_features": [
    {"name":"Mobile Nav Toggle","selector":".nav-toggle","action":"toggle nav-open on .nav-links","guard":"null-check"},
    {"name":"Smooth Scroll","selector":".nav-link","action":"scrollIntoView smooth","guard":"null-check"},
    {"name":"Scroll Reveal","selector":".reveal","action":"IntersectionObserver adds visible","guard":"feature detect"},
    {"name":"Sticky Nav","selector":"window","action":"add scrolled to #nav on scrollY>50","guard":"none"}
  ],
  "google_fonts_url": "https://fonts.googleapis.com/css2?family=..."
}

RULES:
- all_classes: flat deduplicated list of EVERY class from ALL sections
- all_ids: every section id
- js_features: minimum 4, always include nav toggle + smooth scroll + scroll reveal + sticky nav
- font names must be valid Google Fonts"""


def create_plan(user_prompt: str) -> dict:
    print("\n[PHASE 0] Planning...\n")
    user_msg = f"""Website request: "{user_prompt}"

Think step by step:
1. What sections does this page need?
2. What classes does each section need?
3. What images are needed? (we use placeholders, so just name them well)
4. What color palette fits "{user_prompt}"?
5. What JS interactions would a user expect?

Output the complete JSON blueprint. No text before or after."""

    print("   [Call 1/8] Generating plan...")
    raw = _api_call(PLAN_SYSTEM, user_msg, label="Plan")
    return _parse_json(raw, user_prompt, "plan")


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 0b — PLAN VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

VALIDATE_SYSTEM = """You are a code reviewer fixing inconsistencies in a web blueprint.
Return ONLY valid JSON — the corrected plan. No markdown. No text before/after."""


def validate_plan(plan: dict, user_prompt: str) -> dict:
    print("   [Call 2/8] Validating plan...")
    user_msg = f"""Request: "{user_prompt}"
Plan:
{json.dumps(plan, indent=2)}

Fix if needed:
1. all_classes missing classes from sections[].classes → add all
2. all_ids missing section ids → add all
3. js_features selectors not in all_classes/all_ids → fix
4. google_fonts_url missing a font → fix URL
5. Missing obvious sections for this type of website → add them

Return corrected JSON."""

    raw = _api_call(VALIDATE_SYSTEM, user_msg, label="Validate")
    result = _parse_json(raw, user_prompt, "plan")
    print(f"   ✅ Plan: {len(result.get('sections',[]))} sections | "
          f"{len(result.get('all_classes',[]))} classes | "
          f"{len(result.get('image_queries',[]))} images")
    result = _normalize_image_queries(result)
    return result


def _normalize_image_queries(plan: dict) -> dict:
    """Ensure every image_query entry has a key and query field."""
    import re as _re
    fixed = []
    for i, q in enumerate(plan.get("image_queries", [])):
        if not isinstance(q, dict):
            continue
        if "key" not in q:
            key = (q.get("id") or q.get("name") or q.get("image_key") or f"image_{i}")
            q["key"] = _re.sub(r"[^a-zA-Z0-9_-]", "_", str(key))
        if "query" not in q:
            q["query"] = q.get("search", q.get("description", q.get("key", f"image {i}")))
        fixed.append(q)
    plan["image_queries"] = fixed
    return plan


# ═══════════════════════════════════════════════════════════════════════════════
# Context builder
# ═══════════════════════════════════════════════════════════════════════════════

def plan_to_context(plan: dict, images: dict) -> str:
    t = plan.get("theme", {})
    sec_lines = []
    for s in plan.get("sections", []):
        classes = " | ".join(f".{c}" for c in s.get("classes", []))
        sec_lines.append(f"  <{s.get('tag','div')} id=\"{s.get('id','')}\">"
                         f"  [{s.get('name','')}]")
        sec_lines.append(f"    classes: {classes}")
        sec_lines.append(f"    elements: {', '.join(s.get('elements', []))}")

    img_lines = [f"  {k}: \"{v}\"" for k, v in images.items() if k and v]

    js_lines = []
    for f in plan.get("js_features", []):
        js_lines.append(f"  • {f.get('name','')} | selector: {f.get('selector','')} | "
                        f"action: {f.get('action','')} | guard: {f.get('guard','')}")

    return f"""╔══════════════════════════════════════════════════════════╗
║                  BLUEPRINT — FOLLOW EXACTLY              ║
╚══════════════════════════════════════════════════════════╝
TITLE: {plan.get('title','')}   MOOD: {t.get('mood','')}

COLORS (:root vars):
  --primary:{t.get('primary','#333')} --secondary:{t.get('secondary','#666')}
  --accent:{t.get('accent','#09f')} --bg:{t.get('background','#fff')}
  --surface:{t.get('surface','#f5f5f5')} --text:{t.get('text','#222')}
  --text-muted:{t.get('text_muted','#888')} --radius:{t.get('border_radius','8px')}

FONTS: heading={t.get('font_heading','Poppins')} body={t.get('font_body','Open Sans')}
FONTS URL: {plan.get('google_fonts_url','')}

SECTIONS (build ALL in order):
{chr(10).join(sec_lines)}

ALL CLASSES (style/use every one):
  {', '.join('.'+c for c in plan.get('all_classes',[]))}

ALL IDs: {', '.join('#'+i for i in plan.get('all_ids',[]))}

IMAGE PATHS (use exact as src/background-image):
{chr(10).join(img_lines) if img_lines else '  (none)'}

JS FEATURES (implement ALL):
{chr(10).join(js_lines)}
╚══════════════════════════════════════════════════════════╝"""


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — HTML
# ═══════════════════════════════════════════════════════════════════════════════

HTML_SYSTEM = """You are a senior HTML5 developer. Write semantic, complete, production-ready HTML.

RULES:
[R1] Return ONLY raw HTML. No markdown, no explanation, no <think> tags.
[R2] Start: <!DOCTYPE html>   End: </html>
[R3] NO inline <style> or <script>. Link external files only.
[R4] <head> must have: <link rel="stylesheet" href="style.css"> + Google Fonts link
[R5] Before </body>: <script src="script.js" defer></script>
[R6] Use ONLY classes and IDs from the blueprint. Do NOT invent new ones.
[R7] Build EVERY section in order. Add <!-- ═══ SECTION ═══ --> above each.
[R8] Every section except nav gets class="reveal"
[R9] Use picsum image URLs as-is in src attributes."""


def generate_html(user_prompt: str, plan: dict, context: str) -> str:
    print("\n[PHASE 2] HTML generating...\n")
    sections_list = "\n".join(
        f"  {i+1}. #{s.get('id','')} — {s.get('name','')} | {', '.join(s.get('elements',[]))}"
        for i, s in enumerate(plan.get("sections", []))
    )
    msg1 = f'Build: "{user_prompt}"\n\n{context}\n\nSections to build:\n{sections_list}\n\nStart with <!DOCTYPE html> now:'
    msg2_tpl = (
        f'Continuing "{user_prompt}" HTML.\nBlueprint ref:\n{context[:1200]}\n\n'
        'You stopped here:\n```\n{last_lines}\n```\n\n'
        'Continue from where you stopped. Do NOT restart. End with </body></html>. Raw HTML only.'
    )
    return _double_call(HTML_SYSTEM, msg1, msg2_tpl, "HTML",
                        validator=lambda t: "<!doctype" in t.lower())


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — CSS
# ═══════════════════════════════════════════════════════════════════════════════

CSS_SYSTEM = """You are a senior CSS designer. Write modern, mobile-first CSS.

RULES:
[R1] Return ONLY raw CSS. No markdown, no <style> tags, no explanation.
[R2] File order: @import → :root → * reset → sections → @media mobile
[R3] Style EVERY class in the blueprint. Skip none.
[R4] :root must have: --primary --secondary --accent --bg --surface --text --text-muted --radius --shadow --transition
[R5] Every interactive element needs :hover and :focus.
[R6] .reveal { opacity:0; transform:translateY(30px); transition:0.6s ease }
     .reveal.visible { opacity:1; transform:none }
[R7] nav.scrolled { box-shadow: var(--shadow) }
[R8] Mobile nav: .nav-links { display:none } .nav-links.nav-open { display:flex; flex-direction:column }
[R9] Desktop: @media(min-width:768px) { .nav-links{display:flex;flex-direction:row} .nav-toggle{display:none} }
[R10] Stop only at a complete } never mid-rule."""


def generate_css(user_prompt: str, plan: dict, context: str) -> str:
    print("\n[PHASE 3] CSS generating...\n")
    t = plan.get("theme", {})
    all_classes = " | ".join(f".{c}" for c in plan.get("all_classes", []))
    msg1 = f"""Write complete CSS for: "{user_prompt}"

{context}

:root block MUST use these exact values:
:root {{
  --primary:    {t.get('primary',   '#333')};
  --secondary:  {t.get('secondary', '#666')};
  --accent:     {t.get('accent',    '#09f')};
  --bg:         {t.get('background','#fff')};
  --surface:    {t.get('surface',   '#f5f5f5')};
  --text:       {t.get('text',      '#222')};
  --text-muted: {t.get('text_muted','#888')};
  --radius:     {t.get('border_radius','8px')};
  --shadow:     0 4px 20px rgba(0,0,0,0.08);
  --transition: all 0.3s ease;
}}

Style ALL: {all_classes}

Start with @import:"""

    msg2_tpl = (
        f'Continuing CSS for "{user_prompt}".\n'
        f'Classes needed: {all_classes}\n\n'
        'You stopped here:\n```\n{last_lines}\n```\n\n'
        'Continue. Do NOT repeat already-written selectors. '
        'End with @media mobile block if not done. Raw CSS only.'
    )
    raw = _double_call(CSS_SYSTEM, msg1, msg2_tpl, "CSS",
                       validator=lambda t: ":root" in t)
    return _postprocess_css(raw)


def _postprocess_css(css: str) -> str:
    """Remove duplicate CSS selectors — keep the LAST occurrence (more specific/complete)."""
    print("   [CSS Post] Deduplicating selectors...")
    # Split into blocks by finding selector { ... }
    # Strategy: parse rule blocks, keep last seen for each selector
    seen: dict[str, str] = {}
    order: list[str] = []

    # Split on top-level blocks — simple approach: split by \n} and re-join
    # More robust: track by selector string
    lines = css.splitlines()
    current_selector = None
    current_block: list[str] = []
    depth = 0
    result_blocks: list[tuple[str, str]] = []  # (selector, block)
    imports_and_root: list[str] = []
    in_preamble = True

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Collect @import and :root separately
        if in_preamble and (stripped.startswith("@import") or
                            stripped.startswith(":root") or
                            stripped.startswith("*") or
                            stripped == ""):
            imports_and_root.append(line)
            if "{" in line:
                # consume until closing }
                depth = line.count("{") - line.count("}")
                while depth > 0 and i + 1 < len(lines):
                    i += 1
                    imports_and_root.append(lines[i])
                    depth += lines[i].count("{") - lines[i].count("}")
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

    # Deduplicate: keep last occurrence per selector
    seen_order: list[str] = []
    seen_map: dict[str, str] = {}
    for sel, block in result_blocks:
        if sel not in seen_map:
            seen_order.append(sel)
        seen_map[sel] = block  # always overwrite = keep last

    deduped = "\n\n".join(seen_map[sel] for sel in seen_order)
    final = "\n".join(imports_and_root) + "\n\n" + deduped

    original_count = len(result_blocks)
    final_count    = len(seen_order)
    removed        = original_count - final_count
    if removed:
        print(f"   [CSS Post] Removed {removed} duplicate selector blocks ✅")
    else:
        print("   [CSS Post] No duplicates found ✅")
    return final


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — JS
# ═══════════════════════════════════════════════════════════════════════════════

JS_SYSTEM = """You are a senior JavaScript developer. Write clean, defensive, modern vanilla JS.

RULES:
[R1] Return ONLY raw JavaScript. No <script> tags, no markdown, no explanation.
[R2] Script runs after DOM load (defer). No DOMContentLoaded wrapper needed.
[R3] NULL-CHECK every querySelector: const el = document.querySelector('.x'); if(el) { ... }
[R4] Implement EVERY feature from the blueprint. Skip none.
[R5] Add // ════ FEATURE NAME ════ above each feature.
[R6] Scroll reveal: IntersectionObserver threshold 0.15, add class 'visible'.
[R7] Mobile nav: toggle 'nav-open' on .nav-links when .nav-toggle clicked.
[R8] Smooth scroll: .nav-link clicks → scrollIntoView({behavior:'smooth'}).
[R9] Sticky nav: window scroll → toggle 'scrolled' on #nav when scrollY > 50.
[R10] NEVER redeclare the same const/let/var twice. Use unique variable names."""


def generate_js(user_prompt: str, plan: dict, context: str) -> str:
    print("\n[PHASE 4] JS generating...\n")
    features = "\n".join(
        f"  {i+1}. {f.get('name','')} | selector:{f.get('selector','')} | "
        f"action:{f.get('action','')} | guard:{f.get('guard','')}"
        for i, f in enumerate(plan.get("js_features", []))
    )
    classes = ", ".join(f".{c}" for c in plan.get("all_classes", []))
    ids     = ", ".join(f"#{x}" for x in plan.get("all_ids", []))

    msg1 = f"""Write complete JavaScript for: "{user_prompt}"

{context}

DOM elements available:
  Classes: {classes}
  IDs: {ids}

Implement ALL features:
{features}

Extra features to add:
  - Close mobile nav when nav-link clicked
  - Active nav-link highlighting via IntersectionObserver on sections
  - Any page-specific feature (e.g. product filter, counter, accordion, form validation)

IMPORTANT: Never declare the same variable name twice.
Raw JavaScript only. Start now:"""

    # Continuation as plain f-string — avoids KeyError from {behavior:'smooth'} in .format()
    return _double_call_js(JS_SYSTEM, msg1, user_prompt, features, "JS",
                           validator=lambda t: "querySelector" in t)


def _double_call_js(system, msg1, user_prompt, features, label, validator=None):
    for attempt in range(MAX_RETRIES + 1):
        if attempt:
            print(f"   [{label}] Retry {attempt}...")
        print(f"   [{label} 1/2] Part 1...")
        part1 = _api_call(system, msg1, label=f"{label}-1")
        if not validator or validator(part1):
            break
        print(f"   [{label}] Validation failed, retrying...")

    lines = part1.strip().splitlines()
    last_lines = "\n".join(lines[-45:]) if len(lines) > 45 else part1.strip()

    msg2 = (
        f'Continuing JS for "{user_prompt}".\n\n'
        f'Features still needed:\n{features}\n\n'
        f'You stopped here:\n```\n{last_lines}\n```\n\n'
        'Continue EXACTLY. Do NOT repeat already-declared variables or functions. '
        'Use unique names. Null-check all selectors. Raw JS only.'
    )
    print(f"   [{label} 2/2] Part 2...")
    part2 = _api_call(system, msg2, label=f"{label}-2")
    part2 = _remove_overlap(part1, part2)

    raw = part1.strip() + "\n" + part2.strip()
    return _postprocess_js(raw)


def _postprocess_js(js: str) -> str:
    """
    Fix common JS generation bugs:
    1. Remove duplicate const/let/var declarations (keep first)
    2. Remove incomplete string literals at end of file
    3. Remove truncated lines (lines ending mid-string or mid-expression)
    """
    print("   [JS Post] Fixing JS...")
    lines = js.splitlines()

    # ── Fix 1: Remove duplicate top-level const/let/var declarations ─────────
    declared: set[str] = set()
    clean_lines: list[str] = []
    skip_block = False
    brace_depth = 0

    for line in lines:
        stripped = line.strip()

        # Track brace depth to know when a block ends
        brace_depth += line.count("{") - line.count("}")

        # Detect top-level declarations (depth 0 before this line opens a block)
        m = re.match(r'^(const|let|var)\s+(\w+)', stripped)
        if m and brace_depth <= line.count("{"):
            varname = m.group(2)
            if varname in declared:
                # Skip this declaration + its block
                skip_block = True
                brace_depth_at_skip = brace_depth - line.count("{") + line.count("}")
                continue
            else:
                declared.add(varname)

        if skip_block:
            if brace_depth <= 0:
                skip_block = False
                brace_depth = 0
            continue

        clean_lines.append(line)

    js = "\n".join(clean_lines)

    # ── Fix 2: Remove truncated last line (incomplete string/expression) ──────
    js_lines = js.rstrip().splitlines()
    while js_lines:
        last = js_lines[-1].strip()
        # A complete line ends with ; } ) , or is a comment or blank
        if last and not re.search(r'[;}\),]$', last) and not last.startswith("//"):
            js_lines.pop()
        else:
            break
    js = "\n".join(js_lines)

    # ── Fix 3: Fix incomplete hex color strings like '#E  ────────────────────
    js = re.sub(r"'#[0-9A-Fa-f]{0,5}\s*$", "'#E74C3C'", js, flags=re.MULTILINE)
    js = re.sub(r'"#[0-9A-Fa-f]{0,5}\s*$', '"#E74C3C"', js, flags=re.MULTILINE)

    print("   [JS Post] Done ✅")
    return js


# ═══════════════════════════════════════════════════════════════════════════════
# Generic double-call (HTML + CSS only — NOT for JS)
# ═══════════════════════════════════════════════════════════════════════════════

def _double_call(system, msg1, msg2_tpl, label, validator=None):
    for attempt in range(MAX_RETRIES + 1):
        if attempt:
            print(f"   [{label}] Retry {attempt}...")
        print(f"   [{label} 1/2] Part 1...")
        part1 = _api_call(system, msg1, label=f"{label}-1")
        if not validator or validator(part1):
            break

    lines = part1.strip().splitlines()
    last_lines = "\n".join(lines[-45:]) if len(lines) > 45 else part1.strip()

    print(f"   [{label} 2/2] Part 2...")
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

def _api_call(system: str, user: str, label: str = "") -> str:
    payload = {
        "model": MODEL, "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS,
        "messages": [{"role": "system", "content": system},
                     {"role": "user",   "content": user}],
    }
    headers = {"Authorization": f"Bearer {SARVAM_API_KEY}",
               "Content-Type": "application/json"}

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

        return r.json()["choices"][0]["message"]["content"]

    sys.exit("API gave up.")


# ═══════════════════════════════════════════════════════════════════════════════
# JSON parser
# ═══════════════════════════════════════════════════════════════════════════════

def _parse_json(raw: str, user_prompt: str, kind: str) -> dict:
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```[a-z]*\n?", "", raw).replace("```", "").strip()
    m = re.search(r"\{[\s\S]*\}", raw)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception as e:
            print(f"   ⚠️  JSON parse error: {e}")
    print("   ⚠️  Using fallback plan")
    return _fallback_plan(user_prompt)


# ═══════════════════════════════════════════════════════════════════════════════
# Quality Check
# ═══════════════════════════════════════════════════════════════════════════════

def quality_check(html: str, css: str, js: str, plan: dict) -> dict:
    print("\n── Quality Check ────────────────────────────────────────────")
    issues = 0
    checks = [
        ("<!DOCTYPE html>" in html.upper(),        "HTML has DOCTYPE"),
        ("</html>" in html.lower(),                "HTML closed"),
        ("style.css" in html,                      "HTML → style.css"),
        ("script.js" in html,                      "HTML → script.js"),
        (":root" in css,                           "CSS :root vars"),
        ("@media" in css,                          "CSS responsive"),
        (".reveal" in css,                         "CSS scroll reveal"),
        ("nav-open" in js,                         "JS nav toggle"),
        ("scrollIntoView" in js,                   "JS smooth scroll"),
        ("IntersectionObserver" in js,             "JS scroll reveal"),
        ("scrolled" in js,                         "JS sticky nav"),
    ]
    for ok, label in checks:
        print(f"   {'✅' if ok else '❌'}  {label}")
        if not ok: issues += 1

    missing_html = [c for c in plan.get("all_classes", []) if c not in html]
    missing_css  = [c for c in plan.get("all_classes", []) if f".{c}" not in css]
    if missing_html:
        print(f"   ⚠️  HTML missing {len(missing_html)} classes: {', '.join(missing_html[:5])}")
        issues += 1
    if missing_css:
        print(f"   ⚠️  CSS unstyled {len(missing_css)} classes: {', '.join(missing_css[:5])}")
        issues += 1

    # JS duplicate check
    const_names = re.findall(r'\bconst\s+(\w+)', js)
    dupes = [n for n in set(const_names) if const_names.count(n) > 1]
    if dupes:
        print(f"   ⚠️  JS still has duplicate consts: {', '.join(dupes[:5])}")
        issues += 1
    else:
        print("   ✅  JS no duplicate declarations")

    score = max(0, 100 - issues * 10)
    status = "✅ Excellent!" if issues == 0 else f"⚠️  {issues} issue(s)"
    print(f"\n   Score: {score}/100  {status}")
    print("─────────────────────────────────────────────────────────────")
    return {"issues": issues, "score": score}


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
        "theme": {
            "mood": "modern", "primary": "#2d6a4f", "secondary": "#40916c",
            "accent": "#95d5b2", "background": "#f8f9fa", "surface": "#ffffff",
            "text": "#212529", "text_muted": "#6c757d", "border_radius": "8px",
            "font_heading": "Poppins", "font_body": "Open Sans"
        },
        "sections": [
            {"id":"nav","tag":"nav","name":"Navigation","needs_image":False,"image_query":"",
             "elements":["logo","links","toggle"],
             "classes":["navbar","nav-container","nav-logo","nav-links","nav-link","nav-toggle","nav-toggle-bar"]},
            {"id":"hero","tag":"section","name":"Hero","needs_image":True,"image_query":user_prompt+" hero",
             "elements":["heading","subtitle","CTA"],
             "classes":["hero","hero-bg","hero-content","hero-title","hero-subtitle","hero-cta","cta-button"]},
            {"id":"about","tag":"section","name":"About","needs_image":True,"image_query":user_prompt+" interior",
             "elements":["text","image"],
             "classes":["about","about-content","about-text","about-image","image-container"]},
            {"id":"footer","tag":"footer","name":"Footer","needs_image":False,"image_query":"",
             "elements":["copyright","social links"],
             "classes":["footer","footer-content","footer-text","social-links","social-link"]},
        ],
        "image_queries":[
            {"key":"hero_bg","query":user_prompt+" hero","used_in":"hero background"},
            {"key":"about_img","query":user_prompt+" interior","used_in":"about section"},
        ],
        "all_classes":[
            "navbar","nav-container","nav-logo","nav-links","nav-link","nav-toggle","nav-toggle-bar",
            "hero","hero-bg","hero-content","hero-title","hero-subtitle","hero-cta","cta-button",
            "about","about-content","about-text","about-image","image-container",
            "footer","footer-content","footer-text","social-links","social-link",
        ],
        "all_ids":["nav","hero","about","footer"],
        "js_features":[
            {"name":"Mobile Nav Toggle","selector":".nav-toggle","action":"toggle nav-open on .nav-links","guard":"null-check"},
            {"name":"Smooth Scroll","selector":".nav-link","action":"scrollIntoView smooth","guard":"null-check"},
            {"name":"Scroll Reveal","selector":".reveal","action":"IntersectionObserver adds visible","guard":"feature detect"},
            {"name":"Sticky Nav","selector":"window","action":"toggle scrolled on #nav when scrollY>50","guard":"none"},
        ],
        "google_fonts_url":"https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("   WebGen v3 — Advanced Website Builder")
    print("   Phases: Plan → Validate → Images → HTML → CSS → JS")
    print("   Post-processing: CSS dedup + JS auto-fix")
    print("   Images: Free picsum.photos placeholders (no API key)")
    print("=" * 65)

    user_prompt = input("\nKya banana hai?\n>>> ").strip()
    if not user_prompt:
        sys.exit("Kuch toh batao!")

    # ── Phase 0: Plan ─────────────────────────────────────────────
    plan = create_plan(user_prompt)
    plan = validate_plan(plan, user_prompt)
    save(json.dumps(plan, indent=2), f"{OUTPUT_DIR}/plan.json")

    # ── Phase 1: Images (free placeholders) ───────────────────────
    images = generate_placeholders(plan.get("image_queries", []))

    # ── Build context ─────────────────────────────────────────────
    context = plan_to_context(plan, images)

    # ── Phase 2: HTML ─────────────────────────────────────────────
    html = clean_html(generate_html(user_prompt, plan, context))
    save(html, f"{OUTPUT_DIR}/index.html")

    # ── Phase 3: CSS + dedup ──────────────────────────────────────
    css = clean_css(generate_css(user_prompt, plan, context))
    save(css, f"{OUTPUT_DIR}/style.css")

    # ── Phase 4: JS + auto-fix ────────────────────────────────────
    js = clean_js(generate_js(user_prompt, plan, context))
    save(js, f"{OUTPUT_DIR}/script.js")

    # ── Phase 5: Quality check ────────────────────────────────────
    report = quality_check(html, css, js, plan)

    print(f"""
{'='*65}
  WebGen v3 — Complete!
  Files:      index.html  style.css  script.js  plan.json
  Images:     {len(images)} picsum placeholders (swap with real photos later)
  Quality:    {report['score']}/100  ({report['issues']} issues)
  Next step:  Open index.html in browser
{'='*65}
""")


if __name__ == "__main__":
    main()