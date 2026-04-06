# 實作進度：env-settings（2026-04-06 更新）

## 狀態摘要

| 項目 | 說明 |
|------|------|
| **階段** | 核心功能已實作；待本機／容器實跑驗證與必要時補 README |
| **進入點** | **`main.py`**：維持傳統，於本檔填 `settings`，`python main.py`（多站點列表模式不變）。**`main_env.py`**：`python main_env.py`，讀 `.env` + 與 `main.settings` 合併非 env 欄位。 |
| **已捨棄** | `MANGA_FROM_DOTENV` 切換；`manga_settings.py`（改由 `main_env` 直接 `from main import settings` 合併）。 |

---

## 已交付檔案（相對於 repo 根目錄）

| 路徑 | 用途 |
|------|------|
| `main_env.py` | 載入 `config.load_manga_config()`、`downloader_kwargs_for_env()` 合併 `main.settings` |
| `config.py` | `MangaConfig`、`load_manga_config()`（內含 `load_dotenv`） |
| `manga_env.py` | 解析 `MANGA_RES`、`MANGA_IDS`、`MANGA_VIEWER_URL_TEMPLATE`、cookie 別名、資料夾名清理、`DEFAULT_VIEWER_URL_TEMPLATE` |
| `downloader.py` | `viewer_ids` 模式、`viewer_url_template`、`download_book(..., skip_before_download=)`、`_download_one_viewer_id` |
| `.env.example` | 變數說明與預設 Bookwalker TW 模板註解 |
| `check_bookwalker_cookie.py` | `load_dotenv`、cookie／預設 URL 與 `MANGA_VIEWER_URL_TEMPLATE` 對齊 |
| `requirements.txt` | `python-dotenv` |
| `tests/test_manga_env.py` | 解析與清理單元測試 |
| `tests/test_config.py` | `load_manga_config` |
| `tests/test_main_env.py` | `main.settings` 與 env 合併 |
| `tests/test_downloader_helpers.py` | 含 `viewer_ids` 相關 |

**刻意不變：** `main.py` 仍為本檔內嵌 `settings` 字典之原始形態，不依賴 `manga_env`／`config`。

---

## 與 design.md 對齊情況

- **環境變數：** `MANGA_COOKIES`、`MANGA_RES`、`MANGA_SLEEP_TIME`、`MANGA_IDS`；可選 **`MANGA_VIEWER_URL_TEMPLATE`**（預設 Bookwalker TW `browserViewer` URL，含 `{id}`）。
- **非 `.env` 的 Downloader 參數（viewer 模式）：** 由 **`main.py` 的 `settings`** 提供（經 `main_env.downloader_kwargs_for_env` 合併），與 design 初稿「僅程式預設」略有不同——**單一真相改為與列表模式共用 `main.settings`**。
- **標題／路徑清理、viewer 迴圈：** 如 design 第 4、5 節。

---

## 待辦／建議

- [ ] 本機或 Docker 跑通 `python main_env.py`（需有效 cookie、Chrome／headless 環境）。
- [ ] 全量 `pytest`（需安裝 `requirements.txt` + `requirements-dev.txt`）。
- [ ] （選）根目錄 README 補「兩種進入點」一句話。

---

## Git

未於此任務目錄自動記錄 commit hash；完成驗證後可於 `task.json` 的 `commit`／`notes` 補上。
