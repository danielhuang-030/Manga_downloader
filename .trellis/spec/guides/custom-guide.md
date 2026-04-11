# 客製化指引

---

## 概述

---

## 使用時機

---

## 規則

### 語言規範

- 所有文件、說明、註解一律使用**正體中文**撰寫。

### `add_session.py`（Cursor 工具執行時）

> **適用範圍**：以下作法僅在由 **Cursor 內建代理／終端工具** 執行指令時採用；一般在本機互動終端手動操作時不必套用。

呼叫 `.trellis/scripts/add_session.py` 且未使用 `--content-file` 時，**一律**將 stdin 接到 `/dev/null`，例如：

```bash
python3 ./.trellis/scripts/add_session.py --title "…" --commit "…" </dev/null
```

---

## 參考資料
