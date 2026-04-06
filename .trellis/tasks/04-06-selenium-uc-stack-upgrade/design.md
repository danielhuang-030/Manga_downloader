# Design：Selenium + undetected-chromedriver 堆疊升級

**任務目錄：** `04-06-selenium-uc-stack-upgrade`  
**狀態：** Approved — 升級細節見 [upgrade-details.md](./upgrade-details.md)  
**日期：** 2026-04-06（brainstorming 定案細節：2026-04-06）  
**相關評估：** [assessment.md](./assessment.md)（與本任務同目錄）

---

## 1. 背景與目標

- **現況：** Python 3.8（EOL）、舊版依賴 pin、`Dockerfile` 使用已棄用之 apt／Chromedriver 下載方式，且 Chrome 與 driver 可能不一致。
- **目標：** 在**不更換自動化框架**的前提下，依風險由低至高**分階升級**執行環境與依賴，並以端到端下載驗證為準。

---

## 2. 架構定案（ADR）

| 項目 | 決策 |
|------|------|
| 瀏覽器自動化 | **維持** Selenium 4.x + **undetected-chromedriver（uc）** |
| 應用結構 | **維持** `downloader.py` 編排 + `website_actions/*` 站台適配器 |
| 遷移 Playwright／patchright | **本次不做**（評估見 [assessment.md](./assessment.md) §8；若未來要做須另開任務與 spike） |

**理由：** 專案已深度依賴 uc 的反偵測與既有 CDP／cookie 流程；換框架成本高、與「先解除 EOL 與容器脆弱性」的優先順序不同。

---

## 3. 範圍

### 納入

- `requirements.txt`：在相容範圍內更新 Pillow、requests／urllib3、必要時 Selenium／uc 小版或審慎升級。
- `Dockerfile`：現代化 Chrome／Chromedriver 取得方式（例如 Chrome for Testing 配對或經驗證之 uc-only 策略）、移除 `apt-key` 等已棄用寫法。
- **Python** 升級至支援中的版本（建議 **3.11 或 3.12**，見評估文件）。
- 文件：升級步驟、驗證方式、已知風險（可併入 README 或任務筆記）。

### 不納入

- 改寫為 Playwright／patchright 或重構 `website_actions` 合約（除非升級過程中**必須**為相容性做最小調整）。
- 新增完整 CI（若無則可列為後續任務）；本設計以本機／Docker **手動或腳本 smoke** 為最低驗收。

---

## 4. 分階段實作順序（與評估對齊）

實作時應**分 PR／分 commit**，每階段通過再進下一階段（細節見 `assessment.md` §7）。

| 階段 | 重點 | 通過條件（摘要） |
|------|------|------------------|
| 0 — 基線 | 可運作 commit／tag；記錄 Chrome／driver | 現有下載流程可重現 |
| 1 — 安全性 pin | Pillow、requests 等 | `pip check` + 至少一條 smoke |
| 2 — Dockerfile | apt、Chromedriver 來源、與 uc 一致 | 映像建置成功 + 一條 E2E |
| 3 — Python | base image 與 venv | 全依賴安裝 + E2E |
| 4 — Selenium／uc | 主／次版升級 | **多站台** E2E |

---

## 5. 驗證策略

- **最低：** `python -c "import undetected_chromedriver, selenium"`；啟動 `Downloader`（含 `--headless` 若適用）。
- **建議：** 至少兩個 `website_actions` 站台（登入 + 多頁）；檢查 `WebDriverWait` 與既有 `error.html`／`error.png` 行為。

---

## 6. 風險與回滾

- **最高風險步驟：** 階段 4（Selenium／uc 與 Chrome 大版本連動）。
- **回滾：** 每階段前維持可部署之上一版 tag／branch；依賴改動以 lock 或明確 pin 利於 `git revert`。

---

## 7. 文件放置約定（本專案）

- 本設計、**評估**（`assessment.md`）與 **brainstorm／實作規格**（`prd.md`）應放在 **同一 Trellis 任務目錄** `.trellis/tasks/<任務>/`，**不**使用 repo 下獨立 `docs/superpowers/specs/` 作為預設路徑。

---

## 8. 待實作前確認（可寫入 prd）

已於 [upgrade-details.md](./upgrade-details.md)（brainstorming 定案稿）拍板：

- [x] Python：**預設 3.12**，必要時退 **3.11**。
- [x] Dockerfile：**先** uc + 移除手動舊版 chromedriver + 現代化 apt；**不穩則**改 Chrome for Testing 同 build。
- [x] 階段順序：維持 [assessment.md](./assessment.md) §7（0→1→2→3→4）。
