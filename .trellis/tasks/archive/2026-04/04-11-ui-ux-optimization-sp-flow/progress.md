# 實作進度 — 04-11-ui-ux-optimization-sp-flow

> 本檔記錄本 task **截至目前**（2026-04-11）已合入 repo 的變更，供對照 `prd.md`／`plan.md` 與後續 sp flow 收尾。

## 已完成（對照 plan Task 1–6）

| 區塊 | 說明 |
|------|------|
| **Task 1–2** | `manga_env`：`normalize_viewer_url_for_id_extraction`、`extract_viewer_id_from_url`（模板須恰一個 `{id}`）、`append_parsed_id_to_manga_ids`；`tests/test_manga_env.py`。 |
| **Task 3** | `web_app`：`POST /api/env/manga-id-from-url`（Pydantic body）、`download_runner` lazy import 以利輕量測試；`tests/test_web_app.py`（含 manga-id-from-url 三例）。 |
| **Task 4–5** | `web_static/index.html`：主題 `select`、`zh-Hant` 標籤、網址列與「從網址加入 ID」、Google Fonts；`app.js`：主題 `localStorage`、`fetch` API、`detailFromErrorBody`；`style.css`：主題變數、system、`prefers-reduced-motion`、表單版面。 |
| **Task 6** | `README.md`／`README.zh-TW.md`：Web UI 操作、Docker 擁有者、`compose.sh` 說明（後續補上，見下）。 |

## 實作後修正與延伸（同一 task 期間）

| 項目 | 檔案／行為 |
|------|------------|
| **POST `/api/...` 405** | `StaticFiles` 不可掛 `"/"`，改 `GET /` → `FileResponse(index.html)`、`mount("/static", …)`；`index.html` 資源改 `/static/...`；`GET /style.css`、`/app.js` → 301 舊快取；`test_get_root_serves_index`。 |
| **CSS 版面** | `style.css`：`html` 預設 CSS 變數後備、`#env-form` 直向 flex、`label` 直向 flex、`.paste-id-row` input `min-width:0`／`width:auto`；`theme-control label` `inline-flex`。 |
| **`.env` 擁有者** | `env_store.merge_write_dotenv`：`os.replace` 後 `os.chown` 還原原檔或父目錄 uid/gid；`tests/test_env_store.py`。 |
| **Cookie Latin-1** | `manga_env.coerce_http_cookie_header_latin1`；`check_bookwalker_cookie.py`：含非 Latin-1 時 **exit 2**（不靜默刪字）；`tests/test_check_bookwalker_cookie.py`。 |
| **Bookwalker 錯誤文案** | `website_actions/bookwalker_nfbr_wait.py`：`BookwalkerSessionError` 訊息改提 `.env`／`MANGA_COOKIES`。 |
| **Docker root 擁有** | `docker-compose.yml`：`python` 服務加上與 `web` 相同 `user: "${MANGA_WEB_UID:-0}:${MANGA_WEB_GID:-0}"`；註解範例。 |
| **自動 UID/GID** | 新增 `scripts/compose.sh`（`export MANGA_WEB_*` 自 `id`，有 `compose.env` 則帶入）；`scripts/docker-test.sh` 改經 `compose.sh`；README 補充。 |

## 測試（本機／Agent 曾跑）

- `pytest tests/test_manga_env.py tests/test_web_app.py tests/test_env_store.py tests/test_check_bookwalker_cookie.py -v`（建議；全專案 `tests/` 可能需容器內依賴如 `undetected_chromedriver`）。
- `./scripts/compose.sh config` 可確認 `user:` 已帶入主機 uid/gid。

## sp flow 收尾（2026-04-11）

### Verification（證據）

於專案根目錄執行：

`python3 -m pytest tests/test_manga_env.py tests/test_web_app.py tests/test_env_store.py tests/test_check_bookwalker_cookie.py -v --tb=no`

**結果：** 33 passed（約 0.30s）。另有 pytest cache 寫入權限警告（`Permission denied` 寫 `.pytest_cache`），不影響測試結論。

### check-report（影響面／風險）

| 區域 | 說明 |
|------|------|
| **Web 路由** | `GET /` 回傳 `index.html`、`/static/*` 掛靜態；舊書籤 `/style.css`、`/app.js` 301 至 `/static/...`。 |
| **Docker Compose** | `web`／`python` 皆設 `user:`；預設透過 `scripts/compose.sh` 帶入主機 uid/gid。若 CI 或環境未經 `compose.sh` 且需寫入 bind mount，應設 `MANGA_WEB_UID`／`MANGA_WEB_GID` 或 `compose.env`。 |
| **`.env` 寫入** | `merge_write_dotenv` 於 replace 後 `chown`；非 POSIX 或無權限時行為依 OS。 |
| **Cookie 檢查** | 含非 Latin-1 字元時 `check_bookwalker_cookie` **exit 2**，需使用者改貼 raw cookie。 |

### requesting-code-review（自檢摘要）

- PRD 選項 A（解析失敗／重複 ID）與 API／前端訊息對齊；`manga_env` 純函式有測試覆蓋。
- 靜態檔不佔 `POST /`；`test_get_root_serves_index` 防止迴歸。
- Docker 擁有者與 README／`compose.sh` 說明一致。

### Record Session

依 `AGENTS.md`：於**人類已提交**相關 commit 後，在本機執行 `.trellis/scripts/add_session.py`（含 `--commit`、非互動重導向）。本輪封存前若尚未提交，請補跑。

### 封存

已執行：`python3 ./.trellis/scripts/task.py archive 04-11-ui-ux-optimization-sp-flow --no-commit`  
歸檔路徑：`.trellis/tasks/archive/2026-04/04-11-ui-ux-optimization-sp-flow/`（`task.json` 已標 `completed`）。
