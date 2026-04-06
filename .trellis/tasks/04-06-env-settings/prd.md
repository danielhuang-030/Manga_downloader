# 使用 `.env` 存放敏感與主要設定

> **進度（2026-04-06）：** 見同目錄 **[progress.md](./progress.md)**（實作狀態、進入點、檔案清單、待辦）。

> **範圍註記：** 需求已於 brainstorm 收斂。本任務目錄內之 **`design.md`** 為 Bookwalker TW 流程之準據；**實作上** viewer 模式之非 `.env` 參數改與 **`main.py` 內 `settings` 共用**（經 `main_env` 合併），詳見 `progress.md`。下文若與 `design.md`／`progress.md` 牴觸，以 **較新實作紀錄** 為準。

## 目標

將**敏感資料**（尤其是 session cookie）與**主要執行設定**從已提交的 `main.py` 遷出，改存於**本機 `.env`**，避免機密進版控，並集中管理執行參數。

## 背景

- 目前 `main.py` 內嵌 `settings` 字典；cookie 與 URL 容易誤提交。
- `.gitignore` 已忽略 `.env`。
- `downloader.py` 已自環境讀取 `MANGA_HEADLESS`。
- `check_bookwalker_cookie.py` 支援 `BOOKWALKER_COOKIE`，並可經 `--from-main` 從 `main.py` 載入。

## 需求（歷史版本；細節以 design 為準）

1. **於程式進入點載入 `.env`**  
   採標準方式（例如 `python-dotenv`），使執行 `python main.py`（或文件化之進入點）時自專案根目錄（或目前工作目錄）載入 `.env`，無需手動 `export`。

2. **定義環境變數契約**  
   於**可提交之範本**（例如 `.env.example`）附註解列出變數。機密不得提交；實值僅存於本機 `.env`。

3. **涵蓋執行所需之設定能力**  
   詳細鍵名與行為見 **`design.md`**（含 viewer ID、自動下載目錄、`MANGA_RES` 格式等）。

4. **與既有環境變數命名一致**  
   優先使用清楚前綴（如 `MANGA_*`），與既有 `MANGA_HEADLESS` 對齊；`BOOKWALKER_COOKIE` 是否作為別名見 `design.md` 與 `.env.example`。

5. **`main.py` 與進入點（實作結果）**  
   **`main.py`** 維持傳統：本檔內嵌 `settings`，`python main.py`（列表／多站點）。**`.env` 路徑** 使用獨立檔 **`main_env.py`**（`python main_env.py`），不修改 `main.py` 結構；非 env 欄位與 `main.settings` 合併。

6. **Cookie 檢查 CLI**  
   更新 `check_bookwalker_cookie.py`，使驗證 cookie 時與下載程式使用相同設定來源（例如 `.env` 與相同變數名）。在合理範圍內保留向後相容（`--from-main`、`BOOKWALKER_COOKIE`）或於 docstring 說明遷移方式。

7. **測試**  
   新增或調整單元測試（環境解析／設定組裝）；不假設真實瀏覽器或 DB。必要時 mock 或隔離 `.env` 讀檔。

8. **文件**  
   簡短更新 README 或內嵌說明：複製 `.env.example` → `.env` 並填入數值。

## 驗收條件（對齊 design 調整）

- [ ] 僅依本機填妥之 `.env`（且 `main.py` 不含機密）即可跑通支援之流程。
- [ ] `.env.example` 已提交；`.env` 未被追蹤（沿用既有 gitignore）。
- [ ] `check_bookwalker_cookie.py` 可依文件與 `.env` 相同來源取得 cookie／URL。
- [ ] 既有測試已更新；新增測試涵蓋解析邊界（見 `design.md` 測試一節）。
- [ ] `requirements.txt` 含新依賴（例如 `python-dotenv`）。

## 技術備註

- **結構化數值：** 以 `design.md` 為準（例如 `MANGA_RES` 之 `WxH`、`MANGA_IDS` 逗號列表）。
- **優先順序：** 行程環境變數與 `.env` 之優先順序見 `design.md`，並於 `.env.example` 註明。
- **安全：** 勿於 INFO 層級記錄完整 cookie 字串。

## 非範圍

- 除設定載入與 `design.md` 所述流程外，不重寫 downloader 核心邏輯。
- Docker 專用 secret 注入（可另開後續任務）。

## 相關檔案

- `main.py`、`main_env.py`、`config.py`、`manga_env.py`、`downloader.py`、`check_bookwalker_cookie.py`
- `.env.example`、`requirements.txt`、`.gitignore`
- `tests/test_manga_env.py`、`tests/test_config.py`、`tests/test_main_env.py`、`tests/test_downloader_helpers.py`、`tests/test_check_bookwalker_cookie.py`
- 任務紀錄：**[progress.md](./progress.md)**
