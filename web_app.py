"""
本機 Web UI：`.env` 讀寫、啟動下載、SSE 進度（預設僅 127.0.0.1）。
"""
from __future__ import annotations

import json
import queue
import threading
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from config import load_manga_config
from env_store import merge_write_dotenv, read_managed_values
from manga_env import (
    append_parsed_id_to_manga_ids,
    extract_viewer_id_from_url,
    parse_viewer_url_template,
)

PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / ".env"
STATIC_DIR = PROJECT_ROOT / "web_static"

app = FastAPI(title="Manga_downloader Web UI")

_download_lock = threading.Lock()
_active_job_id: str | None = None
_job_queues: dict[str, queue.Queue] = {}


class MangaIdFromUrlBody(BaseModel):
    url: str
    MANGA_IDS: str = Field(..., description="Comma-separated IDs; may be empty string")
    MANGA_VIEWER_URL_TEMPLATE: str | None = None


def _mask_secrets(data: dict[str, str]) -> dict[str, str]:
    out = dict(data)
    if out.get("MANGA_COOKIES"):
        out["MANGA_COOKIES"] = "***masked***"

    return out


@app.get("/api/env")
def api_get_env():
    raw = read_managed_values(ENV_PATH)

    return _mask_secrets(raw)


@app.put("/api/env")
def api_put_env(body: dict):
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Body must be a JSON object")

    str_body = {str(k): str(v) for k, v in body.items()}
    if str_body.get("MANGA_COOKIES") == "***masked***":
        del str_body["MANGA_COOKIES"]

    try:
        merge_write_dotenv(ENV_PATH, str_body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    try:
        load_manga_config(str(ENV_PATH))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"ok": True}


@app.post("/api/download/start")
def api_download_start():
    global _active_job_id

    try:
        load_manga_config(str(ENV_PATH))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    with _download_lock:
        if _active_job_id is not None:
            raise HTTPException(
                status_code=409,
                detail={"error": "download_in_progress", "job_id": _active_job_id},
            )
        job_id = str(uuid.uuid4())
        q: queue.Queue = queue.Queue()
        _job_queues[job_id] = q
        _active_job_id = job_id

    from download_runner import run_download_from_dotenv

    def target():
        global _active_job_id

        def reporter(ev):
            merged = {"job_id": job_id, **ev}
            q.put(merged)

        try:
            run_download_from_dotenv(
                str(ENV_PATH),
                progress_reporter=reporter,
            )
        except Exception as e:
            q.put({"job_id": job_id, "type": "run_error", "message": str(e)[:500]})
        finally:
            with _download_lock:
                if _active_job_id == job_id:
                    _active_job_id = None

    threading.Thread(target=target, daemon=True).start()

    return {"job_id": job_id}


@app.get("/api/download/stream/{job_id}")
def api_download_stream(job_id: str):
    q = _job_queues.get(job_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Unknown job_id")

    def event_stream():
        try:
            while True:
                item = q.get()
                line = "data: %s\n\n" % (json.dumps(item, ensure_ascii=False),)
                yield line
                if item.get("type") in ("run_finished", "run_error"):
                    break
        finally:
            _job_queues.pop(job_id, None)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )


@app.post("/api/env/manga-id-from-url")
def api_env_manga_id_from_url(body: MangaIdFromUrlBody):
    try:
        tpl = parse_viewer_url_template(body.MANGA_VIEWER_URL_TEMPLATE)
        pid = extract_viewer_id_from_url(body.url, tpl)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from e

    if pid is None:
        raise HTTPException(
            status_code=400,
            detail="無法從網址解析出 viewer ID，請確認網址與網址模板是否一致",
        )

    manga_ids = body.MANGA_IDS
    new_csv, st = append_parsed_id_to_manga_ids(manga_ids, pid)

    if st == "appended":
        return {
            "result": "appended",
            "manga_ids": new_csv,
            "parsed_id": pid,
            "message_zh": "已將解析出的 ID 附加至清單",
        }

    return {
        "result": "duplicate",
        "manga_ids": new_csv,
        "parsed_id": pid,
        "message_zh": "清單已包含此 ID，未變更",
    }


# 勿將 StaticFiles 掛在 "/"：會攔截 /api/* 並對 POST 回 405 Method Not Allowed。
if STATIC_DIR.is_dir():

    @app.get("/")
    def serve_index():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/style.css")
    def legacy_style_css():
        """舊版 HTML 曾使用 /style.css；導向避免快取頁面無樣式。"""
        return RedirectResponse(url="/static/style.css", status_code=301)

    @app.get("/app.js")
    def legacy_app_js():
        return RedirectResponse(url="/static/app.js", status_code=301)

    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static",
    )
