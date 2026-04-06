# Phase 0 — Baseline (pre–Phase 1 security pins)

**Date:** 2026-04-06  
**Purpose:** Reproducible rollback point before `requirements.txt` Pillow / requests / urllib3 bumps.

## Git baseline

| Item | Value |
|------|--------|
| **Commit** | `ba825708029268969f5d12b8e81170be1ee7c02a` (`ba82570`) |
| **Branch** | `feat/upgrade` |
| **Tag** | `baseline/pre-phase1-security-pins` (annotated; points to the commit above) |

To restore this tree:

```bash
git checkout baseline/pre-phase1-security-pins
# or: git checkout ba82570
```

## Chrome / Chromedriver (host or container)

Phase 0 does not change `Dockerfile`. Record versions when you run a full stack (recommended in **Phase 2** after Dockerfile work):

- **Chrome:** e.g. `google-chrome-stable --version` (Linux) or container equivalent.
- **Chromedriver / uc:** after `uc.Chrome(...)` starts, note the driver path from logs or `driver.capabilities` / process list; or `chromedriver --version` if a binary is on `PATH`.

Template for a manual smoke:

```
Chrome:   (fill after run)
Driver:   (fill after run)
Python:   3.8.x (Dockerfile FROM) or local venv
Commit:   (this baseline or later)
```

## Notes

- Pytest helper suite: `tests/test_downloader_helpers.py` (import / mocks only; no browser).
- E2E smoke for Phase 1 acceptance: at least one real download path per [prd.md](./prd.md) (developer-run).
