#!/usr/bin/env python3
"""Pre-publish check for the Zarathustra archive. Serves this checkout itself, opens every page a visitor can reach at
desktop, tablet and phone width, and fails (exit 1) when:
  1. an essay page leaves the site: the browser ends up on another URL (2026-11-13: "A Country Without Permission"
     was a meta-refresh + location.replace stub that sent readers to Substack instead of the essay);
  2. an essay listed in js/posts.js has no page, or its page has no <article class="post-body"> with text;
  3. a picture fails to load, or is wider than the text column;
  4. the page scrolls sideways;
  5. the page logs an error.
Also saves screenshots of every essay's picture (desktop and phone) to .check/ for a human look.

Usage: python3 scripts/check_site.py [--no-shots]      Needs Playwright.
"""
import functools, http.server, json, subprocess, sys, threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHOTS = "--no-shots" not in sys.argv
WIDTHS = {"desktop": (1280, 900), "tablet": (768, 1024), "phone": (390, 844)}


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
threading.Thread(target=httpd.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{httpd.server_address[1]}"

slugs = json.loads(subprocess.run(
    ["node", "-e", "global.window={};require(process.argv[1]);console.log(JSON.stringify(window.POSTS.map(p=>p.slug)))",
     str(ROOT / "js" / "posts.js")], capture_output=True, text=True, check=True).stdout)
pages = ["index.html", "canon.html", "tags.html", "about.html"] + [f"canon/{s}.html" for s in slugs]

PROBE = """() => {
  const out = [], doc = document.documentElement;
  if (doc.scrollWidth > doc.clientWidth + 1) out.push(`scrolls sideways (${doc.scrollWidth} > ${doc.clientWidth})`);
  const body = document.querySelector('article.post-body');
  for (const img of document.images) {
    if (!img.complete || img.naturalWidth === 0) out.push(`picture did not load: ${img.getAttribute('src')}`);
    if (body && body.contains(img)) {
      const r = img.getBoundingClientRect(), b = body.getBoundingClientRect();
      if (r.width > b.width + 1) out.push(`picture wider than the text column: ${img.getAttribute('src')}`);
    }
  }
  return {out, essay: body ? body.innerText.trim().length : -1};
}"""

problems, shots = [], []
(ROOT / ".check").mkdir(exist_ok=True)
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    for name, (w, h) in WIDTHS.items():
        ctx = browser.new_context(viewport={"width": w, "height": h})
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        for p in pages:
            errors.clear()
            url = f"{BASE}/{p}"
            resp = page.goto(url, wait_until="load")
            for img in page.locator("img").all():  # lazy pictures: bring each into view so it loads
                img.scroll_into_view_if_needed()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(300)
            where = f"{name} {p}"
            if page.url != url:
                problems.append(f"{where}: left the page for {page.url}")
                continue
            if resp is None or resp.status != 200:
                problems.append(f"{where}: HTTP {resp.status if resp else 'none'}")
                continue
            r = page.evaluate(PROBE)
            problems += [f"{where}: {x}" for x in r["out"]]
            if p.startswith("canon/") and r["essay"] < 200:
                problems.append(f"{where}: no essay text on the page ({r['essay']} characters)")
            problems += [f"{where}: error: {e}" for e in errors if "fonts.g" not in e]
            if SHOTS and name in ("desktop", "phone") and p.startswith("canon/"):
                fig = page.locator("figure.post-figure").first
                if fig.count():
                    fig.scroll_into_view_if_needed()
                    out = ROOT / ".check" / f"{Path(p).stem}-{name}.png"
                    page.screenshot(path=str(out))
                    shots.append(out)
        ctx.close()
    browser.close()

print(f"checked {len(pages)} pages x {len(WIDTHS)} widths; {len(shots)} screenshots in .check/")
for x in problems:
    print("PROBLEM", x)
print("CHECK OK" if not problems else f"CHECK FAILED: {len(problems)} problem(s)")
sys.exit(1 if problems else 0)
