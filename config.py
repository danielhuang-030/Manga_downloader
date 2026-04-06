"""
Load manga downloader config from environment and optional .env file.
"""
from __future__ import annotations

import os
from typing import NamedTuple

from dotenv import load_dotenv

from manga_env import (
    parse_manga_ids,
    parse_manga_res,
    parse_viewer_url_template,
    resolve_cookie_header,
)


class MangaConfig(NamedTuple):
    cookies: str
    res: tuple[int, int]
    sleep_time: float
    viewer_ids: list[str]
    viewer_url_template: str


def load_manga_config(dotenv_path: str | None = None) -> MangaConfig:
    """
    Load dotenv then read MANGA_* / BOOKWALKER_COOKIE from os.environ.
    Process env wins over .env file values for keys already set (dotenv default).
    """
    load_dotenv(dotenv_path)

    env = os.environ
    cookies = resolve_cookie_header(env)
    if not cookies:
        raise ValueError("缺少 MANGA_COOKIES 或 BOOKWALKER_COOKIE（至少一個須為非空字串）")

    res_raw = env.get("MANGA_RES", "").strip()
    if not res_raw:
        raise ValueError("缺少 MANGA_RES")

    res = parse_manga_res(res_raw)

    sleep_raw = env.get("MANGA_SLEEP_TIME")
    if sleep_raw is None or not str(sleep_raw).strip():
        raise ValueError("缺少 MANGA_SLEEP_TIME")

    sleep_time = float(str(sleep_raw).strip())

    ids_raw = env.get("MANGA_IDS", "").strip()
    if not ids_raw:
        raise ValueError("缺少 MANGA_IDS")

    viewer_ids = parse_manga_ids(ids_raw)
    if not viewer_ids:
        raise ValueError("MANGA_IDS 解析後為空")

    viewer_url_template = parse_viewer_url_template(env.get("MANGA_VIEWER_URL_TEMPLATE"))

    return MangaConfig(
        cookies=cookies,
        res=res,
        sleep_time=sleep_time,
        viewer_ids=viewer_ids,
        viewer_url_template=viewer_url_template,
    )
