# 設計稿：Web UI（FastAPI）+ `.env` + SSE 進度

**任務：** `04-06-web-ui-env-download-progress`  
**狀態：** 供實作計畫使用之草稿

---

## 1. 背景

專案已透過 `config.load_manga_config()`（dotenv + `os.environ`）載入設定，並以 `main_env.downloader_kwargs_for_env()` 與 `main.settings` 合併後執行 `Downloader`。目前進度僅為 `downloader.py` 內**非結構化**的 `logging.info`。

---

## 2. 已定決策

| 主題 | 決策 |
|------|------|
| 設定儲存 | **僅專案根目錄 `.env`**，**不引入資料庫**；與 CLI 共用同一來源 |
| Web 框架 | **FastAPI** |
| 即時進度 | **SSE**（單向：伺服器 → 瀏覽器） |
| CLI | **保留** `main_env.py`；與 API 共用編排邏輯 |
| 並行 | **v1 僅單一下載**（第二次啟動回 **HTTP 409** 或等價錯誤，並附清楚 JSON 錯誤內容） |

### 2.1 `.env` 寫入可靠性（實作備忘）

不另建 DB 時，仍應避免半寫入與誤覆蓋：

- **原子寫入**：寫入暫存檔後再替換目標檔（同檔案系統內 `rename`）。
- **鍵級合併**：只更新 UI 管理的鍵，其餘行（含註解）盡量保留；若無法保留順序，於 README／實作註解說明策略。
- **（選填）** 單機下可對 `.env` 使用檔案鎖，避免極短時間內並發寫入。

---

## 3. 架構

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│  瀏覽器      │────▶│ FastAPI（本機）   │────▶│ 共用 runner              │
│  （靜態 UI） │ SSE │ REST + SSE        │     │ 組態 + Downloader        │
└─────────────┘     └──────────────────┘     └───────────┬─────────────┘
                                                         │
┌─────────────┐                                          │
│ main_env.py │──────────────────────────────────────────┘
└─────────────┘
```

- **共用 runner**（新模組，名稱實作時決定，例如 `download_runner.py`）：
  - 接受 `MangaConfig` 或 `.env` 路徑，以既有 `downloader_kwargs_for_env()` 組 kwargs，建立 `Downloader` 並呼叫 `download()`。
  - 可選擇性接受 **進度 sink**（見 §5）；API 使用時接入，CLI 則傳 no-op 或僅記錄 log。

- **FastAPI**：
  - 提供小型**靜態**前端（例如 `web_ui/static/`，或由 Vite 建置的 `frontend/dist/`——實作計畫會決定最小目錄配置）。
  - 提供讀寫環境變數、下載控制與 SSE 端點。

- **綁定位址**：預設僅 **`127.0.0.1`**（`uvicorn` 或 FastAPI 應用程式設定）。

---

## 4. HTTP API（v1 草圖）

> 路徑與名稱以實作計畫為準；**行為**以下列為準。

| 方法 | 路徑 | 用途 |
|------|------|------|
| `GET` | `/api/env` | 回傳可編輯的漫畫相關環境變數鍵值。Cookie **不得**寫入伺服器日誌；回應可對 Cookie 使用遮罩或空字串（選填：若前端傳「顯示」旗標——預設 YAGNI：`GET` 一律遮罩）。 |
| `PUT` | `/api/env` | 請求體：JSON，欲更新的鍵值。以既有解析器驗證（`parse_manga_res`、`parse_manga_ids` 等）。寫入專案根目錄 `.env`。 |
| `POST` | `/api/download/start` | 若目前無執行中任務：在**背景執行緒**（或非同步執行器）啟動下載，回傳 `{ "job_id": "..." }`。若忙碌：**409**，內容 `{ "error": "download_in_progress" }`（或等價）。 |
| `GET` | `/api/download/stream/{job_id}` | **SSE**：`Content-Type` 為 `text/event-stream`，事件見 §5。 |

**取消（v1 選填）：** 若時間允許，可新增 `POST /api/download/cancel`，以 `threading.Event` 通知 runner；若 v1 不做，文件註明「關閉分頁或結束行程即停止」。

---

## 5. SSE 事件約定

- **Content-Type：** `text/event-stream`
- **格式：** 每事件一個或多個 `data: {json}\n\n`；每則 JSON 為一個物件。

最小事件類型：

| `type` | 欄位 | 時機 |
|--------|------|------|
| `run_started` | `job_id` | 下載執行緒開始 |
| `book_started` | `viewer_id`、`index`、`title?` | 進入某 viewer／書籍 |
| `page_progress` | `viewer_id`、`page`、`total_pages`（若已知） | 每存完一頁後 |
| `run_finished` | `ok: true` | 正常結束 |
| `run_error` | `message`（不含 cookie／工作階段洩漏） | 失敗 |

實作細節：在 `Downloader`／`download_book`／`_download_one_viewer_id` 適當處插入 **執行緒安全佇列** 或 callback；SSE 端點從佇列讀取直到 `run_finished` 或 `run_error`。

---

## 6. 安全與隱私

- 預設僅 **本機 loopback**。
- **日誌不含機密**：不記錄原始 `.env` 或完整 Cookie 字串；結構化日誌需脫敏。
- **CORS：** v1 關閉或限制同源。
- **檔案路徑：** `.env` 解析於專案根目錄內；若未來有路徑參數，須拒絕 `..` 遍歷。

---

## 7. 前端（v1）

- 極簡 **HTML + CSS + 原生 JS**，或實作計畫若偏好元件結構則 **Vue 3 + Vite**；二擇一即可，依賴愈少愈好。
- UX：環境變數表單、「儲存」、「開始下載」、以 `EventSource` 餵入的紀錄／進度區塊。

---

## 8. 測試策略（TDD）

- **單元測試**（不啟瀏覽器）：環境請求體 → `MangaConfig` 的解析／驗證；SSE 序列化輔助；並行啟動的「單一執行」防護。
- **整合測試（選填）：** FastAPI `TestClient` + **假 runner** 推送假事件（不啟 Selenium）。

---

## 9. 已決議議題（v1）

- 即時進度選 **SSE**（單向，較 WebSocket 簡單）。
- **執行中再次啟動：** 以 HTTP **409** 拒絕。

---

## 10. 程式參照

- `config.load_manga_config`、`main_env.downloader_kwargs_for_env`、`Downloader.download()`  
- 驗證用 `manga_env.py` 解析器
