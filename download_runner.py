"""
共用下載進入點：從 `.env` 載入設定並執行 Downloader（CLI 與 Web 共用）。
"""
from __future__ import annotations

from config import load_manga_config
from downloader import Downloader
from main_env import downloader_kwargs_for_env


def run_download_from_dotenv(dotenv_path=None, progress_reporter=None):
    """
    載入 manga 設定後建立 Downloader 並執行 download()。

    :param dotenv_path: 傳入 `load_manga_config` 的路徑，預設 None 使用專案預設 .env 搜尋行為。
    :param progress_reporter: 可選；若提供則傳入 Downloader 作為進度回呼。
    """
    cfg = load_manga_config(dotenv_path)
    kwargs = downloader_kwargs_for_env(cfg)
    kwargs["progress_reporter"] = progress_reporter
    downloader = Downloader(**kwargs)
    downloader.download()
