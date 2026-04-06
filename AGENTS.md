<!-- TRELLIS:START -->
# Trellis Instructions

These instructions are for AI assistants working in this project.

Use the `/trellis:start` command when starting a new session to:
- Initialize your developer identity
- Understand current project context
- Read relevant guidelines

Use `@/.trellis/` to learn:
- Development workflow (`workflow.md`)
- Project structure guidelines (`spec/`)
- Developer workspace (`workspace/`)

Keep this managed block so 'trellis update' can refresh the instructions.

<!-- TRELLIS:END -->

## Cursor：記錄 session（`add_session.py`）

在 Cursor 整合終端機由 AI agent 執行 `.trellis/scripts/add_session.py` 時：

1. **必須**在整行指令結尾加上 **`>/dev/null 2>&1`**，以免輸出過多造成終端機卡住或逾時。
2. 在 Linux / WSL / macOS 應寫成 **`/dev/null`**（勿寫成 `del/null`）。
3. 該腳本多數日誌印在 **stderr**，僅使用 `>/dev/null` 仍會刷屏，故需 **`2>&1`** 一併重導向。
4. 若自動 `git commit` 仍卡住（例如 GPG 互動簽署），改加 **`--no-commit`**，再由開發者在本機自行提交 `.trellis/workspace`（與必要時的 `.trellis/tasks`）。

範例：

```bash
python3 ./.trellis/scripts/add_session.py \
  --title "Session Title" \
  --commit "hash1,hash2" \
  --summary "Brief summary" \
  >/dev/null 2>&1
```

**約定**：上述慣例與補充說明以本檔 `AGENTS.md` 為準；請**不要**為了記載這些內容去修改 `.trellis/` 目錄下的檔案。
