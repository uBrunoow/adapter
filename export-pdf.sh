#!/usr/bin/env bash
# Gera adapter.pdf (14 páginas 1920×1080) a partir do index.html usando o Chrome headless.
set -euo pipefail
cd "$(dirname "$0")"
CHROME=$(command -v google-chrome || command -v chromium || command -v chromium-browser)
"$CHROME" --headless=new --no-sandbox --disable-gpu --no-pdf-header-footer \
  --virtual-time-budget=8000 --run-all-compositor-stages-before-draw \
  --print-to-pdf="adapter.pdf" "file://$PWD/index.html?pdf" 2>/dev/null
echo "PDF gerado: $PWD/adapter.pdf"
