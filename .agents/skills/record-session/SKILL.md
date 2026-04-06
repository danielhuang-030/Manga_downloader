---
name: record-session
description: "Record work progress after human has tested and committed code"
---

[!] **Prerequisite**: This skill should only be used AFTER the human has tested and committed the code.

**Do NOT run `git commit` directly** — the scripts below handle their own commits for `.trellis/` metadata. You only need to read git history (`git log`, `git status`, `git diff`) and run the Python scripts.

---

## Record Work Progress

### Step 1: Get Context & Check Tasks

```bash
python3 ./.trellis/scripts/get_context.py --mode record
```

[!] Archive tasks whose work is **actually done** — judge by work status, not the `status` field in task.json:
- Code committed? → Archive it (don't wait for PR)
- All acceptance criteria met? → Archive it
- Don't skip archiving just because `status` still says `planning` or `in_progress`

```bash
python3 ./.trellis/scripts/task.py archive <task-name>
```

### Step 2: One-Click Add Session

**Cursor / AI agent（必讀）**  
在 Cursor 整合終端機由 agent 執行 `add_session.py` 時，**必須**在整行指令結尾加上輸出重導向，否則容易因大量輸出而卡住或逾時：

- Linux / WSL / macOS：路徑是 **`/dev/null`**（不是 `del/null`）。
- 此腳本多數日誌印在 **stderr**，僅 `>/dev/null` 仍會刷屏；請用 **`>/dev/null 2>&1`** 一併丟棄 stdout 與 stderr。
- 若自動 `git commit` 仍卡住（例如 GPG 互動式簽署），改用 **`--no-commit`**，再自行在本機提交 `.trellis/workspace`。

```bash
# Method 1: Simple parameters（Cursor / agent 請保留結尾重導向）
python3 ./.trellis/scripts/add_session.py \
  --title "Session Title" \
  --commit "hash1,hash2" \
  --summary "Brief summary of what was done" \
  >/dev/null 2>&1

# Method 2: Pass detailed content via stdin（Cursor / agent：保留 pipeline 結尾的 >/dev/null 2>&1）
cat << 'EOF' | python3 ./.trellis/scripts/add_session.py --title "Title" --commit "hash" >/dev/null 2>&1
| Feature | Description |
|---------|-------------|
| New API | Added user authentication endpoint |
| Frontend | Updated login form |

**Updated Files**:
- `packages/api/modules/auth/router.ts`
- `apps/web/modules/auth/components/login-form.tsx`
EOF
```

**Auto-completes**:
- [OK] Appends session to journal-N.md
- [OK] Auto-detects line count, creates new file if >2000 lines
- [OK] Updates index.md (Total Sessions +1, Last Active, line stats, history)
- [OK] Auto-commits .trellis/workspace and .trellis/tasks changes

---

## Script Command Reference

| Command | Purpose |
|---------|---------|
| `python3 ./.trellis/scripts/get_context.py --mode record` | Get context for record-session |
| `python3 ./.trellis/scripts/add_session.py ... >/dev/null 2>&1` | **One-click add session** (in Cursor, **must** append redirect) |
| `python3 ./.trellis/scripts/task.py archive <name>` | Archive completed task (auto-commits) |
| `python3 ./.trellis/scripts/task.py list` | List active tasks |
