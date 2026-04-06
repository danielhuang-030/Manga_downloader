"""
從 `.env` 載入設定的進入點（viewer ID + 依頁面標題建立 downloads 子目錄）。

非 `.env` 欄位直接沿用 `main.py` 的 `settings`（改 `main.py` 即同步影響本進入點）。

使用方式：複製 `.env.example` 為 `.env` 並填寫變數後執行：

    python main_env.py

列表模式（manga_url / imgdir）：`python main.py`
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from config import load_manga_config
from downloader import Downloader
from main import settings

if TYPE_CHECKING:
    from config import MangaConfig

# 這些鍵改由 load_manga_config() / .env 提供；其餘一律沿用 main.settings。
_ENV_OVERRIDDEN_KEYS = frozenset(
    {"manga_url", "imgdir", "cookies", "res", "sleep_time"},
)


def downloader_kwargs_for_env(cfg: "MangaConfig") -> dict:
    """合併 main.settings 與 .env 設定，供 viewer 模式建立 Downloader。"""
    base = {k: v for k, v in settings.items() if k not in _ENV_OVERRIDDEN_KEYS}
    base.update(
        manga_url=[],
        imgdir=[],
        cookies=cfg.cookies,
        res=cfg.res,
        sleep_time=cfg.sleep_time,
        viewer_ids=cfg.viewer_ids,
        viewer_url_template=cfg.viewer_url_template,
    )

    return base


def main():
    cfg = load_manga_config()
    downloader = Downloader(**downloader_kwargs_for_env(cfg))
    downloader.download()


if __name__ == "__main__":
    main()
