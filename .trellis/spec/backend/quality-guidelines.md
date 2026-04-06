# Quality Guidelines

> Code quality standards for Python changes in this project.

---

## Overview

This is a **small, script-oriented** codebase targeting **Python 3.8** (see `Dockerfile` and `requirements.txt`). Quality goals: **reliable browser automation**, **clear per-site isolation** in `website_actions/`, and **safe handling of user secrets** (cookies).

---

## Forbidden Patterns

- **Removing** `from website_actions import *` from `downloader.py` without an equivalent registration mechanism — subclasses would not populate `WebsiteActions.__subclasses__()`.
- **Committing** real `cookies`, paid content URLs, or personal download directories in `main.py`.
- **Silent** DOM/JS changes: if a reader site breaks, prefer explicit errors or logs plus optional artifacts (`error.html` / `error.png` pattern).
- Adding **heavy frameworks** (ORM, full web stack) for features that can stay a **single script + modules**.

---

## Required Patterns

- New sites: **subclass** `WebsiteActions` and implement **all** abstract methods in `abstract_website_actions.py`.
- Keep **site-specific** selectors and JS in the **site module**, not in `downloader.py`.
- Use **`logging`** for user-visible progress and failures (see `logging-guidelines.md`).
- Match **existing style** in nearby files: module docstring, class docstrings for public types, Python 2/3 compatible patterns where still present (e.g. `__metaclass__ = ABCMeta` in the base class).

---

## Testing Requirements

There is **no automated test suite** in-tree today. When contributing:

- **Manually verify** a short download against a test title (respect site ToS).
- For parser/DOM changes, capture **before/after** behavior with the existing **error screenshot/HTML** workflow if something fails.
- If adding tests later, prefer **unit tests** for pure helpers (e.g. cookie parsing) with **mocked** WebDriver; avoid requiring a live browser in CI unless explicitly set up.

---

## Code Review Checklist

- [ ] Does a new site module implement every abstract method?
- [ ] Is `check_url` **specific enough** to avoid overlapping with another reader?
- [ ] Are waits **explicit** (`WebDriverWait`) rather than bare `sleep` where possible? (Project still uses `time.sleep` for load delays — do not worsen race conditions.)
- [ ] Are **dependencies** pinned or justified if `requirements.txt` changes?
- [ ] Could **cookies or PII** leak into logs or committed files?

---

## Dependencies

Pinned in `requirements.txt` (excerpt): `selenium`, `undetected-chromedriver`, `Pillow`, `requests`. Keep versions compatible with **Python 3.8** unless the Docker base image is upgraded deliberately.

---

## Examples of Good Structure

- **Thin orchestration**: `downloader.py` — driver, loops, filesystem.
- **Fat per-site logic**: `website_actions/bookwalker_tw_actions.py` — selectors, NFBR JS, canvas decode.
