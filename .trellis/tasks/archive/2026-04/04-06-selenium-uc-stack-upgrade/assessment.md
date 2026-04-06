# 技術堆疊升級評估 — Manga_downloader

> **合併註記：** 本檔由原任務 `04-06-assess-tech-stack-upgrades`（研究／評估）合併至本目錄，與 [design.md](./design.md)、[prd.md](./prd.md) 一併為單一「堆疊升級」任務之依據。

**日期：** 2026-04-06  
**範圍：** 僅研究與建議（本任務不修改程式碼）。

---

## 1. 現況盤點

| 層級 | 版本／來源 | 在本專案中的角色 |
|------|------------|------------------|
| **Python** | 3.8（`Dockerfile` 之 `FROM python:3.8`） | CLI 執行環境、Selenium 編排、PIL 影像處理 |
| **undetected-chromedriver** | 3.5.5（`requirements.txt`） | 降低自動化偵測；`downloader.py` 使用 `uc.Chrome()`／`ChromeOptions` |
| **Selenium** | 4.18.1 | `WebDriverWait`、driver API、`execute_cdp_cmd` |
| **Pillow** | 9.2.0 | 解碼／裁切 canvas 來的 PNG、`ImageOps.invert`、動態裁切 |
| **requests** | 2.31.0 | 間接依賴（依賴樹）；非 `downloader.py` 核心 |
| **urllib3** | 1.26.16 | Selenium／requests 的 HTTP 堆疊；**為 1.x 系列** |
| **Chrome（容器內）** | 透過 Google apt 安裝 `google-chrome-stable`（`Dockerfile`） | 自動化使用的瀏覽器 |
| **Chromedriver（容器內）** | 自 `chromedriver.storage.googleapis.com` 下載 zip，並搭配 `LATEST_RELEASE`（`Dockerfile` 第 15–20 行） | 舊版下載路徑；可能與 **uc**／Selenium Manager 行為**重複或衝突** |
| **docker-compose** | 3.7（`docker-compose.yml`） | 掛載 `.` → `/app`，建置 `Dockerfile` |

**相關檔案：** `requirements.txt`、`Dockerfile`、`docker-compose.yml`、`downloader.py`、`website_actions/*`。

**備註：** `undetected_chromedriver` 常會自行解析或下載對應的 driver。映像檔**另外**安裝了全域 `chromedriver` 二進位檔，可能造成 **Chrome 與 driver 組建版本不一致**，或安裝冗餘。日後調整 `Dockerfile` 時，應**確認實際被 uc 使用的是哪一個**（PATH、Selenium Manager，或 uc 自行下載）。

---

## 2. Python：脫離 3.8

- **Python 3.8** 已達**官方終止支援（EOL）**，上游不再提供安全性修正。若執行環境仍長期使用此映像，屬**資安與供應鏈風險**。
- **建議目標版本（2026）：** **3.11** 或 **3.12**（穩定、wheel 支援廣）。若各套件 pin 皆有對應 wheel 且 CI／Docker 已驗證，**3.13** 亦可考慮。
- **可能阻礙：** 多為**鎖定的 wheel**（Pillow、若被拉入的 `cryptography` 等）— 請在目標 Python 的乾淨 venv 與 Docker build 中實際執行 `pip install -r requirements.txt` 驗證。
- **對程式碼影響：** 本專案以標準函式庫 + Selenium／PIL 為主，未見明顯僅支援 3.8 的語法。**測試重點：** import、`undetected_chromedriver` 與較新 Python 的相容性。

**建議：** 以**獨立 PR** 提升 base image 與依賴解析後的 pin；至少對一個 `website_actions` 站台跑**端到端下載**驗證。

---

## 3. Python 套件（主要 pin）

### undetected-chromedriver（3.5.5）

- **限制：** 專案**依賴 uc 的行為**（`uc.Chrome`、`ChromeOptions`、CDP 等）。升級須以**實際網站**驗證，不能只跑 import。
- **流程：** 在升級 Selenium／Chrome 前，查 [undetected-chromedriver 發布頁](https://github.com/ultrafunkamsterdam/undetected-chromedriver) 與 Chrome 主版本相容說明。

### Selenium（4.18.1）

- **4.x** 合適。較新 minor 可能對 W3C 行為較嚴格；本專案使用 `WebDriverWait`、`execute_cdp_cmd`、`add_cookie`，一般相對穩定。
- **Selenium Manager**（4.6+）：可自動取得 driver；與 **uc** 的互動**必須實測**（uc 並非官方 `webdriver.Chrome`）。

### Pillow（9.2.0）

- **安全性：** 舊版 Pillow 曾有 CVE；常見升級路徑為 **10.x／11.x**。請對照 [Pillow 發行說明](https://pillow.readthedocs.io/en/stable/releasenotes.html) 檢查移除的 API。
- **本專案用法：** `Image.open(BytesIO)`、`convert`、`crop`、`save`、`ImageOps.invert`、`getbbox` 等為常見 API；若有測試載入範例 PNG，破壞性變更風險較低。

### urllib3（1.26.x）+ requests（2.31.x）

- **urllib3 2.x** 含破壞性變更；**requests** 會限制相容的 urllib3 範圍。宜**透過**升級 `requests` 與解析後的依賴樹調整，**不要**單獨硬改 urllib3。
- **風險：** 若 Selenium 仍可啟動，對應用邏輯影響較低；**SSL／proxy** 邊角情境為**中等**風險—建議跑 smoke test。

### 傳遞依賴（trio、websockets 等）

- 由 Selenium 堆疊拉入。建議以 **`pip-compile` 或 `pip install` 解析結果**決定版本；除非 CVE 公告指定下限，避免手動逐行改版本。

---

## 4. Docker／Chrome／Chromedriver

### 目前 `Dockerfile` 的問題

1. **`apt-key add`（第 3 行）** — 已棄用；Debian／Ubuntu 建議改用 signed-by keyring。未來 base image 可能導致建置失敗。
2. **`chromedriver.storage.googleapis.com` + `LATEST_RELEASE`（第 15–18 行）** — 舊版 **ChromeDriver** 發佈方式。Google 已對新版 Chrome 改採 **Chrome for Testing** 等配置；舊端點對**目前 Chrome 主版本**可能**不穩定或已過時**。
3. **Chrome 與 driver 對齊** — `google-chrome-stable` 隨 Google 套件庫更新；獨立下載的 `LATEST_RELEASE` driver 可能與已安裝的 Chrome **主版本不符**，導致**連線／工作階段失敗**。
4. **`DISPLAY=:99`** — 暗示預期有 Xvfb 等；目前範例 `Dockerfile` 未安裝。程式使用 `--headless`；請確認執行環境下 `:99` 是否多餘或仍為必要。

### 替代作法（「現代化」至少須擇一評估）

| 作法 | 概念 | 優點 | 缺點 |
|------|------|------|------|
| **A. Chrome for Testing + 固定版本** | 自 [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/)（或 `storage.googleapis.com/chrome-for-testing-public/`）安裝**同一 build id** 的 Chrome + ChromeDriver | 可重現、符合 Google 建議配對 | Dockerfile 較長；版本須一併升級 |
| **B. 依賴 uc／Selenium 管理 driver** | 盡量減少手動安裝 chromedriver；維持單一來源 | 變因較少 | 須在 Linux 容器內確認 uc 行為；仍須 Chrome 本體版本合理 |
| **C. 現成 Selenium 映像** | 使用 `selenium/standalone-chrome` 等**僅在**仍能注入 **undetected-chromedriver**／自訂 Chrome 時—對 uc **多半無法**直接替換 | 維運常見 | 可能與 uc 的 patch 衝突；需 spike |

**建議：** 先做 **spike**，在 **A** 或 **B** 擇一驗證：建置一個容器，記錄 Chrome 版本、driver 版本，並確認 `uc.Chrome` 工作階段成功。

---

## 5. 風險排序（影響由低至高）

1. **低 — 文件／compose** — 說明 `docker-compose` 掛載、環境變數；不改執行期行為。
2. **低～中 — Pillow／requests／小版號 pin** — 安全性與修正；測試影像裁切路徑（`cut_image` 動態／靜態）。
3. **中 — Dockerfile 整備** — 移除已棄用的 apt key 用法；以 **Chrome for Testing** 配對**或**經驗證的 uc-only driver 策略對齊 Chrome + driver；**重建映像並跑完一次完整下載**。
4. **中～高 — Python 3.11／3.12** — 解析 wheel、跑完整下載 smoke test。
5. **高 — Selenium／uc／Chrome 大跳版** — `get_driver()` 內反偵測與 CDP 腳本可能需要調整；**每個** `website_actions` 模組都是迴歸風險點。

---

## 6. 升級後驗證清單

- [ ] 在目標環境執行：`python -c "import undetected_chromedriver, selenium"`。
- [ ] 啟動 driver：走 `Downloader` 路徑與 `--headless`（或實際使用的參數）。
- [ ] **至少兩個站台：** 例如一個 Bookwalker 系列 + `website_actions` 內另一個實作。
- [ ] 跑 **登入 + 多頁** 流程；留意 `download_book` 內 `WebDriverWait` 逾時。
- [ ] 失敗時，確認 `error.html`／`error.png` 行為仍正常。

---

## 7. 分階段升級路線圖

| 階段 | 內容 | 通過／暫停準則 |
|------|------|----------------|
| **0 — 基線** | 為目前可運作版本打 tag；在 README 或任務筆記記錄 Chrome／driver 版本 | 下載流程正常則可往下一階段 |
| **1 — 安全性 pin** | 在相容範圍內升級 Pillow／requests（連帶 urllib3）；若有公告再升 Selenium 小版 | `pip check` 無誤 + smoke test 通過則 **Go** |
| **2 — Dockerfile** | 移除已棄用 apt key；將舊 Chromedriver URL 改為 **Chrome for Testing** 配對**或**經驗證的 uc-only 策略 | 映像可建置且一條 E2E 通過則 **Go** |
| **3 — Python 升級** | 改用 `python:3.11` 或 `3.12-slim` 等並重裝依賴 | 所有 wheel 可安裝 + E2E 通過則 **Go** |
| **4 — Selenium／uc** | 閱讀 release notes 後謹慎升級 `undetected-chromedriver` 與 Selenium | **僅在**多站台 E2E 通過後 **Go** |

---

## 8. 選項：長期方向（本評估範圍外）

若 **undetected-chromedriver** 維護落後，或 Chrome 變更導致反偵測頻繁失效，可另開 **spike** 評估 **Playwright** 或 **patchright** 等方向。那將涉及大規模改寫 `downloader.py` 與各站 adapter，**不屬於本文件範圍**。

---

## 9. 實作時參考連結

- Chrome for Testing：https://googlechromelabs.github.io/chrome-for-testing/
- Selenium 官方文件：Selenium Manager（4.6+ driver 管理）
- undetected-chromedriver：https://github.com/ultrafunkamsterdam/undetected-chromedriver
