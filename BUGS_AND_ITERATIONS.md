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
