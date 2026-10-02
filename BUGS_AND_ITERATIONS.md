# Bugs & Iterations

## 2026-06-26: Add canon entry — The Shepherds of the Machine

**Change:** Added the sixth canon post, "The Shepherds of the Machine" (Substack, 2026-06-25), mirroring the full essay text locally.
**Details:**
- New metadata entry in `js/posts.js` (slug `the-shepherds-of-the-machine`, tags `open-access` / `governance` / `agents`, canonical → thenullpath.substack.com).
- New full-content page `canon/the-shepherds-of-the-machine.html` (48 paragraphs) following the scripture-of-the-quiet-instrument template.
- Verified via local preview: renders as newest card on home, last entry in canon list, grouped under all three tags, no console errors.

**Fix (incidental):** `.claude/launch.json` `zarathustra` config pointed at a stale path (`Claude x LoveSpark/Zarathustra`, which no longer exists — the site moved under `Web Projects/`). Corrected `-d` to `Claude x LoveSpark/Web Projects/Zarathustra`.

<!-- Format:
## YYYY-MM-DD: Short Title

**Problem:** What went wrong or needed changing
**Root cause:** Why it happened
**Fix:** What was done to resolve it
-->

## 2026-07-08: P2-1/P2-4 — dim-text contrast failure + multi-MB hero PNG (BUG-P2A11Y-03)

**Problem:** (1) `--z-text-dim: #7a756f` on `--z-bg: #0d0d0d` measured 4.26:1 contrast (4.04:1 on `--z-bg-raised: #141414`) — below the WCAG AA 4.5:1 minimum for normal text — and the token is used at `--z-size-xs` (12px) across nav links, meta/footnote text, blockquotes, covenant line, page descriptions, and post provenance, i.e. never at large-text size where 3:1 would suffice. (2) `assets/zarathustra-my-love.png` was a 2.9 MB hero image (1536×1024 PNG) referenced on the home page.
**Root cause:** (1) The token was picked for aesthetic warmth without a contrast check against the near-black background. (2) The hero image was exported as PNG straight from the source without a compressed web-delivery pass.
**Fix:** (1) Raised `--z-text-dim` to `#857f79`, giving 4.91:1 on `--z-bg` and 4.66:1 on `--z-bg-raised` (verified via the standard WCAG relative-luminance formula in Python — both comfortably clear 4.5:1 with margin). (2) Converted the PNG to WebP at q=85 (`cwebp -q 85`) — 2.9 MB → 270 KB, visually lossless — swapped the `<img src>` in `index.html`, and removed the old PNG (`git rm`). No other references to the PNG existed; `fragments-of-the-self.jpg` (468 KB) was already under the 500 KB target and left as-is.
**Files:** css/tokens.css, index.html, assets/zarathustra-my-love.png (removed), assets/zarathustra-my-love.webp (added)
**Commit:** see git log (fleet-p2 batch, branch `add-shepherds-of-the-machine`)


## 2026-10-02 — Full latest essay in the archive

Problem: The latest Substack essay was absent from Zarathustra’s local reading archive. Cause: Articles and metadata are curated manually. Fix: Added complete static reading page with original subtitle, signature, source link and attribution, plus metadata for home, canon and topic index. Verified normalized source text and page links before publishing. Lesson: Both article and metadata must ship together; Substack availability must not gate reading.

Publishing verification caught a cached post catalog in Chrome: version the catalog URL on home, canon and topics so visitors fetch the new essay list immediately.
