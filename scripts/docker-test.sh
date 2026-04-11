#!/usr/bin/env bash
# 在與 Dockerfile 相同的環境中執行 pytest（專案目錄掛載為 /app）。
# 用法：於專案根目錄執行 ./scripts/docker-test.sh
# 額外參數會轉給 pytest，例如：./scripts/docker-test.sh tests/test_env_store.py -q
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v docker >/dev/null 2>&1; then
  echo "找不到 docker，請先安裝 Docker。" >&2
  exit 1
fi

exec "$ROOT/scripts/compose.sh" run --rm python python -m pytest tests/ -v "$@"
