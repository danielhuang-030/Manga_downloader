# Selenium + uc stack upgrade

## 任務合併

原任務 **`04-06-assess-tech-stack-upgrades`**（技術堆疊升級**評估**）已合併至本目錄：評估全文見 [assessment.md](./assessment.md)，並已將該任務**歸檔**至 `.trellis/tasks/archive/`。此後以本目錄為單一「評估 + 設計 + 實作」任務。

## 結案摘要（2026-04-06）

| 項目 | 狀態 |
|------|------|
| 任務狀態 | **`done`**（見 `task.json`）；目錄已移至 `.trellis/tasks/archive/2026-04/` |
| 分支 | `feat/upgrade` |
| 堆疊升級 | Python **3.12**、`Dockerfile`（Chrome `signed-by`、無手動 chromedriver zip）、`docker-compose.yml`（`shm_size`）、**Selenium 4.41.0**、**uc 3.5.5**、依賴 pin |
| 執行期 | `version_main`、`MANGA_HEADLESS`、`bookwalker_nfbr_wait`（NFBR／iframe／debug 產物）、**`BookwalkerSessionError`** 與 **`BookwalkerTW.cookie_domain = '.bookwalker.com.tw'`**（關鍵：`pcreader.bookwalker.com.tw` 需與 `www` 共用 domain cookie；先前誤判為 headless／cookie 無效） |
| 驗證 | 映像內 **`pytest` 25+ passed**；**Docker + headless + Bookwalker TW** 端到端下載 smoke **通過** |
| 工具 | **`check_bookwalker_cookie.py`**：`--from-main` 以 HTTP 驗證 `main.py` 與下載器同源 cookie |

### 第二站台（acceptance 原文）

設計上曾要求 **≥2 個 `website_actions` 站台** E2E。本次**實測以 Bookwalker TW 為主**；**JP 未於同一輪跑通**，`bookwalker_jp_actions` 已預設 **`cookie_domain`**，其餘待日後手動驗證。

## Goal

在**維持 Selenium + undetected-chromedriver 架構**的前提下，分階段升級 Python、依賴與 Docker／Chrome／driver，解除 EOL 與容器脆弱性；驗證以端到端下載為主。

## Requirements

- 依 [design.md](./design.md) 之分階段順序實作；重大變更需可回滾。
- 不遷移至 Playwright／patchright（本次範圍外）。

## Acceptance Criteria（結案時）

- [x] **單元測試：** `pip install -r requirements.txt -r requirements-dev.txt` 後 `pytest` 通過（`tests/`）。
- [x] 階段 0–1：`pip check`／`pytest`；**Bookwalker TW 下載 smoke**（Docker）。
- [x] 階段 2：`docker build` 成功；**容器內 TW E2E** 通過。
- [x] 階段 3：Python 3.12 下依賴可安裝；E2E（TW）通過。
- [~] 階段 4：**TW** 通過；**第二站台（JP）** 未於本次驗證（見上表）。
- [x] 設計決策與已知風險已記錄（[upgrade-details.md](./upgrade-details.md) 等）。

## Technical Approach

見 [design.md](./design.md)。評估依據見 [assessment.md](./assessment.md)。**升級細節定案**見 [upgrade-details.md](./upgrade-details.md)。

## Out of Scope

- Playwright／patchright 遷移、大規模重構 `website_actions` API。

## Definition of Done

- [x] 各階段變更可於 `feat/upgrade` 上檢閱；主要驗證步驟可重現（`docker compose run`、`pytest`、`check_bookwalker_cookie.py --from-main`）。
