# Logging Guidelines

> Logging conventions for the downloader.

---

## Overview

The app uses the Python standard library **`logging`** module. Configuration is **global** in `downloader.py` via `logging.basicConfig` (not structlog or JSON logs).

---

## Log Levels

| Level | Usage in this codebase |
|-------|-------------------------|
| **INFO** | Normal flow: found action class, viewport size, login, page loaded, per-page success, batch start/finish. |
| **ERROR** | Misconfiguration (URL/dir count), unsupported site, failures in download loop (plus exception message). |

**DEBUG** / **WARNING** are available but not heavily used in the current core files; new code should use **INFO** for milestones and **ERROR** for user-actionable problems.

---

## Structured Logging

Format (from `downloader.py`):

```text
[%(levelname)s](%(name)s) %(asctime)s : %(message)s
```

Date format: `%Y-%m-%d %H:%M:%S`.

Messages often use **`%` formatting** in `logging.info(..., arg)` style (lazy interpolation friendly).

---

## What to Log

- Which **WebsiteActions** subclass was selected for a URL.
- **Viewport** dimensions after window sizing (helps debug resolution mismatches).
- **Page progress** (`Page N Downloaded`, total page count).
- **Batch boundaries** when multiple `manga_url` entries are processed.

---

## What NOT to Log

- **Full cookie strings** or **Authorization** headers — they are secrets; `main.py` placeholders should never be replaced with real values in committed logs.
- **Large base64 image payloads** — avoid dumping canvas or screenshot data into log lines.
- Personally identifiable information beyond what is necessary to debug a **local** run.

On failure, **artifacts** (`error.html`, `error.png`) capture page state; logs should point users to those files rather than pasting entire HTML into the log.

---

## Examples

```20:21:downloader.py
logging.basicConfig(format='[%(levelname)s](%(name)s) %(asctime)s : %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
```

```76:77:downloader.py
                logging.info('Find action class, use %s class.',
                             self.actions_class.get_class_name())
```

```196:198:downloader.py
            logging.error('Something wrong or download finished,Please check the error.png to see the web page.\r\nNormally, you should logout and login, then renew the cookies to solve this problem.')
            logging.error(err)
```
