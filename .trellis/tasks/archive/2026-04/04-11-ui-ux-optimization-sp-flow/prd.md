# 優化 UI/UX

## Goal

提升本專案使用者介面與體驗品質；本 task 指定依 **sp flow**（Superpowers + Trellis 整合）執行：頭腦風暴 → 計畫（`plan.md`）→ TDD → 總結 → check-report → code review → Record Session 與封存。

## What I already know

- Task 目錄：`.trellis/tasks/04-11-ui-ux-optimization-sp-flow/`（`task.json` 已建立，assignee：`cursor-agent`）。
- Repo 根目錄有 `run_web_ui.py`，測試含 `tests/test_web_app.py`，推測主要 UI 為 **Web**；細節待確認。
- 依 `superpowers-trellis-integration.md`：**未完成頭腦風暴對話與分段設計確認前，不得撰寫 `plan.md` 或開始實作**。

## Assumptions (temporary)

- 優化範圍以現有 **Web UI**（`run_web_ui.py` 等）為主；使用者已確認選項 **A**（2026-04-11）。

## Open Questions

- （已收斂；細節見 `plan.md`。）

## UX — 網址解析回饋（已確認，2026-04-11）

- 選項 **A**：**無法解析**時顯示**錯誤**訊息且不變更 `MANGA_IDS`；**已存在相同 ID** 時顯示**提示**訊息且不重複寫入。

## Product direction (from brainstorm)

- **主要成功感**：選項 **2)** — **好看、有品牌感**（視覺風格、排版、動效與整體一致性；仍須維持基本可用與可讀對比）。

## Requirements (evolving)

- Web UI；優先強化**視覺與整體一致性**（對齊使用者選項 2）。
- **視覺改動幅度**：選項 **B** — 無硬性品牌資產；在可讀性、對比、焦點與合理無障礙範圍內，整體風格可較大幅度調整。
- **主題**：選項 **4** — 內建主題切換（淺／深，並納入「跟隨系統」為第三狀態或預設之一，於 `plan.md` 拆步驟決定互動細節）。
- **Skill**：實作階段套用 **`frontend-design`**（見 Technical Notes 路徑），與 sp flow 的 TDD／驗證流程一併遵守。
- **URL → ID**：Web UI 提供貼上網址即可解析並**追加**至 `MANGA_IDS`；解析規則與 `MANGA_VIEWER_URL_TEMPLATE` 的 `{id}` 占位一致（實作可於 `manga_env` 新增純函式並附單元測試）。
- **標籤在地化**：表單欄位**正體中文標籤**＋實際參數名稱（鍵名）一併顯示。

## Acceptance Criteria (evolving)

- [x] 需求與範圍經使用者確認並寫入本 PRD 或後續 `plan.md`。
- [x] Web UI：主題切換（淺／深／跟隨系統）、視覺與 `frontend-design` 一致之設計方向。
- [x] Web UI：可依 **viewer 網址** 與 **`MANGA_VIEWER_URL_TEMPLATE`** 解析 **ID** 並**併入** `MANGA_IDS`（行為細節依「解析回饋」與 `plan.md`）。
- [x] Web UI：表單欄位具**正體中文標籤**並附**實際環境變數鍵名**。
- [x] 依 sp flow：先有 `plan.md`（於頭腦風暴完成後），再 TDD（核心路徑已實作與測試；細節見 `progress.md`）。
- [x] 完成前：總結修改、check-report、requesting-code-review；收尾依 Trellis（Record Session 於 commit 後由人類補跑、`task.py archive` 已執行）。

## 實作紀要（見 `progress.md`）

延伸修正含：**靜態檔掛載與 405**、**CSS 版面**、**`.env` chown**、**Cookie Latin-1 嚴格檢查**、**Docker `python`/`web` 的 `user:`**、**`scripts/compose.sh`** 等 — 完整列表以 **`progress.md`** 為準。

## Definition of Done (team quality bar)

- 測試／lint 依專案規範（見 `AGENTS.md`、`README.md` 或 task `plan.md`）。
- 行為變更若有文件需求已更新。
- 高風險變更已考量 rollout／rollback。

## Out of Scope (explicit)

- 未約定前：**不**支援與 `MANGA_VIEWER_URL_TEMPLATE` 結構無法對應的任意第三方網址（僅依模板比對／擷取）；若未來要支援多模板另開 task。
- 不含未經同意的後端大改或資料庫（本專案無 DB）；下載核心邏輯非本 task 主軸，除非因 UI/API 必須最小延伸。

## Visual design (brainstorm — segmented)

### 第一段（已確認，2026-04-11）

精緻工具型儀表板；**深色**為主要基調、**淺色紙感**為對照；中性階層＋單一強調色；主題以 **CSS 變數**管理；頂部或設定區提供**淺／深／跟隨系統**；短過渡並尊重 `prefers-reduced-motion`。

### 第二段（已確認，2026-04-11）

字體採「有性格的標題字＋易讀内文」雙字族，依 `frontend-design` 避開 Inter／Roboto／Arial 等泛用預設；元件以清楚邊界或輕陰影區隔層級，淺／深主題皆需可見的 focus ring；主要操作單一強調色。動效以 CSS 為主，強度有節奏且不干擾下載主流程，並遵守 `prefers-reduced-motion`。

### 第三段 — 功能擴充（與 UI 同 task，2026-04-11）

- **從網址取得 ID**：使用者只要貼上**完整 viewer 網址**，系統依目前有效的 **`MANGA_VIEWER_URL_TEMPLATE`**（與 `manga_env.parse_viewer_url_template` 語意一致；表單未存檔前則以表單內模板或程式預設）**解析出 `MANGA_ID`**，並**自動併入** `MANGA_IDS`（逗號清單；**加入**而非整批取代）。回饋行為見 **「UX — 網址解析回饋」**。
- **表單標籤**：環境參數欄位顯示**正體中文名稱**，並在後方（或括號內）保留**實際環境變數鍵名**（例如：`漫畫 ID 清單（MANGA_IDS）`），利於對照 `.env` 與文件。

## Technical Notes

- **進度與變更清單**：`progress.md`（持續對照本 PRD）。
- **計畫**：`plan.md`（本目錄）。
- 已觸及／新增測試之檔案（非窮舉，完整見 `progress.md`）：`manga_env.py`、`web_app.py`、`web_static/*`、`env_store.py`、`check_bookwalker_cookie.py`、`website_actions/bookwalker_nfbr_wait.py`、`docker-compose.yml`、`scripts/compose.sh`、`scripts/docker-test.sh`、`README.md`、`README.zh-TW.md`、`tests/test_manga_env.py`、`tests/test_web_app.py`、`tests/test_env_store.py`、`tests/test_check_bookwalker_cookie.py`。
- **實作時必讀**：**`frontend-design`** skill（`~/.cursor/skills/frontend-design/SKILL.md`）。
