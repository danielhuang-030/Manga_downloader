# Component Guidelines

> How components are built in this project.

---

## Overview

**Not applicable.** This project does not use React, Vue, or another component-based frontend in-repo. The browser is driven by Selenium against external sites; layout and widgets are not implemented as local components.

Use [Backend directory structure](../backend/directory-structure.md) and [Quality guidelines](../backend/quality-guidelines.md) for Python and `website_actions` patterns.

---

## Component Structure

N/A

---

## Props Conventions

N/A

---

## Styling Patterns

N/A (no app-level CSS framework in this repo)

---

## Accessibility

N/A for first-party UI. When changing automation, prefer stable selectors and avoid breaking reader accessibility on target sites.

---

## Common Mistakes

- Treating `website_actions` classes like UI components — they are **automation adapters**, not view layers; keep site logic in the subclass and shared flow in `Downloader` / `WebsiteActions`.
