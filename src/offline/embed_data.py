#!/usr/bin/env python3
"""Зашивает data/ основного сайта (не TMA) в один JS-файл offline-data.js,
чтобы index.html/phrases.html можно было открыть прямо через file://, без
HTTP-сервера. Используется только package-offline.sh, на собранный
dev.avar.me не влияет.

Ключи — относительные пути вида "data/av-ru/manifest.json", как их просит
fetch() в app.js/phrases.js (после assetUrl() и обрезки ?v=...).
"""
import json
import sys
from pathlib import Path


def main() -> None:
    docs = Path(sys.argv[1])
    data_dir = docs / "data"
    if not data_dir.is_dir():
        print(f"embed_data.py: {data_dir} не найден", file=sys.stderr)
        sys.exit(1)

    embedded: dict[str, str] = {}
    for path in sorted(data_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in (".json", ".txt"):
            continue
        key = path.relative_to(docs).as_posix()
        embedded[key] = path.read_text(encoding="utf-8")

    out = docs / "offline-data.js"
    out.write_text(
        "window.__OFFLINE_DATA__ = " + json.dumps(embedded, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    size_mb = out.stat().st_size / (1024 * 1024)
    print(f"  offline-data.js: {len(embedded)} файлов, {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
