# Bookwalker TW `.env` 與 viewer ID 下載 — 實作計畫

> **給代理／實作者：** 建議依序執行下列任務；步驟使用 `- [ ]` 可勾選追蹤。若使用 subagent 逐任務實作，每任務結束請跑對應測試並檢視 diff。

**目標：** 以本機 `.env` 提供 `MANGA_COOKIES`、`MANGA_RES`（`WxH`）、`MANGA_SLEEP_TIME`、`MANGA_IDS`；依 `design.md` 將每個 viewer ID 下載至 `./downloads/<清理後書名>/`，並更新 `main.py`、`check_bookwalker_cookie.py`、測試與文件。

**架構：** 新增可測試之**純函式**模組（解析環境變數、標題→資料夾名）；新增 **`config` 載入層**（`load_dotenv` + 驗證）；**`Downloader`** 增加 `viewer_ids` 模式：每個 ID 組 URL、導覽、`before_download` 後讀取標題、建立目錄、再呼叫 `download_book`（避免重複 `before_download` 需調整方法簽名）。既有「`manga_url` + `imgdir` 列表」路徑保留供測試／進階用途。

**技術棧：** Python 3、`python-dotenv`、`pytest`、既有 Selenium / undetected-chromedriver 流程。

**準據文件：** [design.md](./design.md)

---

## 檔案對照（將建立／修改）

| 檔案 | 責任 |
|------|------|
| `requirements.txt` | 新增 `python-dotenv` 與鎖版（與現有風格一致）。 |
| `.env.example` | 範本變數、註解、優先順序說明（勿含真實 cookie）。 |
| `manga_env.py`（新建） | 解析 `MANGA_RES`、`MANGA_IDS`、合併 cookie 別名；`sanitize_download_folder_name(title, viewer_id)`。 |
| `config.py`（新建） | `load_manga_config()`：呼叫 `load_dotenv()`、讀 `os.environ`、回傳簡單資料結構（如 `namedtuple` 或小型 dataclass）。 |
| `downloader.py` | `Downloader.__init__` 支援 `viewer_ids=None`；驗證「列表模式」與「viewer 模式」二擇一；`download()` 分支；新私有方法處理單一 viewer ID；`download_book(..., skip_before_download=False)`。 |
| `main.py` | 僅載入設定、建立 `Downloader`、呼叫 `download()`。 |
| `check_bookwalker_cookie.py` | 啟動時 `load_dotenv()`；cookie 來源 `MANGA_COOKIES` / `BOOKWALKER_COOKIE`；無 `--url` 時用 `MANGA_IDS` 第一個 ID 組 URL。 |
| `tests/test_manga_env.py`（新建） | 純函式與解析之單元測試。 |
| `tests/test_downloader_helpers.py` | 視需要更新 mock 建構子呼叫（若 `__init__` 簽名變更）。 |
| `README.md`（若專案已有） | 簡短「複製 `.env.example` → `.env`」與變數說明（使用者若禁止改 README 可改為僅 `.env.example` 註解）。 |

---

### Task 1：依賴與 `.env.example`

**Files:**
- Modify: `/home/danielhuang030/projects/Manga_downloader/requirements.txt`
- Create: `/home/danielhuang030/projects/Manga_downloader/.env.example`

- [ ] **Step 1：加入依賴**

在 `requirements.txt` 新增一行（版本與專案其他套件一樣採 `==`）。安裝後以 `python3 -m pip freeze | grep dotenv` 確認實際版本並與 lockfile／同 repo 慣例一致；常見版本如 `python-dotenv==1.0.1`（若不符請改為當前 PyPI 穩定版）。

- [ ] **Step 2：建立 `.env.example`**

內容須含（繁中註解可）：

- 說明：**先複製為 `.env` 再填寫**；**勿提交**真實 cookie。
- 變數：`MANGA_COOKIES`、`MANGA_RES`、`MANGA_SLEEP_TIME`、`MANGA_IDS`。
- 選填說明：`BOOKWALKER_COOKIE` 為 `MANGA_COOKIES` 之別名（僅當前者未設定時生效）。
- 選填：`MANGA_HEADLESS`（見 `downloader.py` 既有行為）。
- **優先順序：** 已存在之**行程環境變數**優先於 `.env` 檔案。

- [ ] **Step 3：安裝並確認**

```bash
cd /home/danielhuang030/projects/Manga_downloader
pip install -r requirements.txt
python -c "from dotenv import load_dotenv; load_dotenv()"
```

預期：無例外。

- [ ] **Step 4：Commit**

```bash
git add requirements.txt .env.example
git commit -m "chore: add python-dotenv and .env.example for manga config"
```

---

### Task 2：`manga_env.py` 純函式 + 失敗測試（TDD）

**Files:**
- Create: `/home/danielhuang030/projects/Manga_downloader/manga_env.py`
- Create: `/home/danielhuang030/projects/Manga_downloader/tests/test_manga_env.py`

- [ ] **Step 1：撰寫測試（先紅燈）**

`tests/test_manga_env.py` 範例（可整段貼上後跑測試確認 **ImportError 或未定義**）：

```python
import pytest

from manga_env import (
    parse_manga_ids,
    parse_manga_res,
    resolve_cookie_header,
    sanitize_download_folder_name,
)


def test_parse_manga_res_valid():
    assert parse_manga_res("1445x2048") == (1445, 2048)


def test_parse_manga_res_invalid():
    with pytest.raises(ValueError):
        parse_manga_res("1445*2048")


def test_parse_manga_ids():
    assert parse_manga_ids("237928, 340012 ,,") == ["237928", "340012"]


def test_resolve_cookie_header_prefers_manga():
    env = {"MANGA_COOKIES": "a=1", "BOOKWALKER_COOKIE": "b=2"}
    assert resolve_cookie_header(env) == "a=1"


def test_resolve_cookie_header_fallback():
    env = {"BOOKWALKER_COOKIE": "b=2"}
    assert resolve_cookie_header(env) == "b=2"


def test_sanitize_pipe_segment():
    assert sanitize_download_folder_name("書名｜BOOK☆WALKER", "99") == "書名"


def test_sanitize_fallback_id():
    assert sanitize_download_folder_name("   ", "237928") == "browserViewer-237928"
```

執行：

```bash
cd /home/danielhuang030/projects/Manga_downloader
pytest tests/test_manga_env.py -v
```

預期：**全部失敗**（模組或函式不存在）。

- [ ] **Step 2：實作 `manga_env.py`（綠燈）**

必備行為：

- `parse_manga_res(s: str) -> tuple[int,int]`：僅允許 `^\d+x\d+$`（小寫 `x`），否則 `ValueError`。
- `parse_manga_ids(s: str) -> list[str]`：逗號分割、strip、捨棄空字串；**不**強制數字格式於此層（或若設計要拒絕非數字，測試需同步加案例）。
- `resolve_cookie_header(env: dict) -> str`：`env.get("MANGA_COOKIES")` 非空則用之，否則 `env.get("BOOKWALKER_COOKIE","")` strip。
- `sanitize_download_folder_name(raw_title: str, viewer_id: str) -> str`：依 `design.md` 4.2（strip、`|`/`｜` 取首段、替換 `\ / : * ? " < > |` 等為 `_`、合併重複底線、空或 `.`/`..` → `browserViewer-{viewer_id}`）。`viewer_id` 以字串傳入以保留前導零（若有）。

Python 3.9+ 可用 `tuple[int,int]`；若專案最低版本較舊則改 `Tuple[int, int]` 並 `from typing import Tuple`。

- [ ] **Step 3：跑測試**

```bash
pytest tests/test_manga_env.py -v
```

預期：**全部 PASS**。

- [ ] **Step 4：Commit**

```bash
git add manga_env.py tests/test_manga_env.py
git commit -m "feat: add manga_env parsing and folder name sanitization"
```

---

### Task 3：`config.py` 載入與測試

**Files:**
- Create: `/home/danielhuang030/projects/Manga_downloader/config.py`
- Create: `/home/danielhuang030/projects/Manga_downloader/tests/test_config.py`

- [ ] **Step 1：測試 `load_manga_config` 使用隔離環境**

在 `tests/test_config.py` 中撰寫：

```python
def test_load_manga_config_from_environ(monkeypatch, tmp_path):
    monkeypatch.delenv("MANGA_COOKIES", raising=False)
    monkeypatch.delenv("BOOKWALKER_COOKIE", raising=False)
    monkeypatch.setenv("MANGA_COOKIES", "a=b")
    monkeypatch.setenv("MANGA_RES", "800x600")
    monkeypatch.setenv("MANGA_SLEEP_TIME", "1.5")
    monkeypatch.setenv("MANGA_IDS", "1,2")
    from config import load_manga_config

    cfg = load_manga_config(dotenv_path=None)
    assert cfg.cookies == "a=b"
    assert cfg.res == (800, 600)
    assert cfg.sleep_time == 1.5
    assert cfg.viewer_ids == ["1", "2"]
```

`load_manga_config(dotenv_path=None)` 實作時：若 `dotenv_path is None`，呼叫 `load_dotenv()` 無參數（專案根搜尋）；測試僅依賴 `monkeypatch.setenv`，**不**需真實 `.env` 檔。

- [ ] **Step 2：實作 `config.py`**

- `from dotenv import load_dotenv`
- `load_manga_config(dotenv_path=None)`：
  - 呼叫 `load_dotenv(dotenv_path)`（`dotenv_path` 為 `None` 時不傳或維持預設行為依 `python-dotenv` 慣例）。
  - 讀取 `os.environ`：`MANGA_COOKIES`/`BOOKWALKER_COOKIE` 經 `resolve_cookie_header`；`MANGA_RES` → `parse_manga_res`；`MANGA_SLEEP_TIME` → `float`；`MANGA_IDS` → `parse_manga_ids`。
  - 缺任一必填：**明確** `ValueError` 訊息（指出缺哪個鍵）。
- 回傳型別：可用 `typing.NamedTuple` 名稱如 `MangaConfig`，欄位：`cookies`, `res`, `sleep_time`, `viewer_ids`。

- [ ] **Step 3：pytest**

```bash
pytest tests/test_manga_env.py tests/test_config.py -v
```

預期：全部 PASS。

- [ ] **Step 4：Commit**

```bash
git add config.py tests/
git commit -m "feat: add load_manga_config with dotenv"
```

---

### Task 4：`downloader.py` — viewer ID 模式與 `download_book` 旗標

**Files:**
- Modify: `/home/danielhuang030/projects/Manga_downloader/downloader.py`

- [ ] **Step 1：`Downloader.__init__` 簽名**

新增可選參數 `viewer_ids=None`（型別 `Optional[list]`，元素為字串 ID）。

驗證邏輯：

- 若 `viewer_ids` 為非空列表：**忽略**或不要求 `manga_url`/`imgdir` 長度一致（建議：內部存 `self._viewer_ids = list(viewer_ids)`，並將 `self.manga_url`/`self.imgdir` 設為空列表以避免誤用）。
- 若 `viewer_ids` 為 `None` 或空：維持現有行為，`len(manga_url)==len(self.imgdir)` 且 >0。

- [ ] **Step 2：常數**

在模組層級定義：

```python
BOOKWALKER_TW_BROWSER_VIEWER_READ = (
    "https://www.bookwalker.com.tw/browserViewer/{id}/read"
)
```

- [ ] **Step 3：`download_book` 簽名**

改為：

```python
def download_book(self, this_image_dir, skip_before_download=False):
```

當 `skip_before_download` 為 `True` 時，**跳過**開頭的 `self.actions_class.before_download(driver)`（其餘邏輯不變）。既有呼叫處傳入預設 `False`。

- [ ] **Step 4：viewer 模式迴圈（概念偽碼，實作時需對齊專案縮排與 logging）**

對每個 `viewer_id`：

1. `url = BOOKWALKER_TW_BROWSER_VIEWER_READ.format(id=viewer_id)`
2. `self.check_implementation(url)`
3. 僅第一次迭代：`self.login()`
4. `driver.get(url)`
5. `time.sleep(self.loading_wait_time)`
6. `self.actions_class.before_download(driver)`（等待 NFBR，與 `design.md` 一致：標題在讀者初始化後較可靠）
7. `raw = driver.title`（若空字串可選 `driver.execute_script("return document.title")` 同值）
8. `folder = sanitize_download_folder_name(raw, viewer_id)`（自 `manga_env` import）
9. `this_image_dir = os.path.join("downloads", folder)`（必要時 `os.makedirs(..., exist_ok=True)`）
10. `self.download_book(this_image_dir, skip_before_download=True)`
11. 書與書之間保留短暫 `time.sleep(2)`（與現有迴圈一致）

- [ ] **Step 5：`download()` 分支**

```python
def download(self):
    if self._viewer_ids:
        for i, vid in enumerate(self._viewer_ids):
            ...  # 上述步驟
        self.driver.close()
        self.driver.quit()
        return
    # 原有 manga_url / imgdir 迴圈
```

- [ ] **Step 6：手動煙測（選做，需真實 cookie 與 Chrome）**

不列入 CI；本機執行 `python main.py`（於 Task 5 完成後）。

- [ ] **Step 7：Commit**

```bash
git add downloader.py
git commit -m "feat(downloader): support Bookwalker TW viewer_ids download mode"
```

---

### Task 5：`main.py`

**Files:**
- Modify: `/home/danielhuang030/projects/Manga_downloader/main.py`

- [ ] **Step 1：內容改為**

```python
from config import load_manga_config
from downloader import Downloader


def main():
    cfg = load_manga_config()
    downloader = Downloader(
        manga_url=[],
        imgdir=[],
        cookies=cfg.cookies,
        res=cfg.res,
        sleep_time=cfg.sleep_time,
        viewer_ids=cfg.viewer_ids,
    )
    downloader.download()


if __name__ == "__main__":
    main()
```

若 `Downloader` 建構子在 viewer 模式下允許省略 `manga_url`/`imgdir`，可改為僅傳 `viewer_ids` 與必要欄位（以 Task 4 最終簽名為準）。

- [ ] **Step 2：Commit**

```bash
git add main.py
git commit -m "feat: wire main.py to env-based viewer ID config"
```

---

### Task 6：`check_bookwalker_cookie.py`

**Files:**
- Modify: `/home/danielhuang030/projects/Manga_downloader/check_bookwalker_cookie.py`

- [ ] **Step 1：`main()` 開頭** `from dotenv import load_dotenv` 並 `load_dotenv()`。

- [ ] **Step 2：`_load_cookie` 或等效邏輯**在未指定 `--cookie`/`--cookie-file` 時：

  - 先 `resolve_cookie_header(os.environ)`（自 `manga_env`）。

- [ ] **Step 3：無 `--url` 且未 `--from-main` 時**預設 URL：

  - 自 `parse_manga_ids(os.environ.get("MANGA_IDS",""))` 取第一個 ID，組 `https://www.bookwalker.com.tw/browserViewer/{id}/read`；若無 ID 則維持現有 `parser.error`。

- [ ] **Step 4：更新模組頂部 docstring**（繁中）：說明優先使用 `.env` 與 `MANGA_COOKIES`／`BOOKWALKER_COOKIE`。

- [ ] **Step 5：Commit**

```bash
git add check_bookwalker_cookie.py
git commit -m "feat: load cookies and default URL from env for cookie check CLI"
```

---

### Task 7：修正既有測試與全量 pytest

**Files:**
- Modify: `/home/danielhuang030/projects/Manga_downloader/tests/test_downloader_helpers.py`（若 `Downloader(...)` 必傳新參數）

- [ ] **Step 1：**

```bash
cd /home/danielhuang030/projects/Manga_downloader
pytest -q
```

- [ ] **Step 2：** 對每個失敗：補上 `viewer_ids=None` 或依新簽名調整 mock。

- [ ] **Step 3：Commit**

```bash
git add tests/
git commit -m "test: adjust Downloader tests for viewer_ids parameter"
```

---

### Task 8：文件

**Files:**
- Modify: `/home/danielhuang030/projects/Manga_downloader/README.md`（若存在且專案允許）

- [ ] **Step 1：** 新增簡短章節：複製 `.env.example`、填入四個必填變數、`MANGA_IDS` 範例。

- [ ] **Step 2：Commit**

```bash
git add README.md
git commit -m "docs: document .env setup for viewer ID downloads"
```

---

## 自我檢查（對照 design.md）

| design 章節 | 對應任務 |
|-------------|----------|
| 2 環境變數約定 | Task 1、3 |
| 3 URL / ID | Task 4 常數 + Task 6 |
| 4 標題與清理 | Task 2 + Task 4 步驟 7–8 |
| 5 控制流程 | Task 4、5 |
| 6 cookie CLI | Task 6 |
| 7 測試 | Task 2、3、7 |
| 8 依賴 | Task 1 |
| 9 文件 | Task 1、8 |

**占位檢查：** 本計畫不含未填之 TBD；實作時若 Bookwalker 頁面 `document.title` 恒為空，再在 Task 4 增 **備援 selector**（單一註解說明），並補單元測試 mock `driver.title`。

---

## 交付後執行方式

計畫檔路徑：`/home/danielhuang030/projects/Manga_downloader/.trellis/tasks/04-06-env-settings/plan.md`

**執行選項：**

1. **Subagent 驅動（建議）** — 每個 Task 交給獨立 subagent，完成後檢視 diff 與測試。  
2. **同會話逐步實作** — 依 Task 1→8 順序在同一對話實作，每 Task 結束跑 `pytest`。

若要開始實作，建議從 **Task 1** 起；需我直接在 repo 套用變更時，請說「實作 Task N」或「全部實作」。
