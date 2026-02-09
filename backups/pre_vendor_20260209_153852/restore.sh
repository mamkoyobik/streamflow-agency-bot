#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cp "$ROOT/backups/pre_vendor_20260209_153852/index.html" "$ROOT/web/index.html"
cp "$ROOT/backups/pre_vendor_20260209_153852/styles.css" "$ROOT/web/styles.css"
cp "$ROOT/backups/pre_vendor_20260209_153852/app.js" "$ROOT/web/app.js"
echo "Restored web/index.html, web/styles.css, web/app.js from pre_vendor_20260209_153852"
