# 設計摘要（頭腦風暴共識）

本檔為 sp flow 階段 1 對話共識之濃縮，實作細節以 `plan.md` 為準。

| 議題 | 決議 |
|------|------|
| 範圍 | 第一版僅「停止」；暫停／繼續往後迭代 |
| 停止語意 | 盡快於安全邊界中止；最後一小段可不完整；已寫入檔案保留 |
| 再開新下載 | 必須等背景執行緒與 WebDriver 釋放後才允許新的 `start`（收尾前 `start` → 409） |
| 取消機制 | 建議 `threading.Event` 自 `web_app` 傳入 `run_download_from_dotenv` → `Downloader` |
| Stop API | `POST /api/download/stop`，body `{"job_id":"..."}`；須匹配 `_active_job_id`；否則 404；重複 stop 冪等 |
| 終止事件 | 新增 SSE / reporter 型別 **`run_cancelled`**（與 `run_finished`、`run_error` 同為串流結束點） |
| 前端 UX | **同一顆 `#btn-start`**：開始下載 → 停止 → 停止中… → 開始下載；i18n 補鍵 |
