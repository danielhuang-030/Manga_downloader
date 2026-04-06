# Quality Guidelines

> Code quality standards for frontend development.

---

## Overview

**Not applicable** to a separate frontend stack. Quality expectations for this repo are defined for **Python + Selenium** in [Backend quality guidelines](../backend/quality-guidelines.md).

---

## Forbidden Patterns

Follow backend quality doc. Additionally, avoid fragile automation that depends on minified obfuscated one-off selectors without comments explaining breakage risk.

---

## Required Patterns

Site-specific logic in `website_actions/*_actions.py`; shared behavior in `abstract_website_actions.py` / `downloader.py`.

---

## Testing Requirements

See backend quality guidelines. This repo’s tests (if present) target Python behavior, not component snapshots.

---

## Code Review Checklist

- Does the change stay inside the `WebsiteActions` / `Downloader` split?
- Are new selectors documented or obvious from site structure?
- Does error handling follow [Error handling](../backend/error-handling.md)?
