#!/usr/bin/env bash
set -euo pipefail

DEPLOY_DIR="${DEPLOY_DIR:-/opt/canva-image-toolkit}"
STATE_DIR="${STATE_DIR:-/var/lib/canva-image-toolkit}"
cd "$DEPLOY_DIR"

if [[ ! -s "$STATE_DIR/previous-deploy" ]]; then
  echo "No previous deployment commit was recorded." >&2
  exit 1
fi
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Deployment checkout has local changes; refusing rollback." >&2
  exit 1
fi

previous_commit="$(cat "$STATE_DIR/previous-deploy")"
git cat-file -e "${previous_commit}^{commit}"
git switch --detach "$previous_commit"
docker compose -p canva-image-toolkit -f docker-compose.yml -f deploy/docker-compose.prod.yml up -d --build
curl --fail --silent http://127.0.0.1:8000/health >/dev/null
echo "Rollback completed and health check passed."
