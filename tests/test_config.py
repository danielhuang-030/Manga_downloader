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


def test_load_manga_config_explicit_file_overrides_stale_manga_ids(monkeypatch, tmp_path):
    """
    Web UI 等同行程會多次呼叫 load_manga_config(ENV_PATH)。
    預設 load_dotenv(override=False) 時，第一次載入寫入 os.environ 的 MANGA_IDS
    不會被之後更新的 .env 檔取代，造成第二次下載仍用舊 ID。
    """
    env_file = tmp_path / ".env"
    env_file.write_text(
        "MANGA_COOKIES=x=y\n"
        "MANGA_RES=400x300\n"
        "MANGA_SLEEP_TIME=0.5\n"
        "MANGA_IDS=10,20\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("MANGA_COOKIES", "stale=cookie")
    monkeypatch.setenv("MANGA_RES", "999x999")
    monkeypatch.setenv("MANGA_SLEEP_TIME", "9")
    monkeypatch.setenv("MANGA_IDS", "1,2")

    from config import load_manga_config

    cfg = load_manga_config(dotenv_path=str(env_file))
    assert cfg.cookies == "x=y"
    assert cfg.res == (400, 300)
    assert cfg.sleep_time == 0.5
    assert cfg.viewer_ids == ["10", "20"]


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
