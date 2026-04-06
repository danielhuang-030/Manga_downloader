"""main_env merges .env with main.settings (no manga_settings)."""

from config import MangaConfig
from main import settings
from main_env import downloader_kwargs_for_env


def test_downloader_kwargs_for_env_uses_main_settings():
    cfg = MangaConfig(
        cookies="a=b",
        res=(800, 600),
        sleep_time=1.5,
        viewer_ids=["99"],
        viewer_url_template="https://example.com/{id}/read",
    )
    kw = downloader_kwargs_for_env(cfg)

    assert kw["loading_wait_time"] == settings["loading_wait_time"]
    assert kw["cut_image"] == settings["cut_image"]
    assert kw["end_page"] == settings["end_page"]
    assert kw["cookies"] == "a=b"
    assert kw["res"] == (800, 600)
    assert kw["sleep_time"] == 1.5
    assert kw["viewer_ids"] == ["99"]
    assert kw["manga_url"] == []
    assert kw["imgdir"] == []
