# Type Safety

> Type safety patterns in this project.

---

## Overview

**Not applicable** for TypeScript/JavaScript. The application is **Python 3.8**. Type hints and style for Python are covered implicitly by [Backend quality guidelines](../backend/quality-guidelines.md) and existing modules (`downloader.py`, `website_actions/`).

---

## Type Organization

Python modules at repo root and under `website_actions/`. No shared `types/` package unless the codebase introduces one.

---

## Validation

Validate external inputs (URLs, file paths, decoded image data) at boundaries in `Downloader` / site actions; prefer explicit checks over silent failures.

---

## Common Patterns

Follow patterns in `abstract_website_actions.py` and concrete `*_actions.py` subclasses.

---

## Forbidden Patterns

- Adding TypeScript-only conventions to this repo without an actual TS frontend.
