# Progress — 04-06-readme-sync-fork

## Summary

Documentation task: English README aligned with the zh-TW project guide; both READMEs include **Fork 自 / Forked from** upstream link.

## Changes in this task

| Area | Detail |
|------|--------|
| `README.md` | Full replace: English parallel to `README.zh-TW.md` (overview, Usage A/B, `.env` table, Docker/headless, `check_bookwalker_cookie.py`, tests, layout, disclaimer). |
| Fork line | Both READMEs: `https://github.com/xuzhengyi1995/Manga_downloader`. |
| Cross-links | Top language switch; bottom section points to the other language + upstream history on the original repo. |
| Archive PRD | `archive/2026-04/04-06-readme-zh-tw/prd.md` — Follow-up note linking to this task. |

## Related Trellis task (code, not README)

Bookwalker NFBR resolver work is tracked separately: **`04-06-bookwalker-nfbr-resolver`** (`bookwalker-nfbr-resolver`) — see its `prd.md` / `progress.md`.

## Full working-tree diff (same session, uncommitted)

Besides README + Trellis, these files were also modified on `feat/upgrade`:

| Path | Role |
|------|------|
| `website_actions/bookwalker_nfbr_wait.py` | `__nfbrResolveMoveHolder`, classic `a6l` scan, deep search, probes |
| `website_actions/bookwalker_tw_actions.py` | `ensure_nfbr_move_to_page_ready` / `nfbr_move_to_page` |
| `website_actions/bookwalker_jp_actions.py` | same as TW |
| `tests/test_bookwalker_nfbr_wait.py` | tests for ensure / compat / `nfbr_move_to_page` |
| `.trellis/tasks/04-06-readme-sync-fork/` | this task (new) |
| `.trellis/tasks/04-06-bookwalker-nfbr-resolver/` | NFBR task (new) |

## Status

Implemented in working tree; commit when ready.
