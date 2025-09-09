#!/usr/bin/env bash
set -euo pipefail
IMAGE_NAME="llama-fastapi-app"

docker rm -f "${IMAGE_NAME}-container" 2>/dev/null || true

docker run -it \
  --name="${IMAGE_NAME}-container" \
  -p 8001:8080 \
  -v "$PWD":/workspace \
  -w /workspace/app \
  --env-file ./.env \
  ${IMAGE_NAME}:latest \
  uvicorn main:app --host 0.0.0.0 --port 8080 --reload