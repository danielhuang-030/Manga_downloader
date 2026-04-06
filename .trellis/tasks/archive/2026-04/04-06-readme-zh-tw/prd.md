# Update README: add Traditional Chinese version

## Goal

Provide a Traditional Chinese (zh-TW) README alongside the existing English `README.md`, and update `README.md` so readers can switch languages without hunting for files.

## Requirements

- Add a new file `README.zh-TW.md` containing a Traditional Chinese translation of the current repository `README.md` content (structure and technical blocks preserved: code fences, URLs, image markdown, lists).
- Update `README.md` with a short **language / 語言** line near the top linking to `README.zh-TW.md`; mirror the same navigation on `README.zh-TW.md` pointing back to English.
- Do not remove or replace the English default README; GitHub continues to show `README.md` on the repo root.

## Acceptance Criteria

- [x] `README.zh-TW.md` exists and reflects the full content of `README.md` at the time of implementation (no major sections omitted).
- [x] Code samples, commands, and JS snippets remain verbatim where translation would break copy-paste; comments inside code may stay English or be duplicated only if clearly marked.
- [x] `README.md` includes a visible link to the Traditional Chinese document.
- [x] `README.zh-TW.md` includes a visible link back to the English document.
- [x] No unrelated documentation files are added beyond what this task requires.

## Technical Notes

- Prefer terminology consistent with Taiwan Traditional Chinese for UI/instructions where ambiguous.
- Preserve upstream attribution and release links; translate surrounding prose only.

---

## Follow-up (2026-04-06)

- English `README.md` was later **replaced** with a project-focused English version aligned with `README.zh-TW.md` (no longer a line-by-line translation of the old upstream-long README).
- **Fork 自 / Forked from** links to [xuzhengyi1995/Manga_downloader](https://github.com/xuzhengyi1995/Manga_downloader) were added to both READMEs.
- Tracked in task: `04-06-readme-sync-fork` (`readme-sync-fork`).
