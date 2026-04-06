# 升級細節（brainstorming 定案稿）

**任務：** `04-06-selenium-uc-stack-upgrade`  
**依據：** [assessment.md](./assessment.md)、[design.md](./design.md)  
**日期：** 2026-04-06  
**狀態：** 已定案 — 實作前若環境驗證與本文衝突，僅得調整「備援路徑」並更新本檔。

---

## 1. 仍維持的總體原則

- 架構：**Selenium 4.x + undetected-chromedriver**，不遷 Playwright／patchright。
- 驗證：**端到端下載**優先於僅 import；至少 **兩個** `website_actions` 站台（登入 + 多頁）。
- 交付：**分階段、可回滾**（每階段可獨立 PR／tag）。

---

## 2. 方案比較與定案（brainstorming）

### 2.1 Python 目標版本

| 選項 | 說明 | 取捨 |
|------|------|------|
| **A. Python 3.11** | 相容性保守、生態成熟 | 略舊於 3.12，仍為支援中版本 |
| **B. Python 3.12**（**建議**） | 2026 年 wheel／映像支援普遍、效能與語法適中 | 若某 wheel 尚未支援，需 fallback |
| **C. Python 3.13** | 最新 | uc／二進位依賴風險較高，**本次不採** |

**定案：** 以 **`python:3.12`**（或 **`python:3.12-slim`**，依最終 Dockerfile 基底）為預設目標。若 `pip install -r requirements.txt` 或 Docker build **在 3.12 失敗**，再退至 **3.11**，並在本檔「修訂記錄」註明原因。

### 2.2 Dockerfile：Chrome／Chromedriver 策略（對應 assessment §4）

| 選項 | 說明 | 取捨 |
|------|------|------|
| **A. Chrome for Testing（CfT）** | 同一 **build id** 安裝 Chrome + ChromeDriver | 可重現、最利除錯；Dockerfile 較長 |
| **B. 依賴 uc 管理 driver** | 移除手動 chromedriver zip，**不**與 apt Chrome 混用舊 `LATEST_RELEASE` | 變因較少；須確認容器內 uc 實際行為 |
| **C. 現成 selenium 映像** | 與 uc 難以直接套用 | **不採**（見 assessment） |

**定案（兩段式，降低一次改壞風險）：**

1. **階段 2 — 首選路徑（B 為主）：**  
   - **移除** `Dockerfile` 內 **手動下載** `chromedriver.storage.googleapis.com` 之步驟（消除與 Chrome 主版本不一致與過時端點）。  
   - **修正** Google Chrome apt 簽章（**廢除 `apt-key add`**，改為現行 keyring／signed-by 寫法）。  
   - 保留 **單一** Chrome 來源（`google-chrome-stable` 或改為與 spike 一致之單一路徑），讓 **uc 自行解析／下載對應 driver**（與 assessment 備註一致）。  
   - 建置時 **記錄** `google-chrome-stable` 與執行時實際 driver 版本（例如啟動後 log 或 `chromedriver --version`），寫入任務筆記或 README 片段。

2. **階段 2 — 備援路徑（若 B 於容器內不穩）：**  
   - 改採 **A：Chrome for Testing**，**固定**同一 **build id** 的 `chrome` + `chromedriver`，與 assessment 表格一致。  
   - 備援啟動條件（擇一即可）：連續兩次 E2E 失敗且可歸因於 driver／版本；或 uc 無法取得與已裝 Chrome 相容之 driver。

### 2.3 階段順序是否調整（依賴 vs Python vs Docker）

| 選項 | 說明 |
|------|------|
| **維持 assessment §7 順序**（**定案**） | 0→1→2→3→4：先 pin（仍在 3.8）→ 再 Dockerfile → 再升 Python → 最後 Selenium／uc 大版 |
| 先升 Python 再改 Docker | 變因疊加，除錯較難 — **不採** |

**定案：** **維持** [assessment.md §7](./assessment.md) 之階段順序，不調換 2／3。

### 2.4 `DISPLAY=:99`

**定案：** 實作階段 2 spike 時一併驗證：若僅使用 `--headless` 且無 Xvfb，**預設移除或註解** `ENV DISPLAY=:99`（除非驗證證明需要）。最終以「可重現 E2E」為準。

### 2.5 PR／commit 粒度

**定案：** **一階段一 PR**（或同等粒度之獨立 commit 系列），方便 `git revert`。階段 0 可僅 **git tag** + 筆記，不一定開 PR。

---

## 3. 各階段實作細節（濃縮檢核表）

| 階段 | 動作要點 | 通過條件 |
|------|----------|----------|
| **0** | Tag；記錄 Chrome／driver（若可得） | 現行流程可跑 |
| **1** | 升級 Pillow、requests（連帶 urllib3）；必要時 Selenium **僅小版** | `pip check` + 至少 1 smoke + 裁切路徑若有用到 |
| **2** | apt 現代化；刪舊 chromedriver 下載；首選 B、備援 A；處理 `DISPLAY` | `docker build` + 1 E2E |
| **3** | Base image 改 **Python 3.12**（失敗則 3.11）；`pip install -r requirements.txt` | 全依賴安裝 + E2E |
| **4** | 依 uc／Selenium release notes **成對**評估後升級 | **≥2 站台** E2E |

---

## 4. 與 `design.md` §8 對照

| 原待確認項 | 定案 |
|------------|------|
| Python 3.11 vs 3.12 | **預設 3.12**，必要時 **3.11** |
| Dockerfile：CfT vs uc-only | **先 B（uc + 移除手動 driver + apt 修復）**，失敗則 **A（CfT 同 build）** |
| 階段順序 | **維持 assessment §7** |

---

## 5. 修訂記錄

| 日期 | 變更 |
|------|------|
| 2026-04-06 | 初版：brainstorming 定案 |

---

## 6. 下一步（非實作）

- **建議**在通過本檔審閱後，再撰「實作計畫」：逐 PR 列出檔案、指令與驗證步驟（可搭配 Trellis 工作流程或專案內 checklist）。
