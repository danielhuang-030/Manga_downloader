# Web UI：下載停止（合作式取消）實作計畫

> **給代理／實作者：** 建議依序執行下列 Task；每個 Task 內為 TDD 小步。完成後執行驗證指令並保留終端輸出作為 sp flow 階段 4 證據（見專案 `README.md`／`README.zh-TW.md` 之 pytest 說明）。

**Goal:** Web UI 下載進行中可「停止」；後端合作式取消＋`run_cancelled` 終止 SSE；主按鈕單鈕三態；收尾完成前不可再 `start`。

**Architecture:** `web_app` 每 job 建立 `threading.Event`，傳入 `run_download_from_dotenv` → `Downloader` 在迴圈邊界檢查；取消時拋出專用例外由 `download()` 統一發 `run_cancelled` 並 `driver.quit()`。`POST /api/download/stop` 只 set event，不阻塞等待 thread。

**Tech Stack:** Python 3、FastAPI、`threading`、`pytest`、`TestClient`、原生 `web_static/app.js` + `i18n.js`。

**測試驗證（專案根目錄，建議容器或本機已安裝依賴）：**

```bash
python -m pytest tests/test_download_runner.py tests/test_web_app.py -v
```

變更涉及下載核心時可擴大為：

```bash
python -m pytest tests/test_download_runner.py tests/test_web_app.py tests/test_main_env.py -v
```

---

### Task 1：`download_runner` 轉發 `cancel_event`（TDD）

**Files:**

- Modify: `download_runner.py`
- Modify: `tests/test_download_runner.py`

- [ ] **Step 1：寫失敗測試**

在 `tests/test_download_runner.py` 新增測試：mock 與現有測試類似，但呼叫：

```python
run_download_from_dotenv(progress_reporter=reporter, cancel_event=cancel_ev)
```

並斷言 `mock_dl.call_args.kwargs["cancel_event"] is cancel_ev`（`cancel_ev` 為 `threading.Event()`）。

- [ ] **Step 2：執行測試確認紅燈**

執行：`python -m pytest tests/test_download_runner.py -v`
**Expected:** FAIL（`TypeError` 或 kwargs 缺少 `cancel_event`）。

- [ ] **Step 3：最小實作**

修改 `run_download_from_dotenv` 簽名為：

```python
def run_download_from_dotenv(dotenv_path=None, progress_reporter=None, cancel_event=None):
```

在建立 `kwargs` 後加入：

```python
kwargs["cancel_event"] = cancel_event
```

- [ ] **Step 4：執行測試確認綠燈**

執行：`python -m pytest tests/test_download_runner.py -v`
**Expected:** PASS。

- [ ] **Step 5：commit**（訊息範例）`test(download_runner): forward cancel_event to Downloader`

---

### Task 2：`Downloader` 合作式取消（TDD）

**Files:**

- Modify: `downloader.py`
- Create: `tests/test_downloader_cancel.py`

**設計要點：**

- 在 `downloader.py` 模組層新增例外，例如：

```python
class DownloadCancelled(Exception):
    """Cooperative cancel requested (e.g. Web UI stop)."""
```

- `Downloader.__init__` 增加參數 `cancel_event=None`（預設 `None` 表示 CLI 不取消）。
- 新增方法 `_cancel_requested(self)`：若 `self._cancel_event` 為真且 `self._cancel_event.is_set()` 則回 `True`。
- 新增 `_check_cancel(self)`：若 `_cancel_requested()` 則 `raise DownloadCancelled()`。
- 在 `download()`：`run_started` 之後、每個外層迴圈迭代開始處呼叫 `_check_cancel()`。
- 在 `download_book()`：`for i in range(...)` **迴圈開頭**呼叫 `_check_cancel()`。
- `download_book` 的 `except Exception` 改為先：

```python
except DownloadCancelled:
    raise
```

再處理其他 `Exception`。
- 在 `download()` 最外層用 `try/except DownloadCancelled`：呼叫 `emit_progress(..., {"type": "run_cancelled", "ok": False})`，若 `getattr(self, "driver", None)` 存在則安全 `quit()`（可 `try/finally` 避免重複 quit），**不要**再送 `run_finished`。

- [ ] **Step 1：寫失敗測試**

新增 `tests/test_downloader_cancel.py`：使用 `unittest.mock` 建立 `Downloader` 實例時傳入 `cancel_event=threading.Event()`、`progress_reporter=list.append`（或收集用 list）、其餘參數用最小假值 **並** `patch.object(Downloader, "get_driver", lambda self: None)` **不可行**（後續會用到 driver）。改為 **`patch.object(Downloader, "download_book", side_effect=DownloadCancelled)`** 過於取巧。

**較務實單元測試：** 只測 **`_check_cancel` 行為** 與 **`download_book` 在 cancel 時拋出 `DownloadCancelled`**：

```python
import threading
import pytest
from unittest.mock import MagicMock, patch

from downloader import Downloader, DownloadCancelled


def test_check_cancel_raises_when_event_set():
    ev = threading.Event()
    ev.set()
    d = object.__new__(Downloader)
    d._cancel_event = ev
    with pytest.raises(DownloadCancelled):
        Downloader._check_cancel(d)  # 若實作成實例方法，改為 d._check_cancel()
```

依你實作調整呼叫方式（若 `_check_cancel` 為實例方法則建完整 `Downloader` 太難，可將邏輯抽成模組級函式 `_check_cancel_event(ev)` 再包一層 — **YAGNI**：優先保持方法在類別上，測試用 `__new__` 塞 `d._cancel_event` 即可）。

第二個測試：`patch` 掉 `download_book` 內部依賴過重時，改為測 **`download()`** 在 `cancel_event` 已 set 時於第一個 `_check_cancel` 送出 `run_cancelled`：

- `patch.object(Downloader, "get_driver")` 讓 `init_function` 不開真瀏覽器仍困難，因 `__init__` 呼叫 `init_function`。

**建議最小測試組合：**

1. `test_download_cancelled_emits_run_cancelled`：`MagicMock` 作 `progress_reporter`；手動建立已 `set()` 的 `Event`；用 `object.__new__` + 手動設定 `driver=MagicMock()`、`_progress_reporter`、`_cancel_event`、`_viewer_ids=["1"]`，並 mock `check_implementation`、`login`、`_download_one_viewer_id` 等 — 過重。

**簡化為兩個測試即可接受：**

- `test_check_cancel_raises_when_event_set`（如上）。
- `test_download_book_respects_cancel_first_iteration`：`patch` `emit_progress`、`WebsiteActions` 等成本過高時，**改在 Task 3 用 `web_app` 整合測試**覆蓋「取消信號會結束 thread 並送 `run_cancelled`」，本 Task 僅保留 `_check_cancel` 單元測試 + `download_runner` 已轉發。

若仍希望覆蓋 `download()`：可 `patch("downloader.emit_progress")`、`patch.object(Downloader, "get_driver")`、`patch.object(Downloader, "init_function", lambda self: None)` — 需在測試檔案內仔細 patch **`Downloader.__init__` 完成後**再替換 `get_driver` 已晚。**實務建議：** Task 2 實作 `Downloader` 邏輯 + `_check_cancel` 測試；**Task 3** 用 mock `run_download_from_dotenv` 驗證整鏈會呼叫且 SSE 出現 `run_cancelled`（見下）。

- [ ] **Step 2：紅燈** — `pytest tests/test_downloader_cancel.py -v` 預期 FAIL（例外類別或方法不存在）。

- [ ] **Step 3：實作** `downloader.py` 如上述要點（含 `manga_url` 分支迴圈邊界 `_check_cancel`）。

- [ ] **Step 4：綠燈** — `pytest tests/test_downloader_cancel.py -v` PASS。

- [ ] **Step 5：commit** `feat(downloader): cooperative cancel via cancel_event`

---

### Task 3：`web_app` — `POST /api/download/stop`、SSE、`run_cancelled`（TDD）

**Files:**

- Modify: `web_app.py`
- Modify: `tests/test_web_app.py`

**實作要點：**

- 模組層 `_job_cancel_events: dict[str, threading.Event] = {}`。
- 在 `api_download_start` 內建立 `cancel_ev = threading.Event()`，`_job_cancel_events[job_id] = cancel_ev`，`target()` 呼叫：

```python
run_download_from_dotenv(str(ENV_PATH), progress_reporter=reporter, cancel_event=cancel_ev)
```

- `finally` 內除清空 `_active_job_id` 外 `pop` 掉 `_job_cancel_events[job_id]`（若存在）。
- 新增 Pydantic body：

```python
class DownloadStopBody(BaseModel):
    job_id: str
```

- 新增 `@app.post("/api/download/stop")`：在 `_download_lock` 下讀取 `_active_job_id`；若與 `body.job_id` 不同或為 `None`，`HTTPException(404)`；取得 `_job_cancel_events.get(job_id)`，若無則仍 404；`cancel_ev.set()`；回 `{"ok": True}`。
- `api_download_stream` 的終止條件加入 `"run_cancelled"`。

**測試（mock `download_runner.run_download_from_dotenv`）：**

在呼叫 `client.post("/api/download/start")` **之前**：

```python
import threading
from unittest.mock import patch

barrier = threading.Barrier(2)

def fake_run(dotenv_path, progress_reporter=None, cancel_event=None):
    assert cancel_event is not None
    progress_reporter({"type": "run_started", "total_books": 1})
    barrier.wait()  # 測試主執緒同步點 1
    cancel_event.wait(timeout=5)
    progress_reporter({"type": "run_cancelled", "ok": False})

monkeypatch.setattr("download_runner.run_download_from_dotenv", fake_run)
```

流程：`POST /api/download/start` → 讀 `job_id` → 背景 thread 卡在 `barrier.wait()` → 主執緒 `barrier.wait()` → `POST /api/download/stop` with `job_id` → 第二個 `barrier` 或僅依 `cancel_event`：簡化為 `fake_run` 在 `run_started` 後 `progress_reporter` 已可讓測試用 **另一個 `threading.Event`** 通知「已進入 fake_run」。

**較簡單同步：** `fake_run` 第一行把 `cancel_event` 存到 `holder["ev"] = cancel_event`，然後 `started.set()`；測試 `assert started.wait(timeout=2)`；再 `POST stop`；`fake_run` 在 `cancel_event.wait` 返回後 emit `run_cancelled` 並結束；主執緒輪詢 `web_app._active_job_id is None` 或讀 SSE 直到 `run_cancelled`。

- [ ] **Step 1：寫 `test_api_download_stop_unknown_job`**：`POST /api/download/stop` body 隨機 uuid，預期 **404**（無 active job）。

- [ ] **Step 2：寫 `test_api_download_stop_triggers_cancel_and_releases_active`**：上述 mock 流程 + 斷言 stop 回 200、`holder["ev"].is_set()`、最終 `_active_job_id is None`（適度 `time.sleep` 輪詢）。

- [ ] **Step 3：寫 `test_sse_stream_ends_on_run_cancelled`**：`TestClient` `get(stream_url, stream=True)` 讀取直到 chunk 含 `run_cancelled` 或逾時失敗。

- [ ] **Step 4：紅燈** — `pytest tests/test_web_app.py -k stop -v` FAIL。

- [ ] **Step 5：實作** `web_app.py`。

- [ ] **Step 6：綠燈** — `pytest tests/test_web_app.py -v`。

- [ ] **Step 7：commit** `feat(web): download stop API and run_cancelled SSE`

---

### Task 4：前端 — 單鈕三態 + i18n

**Files:**

- Modify: `web_static/app.js`
- Modify: `web_static/i18n.js`
- Modify（若需無障礙文案）：`web_static/index.html`

**實作要點：**

- 以模組層變數保存目前 `jobId`、`eventSource` 參考、`isStopping`。
- `btn-start` click：若目前為「停止」模式（例如 `jobId` 非空且 SSE 開著且非 stopping）：`fetch("/api/download/stop", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({job_id: jobId}) })`；按鈕 `disabled`、文字 `t("download.stopping")`；錯誤時 `setMsg` 並恢復狀態（見 `prd`）。
- `start` 成功後：設定 `jobId`，按鈕文字改 `t("download.stop")`，`aria-busy` 等依現有風格。
- `applyDownloadProgressEvent`：新增 `run_cancelled` 分支 — 進度條顯示 `t("progress.cancelled")`（非 error 色）；關閉 ES、清空 `jobId`、還原按鈕文案 `t("download.start")`、移除 `disabled`。
- `run_finished` / `run_error` 路徑亦須關閉 ES、還原按鈕（與取消一致，避免重複 close）。

**i18n 鍵（`i18n.js` zh-Hant + en）：**

- `download.stop` — 「停止」 / `"Stop"`
- `download.stopping` — 「停止中…」 / `"Stopping…"`
- `progress.cancelled` — 「已停止下載」 / `"Download stopped"`

- [ ] **Step 1：手動 smoke**（文件記錄即可）：`python run_web_ui.py` 啟動 → 開始下載 → 停止 → 確認可再開。Agent 可略過若無顯示環境。

- [ ] **Step 2：commit** `feat(web-ui): single-button stop flow and i18n`

---

### Task 5：全量回歸與文件

- [ ] 執行：`python -m pytest tests/test_download_runner.py tests/test_web_app.py tests/test_downloader_cancel.py -v`（若 Task 2 檔名不同則調整）。
- [ ] 若 `README.zh-TW.md` 的 Web UI 段落需補「停止」一句話 — **僅在使用者要求或明顯缺漏時**更新；本計畫預設可不改 README。
- [ ] **commit** `chore: verify download stop tests`

---

## Self-review（計畫撰寫者自查）

| PRD 條目 | 對應 Task |
|----------|-----------|
| `cancel_event` 傳遞 | Task 1 |
| `Downloader` 邊界檢查、`run_cancelled`、driver quit | Task 2 |
| `POST /api/download/stop`、404、SSE 終止 | Task 3 |
| 單鈕、i18n | Task 4 |
| pytest 證據 | Task 1–5 |

**Placeholder 掃描：** 已避免 TBD；Task 2 測試策略若實作中發現 mock 過重，以 `test_downloader_cancel` 最小案例 + Task 3 整合測試為準，並在 commit 訊息註明。

---

## 執行方式建議

計畫檔路徑：`.trellis/tasks/04-12-web-ui-download-stop/plan.md`（已綁定 Trellis task）。

1. **Subagent-Driven**：每 Task 交給新代理，Task 之間跑 pytest 並對照輸出。
2. **Inline**：單一對話依 Task 1→5 實作，每完成一 Task 執行對應 `pytest`。

若要啟用 Trellis 注入內容：

```bash
python3 ./.trellis/scripts/task.py init-context .trellis/tasks/04-12-web-ui-download-stop fullstack
python3 ./.trellis/scripts/task.py start .trellis/tasks/04-12-web-ui-download-stop
```

---

## 總結修改內容（sp flow）

**目的：** Web UI 在下載進行中可「停止」；後端以 `threading.Event` 合作式取消；SSE 以 `run_cancelled` 結束；主按鈕單鈕三態（開始 → 停止 → 停止中… → 開始）；收尾完成前 `start` 仍回 409。

**變更檔案與行為對照：**

| 檔案 | 變更摘要 |
|------|-----------|
| `download_runner.py` | `run_download_from_dotenv(..., cancel_event=None)`，轉入 `Downloader` kwargs。 |
| `downloader.py` | 新增 `DownloadCancelled`；`cancel_event` 可選；`_check_cancel()` 於 `download()`／`download_book()` 迴圈邊界；取消時 `emit_progress(run_cancelled)` 並 `driver.quit()`；`download_book` 對 `DownloadCancelled` 再拋出。 |
| `web_app.py` | `_job_cancel_events`；`start` 建立並傳入 `cancel_event`；`finally` 清理；`POST /api/download/stop`（body `job_id`）；SSE 終止型別含 `run_cancelled`。 |
| `web_static/app.js` | `downloadUiPhase`／`downloadJobId`／`downloadEs`；單鈕 start/stop/stopping；終止事件關閉 ES 並還原 UI；`applyDownloadProgressEvent` 處理 `run_cancelled`。 |
| `web_static/i18n.js` | `download.stop`、`download.stopping`、`progress.cancelled`、`error.stop_failed`（中／英）。 |
| `web_static/index.html` | `#btn-start` 移除 `data-i18n`，改由 JS 控制文案（避免下載中切語系覆寫「停止」）。 |
| `tests/test_download_runner.py` | 斷言 `cancel_event` 轉發。 |
| `tests/test_downloader_cancel.py` | `_check_cancel` 於 event set 時拋出 `DownloadCancelled`。 |
| `tests/test_web_app.py` | stop 404、整合取消釋放 `_active_job_id`、SSE 遇 `run_cancelled` 結束。 |

**驗證結果（本機／工作區）：**

```text
python3 -m pytest tests/test_download_runner.py tests/test_web_app.py tests/test_downloader_cancel.py -v
# 13 passed（另有 .pytest_cache 權限警告可忽略或修正目錄權限）
```

**行為對照（驗收）：** PRD 中「停止後須等 thread 釋放才可再 start」「錯誤 job_id → 404」「`run_cancelled` 終止 SSE」「單鈕三態」已由測試與實作覆蓋；暫停／繼續未納入本輪。

---

## 修復影響檢查報告（check-report）

依「直接／間接／資料結構／風險」維度整理如下。

### 1. 直接影響

- **`run_download_from_dotenv`**
  - **呼叫端：** `web_app.api_download_start` 的執行緒（傳入 `cancel_event`）、`main_env.main`（不傳，維持 `None`）。
  - **相容性：** 新增可選參數 `cancel_event=None`，**不破壞**既有 CLI 呼叫。

- **`Downloader.__init__`**
  - **呼叫端：** `download_runner`、`main.py`（`Downloader(**settings)`）、`tests/test_downloader_helpers.py` 等。
  - **相容性：** `cancel_event=None` 預設；既有測試建構子無需改動。

- **`DownloadCancelled` / `_check_cancel` / `download()` 控制流**
  - 僅在 `cancel_event.is_set()` 時改變流程；未設 event 時與舊行為一致（除迴圈多幾次極輕量檢查）。

### 2. 間接影響

- **呼叫鏈：** Web → `run_download_from_dotenv` → `Downloader.download()`；取消時以 `run_cancelled` 事件經 queue → SSE → `app.js`，與既有 `run_finished`／`run_error` 對稱。
- **共用狀態：** `_active_job_id`、`_job_queues`、**新增** `_job_cancel_events`；寫入與 `start` 同鎖區間，執行緒 `finally` 清理；`stop` 僅 `set()` 事件，不與下載執行緒共用 queue 寫入邏輯，**競態風險低**。
- **前端事件：** `EventSource.onerror` 在連線異常時將 UI 重設為 `idle`（**Minor**：理論上與伺服器仍在收尾不同步；舊版亦未完整處理 SSE 斷線，屬已知邊界）。

### 3. 資料結構相容性

- **SSE / JSON 事件：** 新增枚舉值 **`type: "run_cancelled"`**；消費端僅 Web UI `app.js` 與後端串流 break 條件；**舊客戶端**若只認識 `run_finished`／`run_error`，需更新才能辨識「使用者停止」（本專案無其他正式客戶端）。
- **REST：** 新增 **`POST /api/download/stop`**，body `{"job_id": string}`；不影響既有路由。

### 4. 風險與建議

| 風險 | 嚴重度 | 建議 |
|------|--------|------|
| 長時間卡在 `WebDriverWait`／第三方 I/O 內，取消延遲 | 中 | 可後續在更多阻塞點前補 `_check_cancel`（非本 PRD 必須）。 |
| SSE 斷線與後端仍在跑 | 低 | 手動 smoke：斷網或重新整理後行為；必要時日後加「查詢 job 狀態」API。 |
| `.pytest_cache` 權限 | 低 | 修正 repo 內目錄權限或改 cache 路徑。 |

**結論：** 簽名向後相容；CLI 路徑不變；Web 與測試已對齊新契約；**可合併前提：** 上述 pytest 指令綠燈、必要時手動 Web smoke。

---

## Code review（requesting-code-review）

**對照：** `prd.md`、`design.md` 與本計畫 Task 1–4；diff 約 8 檔、+338 / −45 行（`git diff --stat`）。

### Strengths

- **測試覆蓋清楚：** `cancel_event` 轉發、stop 404、整合釋放 active job、SSE `run_cancelled`、`_check_cancel` 單元測試，與 PRD 對齊。
- **向後相容：** `cancel_event` 可選；`main_env` 無需改動。
- **鎖與生命週期：** `cancel_ev` 與 `_active_job_id` 在 `start` 同鎖內建立；`finally` 清理 `_job_cancel_events`，避免洩漏。
- **例外分流：** `download_book` 對 `DownloadCancelled` 再拋出，避免誤判為一般 `run_error`。

### Issues

| 嚴重度 | 說明 |
|--------|------|
| **Critical** | 無。 |
| **Important** | 無（若嚴格要求：可補一則「真 thread + 假 runner」測 stop 冪等連送兩次仍 200，屬加強而非缺失）。 |
| **Minor** | `EventSource.onerror` 一律重設 UI 為 `idle`，若僅瞬斷線可能與後端仍在跑短暫不一致（見 check-report）。 |
| **Minor** | README 未描述「停止」按鈕；文件可後續補一句（計畫 Task 5 已標為可選）。 |

### Assessment

**結論：可進入合併／收尾流程**（Critical／Important 無阻擋項）。建議合併前再跑一次：

`python3 -m pytest tests/test_download_runner.py tests/test_web_app.py tests/test_downloader_cancel.py -v`

若需嚴格「子代理審查」再跑一輪，可指定另一位審查者只對 `web_app.py` + `app.js` 做安全與競態複查。
