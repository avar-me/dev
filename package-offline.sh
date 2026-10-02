#!/usr/bin/env bash
# Собрать сайт и упаковать docs/ в zip для офлайн-использования без интернета.
#
# Использование:  ./package-offline.sh
# Результат:       dist/avar-offline-<id>-<дата>.zip
#
# Данные словаря (data/*.json, index.words.txt и т.д.) зашиваются прямо в
# JS (offline-data.js), а fetch() подменяется шимом (src/offline/fetch-shim.js)
# на чтение из них — поэтому index.html/phrases.html открываются двойным
# кликом через file://, без HTTP-сервера и без интернета. TMA (docs/tma/)
# в архив не упаковывается — Telegram Mini App без Telegram не нужен.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "=== 1. Сборка сайта (./build.sh) ==="
"$ROOT/build.sh"

DOCS="${ROOT}/docs"

echo ""
echo "=== 2. Зашиваем data/ в offline-data.js ==="
python3 "$ROOT/src/offline/embed_data.py" "$DOCS"
cp "$ROOT/src/offline/fetch-shim.js" "$DOCS/offline-fetch-shim.js"

declare -A HTML_JS=( [index.html]=app.js [phrases.html]=phrases.js )
for html in "${!HTML_JS[@]}"; do
  cp "$DOCS/$html" "$DOCS/$html.orig"
  js="${HTML_JS[$html]}"
  perl -i -pe "s{(<script src=\"${js}\?)}{<script src=\"offline-data.js\"></script>\n    <script src=\"offline-fetch-shim.js\"></script>\n    \$1}" "$DOCS/$html"
done

PROFILE_ID="$(python3 -c "import json; print(json.load(open('profile.json'))['id'])")"
DATE_TAG="$(date +%Y-%m-%d)"
DIST="${ROOT}/dist"
ZIP_NAME="avar-offline-${PROFILE_ID}-${DATE_TAG}.zip"

echo ""
echo "=== 3. Упаковка docs/ (без tma/) в архив ==="
mkdir -p "$DIST"
rm -f "${DIST}/${ZIP_NAME}"

cat > "${DOCS}/README-OFFLINE.txt" <<'EOF'
Аварский словарь — офлайн-копия dev.avar.me
============================================

Откройте index.html двойным кликом — сработает без интернета и без
локального сервера, все данные уже внутри (offline-data.js).

Шрифты (Onest, Literata) грузятся с Google Fonts — без интернета
просто откатятся на системный шрифт, на работу словаря это не влияет.
EOF

( cd "$DOCS" && zip -r -q "${DIST}/${ZIP_NAME}" . -x 'tma/*' '*.orig' )
rm -f "${DOCS}/README-OFFLINE.txt" "${DOCS}/offline-data.js" "${DOCS}/offline-fetch-shim.js"
for html in index.html phrases.html; do
  mv "${DOCS}/$html.orig" "${DOCS}/$html"
done

echo ""
echo "Готово: ${DIST}/${ZIP_NAME}"
du -h "${DIST}/${ZIP_NAME}"
