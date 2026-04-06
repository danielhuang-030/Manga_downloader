# 設計：Bookwalker TW `.env` 設定與 viewer ID 下載流程

**任務：** `04-06-env-settings`  
**狀態：** 已實作（細節以 [progress.md](./progress.md) 為準）  
**取代說明：** 先前 PRD 中「所有 `settings` 鍵都放進 `.env`」的寬泛描述；**本文件為設計準據**；與實作差異見 **§12** 與 `progress.md`。

---

## 1. 目標

1. 將預設流程所需的**機密與執行參數**放在**本機 `.env`**（不提交版控）。
2. 以 **多個 Bookwalker `browserViewer` 數字 ID** 取代手動維護的 **`manga_url[]` / `imgdir[]` 對應**，輸出路徑自動落在 **`./downloads/<中文書名>/`**。
3. 導覽至讀者頁後，從 **title / DOM** 取得**中文書名**，並在 Windows / WSL / macOS 下使用**安全的資料夾名稱**。

---

## 2. 環境變數約定（`.env` / `.env.example`）

### 2.1 寫入 `.env` 的變數（產品決策）

| 變數 | 必填 | 格式／說明 |
|------|------|------------|
| `MANGA_COOKIES` | 是 | 與目前 `settings["cookies"]` 相同之**分號分隔** cookie 字串。 |
| `MANGA_RES` | 是 | **自訂格式：** `{寬}x{高}`（ASCII 小寫 `x`），例如 `1445x2048`。解析為 `(int, int)` 供 `Downloader.res` 使用。 |
| `MANGA_SLEEP_TIME` | 是 | 數字（秒）；對應 `Downloader.sleep_time`。 |
| `MANGA_IDS` | 是 | **逗號分隔**的**數字** viewer ID，例如 `237928,340012`。前後空白可 trim；空項目忽略。 |

### 2.2 向後相容與既有環境變數

- **`BOOKWALKER_COOKIE`**：當未設定 `MANGA_COOKIES` 時，視為 `MANGA_COOKIES` 的**別名**（供 `check_bookwalker_cookie.py` 與既有習慣）。兩者皆設定時，**以 `MANGA_COOKIES` 為準**（於 `.env.example` 註明）。
- **`MANGA_HEADLESS`**：維持現狀，由 `downloader.py` 讀取。可選擇性在 `.env.example` 中僅作說明（不要求一定寫入 `.env`）。

### 2.3 不放入 `.env`（viewer 模式與 `main.py` 共用）

`loading_wait_time`、`cut_image`、`file_name_prefix`、`number_of_digits`、`start_page`、`end_page` 等：**實作上** 由 **`main.py` 的 `settings`** 提供，`main_env.py` 合併時覆寫僅 env 相關鍵（見 `progress.md`）。未使用獨立 `manga_settings` 模組。

### 2.4 優先順序

1. 行程環境變數（例如 `export MANGA_IDS=...`）
2. 於行程啟動時經 `python-dotenv` 自 `.env` 載入之值（`load_dotenv()`）

此順序須在 `.env.example` 中說明。

---

## 3. URL 與 ID 模型

- **預設基底格式（Bookwalker 台灣）：**  
  `https://www.bookwalker.com.tw/browserViewer/{id}/read`  
  其中 `{id}` 為 `MANGA_IDS` 中的每一筆。
- **實作：** 可選環境變數 **`MANGA_VIEWER_URL_TEMPLATE`** 覆寫（須含 `{id}`），預設為上列 TW URL（見 `manga_env.DEFAULT_VIEWER_URL_TEMPLATE`）。
- **範圍：** 預設為 TW `browserViewer`；模板機制保留多站點擴充空間。

---

## 4. 標題 → 資料夾名稱（`./downloads/<中文書名>`）

### 4.1 來源（已定：選項 A）

在既有 Selenium 流程中導覽至 viewer URL 後，自下列來源取得**可讀標題**：

1. **優先：** `document.title`（`execute_script` 或 `driver.title`），或  
2. **備援：** 若標題為空或過於通用，則於 Bookwalker TW 專用 actions 中使用小型、站別專屬 selector（實作細節；若啟用須於註解或文件中註記）。

### 4.2 清理規則（已定：選項 1）

1. `strip()` 去除前後空白。
2. 若出現 **`|` 或 `｜`**，只取**第一段**（捨去站臺／品牌後綴）。
3. 將路徑不安全字元 `\ / : * ? " < > |` 及各平台禁止字元替換為單一安全字元（例如 `_`），並合併重複分隔。
4. 若結果為空、僅 `.` / `..` 或無法使用 → 改為 **`browserViewer-{id}`**（ASCII、穩定可重現）。

### 4.3 輸出路徑

- **根目錄：** `./downloads/`（相對於目前工作目錄 CWD），除非日後任務另增覆寫選項。
- **每個 ID：** `os.path.join("downloads", sanitized_title)`（或等價寫法），於寫入圖檔前建立目錄。

### 4.4 日誌與安全

- **不要**在 INFO 層級記錄完整 cookie 字串。
- 標題於 INFO 記錄可接受；除非有除錯旗標，避免記錄整頁 HTML。

---

## 5. 控制流程調整（架構）

### 5.1 現況

`Downloader` 以平行列表 `manga_url` 與 `imgdir` 建構，於 `download()` 中檢查長度一致。

### 5.2 目標

- **設定層**（例如 `config.py`）：`load_dotenv()`、解析上述環境變數、驗證必填與格式、組出內部結構（cookies、res 元組、sleep、id 列表）。
- **進入點：** **`main_env.py`** 載入 `config`／`.env`；**`main.py`** 仍為傳統列表模式，二者並存。
- **`Downloader`**：支援 **viewer ID 驅動模式**，對每個 ID：
  1. 組出 viewer URL。
  2. 導覽（沿用既有 `login()` + `prepare_download` 語意：第一本套用 cookie 後同一會話）。
  3. 自已載入之讀者頁**解析標題**，並在 `./downloads/…` 下計算 `imgdir`。
  4. 對該目錄與 URL 執行既有**下載管線**（`download_book` 等）。

實作可重構 `prepare_download` 或迴圈順序，使**在 `mkdir` 前已知標題**並**盡量避免重複 `get()`**；對外行為須一致：cookie 有效、讀者能載入、分頁下載與現況相同。

### 5.3 列表模式（保留）

**`main.py`** 持續使用 `manga_url` + `imgdir` 列表；**`main_env`** 為 viewer ID 模式。測試仍以建構子傳列表或 viewer 參數覆蓋。

---

## 6. `check_bookwalker_cookie.py`

- **主要路徑：** 在 `load_dotenv()` 後從 **`MANGA_COOKIES`** 或 **`BOOKWALKER_COOKIE`** 讀取 cookie，**不必**依賴 `main.py` 的 `settings`。
- **URL：** 快速檢查時，除非傳入 `--url`，否則以 `MANGA_IDS` 的**第一個** ID 組預設 viewer URL。
- **`--from-main`：** 若可維持向後相容則保留；否則改為棄用提示，並於 docstring 指向 `.env`。

---

## 7. 測試策略

| 範圍 | 作法 |
|------|------|
| 解析 `MANGA_RES`（`1445x2048`） | 單元測試：合法、非法、缺漏 |
| 解析 `MANGA_IDS` | 單元測試：逗號、空白、空 token |
| 標題清理 → 資料夾名 | 單元測試：`|`、`｜`、非法字元、空字串 → `browserViewer-{id}` |
| Cookie 別名優先順序 | 單元測試：`MANGA_COOKIES` 與 `BOOKWALKER_COOKIE` |
| 瀏覽器／整合 | 手動或選用；CI 無環境可不強制 |

不使用資料庫；預設單元測試不連真實網路。

---

## 8. 依賴

- 於 `requirements.txt` 新增 **`python-dotenv`**。

---

## 9. 文件

- **`.env.example`：** 列出所有鍵、格式、別名規則、優先順序、非機密占位符。
- **README（簡短）：** 複製 `.env.example` → `.env` 並填入 cookie 與 ID。

---

## 10. 非範圍

- Docker 專用之注入模式。
- JP Bookwalker 或非 `browserViewer` 之 URL 形狀。
- 將所有 `Downloader` 旋鈕都移入 `.env`。

---

## 11. 待決議事項（v1 無）

Brainstorm 決策已盡數納入；實作時若需 Bookwalker 專用 selector 作標題備援，僅於程式註解中簡述即可。

---

## 12. 實作對照（2026-04-06）

| 設計項 | 實作 |
|--------|------|
| 單一 `main` 改寫 | **否**：`main.py` 維持原貌；新增 **`main_env.py`** |
| 非 env 參數來源 | **`main.settings`**（`main_env` `import` 後合併），非獨立預設表 |
| URL 模板 | **`MANGA_VIEWER_URL_TEMPLATE`** + 程式預設 Bookwalker TW |
| 進度追蹤 | **[progress.md](./progress.md)** |
