"""
Parse manga-related environment strings and safe download folder names (no I/O).
"""
from __future__ import annotations

import re
from typing import Mapping

# 預設：Bookwalker 台灣 browserViewer；多站點時可於 .env 覆寫 MANGA_VIEWER_URL_TEMPLATE。
DEFAULT_VIEWER_URL_TEMPLATE = (
    "https://www.bookwalker.com.tw/browserViewer/{id}/read"
)
BOOKWALKER_TW_BROWSER_VIEWER_READ = DEFAULT_VIEWER_URL_TEMPLATE

_RES_PATTERN = re.compile(r"^(\d+)x(\d+)$")
_UNSAFE_PATH_CHARS = re.compile(r'[\\/:*?"<>|]')


def parse_viewer_url_template(raw: str | None) -> str:
    """
    MANGA_VIEWER_URL_TEMPLATE：須含 {id}；空字串或未設定則用 DEFAULT_VIEWER_URL_TEMPLATE。
    """
    s = (raw or "").strip()
    if not s:
        return DEFAULT_VIEWER_URL_TEMPLATE
    if "{id}" not in s:
        raise ValueError("MANGA_VIEWER_URL_TEMPLATE 必須包含 {id} 占位符")

    return s


def parse_manga_res(value: str) -> tuple[int, int]:
    """Parse MANGA_RES as '{width}x{height}' (ASCII x only)."""
    s = (value or "").strip()
    m = _RES_PATTERN.fullmatch(s)
    if not m:
        raise ValueError("MANGA_RES must match widthxheight, e.g. 1445x2048")

    return int(m.group(1)), int(m.group(2))


def parse_manga_ids(value: str) -> list[str]:
    """Parse MANGA_IDS as comma-separated tokens (trimmed, empty dropped)."""
    if not (value or "").strip():
        return []
    out: list[str] = []
    for part in value.split(","):
        t = part.strip()
        if t:
            out.append(t)

    return out


def resolve_cookie_header(env: Mapping[str, str]) -> str:
    """Prefer MANGA_COOKIES; else BOOKWALKER_COOKIE. Returns stripped string."""
    raw = env.get("MANGA_COOKIES") or ""
    if isinstance(raw, str) and raw.strip():
        return raw.strip()

    fallback = env.get("BOOKWALKER_COOKIE") or ""
    if isinstance(fallback, str):
        return fallback.strip()

    return ""


def sanitize_download_folder_name(raw_title: str, viewer_id: str) -> str:
    """
    Build a single path segment under downloads/ from page title.
    Falls back to browserViewer-{viewer_id} when unusable.
    """
    sid = str(viewer_id).strip()
    fallback = "browserViewer-%s" % sid if sid else "browserViewer-unknown"

    s = (raw_title or "").strip()
    if not s:
        return fallback

    if "|" in s or "｜" in s:
        s = re.split(r"[|｜]", s, maxsplit=1)[0].strip()

    if not s or s in (".", ".."):
        return fallback

    s = _UNSAFE_PATH_CHARS.sub("_", s)
    s = re.sub(r"_+", "_", s)
    s = s.strip("_").strip()
    if not s or s in (".", ".."):
        return fallback

    return s
