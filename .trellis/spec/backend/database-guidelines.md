# Database Guidelines

> Persistence and data storage in this project.

---

## Overview

**This project does not use a database.** There is no ORM, no migrations, and no SQL layer.

State and output are handled as:

- **Filesystem**: Downloaded pages are written as PNG files under user-configured directories (`imgdir` in `main.py` / `Downloader`).
- **In-memory / session**: Selenium `WebDriver` session, cookies passed from configuration, and optional PIL `image_box` for dynamic crop (see `downloader.py`).

---

## Query Patterns

Not applicable.

---

## Migrations

Not applicable.

---

## Naming Conventions

- **Output folders**: User-defined via `settings['imgdir']`; keep names filesystem-safe and consistent with `manga_url` order.
- **Image files**: Pattern `file_name_prefix` + zero-padded index + `.png` (see `Downloader.__init__` in `downloader.py`).

---

## Common Mistakes

- Assuming a **DB** or **ORM** when adding features — prefer small files, JSON sidecars next to images, or env-based config if persistence beyond PNGs is needed.
- Committing **real cookies** or **session secrets** into `main.py`; treat `cookies` as local-only configuration.
