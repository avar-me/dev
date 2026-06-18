#!/usr/bin/env bash
# Сборка статического сайта dev.avar.me.
#
# Использование:  ./build.sh
# Локальная проверка: python3 -m http.server -d docs 8000
#
# Источник данных — https://sources.avar.me/data/av-ru.jsonl. Скачивается во
# временный файл, в репозитории JSONL не хранится.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

JSONL_URL="${JSONL_URL:-https://sources.avar.me/data/av-ru.jsonl}"
JSONL_FILE="${ROOT}/av-ru.jsonl"
DOCS="${ROOT}/docs"
TPL="${ROOT}/src/templates"

echo "=== 1. Скачать av-ru.jsonl ==="
curl -fsSL "$JSONL_URL" -o "$JSONL_FILE"
wc -l "$JSONL_FILE"

echo ""
echo "=== 2. Очистка docs/ и копирование шаблонов ==="
rm -rf "$DOCS"
mkdir -p "$DOCS/tma"
cp "$TPL/html/index.html" "$TPL/html/app.js" "$TPL/html/styles.css" "$DOCS/"
cp "$TPL/html/favicon.ico" "$TPL/html/favicon-32.png" "$TPL/html/favicon-192.png" "$DOCS/"
cp "$TPL/tma/index.html"  "$TPL/tma/app.js"  "$TPL/tma/styles.css"  "$DOCS/tma/"

echo ""
echo "=== 3. build_data.py (av-ru.jsonl → docs/data/) ==="
DICTIONARY_JSONL="$JSONL_FILE" DOCS_ROOT="$DOCS" python3 "$ROOT/src/build_data.py"

echo ""
echo "=== 4. Cache-bust (__ASSET_VERSION__ → build_id) ==="
export DOCS_ROOT="$DOCS"
python3 - <<'PY'
import json, os
from pathlib import Path

docs = Path(os.environ["DOCS_ROOT"])
manifest = json.loads((docs / "data/av-ru/manifest.json").read_text(encoding="utf-8"))
build_id = manifest.get("build_id") or manifest.get("build_date", "").replace(":", "").replace("-", "")[:15]
target = docs / "index.html"
text = target.read_text(encoding="utf-8")
if "__ASSET_VERSION__" in text:
    target.write_text(text.replace("__ASSET_VERSION__", build_id), encoding="utf-8")
print(f"build_id={build_id}")
PY

if [ ! -f "$DOCS/index.html" ]; then
  echo "build.sh: docs/index.html не создан" >&2
  exit 1
fi

echo ""
echo "Готово. Локально:  python3 -m http.server -d docs 8000"
