#!/usr/bin/env bash
# 執行 docker compose 前自動帶入主機 UID/GID，避免 bind mount 下 .env、downloads/ 變 root:root。
# 用法（於專案根目錄）：./scripts/compose.sh run --rm python python main_env.py
# 若已手動 export MANGA_WEB_UID / MANGA_WEB_GID，則不覆寫。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export MANGA_WEB_UID="${MANGA_WEB_UID:-$(id -u)}"
export MANGA_WEB_GID="${MANGA_WEB_GID:-$(id -g)}"

if [[ -f compose.env ]]; then
  exec docker compose --env-file compose.env "$@"
fi

exec docker compose "$@"
