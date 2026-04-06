# State Management

> How state is managed in this project.

---

## Overview

**Not applicable** in the SPA sense (no Redux/Pinia/etc.).

Runtime configuration is supplied via the `settings` dict in `main.py` and held on the `Downloader` instance / driver session. Persistence is primarily **files on disk** (images under `imgdir`) and optional cookies passed into settings.

---

## State Categories

| Category | Where it lives |
|----------|----------------|
| User config | `main.py` → `settings` keys (`manga_url`, `cookies`, `imgdir`, …) |
| Browser session | Selenium WebDriver, cookie injection in `downloader.py` |
| Download progress | In-memory during `download_book`; output files as PNGs |

---

## When to Use Global State

Avoid new global mutable state in Python modules. Prefer passing dependencies through `Downloader` and `WebsiteActions` methods.

---

## Server State

N/A — no app-owned REST/GraphQL client in-repo.

---

## Common Mistakes

- Hard-coding paths or URLs in multiple modules — centralize in `main.py` / settings or shared constants after searching the repo.
