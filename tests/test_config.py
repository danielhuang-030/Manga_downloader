"""TDD: config.load_manga_config (no real .env file; monkeypatch os.environ)."""

import pytest


def test_load_manga_config_from_environ(monkeypatch, tmp_path):
    monkeypatch.delenv("MANGA_COOKIES", raising=False)
    monkeypatch.setenv("MANGA_COOKIES", "a=b")
    monkeypatch.setenv("MANGA_RES", "800x600")
    monkeypatch.setenv("MANGA_SLEEP_TIME", "1.5")
    monkeypatch.setenv("MANGA_IDS", "1,2")

    from config import load_manga_config

    missing_env = tmp_path / "nonexistent.env"
    cfg = load_manga_config(dotenv_path=str(missing_env))
    assert cfg.cookies == "a=b"
    assert cfg.res == (800, 600)
    assert cfg.sleep_time == 1.5
    assert cfg.viewer_ids == ["1", "2"]
    assert "bookwalker.com.tw" in cfg.viewer_url_template
    assert "{id}" in cfg.viewer_url_template


def test_load_manga_config_missing_manga_res(monkeypatch, tmp_path):
    monkeypatch.delenv("MANGA_COOKIES", raising=False)
    monkeypatch.setenv("MANGA_COOKIES", "a=b")
    monkeypatch.setenv("MANGA_SLEEP_TIME", "1")
    monkeypatch.setenv("MANGA_IDS", "1")
    monkeypatch.delenv("MANGA_RES", raising=False)

    from config import load_manga_config

    missing_env = tmp_path / "nonexistent.env"
    with pytest.raises(ValueError, match="MANGA_RES"):
        load_manga_config(dotenv_path=str(missing_env))
