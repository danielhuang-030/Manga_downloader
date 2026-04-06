# Error Handling

> How errors are handled in this Python/Selenium downloader.

---

## Overview

The codebase uses **standard Python exceptions** plus **logging**. There is no HTTP API layer, so there are no structured “client error responses.” Failures surface as log lines and, during download, **debug artifacts** written to disk.

---

## Error Types

| Mechanism | When |
|-----------|------|
| `NotImplementedError` | No `WebsiteActions` subclass matches the URL (`Downloader.check_implementation`). |
| Bare `Exception` in `download_book` | Caught around the page loop; triggers snapshot dump and graceful return from the book (does not re-raise). |
| Early `return` | Validation failures (e.g. `manga_url` vs `imgdir` length mismatch) log at ERROR and exit the flow without raising. |

Custom exception classes are **not** defined today; new features may introduce them if they improve testability or caller handling.

---

## Error Handling Patterns

**URL / implementation guard** (`downloader.py`):

- Iterate `WebsiteActions.__subclasses__()`, call `check_url(this_manga_url)`.
- If none match: `logging.error` then `raise NotImplementedError`.

**Download loop** (`Downloader.download_book`):

- Broad `try`/`except Exception`: writes `error.html` (page source) and `error.png` (screenshot), logs guidance about cookies/login, resets `image_box`, **returns** (swallows exception).

**Site modules** (`website_actions/*`):

- Often rely on Selenium `find_element` / `WebDriverWait`; failures propagate to `download_book` unless locally caught.
- Some modules use `try/except ImportError` for `abstract_website_actions` vs `website_actions.abstract_website_actions` when run as script vs package.

---

## API Error Responses

Not applicable (no REST/GraphQL server).

---

## Common Mistakes

- **Swallowing errors** in `download_book` without checking `error.html` / `error.png` — users may think the run succeeded.
- **Raising** from site code without ensuring the driver is left in a safe state — prefer logging and explicit waits.
- Relying on **fragile DOM/JS** (e.g. `NFBR` internals) without a fallback path when the reader changes (document site-specific quirks in the site module docstring).

---

## Examples

```146:200:downloader.py
    def download_book(self, this_image_dir):
        driver = self.driver
        logging.info('Run before downloading...')
        self.actions_class.before_download(driver)
        logging.info('Start download...')
        try:
            page_count = self.actions_class.get_sum_page_count(driver)
            # ... page loop ...
        except Exception as err:
            with open("error.html", "w", encoding="utf-8") as err_source:
                err_source.write(driver.page_source)
            driver.save_screenshot('./error.png')
            logging.error('Something wrong or download finished,Please check the error.png to see the web page.\r\nNormally, you should logout and login, then renew the cookies to solve this problem.')
            logging.error(err)
            self.image_box = None
            return
```

```70:82:downloader.py
    def check_implementation(self, this_manga_url):
        is_implemented_website = False
        for temp_actions_class in WebsiteActions.__subclasses__():
            if temp_actions_class.check_url(this_manga_url):
                is_implemented_website = True
                self.actions_class = temp_actions_class()
                logging.info('Find action class, use %s class.',
                             self.actions_class.get_class_name())
                break

        if not is_implemented_website:
            logging.error('This website has not been added...')
            raise NotImplementedError
```
