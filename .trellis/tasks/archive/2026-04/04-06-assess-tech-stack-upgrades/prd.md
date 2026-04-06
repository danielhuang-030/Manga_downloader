# Assess tech stack upgrades

## Goal

Produce a **written assessment** of how the Manga_downloader project could evolve its current technology stack: what to upgrade, in what order, risks (especially Selenium / `undetected-chromedriver` / Chrome), and a suggested phased plan. This task is **research and recommendation only** unless explicitly extended to implementation.

## Current stack (baseline for review)

| Area | Observed baseline |
|------|-------------------|
| Language | Python **3.8** (`Dockerfile` base image) |
| Browser automation | **Selenium** 4.18.x, **undetected-chromedriver** 3.5.5 |
| Images / I/O | **Pillow** 9.2.x |
| HTTP | **requests** 2.31.x, **urllib3** 1.26.x |
| Container | `python:3.8`, **Google Chrome** stable from Google apt repo, **Chromedriver** via `chromedriver.storage.googleapis.com` zip in Dockerfile |
| Entry | `main.py` → `downloader.py` + `website_actions/*` |

> Confirm versions from `requirements.txt` and `Dockerfile` at time of work; pins may drift.

## Requirements

1. **Inventory** — List runtime and build-time dependencies with versions and roles (why each matters for this app).
2. **Python** — Evaluate moving beyond 3.8 (EOL): supported target versions, blockers in dependencies, and test implications.
3. **Python packages** — For major pins (selenium, Pillow, requests/urllib3, undetected-chromedriver), note known breaking changes, security posture, and compatibility with the codebase patterns actually used.
4. **Docker / Chrome / Chromedriver** — Assess Dockerfile fragility (deprecated chromedriver distribution, `apt-key`, Chrome/driver version skew). Compare options (e.g. official Selenium images, driver management baked into Selenium 4.6+, matching Chrome major versions).
5. **Risk ranking** — Order upgrades by risk vs benefit; call out what must be validated manually (site-specific `website_actions` against real readers).
6. **Deliverable** — A short **upgrade roadmap** (phases: e.g. “security pins only” → “Python bump” → “container modernization”) with go/no-go criteria.

## Acceptance criteria

- [x] Document lists current stack with file references (`requirements.txt`, `Dockerfile`, optionally `docker-compose.yml`).
- [x] Python upgrade path is justified (target version(s), dependency constraints, deprecation notes).
- [x] Docker/Chrome/driver approach is evaluated with at least one concrete alternative to the current Dockerfile pattern.
- [x] Risks and recommended validation steps (manual or automated) are explicit for Selenium-based flows.
- [x] Output is suitable to paste into an issue or follow-up implementation tasks (clear phases).

**Deliverable:** [`assessment.md`](./assessment.md)（正體中文，2026-04-06）。

## Out of scope (unless agreed later)

- Applying upgrades in production code or opening a dependency bump PR.
- Rewriting scrapers to Playwright or other stacks (may be mentioned as optional long-term note only).

## Technical notes

- **undetected-chromedriver** lag vs upstream Chrome/Selenium is a primary constraint; assessment should not assume latest Selenium “just works” without checking project issues/releases.
- Site modules under `website_actions/` are the regression surface; any upgrade plan should mention spot-checking 1–2 representative sites after driver/Python changes.

## Related files

- `requirements.txt`
- `Dockerfile`
- `docker-compose.yml` (if present)
- `downloader.py`, `website_actions/abstract_website_actions.py`
