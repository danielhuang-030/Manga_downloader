"""
啟動本機 Web UI（固定監聽 127.0.0.1:8765）。於專案根目錄執行：

    python run_web_ui.py

Docker 對外連接埠請見 docker-compose.yml（`MANGA_WEB_PORT` 僅用於主機→容器映射，應用程式內仍為 8765）。
"""
from __future__ import annotations

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "web_app:app",
        host="127.0.0.1",
        port=8765,
        reload=False,
    )
