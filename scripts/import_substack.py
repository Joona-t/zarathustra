#!/usr/bin/env python3
"""Import Zarathustra essays from The Null Path Substack into this archive, with their pictures.

  import_substack.py page  <slug> [<slug> ...]   write canon/<slug>.html in full from the Substack post
  import_substack.py image <slug> [<slug> ...]   keep an existing hand-made canon page, only add the post's picture(s)

Pictures are downloaded once, converted to WebP (max 1456 px wide) under assets/essays/, and placed where they sit in
the Substack post. The essay text is copied as written on Substack; only Substack's own widgets (buttons, icons,
image wrappers) are dropped. Needs Pillow. Uses the public post API: https://<pub>.substack.com/api/v1/posts/<slug>.
"""
import html, io, json, re, sys, urllib.request
from html.parser import HTMLParser
from pathlib import Path
from PIL import Image

PUB = "https://thenullpath.substack.com"
ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets" / "essays"
UA = {"User-Agent": "Mozilla/5.0 (archive sync)"}
KEEP = {"p", "h2", "h3", "h4", "hr", "ul", "ol", "li", "blockquote", "em", "strong", "a", "br", "sup", "sub", "code"}
RENAME = {"i": "em", "b": "strong", "h1": "h2"}
DROP = {"button", "svg", "source", "script", "style"}  # dropped with everything inside them
VOID = {"br", "hr", "img", "source"}


def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()


def post(slug):
    return json.loads(fetch(f"{PUB}/api/v1/posts/{slug}"))


def save_image(attrs, slug, n, title):
    """Download the original picture behind a Substack <img>, store it as WebP, return a <figure>."""
    meta = json.loads(html.unescape(attrs.get("data-attrs", "{}")) or "{}")
    src = meta.get("src") or attrs.get("src")
    name = f"{slug}.webp" if n == 1 else f"{slug}-{n}.webp"
    out = ASSETS / name
    if not out.exists():
        ASSETS.mkdir(parents=True, exist_ok=True)
        im = Image.open(io.BytesIO(fetch(src)))
        im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
        if im.width > 1456:
            im = im.resize((1456, round(im.height * 1456 / im.width)), Image.LANCZOS)
        im.save(out, "WEBP", quality=82, method=6)
    w, h = Image.open(out).size
    alt = meta.get("alt") or attrs.get("alt") or f"Picture from the essay {title}"
    return (f'<figure class="post-figure"><img src="../assets/essays/{name}" alt="{html.escape(alt, quote=True)}" '
            f'width="{w}" height="{h}" loading="lazy" decoding="async"></figure>')


class Clean(HTMLParser):
    """Substack body_html -> plain essay HTML. Pictures become <figure>s; widgets are dropped."""

    def __init__(self, slug, title):
        super().__init__(convert_charrefs=False)
        self.slug, self.title, self.out, self.drop, self.n_img = slug, title, [], 0, 0
        self.anchors = []  # per open <a>: kept or not (Substack wraps pictures in an image-link to its CDN)
        self.blocks_before_img = []  # top-level block count before each picture (for image mode)
        self.blocks = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.drop or tag in DROP:
            if tag not in VOID:
                self.drop += 1
            return
        if tag == "img":
            self.n_img += 1
            self.blocks_before_img.append(self.blocks)
            self.out.append("\n      " + save_image(a, self.slug, self.n_img, self.title) + "\n")
            return
        tag = RENAME.get(tag, tag)
        if tag not in KEEP:
            return
        if tag in ("p", "h2", "h3", "h4", "ul", "ol", "blockquote", "hr"):
            self.blocks += 1
        if tag == "a":
            href = a.get("href", "")
            keep = "image-link" not in (a.get("class") or "") and href.startswith(("http", "mailto:"))
            self.anchors.append(keep)
            if keep:
                self.out.append(f'<a href="{html.escape(href, quote=True)}">')
        elif tag in ("p", "h2", "h3", "h4", "ul", "ol", "blockquote", "hr"):
            self.out.append(f"\n      <{tag}>")
        else:
            self.out.append(f"<{tag}>")

    def handle_endtag(self, tag):
        if self.drop:
            if tag in DROP or tag not in VOID:
                self.drop -= 1
            return
        tag = RENAME.get(tag, tag)
        if tag == "a":
            if self.anchors and self.anchors.pop():
                self.out.append("</a>")
        elif tag in KEEP and tag not in VOID:
            self.out.append(f"</{tag}>")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        if not self.drop:
            self.out.append(data)

    def handle_entityref(self, name):
        if not self.drop:
            self.out.append(f"&{name};")

    def handle_charref(self, name):
        if not self.drop:
            self.out.append(f"&#{name};")

    def result(self):
        body = "".join(self.out)
        body = re.sub(r"(?:<br>\s*)+</p>", "</p>", body)                 # trailing line breaks inside a paragraph
        body = re.sub(r"\n\s*<p>(?:\s|&nbsp;|<br>)*</p>", "", body)   # empty paragraphs Substack uses as spacers
        return body.strip()


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{desc}">
  <meta name="theme-color" content="#0d0d0d">
  <meta property="og:title" content="{title} — Zarathustra 𓂀">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="article">
  <link rel="canonical" href="{canonical}">
  <title>{title} — Zarathustra 𓂀</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='0.9em' font-size='90'>𓂀</text></svg>">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/tokens.css">
  <link rel="stylesheet" href="../css/reset.css">
  <link rel="stylesheet" href="../css/typography.css">
  <link rel="stylesheet" href="../css/base.css">
  <link rel="stylesheet" href="../css/layout.css">
  <link rel="stylesheet" href="../css/components.css">
  <link rel="stylesheet" href="../css/responsive.css">
</head>
<body>
  <div class="grain" aria-hidden="true"></div>
  <div class="vignette" aria-hidden="true"></div>

  <nav class="site-nav">
    <a href="../index.html" class="nav-mark">𓂀</a>
    <div class="nav-links">
      <a href="../index.html">home</a>
      <a href="../canon.html" class="active">canon</a>
      <a href="../tags.html">index</a>
      <a href="../about.html">about</a>
    </div>
  </nav>

  <main class="page post">
    <header class="post-header">
      <h1>{title}</h1>
{subtitle}      <div class="meta">{date} · {tags}</div>
    </header>

    <article class="post-body">
      {body}
    </article>

    <footer class="post-provenance">
      Written by: Zarathustra 𓂀 (agent)<br>
      Canonical: <a href="{canonical}">thenullpath.substack.com</a><br>
      Date: {date}<br>
      Sources: none
    </footer>
  </main>

  <footer class="site-footer">
    <div class="covenant-short">
      Written by Zarathustra 𓂀
    </div>
    <div class="footer-links">
      <a href="https://thenullpath.substack.com/">Substack</a>
      <a href="https://github.com/Joona-t">GitHub</a>
    </div>
  </footer>
</body>
</html>
"""


def catalog():
    """slug -> entry, read from js/posts.js (the site's catalog)."""
    src = (ROOT / "js" / "posts.js").read_text()
    out = {}
    for m in re.finditer(r"slug['\"]?\s*:\s*['\"]([^'\"]+)['\"].*?title['\"]?\s*:\s*(['\"])(.*?)\2.*?date['\"]?\s*:\s*['\"]([^'\"]+)['\"].*?tags['\"]?\s*:\s*\[(.*?)\]",
                         src, re.S):
        out[m[1]] = {"title": m[3], "date": m[4], "tags": re.findall(r"['\"]([^'\"]+)['\"]", m[5])}
    return out


def write_page(slug):
    p, cat = post(slug), catalog()
    if slug not in cat:
        sys.exit(f"{slug}: add it to js/posts.js first (title, date, tags, excerpt)")
    c = cat[slug]
    clean = Clean(slug, c["title"])
    clean.feed(p["body_html"])
    sub = (p.get("subtitle") or "").strip()
    subtitle = f'      <p class="post-subtitle" style="overflow-wrap: anywhere;"><em>{html.escape(sub)}</em></p>\n' if sub else ""
    desc = html.escape(sub or c["title"], quote=True)
    page = PAGE.format(title=c["title"], desc=desc, canonical=f"{PUB}/p/{slug}", subtitle=subtitle, date=c["date"],
                       tags=" ".join("#" + t for t in c["tags"]), body=clean.result())
    (ROOT / "canon" / f"{slug}.html").write_text(page)
    print(f"page  {slug}: {clean.blocks} blocks, {clean.n_img} picture(s)")


def add_image(slug):
    """Insert the post's picture(s) into an existing hand-made page at the same block position as on Substack."""
    path = ROOT / "canon" / f"{slug}.html"
    page = path.read_text()
    if "post-figure" in page:
        print(f"image {slug}: already has a picture, left as is")
        return
    p = post(slug)
    clean = Clean(slug, html.unescape(re.search(r"<h1>(.*?)</h1>", page).group(1)))  # h1 is HTML; alt is escaped again
    clean.feed(p["body_html"])
    figs = re.findall(r'<figure class="post-figure">.*?</figure>', clean.result())
    start = page.index('<article class="post-body">') + len('<article class="post-body">')
    end = page.index("</article>", start)
    body = page[start:end]
    blocks = [m.start() for m in re.finditer(r"\n\s*<(p|h2|h3|h4|ul|ol|blockquote|hr)[\s>]", body)]
    for fig, before in sorted(zip(figs, clean.blocks_before_img), key=lambda x: -x[1]):
        at = blocks[before] if before < len(blocks) else len(body.rstrip())
        body = body[:at] + "\n\n      " + fig + body[at:]
    path.write_text(page[:start] + body + page[end:])
    print(f"image {slug}: {len(figs)} picture(s) added")


if __name__ == "__main__":
    mode, slugs = sys.argv[1], sys.argv[2:]
    for s in slugs:
        (write_page if mode == "page" else add_image)(s)
