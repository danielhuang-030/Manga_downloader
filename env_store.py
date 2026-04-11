"""
專案根目錄 `.env` 的鍵級合併與原子寫入（僅允許已知漫畫下載相關鍵）。
"""
from __future__ import annotations

import os
import re
from pathlib import Path

_LINE_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")

MANAGED_KEYS: frozenset[str] = frozenset(
    {
        "MANGA_COOKIES",
        "MANGA_RES",
        "MANGA_SLEEP_TIME",
        "MANGA_IDS",
        "MANGA_VIEWER_URL_TEMPLATE",
        "MANGA_HEADLESS",
    }
)


def _quote_value(value: str) -> str:
    if value == "":
        return '""'
    if re.search(r'[\s#"\'\\]', value) or "\n" in value:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return '"%s"' % escaped

    return value


def _format_line(key: str, value: str) -> str:
    return "%s=%s\n" % (key, _quote_value(value))


def read_managed_values(path: str | Path) -> dict[str, str]:
    """讀取檔案中屬於 MANAGED_KEYS 的鍵（每鍵取第一次出現）。"""
    path = Path(path)
    out: dict[str, str] = {}
    if not path.is_file():
        return out

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _LINE_KEY_RE.match(line)
        if not m:
            continue
        key, rest = m.group(1), m.group(2)
        if key not in MANAGED_KEYS or key in out:
            continue
        if len(rest) >= 2 and rest[0] == rest[-1] and rest[0] in "\"'":
            out[key] = rest[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        else:
            out[key] = rest

    return out


def merge_write_dotenv(
    path: str | Path,
    updates: dict[str, str],
    *,
    managed_keys: frozenset[str] | None = None,
) -> None:
    """
    將 updates 合併寫入 path：已存在的鍵替換該行，否則於檔尾附加。
    僅允許 managed_keys 內的鍵；其餘鍵與註解盡量保留。
    """
    keys = managed_keys or MANAGED_KEYS
    unknown = set(updates) - keys
    if unknown:
        raise ValueError("Unknown keys: %s" % (", ".join(sorted(unknown)),))

    path = Path(path)
    lines: list[str] = []
    if path.is_file():
        text = path.read_text(encoding="utf-8")
        if text:
            lines = text.splitlines(keepends=True)

    key_to_index: dict[str, int] = {}
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("#") or not stripped.strip():
            continue
        m = _LINE_KEY_RE.match(stripped)
        if not m:
            continue
        k = m.group(1)
        if k in keys and k not in key_to_index:
            key_to_index[k] = i

    for key, val in updates.items():
        new_line = _format_line(key, val)
        if key in key_to_index:
            lines[key_to_index[key]] = new_line
        else:
            if lines and not lines[-1].endswith("\n"):
                lines[-1] = lines[-1] + "\n"
            lines.append(new_line)

    tmp = path.with_name(path.name + ".tmp")
    data = "".join(lines)
    path.parent.mkdir(parents=True, exist_ok=True)

    owner: tuple[int, int] | None = None
    if path.is_file():
        st = path.stat()
        owner = (st.st_uid, st.st_gid)
    elif path.parent.is_dir():
        pst = path.parent.stat()
        owner = (pst.st_uid, pst.st_gid)

    tmp.write_text(data, encoding="utf-8")
    os.replace(tmp, path)

    if owner is not None:
        uid, gid = owner
        try:
            os.chown(path, uid, gid, follow_symlinks=False)
        except OSError:
            pass
