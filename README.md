# dev.avar.me

Аварско-русский словарь — статический сайт, публикуется через GitHub Pages: <https://dev.avar.me>.

Данные не хранятся в этом репозитории. При сборке выкачивается `av-ru.jsonl` из [sources.avar.me](https://sources.avar.me) — это единственный источник правды. Любые правки данных делайте в репозитории [`avar-me/sources`](https://github.com/avar-me/sources); после его пересборки можно дернуть workflow здесь (раз в сутки запускается автоматически) и сайт подтянет свежие данные.

## Структура

```
.
├── .github/workflows/deploy.yml   # Сборка и публикация на Pages
├── CNAME                          # dev.avar.me
├── build.sh                       # Локальная сборка
└── src/
    ├── build_data.py              # JSONL → chunks/, browse.json, индексы, манифест
    └── templates/
        ├── html/                  # index.html, app.js, styles.css — основной сайт
        └── tma/                   # index.html, app.js, styles.css — Telegram Mini App
```

Все, что не в этом списке — артефакт сборки и в репо не лежит.

## Сборка локально

```bash
./build.sh
python3 -m http.server -d docs 8000
# открыть http://localhost:8000
```

`build.sh` скачивает `av-ru.jsonl` из sources.avar.me, кладет шаблоны в `docs/`, запускает `src/build_data.py`, проставляет cache-bust по `build_id` манифеста.

URL источника можно переопределить:

```bash
JSONL_URL=https://example.com/foo.jsonl ./build.sh
```

## Деплой

`git push origin main` → GitHub Actions собирает `docs/` и публикует на Pages. Также workflow запускается по расписанию раз в сутки (cron) и вручную через `workflow_dispatch` — чтобы подхватить правки на sources.avar.me без push в этот репозиторий.

## Что менять

| Хочется поменять | Куда лезть |
|------------------|-----------|
| Опечатку / перевод / пример | [`avar-me/sources`](https://github.com/avar-me/sources), `data/av-ru.jsonl` |
| Внешний вид сайта | `src/templates/html/styles.css` (или `tma/styles.css`) |
| Логику поиска / саджестов / рандомайзера | `src/templates/html/app.js` |
| Сборку данных | `src/build_data.py` |
| Доменное имя | `CNAME` |
| Деплой | `.github/workflows/deploy.yml` |

Никогда не правьте `docs/` руками — оно перезаписывается при каждой сборке.

## Лицензии

- Код — MIT.
- Данные — см. `sources.json` в [`avar-me/sources`](https://github.com/avar-me/sources).

---

Координация: Telegram-канал [@avarlangme](https://t.me/avarlangme). Чат правок: [@avarme_chat](https://t.me/avarme_chat). Связь: [admin@avar.me](mailto:admin@avar.me).
