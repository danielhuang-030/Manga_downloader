# Selenium + uc stack upgrade

## 任務合併

原任務 **`04-06-assess-tech-stack-upgrades`**（技術堆疊升級**評估**）已合併至本目錄：評估全文見 [assessment.md](./assessment.md)，並已將該任務**歸檔**至 `.trellis/tasks/archive/`。此後以本目錄為單一「評估 + 設計 + 實作」任務。

## 目前進度（2026-04-06）

| 項目 | 狀態 |
|------|------|
| 任務狀態 | `in_progress`（見 `task.json`） |
| 分支 | `feat/upgrade` |
| 評估／合併／歸檔 | 完成 |
| [design.md](./design.md) + [upgrade-details.md](./upgrade-details.md)（brainstorming 定案） | 完成 |
| Pytest 單元測試骨架（`tests/test_downloader_helpers.py`、`requirements-dev.txt`、`pytest.ini`） | 已提交 **0c327f4** |
| **階段 0** — baseline tag + 筆記 | 完成：`baseline/pre-phase1-security-pins` → [baseline-phase0.md](./baseline-phase0.md) |
| **階段 1** — 安全性 pin（Pillow／requests／urllib3 等） | `requirements.txt` 已更新；`pip check`／`pytest`／smoke 待具 pip 環境執行 |
| **階段 2** — `Dockerfile`（apt keyring、移除舊 chromedriver zip、`DISPLAY`） | 已改；`docker build` 已成功（映像內 **Google Chrome 146.0.7680.177**）；**容器內一條 E2E** 仍待你方跑通 |
| **階段 3** — Python **3.12** 基底 + 依賴 | 完成：`FROM python:3.12-bookworm`；`requirements.txt` 增 **setuptools**（供 uc 在 3.12 使用 `distutils`）；映像內 `pip check` + `pytest` **12 passed** |
| 本機執行 `pytest` 全綠 | 待開發者於具 pip 環境執行（或沿用容器驗證） |
| [upgrade-details.md](./upgrade-details.md) 階段 4（Selenium／uc 升級 + 多站台 E2E） | 未開始 |

**近期 commit：** `0c327f4`（pytest）、`472412d`（Trellis 任務與 upgrade-details）；進度寫入見 `feat/upgrade` 上 `docs(trellis): record selenium+uc upgrade task progress` 等（`git log --oneline .trellis/tasks/04-06-selenium-uc-stack-upgrade/`）。

## Goal

在**維持 Selenium + undetected-chromedriver 架構**的前提下，分階段升級 Python、依賴與 Docker／Chrome／driver，解除 EOL 與容器脆弱性；驗證以端到端下載為主。

## Requirements

- 依 [design.md](./design.md) 之分階段順序實作；重大變更需可回滾。
- 不遷移至 Playwright／patchright（本次範圍外）。
- 升級後通過評估文件中的驗證清單（至少 smoke + 建議多站台）。

## Acceptance Criteria

- [ ] **單元測試：** `pip install -r requirements.txt -r requirements-dev.txt` 後 `pytest` 全數通過（見 repo 根目錄 `tests/`）。（測試檔已加入，**需本機／CI 跑通**後可勾選。）
- [ ] 階段 0–1：`requirements.txt` 更新後 `pip check` 通過，且至少一條下載 smoke 通過。
- [ ] 階段 2：`docker build` 成功；容器內一條 E2E 通過。
- [ ] 階段 3：Python 目標版本下依賴可安裝；E2E 通過。
- [ ] 階段 4：Selenium／uc 升級後，**至少兩個** `website_actions` 站台 E2E 通過。
- [ ] 設計決策與已知風險已記錄（README 或任務筆記）。

## Technical Approach

見 [design.md](./design.md)。評估依據見 [assessment.md](./assessment.md)。**升級細節定案**見 [upgrade-details.md](./upgrade-details.md)。

## Out of Scope

- Playwright／patchright 遷移、大規模重構 `website_actions` API。

## Definition of Done

- 各階段 PR／commit 可審查；主要驗證步驟可重現（命令或簡短說明）。
