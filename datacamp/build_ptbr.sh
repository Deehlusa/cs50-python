#!/usr/bin/env bash
# Build do futurecoder PT-BR: reaplica overrides, desliga firebase (sem login),
# desliga precache (sem service worker travando build velho).
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Aplicando patches (futurecoder-patches/ e a fonte de verdade -> clone)"
( cd futurecoder-patches && find . -type f ! -name README.md -print0 ) | while IFS= read -r -d '' f; do
  dest=".futurecoder-src/${f#./}"
  mkdir -p "$(dirname "$dest")"
  cp "futurecoder-patches/${f#./}" "$dest"
done

echo "==> Reaplicando overrides PT-BR (idempotente)"
python3 scripts_ptbr/merge_overrides.py

echo "==> Build (REACT_APP_DISABLE_FIREBASE=true, sem precache)"
cd .futurecoder-src/frontend
REACT_APP_LANGUAGE=br REACT_APP_DISABLE_FIREBASE=true CI=false npm run build

echo "==> Pronto. Rode:  python3 datacamp/server.py  ->  http://localhost:8000/course/"
