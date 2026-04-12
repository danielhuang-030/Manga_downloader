**Languages / 語言:** English | [正體中文](README.zh-TW.md)

# Manga_downloader

**Forked from:** [github.com/xuzhengyi1995/Manga_downloader](https://github.com/xuzhengyi1995/Manga_downloader)

This project uses **Python**, **Selenium**, and **undetected_chromedriver** to drive **Google Chrome / Chromium** and capture page images from supported site readers into files. Use it only where permitted by law, the platform’s terms of service, and personal backup norms.

---

## Overview

- **List mode** (`python main.py`): set multiple `manga_url` entries and matching `imgdir` values in `settings` in `main.py`, log in once, then download in order.
- **Viewer / environment mode** (`python main_env.py`): read `MANGA_IDS`, cookies, resolution, and more from a `.env` file in the project root; values **not** overridden by the environment are merged from `settings` in `main.py` (e.g. `loading_wait_time`, `cut_image`, page range). Download folders are created under `downloads/` from the **browser tab title** (see below).

Site-specific logic lives under `website_actions/`; `Downloader` picks the implementation by URL.

---

## Supported sites (registered in code)

The table lists modules under `website_actions/`. **In this fork, only Bookwalker Taiwan has been verified end-to-end** (including viewer / `.env` defaults and tooling). Other rows inherit upstream implementations and are **not verified** here—selectors or reader flows may be outdated.

| Module | Site | Verification (this fork) |
|--------|------|----------------------------|
| `bookwalker_tw_actions` | Bookwalker Taiwan (`bookwalker.com.tw`) | **Verified** |
| `bookwalker_jp_actions` | Bookwalker Japan (`bookwalker.jp`) | Not verified |
| `cmoa_jp_actions` | Cmoa manga (`cmoa.jp`) | Not verified |
| `coma_jp_novel` (`CmoaJPNovels`) | Cmoa novels | Not verified |
| `takeshobo_co_jp_actions` | Takeshobo Gamma Plus, etc. (`gammaplus.takeshobo.co.jp`) | Not verified |

If the URL does not match any `WebsiteActions.check_url`, the program raises `NotImplementedError`.

---

## Requirements

- **Python**: 3.12 recommended (see `Dockerfile`; versions are pinned in `requirements.txt`).
- **Browser**: **Google Chrome** or **Chromium** must be runnable locally (`downloader` detects the major version for `undetected_chromedriver` to reduce driver mismatch).
- **OS**: Development targets Linux / containers; on Windows / macOS, verify Chrome and paths yourself.

---

## Install

```bash
pip install -r requirements.txt
# For development / tests also install:
pip install -r requirements-dev.txt
```

### Run tests in a container (matches Dockerfile / CI)

Requires **Docker** and **Docker Compose**. From the project root, **prefer `./scripts/compose.sh`** (sets host `MANGA_WEB_UID` / `MANGA_WEB_GID` and adds `--env-file compose.env` when that file exists):

```bash
./scripts/compose.sh build python
./scripts/docker-test.sh
```

`./scripts/docker-test.sh` already invokes Compose via **`./scripts/compose.sh`**.

If you must call Compose directly (e.g. CI without the wrapper) and the project `.env` triggers `$` YAML warnings, use:

```bash
docker compose --env-file compose.env run --rm python python -m pytest tests/ -v
```

Equivalent with the wrapper:

```bash
./scripts/compose.sh run --rm python python -m pytest tests/ -v
```

Pass extra pytest args after the test script, e.g. `./scripts/docker-test.sh tests/test_env_store.py -q`.

---

## Web UI (local, optional)

The app **always** binds **`127.0.0.1:8765`** when you run `run_web_ui.py` (hardcoded; not read from `.env`).

```bash
python run_web_ui.py
```

Open `http://127.0.0.1:8765/` to edit `.env`, start downloads, and stream progress over **SSE**. Do not expose this service to untrusted networks.

- **Stop (running job):** After **Start download** succeeds, the same primary button becomes **Stop**. Click it to request cooperative cancellation; the label shows **Stopping…** until the worker thread exits and the WebDriver is released. **Start download** stays unavailable until then (another start returns HTTP **409** while a job is still active or finishing). The SSE stream ends with `type: "run_cancelled"` when you stop the job. Pause/resume is not implemented.
- **Theme:** Use the header control to switch **light**, **dark**, or **follow system** (stored in browser `localStorage` as `manga_web_theme`).
- **Add ID from URL:** Paste a full viewer URL in the helper row under **MANGA_IDS**, then click **Append ID from URL**; the server parses the numeric ID using **`MANGA_VIEWER_URL_TEMPLATE`** (from the form, or the default when empty) and merges it into the list. **Save** still writes `.env`. Parse failures return an error message; duplicate IDs show a notice and do not change the list.
- **Language / labels:** Use the header **Language** control for **English** or **Traditional Chinese**; form labels and messages follow the selection (env var keys stay in parentheses).

### Docker Compose: published (host) port

Inside the container the server listens on **`0.0.0.0:8765`** (fixed in `docker-compose.yml`). Only the **host port** is configurable via **`MANGA_WEB_PORT`** for Compose variable substitution (you can put it in the project root `.env` for Docker; the Python app does not read it).

| Setting | Mapping |
|---------|---------|
| (unset) | host `8765` → container `8765` |
| `MANGA_WEB_PORT=9000` | host `9000` → container `8765` |

```bash
./scripts/compose.sh build web
./scripts/compose.sh up web
```

Example: with `MANGA_WEB_PORT=9000` in `.env`, open `http://127.0.0.1:9000/` on the host.

**Bind-mounted file ownership (Docker):** processes running as **root** often create `root:root` files on the host (including `.env` and `downloads/`). `merge_write_dotenv` tries to **`chown`** `.env` back after replace. Both **`web`** and **`python`** services use `user: "${MANGA_WEB_UID:-0}:${MANGA_WEB_GID:-0}"` in `docker-compose.yml`, and set **`HOME=/app`** so Chrome / undetected_chromedriver does not try to write **`/.local`** when the numeric user has no real home directory in the image.

- **Recommended:** run **`./scripts/compose.sh …`** for any Compose command (build / up / run). It exports `MANGA_WEB_UID` / `MANGA_WEB_GID` from `id -u` / `id -g` unless already set, and adds `--env-file compose.env` when that file exists. Examples: `./scripts/compose.sh up web`, `./scripts/compose.sh run --rm python python main_env.py`. **`./scripts/docker-test.sh`** uses this wrapper.
- **Manual (only if you skip the script):** `export MANGA_WEB_UID=$(id -u) MANGA_WEB_GID=$(id -g)` then `docker compose --env-file compose.env …`.

---

## Usage A: `main_env.py` (recommended for Bookwalker TW + `.env`)

1. Copy the example and edit (**do not commit a `.env` with real cookies**):

   ```bash
   cp .env.example .env
   ```

2. Fill in at least the following (see comments in `.env.example`):

   - `MANGA_COOKIES`: cookie string in the same format as `main.py` (typically `name=value; ...`).
   - `MANGA_RES`: width and height as `WIDTHxHEIGHT`, e.g. `1445x2048` (ASCII `x` only).
   - `MANGA_SLEEP_TIME`: delay between pages in seconds (decimals allowed).
   - `MANGA_IDS`: numeric `browserViewer` IDs, comma-separated.

3. Optional `MANGA_VIEWER_URL_TEMPLATE`: must include `{id}`; default is Bookwalker Taiwan:

   `https://www.bookwalker.com.tw/browserViewer/{id}/read`

4. Run:

   ```bash
   python main_env.py
   ```

**Output location**: In viewer mode, each ID opens the matching URL and writes PNGs under **`downloads/<folder>/`**, where the folder name comes from the **page title** (via `sanitize_download_folder_name`); if the title is unusable, names like `browserViewer-<id>` are used.

**Relationship to `main.py`**: `MANGA_COOKIES`, `MANGA_RES`, `MANGA_SLEEP_TIME`, and viewer-related fields come from `.env`; other keys (e.g. `loading_wait_time`, `cut_image`, `start_page`, `end_page`, `file_name_prefix`) default from `settings` in `main.py`.

---

## Usage B: `main.py` (URL list + custom directories)

Edit `settings` in `main.py`:

- `manga_url`: same count as `imgdir`, and one batch should be the **same site**.
- `imgdir`: output directory per manga (can be relative, e.g. `./downloads/example`).
- `cookies`: exported after login; never commit real cookies.

Then:

```bash
python main.py
```

---

## Environment variables (`.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `MANGA_COOKIES` | yes | Cookie string |
| `MANGA_RES` | yes | `WIDTHxHEIGHT` |
| `MANGA_SLEEP_TIME` | yes | Seconds between pages |
| `MANGA_IDS` | yes | Comma-separated viewer IDs |
| `MANGA_VIEWER_URL_TEMPLATE` | no | URL template with `{id}` |
| `MANGA_HEADLESS` | no | `new` (default) / `old` / `0` to disable headless; see `downloader.py` |

**Docker Compose note**: If both `docker-compose.yml` and `.env` exist at the project root, Compose uses `.env` for **YAML variable substitution**, and `$` inside cookies can trigger warnings. Prefer **`./scripts/compose.sh …`** (adds `--env-file compose.env` when present) or **`docker compose --env-file compose.env ...`** (see `compose.env` and comments in `docker-compose.yml`). The app still loads the real `.env` via **python-dotenv** from the mounted project directory.

---

## Headless and Docker

- `downloader.get_driver()` defaults to **`--headless=new`** (override with `MANGA_HEADLESS`).
- The `Dockerfile` installs **Google Chrome stable**; `docker-compose.yml` mounts the project to `/app` and increases **`shm_size`** to reduce tab crashes.
- Example (run tests):

  ```bash
  ./scripts/compose.sh run --rm python python -m pytest tests/ -v
  ```

The image default `CMD` is `sleep infinity`, and the **`python` service in `docker-compose.yml` sets `command: sleep infinity`** to override the image CMD (so old cached images that still had `python main.py` do not auto-run). After pulling compose changes, recreate containers: `./scripts/compose.sh up -d --force-recreate` (or `down` then `up`).

Run downloads explicitly, e.g. `./scripts/compose.sh run --rm python python main_env.py` or `python main.py` on the host.

---

## Cookies and connectivity checks

- **Bookwalker Taiwan** sets cookies with **`cookie_domain='.bookwalker.com.tw'`** so the session is visible on `www` and `pcreader` subdomains (see `downloader.add_cookies`).
- **`check_bookwalker_cookie.py`**: checks cookies and URLs over **HTTP** (no Chrome). Can read from `.env` or `--from-main`. Exit codes: `0` no login gate detected, `1` login gate, `2` request error.

---

## Downloads and debug artifacts

- On errors, `downloader` may write **`error.html`** and **`error.png`** in the current working directory and log details; refreshing cookies after re-login often fixes session issues.

---

## Tests

```bash
python -m pytest tests/ -v
```

Config loading and related logic have unit tests (no real browser or database).

---

## Project layout (short)

```
main.py              # List mode settings
main_env.py          # Entry point for .env + viewer mode
config.py            # load_manga_config()
manga_env.py         # String parsing, safe folder names
downloader.py        # Downloader, Chrome, download loop
website_actions/     # Per-site implementations
tests/               # pytest
```

---

## Disclaimer

This tool only automates backup of **content you are authorized to access**. You must comply with each platform’s terms and copyright law. The authors and this repository are not responsible for misuse or infringement.

---

## Other languages

Traditional Chinese version: [README.zh-TW.md](README.zh-TW.md).

Historical notes and the upstream author’s BW Chrome downloader releases remain on the [original repository](https://github.com/xuzhengyi1995/Manga_downloader).
