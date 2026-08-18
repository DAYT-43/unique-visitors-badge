#!/usr/bin/env python3
"""Сбор данных GitHub Traffic API и генерация бейджей посетителей.

Берёт срез traffic/views (и clones) целевого репозитория, накапливает историю
в traffic_history.json (GitHub хранит трафик только 14 дней — историю ведём сами)
и генерирует два файла в формате shields.io endpoint badge:
- badge.json  — «unique visitors (14d)» (уникальные посетители за окно 14 дней);
- views.json  — «views (14d)» (просмотры за окно 14 дней).

Используется в GitHub Actions (см. .github/workflows/update-badge.yml).
Требует env: GH_TOKEN (PAT с доступом к целевому репозиторию), TARGET_REPO.
"""
import json
import os
import urllib.request
from datetime import date
from pathlib import Path

API = "https://api.github.com/repos"
TARGET_REPO = os.environ.get("TARGET_REPO", "DAYT-43/DAYT-43")
TOKEN = os.environ.get("GH_TOKEN", "")

BASE_DIR = Path(__file__).resolve().parent.parent
HISTORY_FILE = BASE_DIR / "traffic_history.json"
BADGE_FILE = BASE_DIR / "badge.json"
VIEWS_BADGE_FILE = BASE_DIR / "views.json"


def api_get(path: str) -> dict:
    req = urllib.request.Request(
        f"{API}/{TARGET_REPO}/{path}",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "unique-visitors-badge",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def load_history() -> dict:
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    return {}


def main() -> None:
    if not TOKEN:
        raise SystemExit("GH_TOKEN not set")

    views = api_get("traffic/views")
    clones = api_get("traffic/clones")

    today = date.today().isoformat()
    history = load_history()
    history[today] = {
        "views_count": views.get("count", 0),
        "views_uniques": views.get("uniques", 0),
        "clones_count": clones.get("count", 0),
        "clones_uniques": clones.get("uniques", 0),
    }
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    badge = {
        "schemaVersion": 1,
        "label": "unique visitors (14d)",
        "message": str(views.get("uniques", 0)),
        "color": "blue",
        "cacheSeconds": 3600,
    }
    BADGE_FILE.write_text(
        json.dumps(badge, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    views_badge = {
        "schemaVersion": 1,
        "label": "views (14d)",
        "message": str(views.get("count", 0)),
        "color": "blue",
        "cacheSeconds": 3600,
    }
    VIEWS_BADGE_FILE.write_text(
        json.dumps(views_badge, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"{today}: unique visitors = {views.get('uniques', 0)}, views = {views.get('count', 0)}")


if __name__ == "__main__":
    main()
