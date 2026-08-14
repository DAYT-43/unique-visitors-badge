# unique-visitors-badge

Автообновляемый бейдж **уникальных** посетителей страницы профиля GitHub, построенный на официальном GitHub Traffic API.

![Unique visitors](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/DAYT-43/unique-visitors-badge/main/badge.json)

## Описание

Бейджи вроде `visitor-badge.laobi.icu` считают **хиты** (просмотры страницы), а не уникальных пользователей: GitHub проксирует изображения README через Camo, подменяя IP и cookie, поэтому сторонние сервисы физически не могут определить уникальных посетителей.

Этот проект решает проблему честно: GitHub Traffic API возвращает реальные `uniques` (уникальные посетители) за последние 14 дней, а GitHub Actions раз в день снимает срез и накапливает историю. Бейдж показывает актуальное значение за окно 14 дней в стиле shields.io — как остальные бейджи профиля.

## Почему это интересно (ход мысли)

1. **Проблема**: бейдж визитов считает хиты, а не уникальных. Хиты растут при каждом открытии README, даже одним человеком.
2. **Корень проблемы — Camo**: GitHub проксирует изображения в README, подменяя IP и cookie. Поэтому сервисы-бейджи не могут считать уникальных по IP — они видят только IP прокси GitHub.
3. **Открытие**: у GitHub есть Traffic API для репозиториев — `GET /repos/{owner}/{repo}/traffic/views` возвращает `count` и `uniques` за последние 14 дней. Это официальные данные, которые знает сам GitHub.
4. **Ограничение**: данные хранятся только 14 дней → без регулярных срезов статистика теряется. Решение — раз в день накапливать историю в `traffic_history.json`.
5. **Бейдж**: из истории генерируется `badge.json` по schema shields.io endpoint badge, и в README ставится `https://img.shields.io/endpoint?url=...` — стиль совпадает с остальными бейджами профиля.
6. **Честная метрика**: «unique visitors (14d)». Суммировать уникальных из разных окон нельзя из-за пересечений — показываем актуальное окно.

## Установка / Запуск

Для владельца профиля (скопировать в свой аккаунт):

1. Создать репозиторий `unique-visitors-badge` (или форкнуть этот).
2. Добавить секрет **`GH_TOKEN`** в `Settings → Secrets and variables → Actions` — PAT с доступом к целевому репозиторию (чью статистику считаем, например `OWNER/OWNER` для README профиля).
3. Скопировать файлы: `.github/workflows/update-badge.yml`, `scripts/update_traffic.py`.
4. Указать целевой репозиторий в настройках workflow/скрипта (переменная `TARGET_REPO`).
5. В README профиля добавить бейдж:

```markdown
![Unique visitors](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/OWNER/unique-visitors-badge/main/badge.json)
```

Запуск:

```bash
# ручной запуск workflow из Actions → Update traffic badge → Run workflow
# либо дождаться ежедневного cron (по расписанию)
```

## Структура проекта

```
unique-visitors-badge/
├── .github/
│   └── workflows/
│       └── update-badge.yml     # ежедневный cron + workflow_dispatch
├── scripts/
│   └── update_traffic.py        # сбор Traffic API + генерация badge.json
├── badge.json                   # сгенерированные данные для shields.io endpoint
├── traffic_history.json         # накопленная история срезов (views/clones)
├── README.md
└── LICENSE
```

## Решения (ADR-lite)

| Проблема | Решение | Почему |
|---|---|---|
| Camo-прокси не даёт считать уникальных по IP | GitHub Traffic API | Официальные данные о `uniques` знает только сам GitHub |
| Данные трафика хранятся 14 дней | Накопление истории в `traffic_history.json` | Без регулярных срезов статистика теряется |
| Суммировать уникальных из окон нельзя (пересечения) | Метрика «unique visitors (14d)» | Честная цифра за актуальное окно, без завышения |
| Единый стиль бейджей профиля | shields.io endpoint badge | `img.shields.io/endpoint?url=badge.json` — тот же стиль, что и остальные бейджи |
| Доступ к Traffic API | Секрет `GH_TOKEN` (PAT) | Токен не попадает в логи и не публикуется в репозитории |

## Стек

- Python — скрипт сбора и генерации `badge.json`
- GitHub Actions — расписание (cron) + ручной запуск (`workflow_dispatch`)
- GitHub REST API — `traffic/views`, `traffic/clones`
- shields.io — endpoint badge
- JSON — хранение данных и обмен с shields.io
- git — версионирование и публикация

## Лицензия

MIT

## Контакты

Дмитрий (DAYT-43) — https://github.com/DAYT-43
