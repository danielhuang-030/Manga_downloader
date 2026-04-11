# Web UI／UX 與網址解析 MANGA_ID — Implementation Plan

> **狀態（2026-04-11）：** Task 1–6 與延伸修正皆已完成；**sp flow 收尾**已記入 **`progress.md`**（含 verification 33 passed、check-report、自檢 code review、封存路徑說明）。**Record Session** 請於 commit 後依 `AGENTS.md` 補跑 `add_session.py`。
>
> **For agentic workers:** 建議依序完成下列 checkbox；每個 Task 內先 **紅燈測試** 再實作（sp flow + TDD）。驗證指令與證據依本 repo 慣例由實作者執行並保留輸出。
>
> **Trellis 路徑說明：** 本計畫存於 task 目錄（`superpowers-trellis-integration.md` 要求），**不**寫入 `docs/superpowers/plans/`。
>
> **設計依據：** `prd.md`（含 `frontend-design` skill：`~/.cursor/skills/frontend-design/SKILL.md`）。

**Goal:** 強化本機 Web UI 的視覺與主題切換（淺／深／跟隨系統）、表單正體中文標籤；並支援貼上 viewer 網址後依 `MANGA_VIEWER_URL_TEMPLATE` 解析數字 ID、合併至 `MANGA_IDS`，解析失敗或重複 ID 時依 PRD 選項 **A** 顯示訊息。

**Architecture:** 網址→ID 與清單合併放在 **`manga_env.py` 純函式**（單元測試）；FastAPI 新增 **JSON API** 供前端呼叫；靜態 **`index.html` / `style.css` / `app.js`** 負責主題、表單標籤、訊息區與呼叫 API。視覺 token 以 **`style.css` 的 `:root` / `[data-theme]`** 管理。

**Tech Stack:** Python 3、FastAPI、Starlette TestClient、`manga_env`、`pytest`、原生 HTML/CSS/JS（無前端框架）。

**測試執行（專案根目錄）：** 安裝依賴後執行 `pytest tests/test_manga_env.py tests/test_web_app.py -v`；變更後應全綠。Agent 於使用者環境執行並自行對照輸出（見 `AGENTS.md` 測試相關約定）。

---

## 檔案對照（預計變更）

| 檔案 | 責任 |
|------|------|
| `manga_env.py` | 新增：URL 正規化、`extract_viewer_id_from_url`、`append_parsed_id_to_manga_ids`（或等價命名） |
| `tests/test_manga_env.py` | 上述行為之單元測試（含成功、查詢字串剥离、不匹配、重複） |
| `web_app.py` | 新增 `POST` API：接收 `url`、可選 `MANGA_VIEWER_URL_TEMPLATE`、目前 `MANGA_IDS`；回傳合併結果與狀態 |
| `tests/test_web_app.py` | API 契約測試（400／200 duplicate／200 appended） |
| `web_static/index.html` | 中文標籤、主題切換 UI、viewer 網址列與「從網址加入 ID」按鈕；可選 `link` 載入 webfonts |
| `web_static/style.css` | 淺／深／system 主題變數、版面、`prefers-reduced-motion`、focus 可見、避免泛用「紫白漸層臉」 |
| `web_static/app.js` | 主題持久化（`localStorage`）、API 串接、訊息寫入 `#env-msg`（錯誤 class、非錯誤提示） |
| `README.md` / `README.zh-TW.md` | 簡短補充 Web UI 新操作（若維護者需要） |

---

### Task 1: `extract_viewer_id_from_url`（紅→綠）

**Files:** 修改 `manga_env.py`；測試 `tests/test_manga_env.py`

- [ ] **Step 1: 寫失敗測試**

新增測試（範例行為，實作時可微調函式名稱但需覆蓋同語意）：

```python
from manga_env import extract_viewer_id_from_url, parse_viewer_url_template


def test_extract_viewer_id_default_template():
    tpl = parse_viewer_url_template("")
    url = "https://www.bookwalker.com.tw/browserViewer/237928/read"
    assert extract_viewer_id_from_url(url, tpl) == "237928"


def test_extract_viewer_id_strips_query_before_match():
    tpl = parse_viewer_url_template("")
    url = "https://www.bookwalker.com.tw/browserViewer/237928/read?ref=1"
    assert extract_viewer_id_from_url(url, tpl) == "237928"


def test_extract_viewer_id_custom_template():
    tpl = parse_viewer_url_template("https://example.com/v/{id}/end")
    assert extract_viewer_id_from_url("https://example.com/v/42/end", tpl) == "42"


def test_extract_viewer_id_no_match():
    tpl = parse_viewer_url_template("https://example.com/v/{id}/end")
    assert extract_viewer_id_from_url("https://evil.com/other", tpl) is None
```

執行：`pytest tests/test_manga_env.py -k extract_viewer -v`  
**Expected:** 失敗（未定義函式或 assert 失敗）。

- [ ] **Step 2: 實作最小邏輯**

在 `manga_env.py`：

1. 新增 `normalize_viewer_url_for_id_extraction(url: str) -> str`：strip、`urldefrag` 去 fragment、`urlparse` 後 **捨去 query**（`urlunparse` 僅保留 scheme、netloc、path），避免 `?` 造成模板比對失敗。
2. 新增 `extract_viewer_id_from_url(url: str, template: str) -> str | None`：  
   - 使用已驗證的 `template`（呼叫端傳入 `parse_viewer_url_template(...)` 之結果）。  
   - 將 `template` 以 **`{id}` 恰出現一次** 為前提拆成 `prefix` + `suffix`（若未來需支援多占位，另開 task；本 plan 僅處理單一 `{id}`）。  
   - 組合 regex：`^` + `re.escape(prefix)` + `(\d+)` + `re.escape(suffix)` + `$`，對**正規化後**的 URL 字串做 `re.match`；成功則回傳 `group(1)`，否則 `None`。

執行：`pytest tests/test_manga_env.py -k extract_viewer -v`  
**Expected:** PASS。

- [ ] **Step 3: Commit（人類或本機）**  
  訊息範例：`test(manga_env): add extract_viewer_id_from_url` → `feat(manga_env): extract viewer id from url using template`

---

### Task 2: `append_parsed_id_to_manga_ids`（紅→綠）

**Files:** 修改 `manga_env.py`；測試 `tests/test_manga_env.py`

- [ ] **Step 1: 寫失敗測試**

```python
from manga_env import append_parsed_id_to_manga_ids


def test_append_id_appends_and_normalizes_commas():
    new_csv, status = append_parsed_id_to_manga_ids("10, 20", "99")
    assert status == "appended"
    assert new_csv == "10,20,99"


def test_append_id_duplicate():
    new_csv, status = append_parsed_id_to_manga_ids("10,20", "20")
    assert status == "duplicate"
    assert new_csv == "10,20"
```

執行：`pytest tests/test_manga_env.py -k append_parsed -v` → **Expected:** FAIL。

- [ ] **Step 2: 實作**

`append_parsed_id_to_manga_ids(manga_ids_csv: str, parsed_id: str) -> tuple[str, Literal["appended", "duplicate"]]`：

- 以 `parse_manga_ids` 取得清單；若 `parsed_id` 已存在（字串完全相等比對）→ 回傳**原始**逗號字串（或規範化後 `",".join(ids)` 擇一，但 duplicate 時內容須與「未新增」一致）、`"duplicate"`。
- 否則 append 後 `",".join(ids)`、`"appended"`。

執行：`pytest tests/test_manga_env.py -k append_parsed -v` → **Expected:** PASS。

---

### Task 3: FastAPI `POST /api/env/manga-id-from-url`

**Files:** 修改 `web_app.py`；測試 `tests/test_web_app.py`

- [ ] **Step 1: 寫失敗測試**

使用 `TestClient`，`monkeypatch` `ENV_PATH` 仍可用現有 `_write_minimal_env`。

```python
def test_manga_id_from_url_appended(tmp_path, monkeypatch):
    import web_app
    monkeypatch.setattr(web_app, "ENV_PATH", tmp_path / ".env")
    _write_minimal_env(tmp_path / ".env")
    client = TestClient(web_app.app)
    body = {
        "url": "https://www.bookwalker.com.tw/browserViewer/999/read",
        "MANGA_IDS": "1",
        "MANGA_VIEWER_URL_TEMPLATE": "",
    }
    r = client.post("/api/env/manga-id-from-url", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["result"] == "appended"
    assert data["manga_ids"] == "1,999"
    assert data["parsed_id"] == "999"


def test_manga_id_from_url_duplicate(tmp_path, monkeypatch):
    import web_app
    monkeypatch.setattr(web_app, "ENV_PATH", tmp_path / ".env")
    _write_minimal_env(tmp_path / ".env")
    client = TestClient(web_app.app)
    body = {
        "url": "https://www.bookwalker.com.tw/browserViewer/1/read",
        "MANGA_IDS": "1",
        "MANGA_VIEWER_URL_TEMPLATE": "",
    }
    r = client.post("/api/env/manga-id-from-url", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["result"] == "duplicate"
    assert data["manga_ids"] == "1"


def test_manga_id_from_url_bad_url(tmp_path, monkeypatch):
    import web_app
    monkeypatch.setattr(web_app, "ENV_PATH", tmp_path / ".env")
    _write_minimal_env(tmp_path / ".env")
    client = TestClient(web_app.app)
    r = client.post(
        "/api/env/manga-id-from-url",
        json={"url": "https://wrong.example/nope", "MANGA_IDS": "1", "MANGA_VIEWER_URL_TEMPLATE": ""},
    )
    assert r.status_code == 400
```

執行：`pytest tests/test_web_app.py -k manga_id_from_url -v` → **Expected:** FAIL（無路由）。

- [ ] **Step 2: 實作路由**

- Body：`url`（必填）、`MANGA_IDS`（必填字串，可空）、`MANGA_VIEWER_URL_TEMPLATE`（選填，空則用 `parse_viewer_url_template(None)`）。
- 流程：`tpl = parse_viewer_url_template(body.get(...))` → `pid = extract_viewer_id_from_url(url, tpl)` → 若 `None`：`HTTPException(400, detail=...)`（正體中文訊息，例如「無法從網址解析出 viewer ID，請確認網址與網址模板是否一致」）。
- 否則：`new_csv, st = append_parsed_id_to_manga_ids(manga_ids, pid)`  
  - `st == "appended"`：`result: "appended"`，可選 `message_zh` 成功提示。  
  - `st == "duplicate"`：`result: "duplicate"`，`message_zh` 提示「清單已包含此 ID，未變更」。  
- **不**在此 API 內寫入 `.env`（僅回傳合併後字串供前端填入表單）；使用者仍按「儲存」寫檔。若你希望「一鍵寫入 .env」可另開 task。

執行：`pytest tests/test_web_app.py -k manga_id_from_url -v` → **Expected:** PASS。

---

### Task 4: 靜態頁 — 正體中文標籤、網址列、主題切換（結構）

**Files:** `web_static/index.html`、`web_static/app.js`（初版行為可與 Task 5 分開 commit）

- [ ] **Step 1: 更新 `index.html`**
  - `<head>`：加入主題切換用控制項占位（例：`header` 內 `select#theme-select`：淺色／深色／跟隨系統）。
  - 表單：每個 `label` 改為 **正體中文** + **括號內英文鍵名**（與 PRD 範例一致），例如：  
    - `Cookie（MANGA_COOKIES）`  
    - `備用 Cookie（BOOKWALKER_COOKIE）`  
    - `視窗解析度 WxH（MANGA_RES）`  
    - `翻頁間隔秒數（MANGA_SLEEP_TIME）`  
    - `漫畫 ID 清單（MANGA_IDS）`  
    - `Viewer 網址模板（MANGA_VIEWER_URL_TEMPLATE）`  
    - `Headless 模式（MANGA_HEADLESS）`  
  - 在 `MANGA_IDS` 附近新增：`input#viewer-url-paste`（placeholder：貼上完整 viewer 網址）+ `button#btn-append-id`（例：從網址加入 ID）。

- [ ] **Step 2: `app.js` — 主題**
  - 讀取／寫入 `localStorage` 鍵（例：`manga_web_theme`）：`light` | `dark` | `system`。  
  - 變更時設定 `document.documentElement.dataset.theme`。  
  - 初次載入套用儲存值。

- [ ] **Step 3: `app.js` — 從網址加入 ID**
  - `click` `#btn-append-id`：讀取網址輸入、`MANGA_IDS`、表單內 `MANGA_VIEWER_URL_TEMPLATE`，`POST /api/env/manga-id-from-url`。  
  - `appended`：把回傳的 `manga_ids` 寫回 `MANGA_IDS` 欄位、`#env-msg` 成功訊息（非 error class）。  
  - `duplicate`：**不**改 `MANGA_IDS`，`#env-msg` 顯示提示（非 error class）。  
  - `400`：`#env-msg` error class + `detail`。  
  - 成功加入後可選：清空網址輸入框。

手動驗證：`python run_web_ui.py` 後於瀏覽器操作（本計畫不要求自動化 E2E）。

---

### Task 5: `style.css` — 主題變數與 `frontend-design` 視覺

**Files:** `web_static/style.css`；必要時微調 `index.html` 的 class

- [ ] **Step 1: 變數與 `data-theme`**
  - `:root` 或 `html[data-theme="light"]` / `html[data-theme="dark"]` 定義 **背景、表面、邊界、文字、主色、focus ring**。  
  - `html[data-theme="system"]`：以 `@media (prefers-color-scheme: dark)` 與 `light` 兩段套用對應 token（與 PRD「淺／深／跟隨系統」一致）。

- [ ] **Step 2: 字體與質感（`frontend-design`）**
  - 於 `index.html` 以 `link` 引入 **非 Inter／Roboto／Arial** 的字體組（例：標題用 *Fraunces* 或 *Playfair Display*，內文用 *Source Sans 3* 或 *IBM Plex Sans* — 擇一組合並在計畫實作中固定下來）。  
  - `body` 使用 `font-family` 堆疊，保留合理 fallback（仍避免把 Inter 放第一順位）。

- [ ] **Step 3: 元件與動效**
  - `.panel`、按鈕、input focus 可見；主按鈕用主色。  
  - `@media (prefers-reduced-motion: reduce)` 內關閉非必要 transition／animation。

- [ ] **Step 4: 可選小型迴歸**  
  `pytest tests/test_web_app.py -v` 確保 API 測試仍通過。

---

### Task 6: 文件與自我檢查

- [ ] **Step 1:** 更新 `README.zh-TW.md`（與 `README.md` 若需英文對照）中 Web UI 小節：主題切換、從網址加入 ID、儲存仍寫入 `.env`。
- [ ] **Step 2:** 對照 `prd.md` **Acceptance Criteria** 逐項勾選；補遺漏測試。
- [ ] **Step 3:** 全量 `pytest`（或專案慣用之測試指令）並保留終端輸出作為 sp flow 階段 4 證據。

---

## 總結修改內容（實作完成後填寫）

- **變更檔案列表：** 見 **`progress.md`**（含 `manga_env`、`web_app`、`web_static`、`env_store`、`check_bookwalker_cookie`、`bookwalker_nfbr_wait`、`docker-compose`、`scripts/compose.sh`、`scripts/docker-test.sh`、`README*`、相關 `tests/*`）。
- **行為對照：** Web UI 主題（淺／深／系統）、正體中文標籤＋鍵名、網址→ID 經 API 合併至表單 `MANGA_IDS`、解析失敗／重複之訊息（PRD 選項 A）；靜態改 `/static` 避免 API POST 405；Cookie 檢查遇非 Latin-1 字元 exit 2；`.env` 寫入後嘗試還原擁有者；Docker `python`/`web` 可經 `MANGA_WEB_*` 或 **`./scripts/compose.sh`** 對齊主機 uid/gid。
- **驗證：** 建議 `pytest tests/test_manga_env.py tests/test_web_app.py tests/test_env_store.py tests/test_check_bookwalker_cookie.py -v`；手動：`./scripts/compose.sh up web` 或本機 `python run_web_ui.py` 驗 UI／儲存／從網址加入 ID。

---

## Self-review（對照 `prd.md`）

| PRD 要點 | 涵蓋 Task |
|----------|-----------|
| 主題淺／深／跟隨系統 | Task 4–5 |
| `frontend-design` 質感 | Task 5 + 實作時必讀 skill |
| URL→ID 併入 `MANGA_IDS` | Task 1–4 |
| 中文標籤＋鍵名 | Task 4 |
| 解析失敗／重複訊息（A） | Task 3–4 |

---

## 執行方式（選擇）

1. **Subagent-driven**：每 Task 交子代理實作，Task 間人工或自動複查。（本 task 已採此路徑完成實作。）  
2. **Inline**：於單一 session 依序執行 Task 1→6，每完成一 Task 跑對應 `pytest`。

---

## Docker 建議指令（擁有者）

```bash
./scripts/compose.sh run --rm python python main_env.py
./scripts/compose.sh up web
```
