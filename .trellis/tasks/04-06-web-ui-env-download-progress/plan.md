# Web UI（FastAPI + `.env` + SSE）實作計畫

> **給代理工作者：** 建議依序執行；步驟使用 `- [ ]` 核取方塊追蹤。實作採 **TDD**：先寫失敗測試 → 最小實作 → 全綠 → 再重構。

**目標：** 本機 FastAPI 提供 `.env` 讀寫、啟動下載、SSE 即時進度；CLI `main_env.py` 與 API 共用 `download_runner`。

**架構：** `env_store`（原子寫入 + 鍵級合併）→ `Downloader`（可選 `progress_reporter`）→ `download_runner` → `web`（FastAPI + 靜態前端）。

**技術棧：** Python 3、FastAPI、uvicorn、既有 Selenium Downloader；前端極簡 HTML/JS（或後續再換 Vue）。

---

### Task 1：`env_store` — `.env` 讀取與合併寫入

**檔案：**
- 新增：`env_store.py`
- 新增：`tests/test_env_store.py`

- [x] **步驟 1：寫失敗測試** — 臨時目錄建立 `.env`（含註解與未知鍵），呼叫合併函式更新 `MANGA_RES`，斷言註解與未知行保留、目標鍵已更新。
- [x] **步驟 2：** `pytest tests/test_env_store.py -v` → 預期失敗（模組不存在）。
- [x] **步驟 3：** 實作 `read_managed_values` 與 `merge_write_dotenv`，含同目錄暫存檔 + `os.replace` 原子替換。
- [x] **步驟 4：** `pytest tests/test_env_store.py -v` → 全通過（請於本機執行）。

---

### Task 2：`Downloader` 進度回呼

**檔案：**
- 修改：`downloader.py`（`__init__` 增加可選 `progress_reporter`；在 `_download_one_viewer_id`、`download_book` 適當處呼叫）
- 新增：`tests/test_downloader_progress.py`（使用 `unittest.mock` 建立假 `Downloader` 或 patch 掉 `get_driver`／`download_book` 內部 — **以不啟 Chrome 為原則**）

- [x] **步驟 1：** `progress_support.emit_progress` 單元測試；`Downloader` 內建 `progress_reporter` 與各節點 `emit_progress`。
- [x] **步驟 2：** 事件類型對齊 `design.md`（`run_started`、`book_started`、`page_progress`、`run_finished`、`run_error`）。
- [ ] **步驟 3：** `pytest tests/test_progress_support.py`（Downloader 端請以實機／整合測試補強，見下）。

---

### Task 3：`download_runner` + 重構 `main_env.py`

**檔案：**
- 新增：`download_runner.py`
- 修改：`main_env.py`（改呼叫 runner）
- 新增：`tests/test_download_runner.py`（Mock `Downloader` 類別注入）

- [x] **步驟 1：** `tests/test_download_runner.py` Mock `Downloader` 與 `load_manga_config`。
- [x] **步驟 2：** `download_runner.py`；`main_env.main()` 改為 `run_download_from_dotenv()`。
- [ ] **步驟 3：** 請本機執行 `pytest tests/test_download_runner.py tests/test_main_env.py -v`。

---

### Task 4：FastAPI — `/api/env`、下載與 SSE

**檔案：**
- 新增：`web_app.py`（或 `web/app.py`，依 repo 慣例集中一檔先）
- 修改：`requirements.txt`（`fastapi`、`uvicorn[standard]`）
- 新增：`tests/test_web_app.py`（`TestClient`；runner / queue mock）

- [x] **步驟 1：** `tests/test_web_app.py`：`GET` 遮罩、`PUT` 更新、`409` 衝突。
- [ ] **步驟 2：** SSE 串流可另補整合測試（假佇列）；核心已於 `web_app.api_download_stream` 實作。
- [x] **步驟 3：** `web_app.py`、單一下載鎖、背景執行緒 + `run_download_from_dotenv`。
- [ ] **步驟 4：** 請本機執行 `pytest tests/test_web_app.py -v`。

---

### Task 5：靜態前端

**檔案：**
- 新增：`web_static/index.html`、`web_static/app.js`（或 `static/` 下）
- 修改：`web_app.py` 掛載 `StaticFiles`

- [x] **步驟 1：** `web_static/index.html`、`app.js`、`style.css`。
- [ ] **步驟 2：** 手動本機 smoke（啟動 `run_web_ui.py` + 實際下載）。

---

### Task 6：入口與文件

**檔案：**
- 新增：`run_web_ui.py`（`uvicorn.run(..., host="127.0.0.1")`）
- 修改：`README.zh-TW.md` 或 `README.md` 一小節（如何啟動 Web UI）

- [x] **步驟 1：** `README.md` / `README.zh-TW.md` 已補 Web UI 小節；`run_web_ui.py` 預設 `127.0.0.1:8765`。
- [ ] **步驟 2：** 請本機 `pip install -r requirements.txt` 後執行全專案 `pytest`。

---

## 自我檢查（計畫 vs prd/design）

- [x] 設定僅 `.env`、原子寫入／合併 — Task 1
- [x] SSE、單一下載 — Task 4
- [x] 共用 runner — Task 3
- [x] 機密不寫 log — 實作時於 `web_app` 與 runner 遵守

---

**執行選項：** 可於單一 session 依 Task 1→6 連續實作；或每 Task 結束後人工 review 再繼續。
