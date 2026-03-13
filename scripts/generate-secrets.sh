#!/usr/bin/env bash
set -euo pipefail

gen() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 32
    return
  fi
  if command -v python3 >/dev/null 2>&1; then
    python3 - <<'PY'
import secrets
print(secrets.token_hex(32))
PY
    return
  fi
  echo "ERROR: need openssl or python3 to generate secrets" >&2
  exit 1
}

cat <<EOF
POSTGRES_PASSWORD=$(gen)
REDIS_PASSWORD=$(gen)
SECRET_KEY=$(gen)
JWT_SECRET_KEY=$(gen)
OPENVAS_PASSWORD=$(gen)
EOF

