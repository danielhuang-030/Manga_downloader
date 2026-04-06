# Directory Structure

> How Python application code is organized in this project.

---

## Overview

This repository is a **Python 3.8** command-line tool that drives **Chrome via Selenium** (`undetected-chromedriver`) to capture manga pages from supported sites. There is **no separate API server**; the “backend” is the Python package at the repo root plus per-site adapters.

---

## Directory Layout

```
Manga_downloader/
├── main.py                 # User entry: settings dict + Downloader(**settings).download()
├── downloader.py         # Chrome setup, cookie login, download loop, orchestration
├── requirements.txt      # Pinned dependencies (selenium, Pillow, undetected-chromedriver, …)
├── Dockerfile            # Python 3.8 + Chrome/Chromedriver image; CMD python main.py
├── docker-compose.yml    # Mounts repo at /app
└── website_actions/      # Per-site implementations of WebsiteActions
    ├── __init__.py       # Dynamic export of sibling modules (glob); enables `from website_actions import *`
    ├── abstract_website_actions.py   # Abstract base: URL check, page count, navigation, canvas capture
    ├── bookwalker_tw_actions.py      # Example: Bookwalker Taiwan
    ├── bookwalker_jp_actions.py
    ├── cmoa_jp_actions.py
    └── …                 # One module per supported site / variant
```

Trellis tooling (`.trellis/`) is **meta** for agent workflow; it is not part of the downloader runtime.

---

## Module Organization

| Area | Responsibility |
|------|----------------|
| `main.py` | Default configuration template (`settings` dict). Users copy URLs, cookies, output dirs. |
| `downloader.py` | `Downloader` class: driver lifecycle, cookie injection, dispatch to `WebsiteActions` subclass, file I/O and optional PIL crop. |
| `website_actions/abstract_website_actions.py` | Contract every site must implement (`check_url`, `login_url`, page navigation, `get_imgdata`, etc.). |
| `website_actions/*_actions.py` | Site-specific selectors, JS calls (e.g. `NFBR…moveToPage`), canvas `toDataURL` decoding. |

**Adding a new site**

1. Subclass `WebsiteActions` in a new module under `website_actions/`.
2. Implement all abstract methods; override `before_download` if the reader needs a setup pass (see `bookwalker_tw_actions.py` for dynamic JS key discovery).
3. Ensure the module is a `*.py` sibling so `website_actions/__init__.py` picks it up.
4. Keep `from website_actions import *` in `downloader.py` so subclasses register on `WebsiteActions.__subclasses__()`.

---

## Naming Conventions

- **Site modules**: `something_actions.py` with a **PascalCase** class inheriting `WebsiteActions` (e.g. `BookwalkerTW`).
- **Entry/settings**: `main.py` uses a lowercase `settings` dict with documented keys (`manga_url`, `cookies`, `imgdir`, `res`, …).
- **Outputs**: Image paths are built from `imgdir` + `file_name_model` (PNG, zero-padded index).

---

## Examples

- **Orchestration and driver**: `downloader.py` — `Downloader.check_implementation`, `get_driver`, `download_book`.
- **Base contract**: `website_actions/abstract_website_actions.py`.
- **Concrete site**: `website_actions/bookwalker_tw_actions.py` — `check_url`, canvas capture, `before_download` for NFBR initializer key.

---

## Cross-Platform Notes

- **Docker**: Linux image with Chrome; `DISPLAY=:99` in Dockerfile for headless-style setups.
- **Local**: Users often run on Windows/macOS with their own Chrome profile patterns; paths in `main.py` are examples only.

When changing paths or browser flags, search the repo for existing values before editing (see guides: pre-modification rule).
