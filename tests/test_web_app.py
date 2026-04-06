"""web_app — FastAPI TestClient（需已安裝 fastapi）。"""

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient


def _write_minimal_env(path):
    path.write_text(
        "MANGA_COOKIES=a=b\n"
        "MANGA_RES=1445x2048\n"
        "MANGA_SLEEP_TIME=1\n"
        "MANGA_IDS=1\n",
        encoding="utf-8",
    )


def test_api_get_env_masks_cookie(tmp_path, monkeypatch):
    import web_app

    monkeypatch.setattr(web_app, "ENV_PATH", tmp_path / ".env")
    _write_minimal_env(tmp_path / ".env")

    client = TestClient(web_app.app)
    r = client.get("/api/env")
    assert r.status_code == 200
    assert r.json()["MANGA_COOKIES"] == "***masked***"


def test_api_put_env_updates_and_validates(tmp_path, monkeypatch):
    import web_app

    monkeypatch.setattr(web_app, "ENV_PATH", tmp_path / ".env")
    _write_minimal_env(tmp_path / ".env")

    client = TestClient(web_app.app)
    r = client.put(
        "/api/env",
        json={"MANGA_RES": "800x600", "MANGA_SLEEP_TIME": "1.5"},
    )
    assert r.status_code == 200
    text = (tmp_path / ".env").read_text(encoding="utf-8")
    assert "MANGA_RES=800x600" in text
    assert "MANGA_SLEEP_TIME=1.5" in text


def test_api_download_start_conflict(tmp_path, monkeypatch):
    import web_app

    monkeypatch.setattr(web_app, "ENV_PATH", tmp_path / ".env")
    _write_minimal_env(tmp_path / ".env")
    monkeypatch.setattr(web_app, "_active_job_id", "existing")

    client = TestClient(web_app.app)
    r = client.post("/api/download/start")
    assert r.status_code == 409
