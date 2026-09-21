
# Anti-patterns: Visual audit

- NEVER approve UI based on desktop-only IDE preview.
- NEVER deliver **only** an issue list: fix errors and actionable warns in the same session.
- NEVER fix without `append_fix_log`: every change needs spec reference + files.
- NEVER skip re-capture + `finalize_visual_review --check` after fixes (finalize defaults to **done** 6 widths).
- NEVER call flagship/marketing done after only fast widths (375/768/1440) — use `--preset done`.
- NEVER ignore horizontal scroll at 375px or 430px width.
- NEVER ship green-on-green or illegible text: contrast audit + visual review.
- NEVER leave edge/link colors invisible on washed paper — edges must read on the plane.
- NEVER change IA or add components without design.md / heyeddi-product alignment.
- NEVER ship AI prose slop (em/en dashes, delve/leverage/tapestry, "Certainly!", "it is important to note", emoji theater); follow `context/PROSE_ANTI_SLOP.md` fully
