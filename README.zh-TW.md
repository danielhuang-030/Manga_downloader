**語言 / Languages:** [English](README.md) | 正體中文

# Manga_downloader 使用說明（正體中文）

以 **Python**、**Selenium** 與 **undetected_chromedriver** 驅動 **Google Chrome／Chromium**，從已實作之網站閱讀器擷取頁面圖像並存成檔案。請僅在合法、符合服務條款與個人備份範圍內使用。

---

## 專案概要

- **列表模式**（`python main.py`）：在 `main.py` 的 `settings` 裡設定多組 `manga_url` 與對應的 `imgdir`，一次登入後依序下載。
- **Viewer／環境變數模式**（`python main_env.py`）：從專案根目錄的 `.env` 讀取 `MANGA_IDS`、cookie、解析度等；會合併 `main.py` 裡**未被**環境覆寫的選項（例如 `loading_wait_time`、`cut_image`、頁碼範圍等）。下載目錄會依**瀏覽器分頁標題**建立在 `downloads/` 下（見下文）。

實際站台邏輯在 `website_actions/` 各子類別；`Downloader` 會依網址自動選擇對應實作。

---

## 目前實作之網站（程式內註冊）

| 模組 | 說明 |
|------|------|
| `bookwalker_tw_actions` | Bookwalker 台灣（`bookwalker.com.tw`） |
| `bookwalker_jp_actions` | Bookwalker 日本（`bookwalker.jp`） |
| `cmoa_jp_actions` | Cmoa 漫畫（`cmoa.jp`） |
| `coma_jp_novel`（`CmoaJPNovels`） | Cmoa 小說相關 |
| `takeshobo_co_jp_actions` | 竹書房 Gamma Plus 等（`gammaplus.takeshobo.co.jp`） |

若網址無法對應任一 `WebsiteActions.check_url`，程式會拋出 `NotImplementedError`。

---

## 系統需求

- **Python**：建議 3.12（見 `Dockerfile`；專案依 `requirements.txt` 鎖版本）。
- **瀏覽器**：本機需能執行 **Google Chrome** 或 **Chromium**（`downloader` 會偵測主版本並傳給 `undetected_chromedriver`，減少與驅動程式版本不符的問題）。
- **OS**：開發以 Linux／容器為主；Windows／macOS 請自行確認 Chrome 與路徑。

---

## 安裝

```bash
pip install -r requirements.txt
# 開發／跑測試時另裝：
pip install -r requirements-dev.txt
```

---

## 使用方式一：`main_env.py`（建議：Bookwalker TW + `.env`）

1. 複製範本並編輯（**勿將含真實 cookie 的 `.env` 提交版控**）：

   ```bash
   cp .env.example .env
   ```

2. 依 `.env.example` 註解填寫至少：

   - `MANGA_COOKIES`（或相容的 `BOOKWALKER_COOKIE`）：與 `main.py` 相同格式的 cookie 字串（多為 `name=value; ...`）。
   - `MANGA_RES`：寬高，格式 `寬x高`，例如 `1445x2048`（僅 ASCII 小寫 `x`）。
   - `MANGA_SLEEP_TIME`：每頁下載間隔（秒，可為小數）。
   - `MANGA_IDS`：`browserViewer` 的數字 ID，多筆以英文逗號分隔。

3. 選填 `MANGA_VIEWER_URL_TEMPLATE`：必須包含 `{id}`；預設為 Bookwalker 台灣：

   `https://www.bookwalker.com.tw/browserViewer/{id}/read`

4. 執行：

   ```bash
   python main_env.py
   ```

**下載位置**：Viewer 模式下，每個 ID 會開對應網址，並以**頁面標題**（經 `sanitize_download_folder_name` 清理）在 **`downloads/<資料夾名稱>/`** 輸出 PNG；標題異常時會退回 `browserViewer-<id>` 等形式。

**與 `main.py` 的關係**：`MANGA_COOKIES`、`MANGA_RES`、`MANGA_SLEEP_TIME` 以及 viewer 相關欄位由 `.env` 提供；其餘鍵（例如 `loading_wait_time`、`cut_image`、`start_page`、`end_page`、`file_name_prefix` 等）沿用 `main.py` 的 `settings`。

---

## 使用方式二：`main.py`（列表網址 + 自訂目錄）

在 `main.py` 修改 `settings`：

- `manga_url`：與 `imgdir` 數量一致、且同一批次應為**同一網站**。
- `imgdir`：各漫畫輸出目錄（可為相對路徑，例如 `./downloads/example`）。
- `cookies`：登入後匯出之字串；請勿提交真實 cookie。

然後：

```bash
python main.py
```

---

## 環境變數參考（`.env`）

| 變數 | 必填 | 說明 |
|------|------|------|
| `MANGA_COOKIES` | 與 `BOOKWALKER_COOKIE` 二擇一 | Cookie 字串 |
| `BOOKWALKER_COOKIE` | 同上 | 舊慣例／相容用 |
| `MANGA_RES` | 是 | `寬x高` |
| `MANGA_SLEEP_TIME` | 是 | 每頁間隔（秒） |
| `MANGA_IDS` | 是 | 逗號分隔的 viewer ID |
| `MANGA_VIEWER_URL_TEMPLATE` | 否 | 含 `{id}` 的網址模板 |
| `MANGA_HEADLESS` | 否 | `new`（預設）／`old`／`0` 等關閉 headless；見 `downloader.py` |

**Docker Compose 注意**：專案根若同時有 `docker-compose.yml` 與 `.env`，Compose 會用 `.env` 做 **YAML 變數替換**，cookie 內的 `$` 可能造成警告。建議執行容器時使用 **`--env-file compose.env`**（見 `compose.env` 與 `docker-compose.yml` 註解）；應用程式仍透過掛載的專案目錄由 **python-dotenv** 讀取實際 `.env`。

---

## Headless 與容器

- `downloader.get_driver()` 預設使用 **`--headless=new`**（可透過 `MANGA_HEADLESS` 調整）。
- `Dockerfile` 內建 **Google Chrome stable**；`docker-compose.yml` 將專案掛載至 `/app`，並加大 **`shm_size`** 以降低分頁崩潰機率。
- 範例（跑測試）：

  ```bash
  docker compose --env-file compose.env run --rm python python -m pytest tests/ -v
  ```

預設 `CMD` 為 `python main.py`；Viewer 流程請在容器內改執行 `python main_env.py` 或覆寫指令。

---

## Cookie 與連線檢查

- **Bookwalker 台灣** 注入 cookie 時使用 **`cookie_domain='.bookwalker.com.tw'`**，以便在 `www` 與 `pcreader` 等子網域共用工作階段（見 `downloader.add_cookies`）。
- **`check_bookwalker_cookie.py`**：以 **HTTP** 檢查 cookie 與網址是否仍被導向登入頁等（**不需**開 Chrome）。支援從 `.env` 或 `--from-main` 讀取設定。結束代碼：`0` 未偵測到登入門檻、`1` 有登入門檻、`2` 請求錯誤。

---

## 下載與除錯檔案

- 發生例外時，`downloader` 可能寫入 **`error.html`**、**`error.png`** 於目前工作目錄，並記錄 log；常見處理為重新登入並更新 cookie。

---

## 測試

```bash
python -m pytest tests/ -v
```

設定載入等邏輯有單元測試（不依賴真實瀏覽器或資料庫）。

---

## 專案結構（精簡）

```
main.py              # 列表模式設定
main_env.py          # .env + viewer 模式進入點
config.py            # load_manga_config()
manga_env.py         # 字串解析、資料夾名稱清理
downloader.py        # Downloader、Chrome、下載流程
website_actions/     # 各站實作
tests/               # pytest
```

---

## 免責說明

本工具僅協助自動化**已授權存取之內容**的備份流程；使用者須自行遵守各平台服務條款與著作權法。開發者與本儲存庫不對濫用或侵權行為負責。

---

## 其他語言

完整英文說明（含上游專案歷史與較長版本紀錄）見 [README.md](README.md)。
