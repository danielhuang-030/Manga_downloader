# Bookwalker NFBR moveToPage resolver (minified bundles)

## Goal

Restore reliable page navigation for Bookwalker TW/JP after upstream JS bundles renamed keys (e.g. `X3N`, `v4O`) and/or moved `moveToPage` under `menu.options.a6l` or renamed methods, so `main_env.py` / Docker headless runs no longer fail at `before_download`.

## Requirements (completed)

- Resolve a callable **page mover** without hard-coding `NFBR.a6G.Initializer.<name>.menu.options.a6l.moveToPage` only.
- Strategies implemented in JS (injected via `execute_script`):
  - Classic chains: `menu` / `views_.menu` → `options.a6l`, then `moveToPage` or scan `a6l` methods.
  - Scan `a6l` for functions whose source contains `moveToPage` or `pageSliderCounter` (minified renames).
  - Deep DFS from `Initializer` for objects with `moveToPage`, traversing **functions** as well as plain objects (WeakSet, depth cap).
  - Fallback search under `NFBR.a6G` and `NFBR` roots.
- `BookwalkerTW` / `BookwalkerJP`: `before_download` calls `ensure_nfbr_move_to_page_ready`; `move_to_page` delegates to `nfbr_move_to_page`.
- Unit tests updated for probe / compat helpers in `tests/test_bookwalker_nfbr_wait.py`.

## Acceptance Criteria

- [x] Viewer download proceeds past `before_download` on current Bookwalker TW browserViewer (Docker + headless verified by user).
- [x] Shared logic lives in `website_actions/bookwalker_nfbr_wait.py` (`__nfbrResolveMoveHolder`, etc.).
- [x] Tests cover `ensure_nfbr_move_to_page_ready`, `resolve_nfbr_menu_accessor` compat, `nfbr_move_to_page` mock.

## Related Files

- `website_actions/bookwalker_nfbr_wait.py`
- `website_actions/bookwalker_tw_actions.py`
- `website_actions/bookwalker_jp_actions.py`
- `tests/test_bookwalker_nfbr_wait.py`
