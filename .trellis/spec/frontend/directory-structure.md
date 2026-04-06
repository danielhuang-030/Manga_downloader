# Directory Structure

> How frontend code is organized in this project.

---

## Overview

This repository is a **Python CLI + Selenium** manga downloader. There is **no first-party web application or `src/` frontend tree** in the repo. User-facing “UI” work is limited to **automating third-party reader sites** in the browser (selectors and behavior live under `website_actions/`, orchestrated by `downloader.py`).

For structure and conventions of the Python codebase, see [Backend directory structure](../backend/directory-structure.md).

---

## Directory Layout

```
N/A — no in-repo SPA or static frontend package.
```

---

## Module Organization

Not applicable. New site-specific automation belongs in `website_actions/` as a `WebsiteActions` subclass (backend spec).

---

## Naming Conventions

Not applicable at the SPA/component level. Site modules use `*_actions.py` and PascalCase classes (documented under backend).

---

## Examples

- **Site automation (closest analogue to “page-level” work):** `website_actions/bookwalker_tw_actions.py`
- **Orchestration:** `downloader.py`, `main.py`
