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
    Load dotenv then read MANGA_* keys from os.environ.

    若傳入 ``dotenv_path``，則以該檔為準並 **覆寫** 已存在之環境變數
    （``override=True``）。長連線的 Web 程序在寫入新 ``.env`` 後可再度載入，
    否則第一次 ``load_dotenv`` 寫入的 ``MANGA_IDS`` 等會永遠留在 ``os.environ``，
    導致之後讀到的仍是舊清單。

    若 ``dotenv_path`` 為 ``None``，則呼叫無路徑的 ``load_dotenv()`` 且 **不**覆寫，
    讓行程環境（例如 Docker / CLI 的 ``export``）優先於檔案。
    """
    if dotenv_path is not None:
        load_dotenv(dotenv_path, override=True)
    else:
        load_dotenv()

    env = os.environ
    cookies = resolve_cookie_header(env)
    if not cookies:
        raise ValueError("缺少 MANGA_COOKIES（須為非空字串）")

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
