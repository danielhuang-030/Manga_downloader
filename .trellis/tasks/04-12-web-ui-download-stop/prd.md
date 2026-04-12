# Web UI：下載進行中「停止」（合作式取消）

## 目標

使用者在 Web UI 啟動下載後，可透過**同一顆主要按鈕**由「開始下載」切換為「停止」，以**合作式取消**盡快中止背景下載；**必須等**背景執行緒與 WebDriver 釋放完成後，才可再次成功啟動新任務。第一版**不包含**暫停／繼續。

## 需求

### 範圍與語意

- **第一版**：僅實作「**停止**」；暫停／繼續列為後續迭代。
- **停止時機**：在可安全檢查的邊界盡快中止；**允許**最後一頁／檔寫入不完整；已落地檔案保留。
- **鎖與再接續**：停止請求送出後，在執行緒 `finally` 清空 `_active_job_id` 並釋放資源**之前**，`/api/download/start` 仍視為忙碌並回 **409**（與現有「進行中下載」語意一致）。

### 後端

- 新增 **`POST /api/download/stop`**，JSON body 帶 **`job_id`**（字串 UUID）。
  - `job_id` 等於目前 `_active_job_id`：設定**取消信號**（建議 `threading.Event`），回 **200**（或 **202**；計畫中固定一種並寫測試）。
  - `job_id` 不符或無進行中 job：**404**。
  - 重複停止同一進行中 job：**冪等**成功（事件已 set 不視為錯誤）。
- 下載執行緒呼叫 `run_download_from_dotenv(..., cancel_event=...)`，將信號傳入 **`Downloader`**，在 **`download()`** 外層迴圈與 **`download_book()`** 內頁迴圈等邊界檢查；取消時送出 **`type: "run_cancelled"`**（或計畫內固定之名稱）之進度事件，並 **`quit()`** 釋放 driver（與正常結束路徑一致，避免重複 quit 需防呆）。
- **`GET /api/download/stream/{job_id}`** 在收到終止型別時結束串流，終止集合須包含 **`run_cancelled`**（與既有 `run_finished`、`run_error` 並列）。

### 前端

- **`#btn-start`**：閒置顯示「開始下載」；成功 `start` 且取得 `job_id` 後，同鈕改為「停止」；呼叫 `stop` 後改為 disabled「停止中…」；SSE 收到終止事件（含 **`run_cancelled`**）後關閉 `EventSource`，還原為「開始下載」並可再次 `start`。
- 所有使用者可見字串走 **`i18n.js`**（zh-Hant / en）。

### 相容性

- **`python main_env.py`** 不傳 `cancel_event` 時行為與現況相同（CLI 無停止 API）。

## 驗收準則

- [ ] 下載進行中主要按鈕為「停止」；按下後進入「停止中…」且無法再次成功 `start`，直到 SSE 終止且後端釋放鎖。
- [ ] `POST /api/download/stop` 正確 `job_id` 會觸發取消；錯誤 `job_id` → **404**；收尾期間 `start` → **409**。
- [ ] SSE 在 **`run_cancelled`** 後結束，`EventSource` 可關閉。
- [ ] **`pytest`**：`tests/test_download_runner.py`（參數轉發）、`tests/test_web_app.py`（stop 與鎖行為，以 mock 下載函式避免真瀏覽器）新增／更新案例通過；驗證指令與證據依 `plan.md` 與專案 README。

## 技術備註

- 取消信號建議 **`threading.Event`**，自 `web_app` 每 job 建立，執行緒 `finally` 仍負責清空 `_active_job_id`。
- `Downloader.download_book` 既有 **`except Exception`** 須讓取消例外**向上傳播**（獨立 `DownloadCancelled` 或等同機制），避免被誤判為 `run_error`。
- 設計對話共識見同目錄 **`design.md`**。
