#!/usr/bin/env bash
set -euo pipefail

REPOSITORY_URL="https://github.com/Lucasthai1/canva-image-toolkit.git"
DEPLOY_BRANCH="${DEPLOY_BRANCH:-codex/complete-toolkit-tencent-deploy}"
DEPLOY_DIR="${DEPLOY_DIR:-/opt/canva-image-toolkit}"
STATE_DIR="${STATE_DIR:-/var/lib/canva-image-toolkit}"
TOOLKIT_DOMAIN_DEFAULT="43.156.64.19.sslip.io"

for command_name in git docker curl openssl; do
  command -v "$command_name" >/dev/null || {
    echo "Missing required command: $command_name" >&2
    exit 1
  }
done
docker compose version >/dev/null
sudo install -d -o "$(id -u)" -g "$(id -g)" "$STATE_DIR"

if [[ -d "$DEPLOY_DIR/.git" ]]; then
  if [[ -n "$(git -C "$DEPLOY_DIR" status --porcelain)" ]]; then
    echo "Deployment checkout has local changes; refusing to overwrite them." >&2
    exit 1
  fi
  git -C "$DEPLOY_DIR" rev-parse HEAD >"$STATE_DIR/previous-deploy"
  git -C "$DEPLOY_DIR" fetch --prune origin "$DEPLOY_BRANCH"
  git -C "$DEPLOY_DIR" switch --detach "origin/$DEPLOY_BRANCH"
else
  sudo install -d -o "$(id -u)" -g "$(id -g)" "$DEPLOY_DIR"
  git clone --branch "$DEPLOY_BRANCH" --single-branch "$REPOSITORY_URL" "$DEPLOY_DIR"
fi

cd "$DEPLOY_DIR"
if [[ ! -f .env ]]; then
  umask 077
  cp .env.example .env
  token="$(openssl rand -hex 32)"
  sed -i \
    -e 's/^APP_ENV=.*/APP_ENV=production/' \
    -e "s/^API_AUTH_TOKEN=.*/API_AUTH_TOKEN=$token/" \
    -e 's|^CORS_ORIGINS=.*|CORS_ORIGINS=https://app-aahognuahcw.canva-apps.com|' \
    -e "s/^TOOLKIT_DOMAIN=.*/TOOLKIT_DOMAIN=${TOOLKIT_DOMAIN:-$TOOLKIT_DOMAIN_DEFAULT}/" \
    -e 's/^MAX_CONCURRENT_REQUESTS=.*/MAX_CONCURRENT_REQUESTS=2/' \
    -e 's/^MAX_BATCH_FILES=.*/MAX_BATCH_FILES=10/' \
    .env
  unset token
fi
chmod 600 .env

if ! grep -Eq '^API_AUTH_TOKEN=.{24,}$' .env; then
  echo "Production API token is missing or too short." >&2
  exit 1
fi

if ss -ltn '( sport = :80 or sport = :443 )' | tail -n +2 | grep -q .; then
  existing="$(docker compose -p canva-image-toolkit -f docker-compose.yml -f deploy/docker-compose.prod.yml ps -q caddy 2>/dev/null || true)"
  if [[ -z "$existing" ]]; then
    echo "Ports 80 or 443 are already occupied; refusing to disrupt an existing proxy." >&2
    exit 1
  fi
fi

docker compose -p canva-image-toolkit -f docker-compose.yml -f deploy/docker-compose.prod.yml config --quiet
docker compose -p canva-image-toolkit -f docker-compose.yml -f deploy/docker-compose.prod.yml up -d --build

for _attempt in $(seq 1 30); do
  if curl --fail --silent http://127.0.0.1:8000/health >/dev/null; then
    break
  fi
  sleep 2
done
curl --fail --silent http://127.0.0.1:8000/health >/dev/null
api_token="$(sed -n 's/^API_AUTH_TOKEN=//p' .env)"
curl --fail --silent -H "Authorization: Bearer $api_token" http://127.0.0.1:8000/v1/providers >/dev/null
unset api_token
git rev-parse HEAD >"$STATE_DIR/deployed-commit"
echo "Deployment completed and authenticated smoke tests passed."
