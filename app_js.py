import requests
import re
import sys
import json
import time

# ─── Configuration ───────────────────────────────────────────────────────────
SARVAM_API_KEY = "sk_9mq4tvEGOMzACqmABwkMG"
MODEL          = "sarvam-105b"
API_URL        = "https://api.sarvam.ai/v1/chat/completions"
MAX_TOKENS     = 4096
TEMPERATURE    = 0.10
MAX_RETRIES    = 2
# ─────────────────────────────────────────────────────────────────────────────


# ══════════════════════════════════════════════════════════════════
# NOTE: All literal { } inside JS_SYSTEM that are NOT format
# placeholders are doubled {{ }} so .format() won't choke on them.
# ══════════════════════════════════════════════════════════════════

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


def _remove_overlap(p1: str, p2: str) -> str:
    l1, l2 = p1.strip().splitlines(), p2.strip().splitlines()
    anchor  = l1[-12:] if len(l1) >= 12 else l1
    for i in range(len(anchor), 0, -1):
        if l2[:i] == anchor[-i:]:
            return "\n".join(l2[i:])
    return p2


def clean_js(raw: str) -> str:
    s = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE)
    s = re.sub(r"</?script[^>]*>", "", s, flags=re.IGNORECASE)
    s = re.sub(r"```[a-z]*\n?", "", s).replace("```", "").strip()
    m = re.search(r"(//|const |let |var |document|window|function )", s)
    return s[m.start():].strip() if m else s


def generate_js(user_prompt: str, plan: dict) -> str:
    print("\n[JS] JavaScript generate ho raha hai...\n")

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

Available DOM elements:
  Classes: {classes}
  IDs:     {ids}

Implement ALL these features:
{features}

Also add:
  - Active nav-link highlighting based on scroll position (Intersection Observer)
  - Close mobile nav when a nav-link is clicked
  - Any feature specific to "{user_prompt}"

Raw JavaScript only. Start with the nav toggle."""

    # ── Part 1 ──────────────────────────────────────────────────
    print("   [JS 1/2] Part 1 generating...")
    for attempt in range(MAX_RETRIES + 1):
        if attempt:
            print(f"   [JS] Retry {attempt}...")
        part1 = _api_call(JS_SYSTEM, user_msg_1, label="JS-1")
        if "querySelector" in part1 or "addEventListener" in part1:
            break
        print("   [JS] Validation failed — retrying part 1")

    lines      = part1.strip().splitlines()
    last_lines = "\n".join(lines[-45:]) if len(lines) > 45 else part1.strip()

    # ── Part 2 continuation message — NO .format(), use f-string directly ───
    # Key fix: we build the continuation prompt with an f-string so there
    # is no .format() call on a string containing {behavior:'smooth'}.
    user_msg_2 = (
        f'You were writing JS for: "{user_prompt}"\n\n'
        f"Features blueprint:\n{features}\n\n"
        f"You stopped here:\n```\n{last_lines}\n```\n\n"
        "Continue EXACTLY. Do NOT repeat already-written functions.\n"
        "Write remaining JS features. Use null-checks on all selectors.\n"
        "Raw JavaScript only."
    )

    print("   [JS 2/2] Part 2 generating (continuation)...")
    part2 = _api_call(JS_SYSTEM, user_msg_2, label="JS-2")
    part2 = _remove_overlap(part1, part2)

    return part1.strip() + "\n" + part2.strip()


def main():
    print("=" * 55)
    print("   JS-Only Generator — isolated test")
    print("=" * 55)

    # ── Load plan.json if it exists, else use a minimal fallback ──
    try:
        with open("plan.json", encoding="utf-8") as f:
            plan = json.load(f)
        print("   ✅  plan.json loaded")
        user_prompt = plan.get("title", "website")
    except FileNotFoundError:
        print("   ⚠️  plan.json not found — using minimal fallback plan")
        user_prompt = input("Website description: ").strip() or "restaurant landing page"
        plan = {
            "all_classes": [
                "navbar", "nav-container", "nav-logo", "nav-links",
                "nav-link", "nav-toggle", "nav-toggle-bar",
                "hero", "hero-content", "hero-title", "hero-subtitle", "hero-cta",
                "about", "about-container", "about-text", "about-image",
                "footer", "footer-copy", "reveal",
            ],
            "all_ids": ["nav", "hero", "about", "footer"],
            "js_features": [
                {
                    "name": "Mobile Nav Toggle",
                    "selector": ".nav-toggle",
                    "action": "toggle 'nav-open' on .nav-links",
                    "guard": "null-check before addEventListener",
                },
                {
                    "name": "Smooth Scroll",
                    "selector": ".nav-link",
                    "action": "preventDefault, scrollIntoView({behavior:'smooth'})",
                    "guard": "null-check",
                },
                {
                    "name": "Scroll Reveal",
                    "selector": ".reveal",
                    "action": "IntersectionObserver adds class 'visible' when 20% in view",
                    "guard": "check IntersectionObserver support",
                },
                {
                    "name": "Sticky Nav Shadow",
                    "selector": "window scroll",
                    "action": "add class 'scrolled' to nav when scrollY > 50",
                    "guard": "none needed",
                },
            ],
        }

    raw_js = generate_js(user_prompt, plan)
    js     = clean_js(raw_js)

    out = "script.js"
    with open(out, "w", encoding="utf-8") as f:
        f.write(js)
    kb = len(js.encode()) / 1024
    print(f"\n   ✅  {out}  ({kb:.1f} KB)")

    # Quick quality check
    checks = [
        ("querySelector"      in js, "querySelector used"),
        ("nav-open"           in js, "nav toggle present"),
        ("scrollIntoView"     in js, "smooth scroll present"),
        ("IntersectionObserver" in js, "scroll reveal present"),
        ("scrolled"           in js, "sticky nav present"),
    ]
    print("\n── Quality ─────────────────────────")
    for ok, label in checks:
        print(f"   {'✅' if ok else '❌'}  {label}")
    print("────────────────────────────────────")
    print("\nDone! Open script.js to inspect.")


if __name__ == "__main__":
    main()