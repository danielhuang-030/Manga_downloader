"""web_app — FastAPI TestClient（需已安裝 fastapi）。"""

import json
import threading
import time
import uuid

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


def test_get_root_serves_index(tmp_path, monkeypatch):
    import web_app

    monkeypatch.setattr(web_app, "ENV_PATH", tmp_path / ".env")
    client = TestClient(web_app.app)
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")
    assert b"Manga_downloader" in r.content
    assert b"/static/i18n.js" in r.content
    assert b"data-i18n" in r.content


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


def test_manga_id_from_url_appended(tmp_path, monkeypatch):
    import web_app

    monkeypatch.setattr(web_app, "ENV_PATH", tmp_path / ".env")
    _write_minimal_env(tmp_path / ".env")
    client = TestClient(web_app.app)
    body = {
        "url": "https://www.bookwalker.com.tw/browserViewer/999/read",
        "MANGA_IDS": "1",
        "MANGA_VIEWER_URL_TEMPLATE": "",
    }
    r = client.post("/api/env/manga-id-from-url", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["result"] == "appended"
    assert data["manga_ids"] == "1,999"
    assert data["parsed_id"] == "999"


def test_manga_id_from_url_duplicate(tmp_path, monkeypatch):
    import web_app

    monkeypatch.setattr(web_app, "ENV_PATH", tmp_path / ".env")
    _write_minimal_env(tmp_path / ".env")
    client = TestClient(web_app.app)
    body = {
        "url": "https://www.bookwalker.com.tw/browserViewer/1/read",
        "MANGA_IDS": "1",
        "MANGA_VIEWER_URL_TEMPLATE": "",
    }
    r = client.post("/api/env/manga-id-from-url", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["result"] == "duplicate"
    assert data["manga_ids"] == "1"


def test_manga_id_from_url_bad_url(tmp_path, monkeypatch):
    import web_app

    monkeypatch.setattr(web_app, "ENV_PATH", tmp_path / ".env")
    _write_minimal_env(tmp_path / ".env")
    client = TestClient(web_app.app)
    r = client.post(
        "/api/env/manga-id-from-url",
        json={"url": "https://wrong.example/nope", "MANGA_IDS": "1", "MANGA_VIEWER_URL_TEMPLATE": ""},
    )
    assert r.status_code == 400


def test_api_download_stop_unknown_job(tmp_path, monkeypatch):
    import web_app

    monkeypatch.setattr(web_app, "ENV_PATH", tmp_path / ".env")
    _write_minimal_env(tmp_path / ".env")
    monkeypatch.setattr(web_app, "_active_job_id", None)

    client = TestClient(web_app.app)
    r = client.post("/api/download/stop", json={"job_id": str(uuid.uuid4())})
    assert r.status_code == 404


def test_api_download_stop_triggers_cancel_and_releases_active(tmp_path, monkeypatch):
    import web_app

    monkeypatch.setattr(web_app, "ENV_PATH", tmp_path / ".env")
    _write_minimal_env(tmp_path / ".env")

    holder = {}
    started = threading.Event()

    def fake_run(dotenv_path, progress_reporter=None, cancel_event=None):
        assert cancel_event is not None
        holder["ev"] = cancel_event
        progress_reporter({"type": "run_started", "total_books": 1})
        started.set()
        cancel_event.wait(timeout=5)
        progress_reporter({"type": "run_cancelled", "ok": False})

    monkeypatch.setattr("download_runner.run_download_from_dotenv", fake_run)

    client = TestClient(web_app.app)
    r = client.post("/api/download/start")
    assert r.status_code == 200
    job_id = r.json()["job_id"]
    assert started.wait(timeout=2)

    r2 = client.post("/api/download/stop", json={"job_id": job_id})
    assert r2.status_code == 200
    assert r2.json() == {"ok": True}
    assert holder["ev"].is_set()

    for _ in range(100):
        if web_app._active_job_id is None:
            break
        time.sleep(0.05)
    assert web_app._active_job_id is None


def test_sse_stream_ends_on_run_cancelled(tmp_path, monkeypatch):
    import web_app

    monkeypatch.setattr(web_app, "ENV_PATH", tmp_path / ".env")
    _write_minimal_env(tmp_path / ".env")

    started = threading.Event()

    def fake_run(dotenv_path, progress_reporter=None, cancel_event=None):
        progress_reporter({"type": "run_started", "total_books": 1})
        started.set()
        cancel_event.wait(timeout=5)
        progress_reporter({"type": "run_cancelled", "ok": False})

    monkeypatch.setattr("download_runner.run_download_from_dotenv", fake_run)

    client = TestClient(web_app.app)
    r = client.post("/api/download/start")
    assert r.status_code == 200
    job_id = r.json()["job_id"]
    assert started.wait(timeout=2)

    saw_cancelled = threading.Event()

    def consume():
        with client.stream("GET", "/api/download/stream/%s" % job_id) as resp:
            assert resp.status_code == 200
            for line in resp.iter_lines():
                if not line:
                    continue
                if isinstance(line, (bytes, bytearray)):
                    line = line.decode("utf-8")
                if line.startswith("data: "):
                    payload = json.loads(line[6:])
                    if payload.get("type") == "run_cancelled":
                        saw_cancelled.set()
                        break

    th = threading.Thread(target=consume, daemon=True)
    th.start()
    time.sleep(0.1)
    rstop = client.post("/api/download/stop", json={"job_id": job_id})
    assert rstop.status_code == 200
    th.join(timeout=5)
    assert saw_cancelled.is_set()
