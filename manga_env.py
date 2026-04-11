"""
Parse manga-related environment strings and safe download folder names (no I/O).
"""
from __future__ import annotations

import re
from typing import Literal, Mapping
from urllib.parse import urldefrag, urlparse, urlunparse

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


def normalize_viewer_url_for_id_extraction(url: str) -> str:
    """Strip, drop fragment and query; keep scheme, netloc, path only."""
    s = (url or "").strip()
    s, _frag = urldefrag(s)
    p = urlparse(s)

    return urlunparse((p.scheme, p.netloc, p.path, "", "", ""))


def extract_viewer_id_from_url(url: str, template: str) -> str | None:
    """
    Match normalized URL against template with exactly one `{id}` (digits only).
    `template` should come from parse_viewer_url_template.
    """
    if template.count("{id}") != 1:
        raise ValueError("MANGA_VIEWER_URL_TEMPLATE 必須包含恰好一個 {id} 占位符")

    idx = template.index("{id}")
    prefix = template[:idx]
    suffix = template[idx + len("{id}") :]
    pattern = re.compile(
        "^" + re.escape(prefix) + r"(\d+)" + re.escape(suffix) + "$"
    )
    normalized = normalize_viewer_url_for_id_extraction(url)
    m = pattern.fullmatch(normalized)

    return m.group(1) if m else None


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


def append_parsed_id_to_manga_ids(
    manga_ids_csv: str, parsed_id: str
) -> tuple[str, Literal["appended", "duplicate"]]:
    """Append parsed_id after parse_manga_ids list, or return normalized CSV if duplicate."""
    ids = parse_manga_ids(manga_ids_csv)
    if parsed_id in ids:
        return ",".join(ids), "duplicate"
    next_ids = [*ids, parsed_id]

    return ",".join(next_ids), "appended"


def coerce_http_cookie_header_latin1(cookie: str) -> tuple[str, int]:
    """
    urllib3/http.client require header field values encodable as latin-1.
    Returns (sanitized_cookie, number_of_removed_characters).
    Code points U+0100 and above are removed (e.g. pasted U+2026 …).
    """
    out: list[str] = []
    dropped = 0
    for ch in cookie or "":
        if ord(ch) < 256:
            out.append(ch)
        else:
            dropped += 1

    return "".join(out), dropped


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
