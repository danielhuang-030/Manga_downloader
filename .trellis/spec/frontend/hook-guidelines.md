# Hook Guidelines

> How hooks are used in this project.

---

## Overview

**Not applicable.** There are no React/Vue “hooks” in this codebase.

Stateful setup for downloads uses Python methods on `WebsiteActions` (e.g. `before_download`) and the `Downloader` class. See [Backend directory structure](../backend/directory-structure.md).

---

## Custom Hook Patterns

N/A

---

## Data Fetching

Page data is obtained via Selenium (DOM, canvas, JS execution) inside `website_actions/*`, not via client-side fetch hooks.

---

## Naming Conventions

N/A

---

## Common Mistakes

- Introducing a JS framework “hook style” in Python — prefer explicit methods on the site action class and clear orchestration in `downloader.py`.
