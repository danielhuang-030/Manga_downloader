"""TDD: env_store — .env 鍵級合併與原子寫入（無瀏覽器）。"""

from pathlib import Path

import pytest

from env_store import MANAGED_KEYS, merge_write_dotenv, read_managed_values


def test_merge_write_updates_key_and_preserves_comments_and_unknown(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text(
        "# header comment\n"
        "FOO=bar\n"
        "MANGA_RES=800x600\n"
        "# inline note\n"
        "UNRELATED=keep-me\n",
        encoding="utf-8",
    )

    merge_write_dotenv(env_path, {"MANGA_RES": "1445x2048"})

    text = env_path.read_text(encoding="utf-8")
    assert "# header comment" in text
    assert "FOO=bar" in text
    assert "MANGA_RES=1445x2048" in text
    assert "# inline note" in text
    assert "UNRELATED=keep-me" in text
    assert "800x600" not in text


def test_merge_write_appends_missing_key(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("FOO=1\n", encoding="utf-8")

    merge_write_dotenv(env_path, {"MANGA_IDS": "1,2,3"})

    text = env_path.read_text(encoding="utf-8")
    assert "FOO=1" in text
    assert "MANGA_IDS=1,2,3" in text


def test_merge_write_rejects_unknown_key(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="Unknown"):
        merge_write_dotenv(env_path, {"NOT_A_MANAGED_KEY": "x"})


def test_read_managed_values_roundtrip(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text(
        "MANGA_RES=1445x2048\n"
        "MANGA_SLEEP_TIME=1.5\n"
        "MANGA_IDS=10, 20\n",
        encoding="utf-8",
    )

    data = read_managed_values(env_path)

    assert data["MANGA_RES"] == "1445x2048"
    assert data["MANGA_SLEEP_TIME"] == "1.5"
    assert data["MANGA_IDS"] == "10, 20"


def test_managed_keys_covers_design_keys():
    for key in (
        "MANGA_COOKIES",
        "BOOKWALKER_COOKIE",
        "MANGA_RES",
        "MANGA_SLEEP_TIME",
        "MANGA_IDS",
        "MANGA_VIEWER_URL_TEMPLATE",
        "MANGA_HEADLESS",
    ):
        assert key in MANAGED_KEYS
