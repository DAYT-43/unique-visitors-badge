#!/usr/bin/env python3
"""Лаконичная аналитика из накопленной истории traffic_history.json.

GitHub Traffic API отдаёт только скользящее окно 14 дней. Проект каждый день
снимает срез (views/clones count+uniques) — эта история позволяет строить
тренды и оценки за произвольный период (месяц, год), не претендуя на
точные «уникальные за месяц» (их GitHub не хранит и не отдаёт).

Что считаем (честно):
- период сбора и число срезов;
- последний срез (актуальное окно 14d);
- максимум уникальных в 14-дневном окне за период — оценка охвата;
- сумму count по срезам за период — ВЕРХНЯЯ граница просмотров
  (окна пересекаются: один хит попадает в ~14 срезов);
- тренд: каждый срез (дата → views/clones uniques).

Пишет analytics.json (лаконичный, готов для бейджей/графиков).
Используется в GitHub Actions после update_traffic.py.
"""
import json
from datetime import date, datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
HISTORY_FILE = BASE_DIR / "traffic_history.json"
ANALYTICS_FILE = BASE_DIR / "analytics.json"


def summarize(records: dict, days: int | None = None) -> dict | None:
    """Сводка по всем срезам за последние `days` дней (None — все)."""
    dates = sorted(records)
    if not dates:
        return None
    if days is not None:
        cutoff = date.today().toordinal() - days
        dates = [d for d in dates if date.fromisoformat(d).toordinal() >= cutoff]
    if not dates:
        return None

    views_count = [records[d]["views_count"] for d in dates]
    views_uniques = [records[d]["views_uniques"] for d in dates]
    clones_count = [records[d]["clones_count"] for d in dates]
    clones_uniques = [records[d]["clones_uniques"] for d in dates]

    return {
        "samples": len(dates),
        "start": dates[0],
        "end": dates[-1],
        "views": {
            "last_count": views_count[-1],
            "last_uniques": views_uniques[-1],
            "max_count": max(views_count),
            "max_uniques": max(views_uniques),
            "sum_count": sum(views_count),  # верхняя граница (окна пересекаются)
        },
        "clones": {
            "last_count": clones_count[-1],
            "last_uniques": clones_uniques[-1],
            "max_count": max(clones_count),
            "max_uniques": max(clones_uniques),
            "sum_count": sum(clones_count),  # верхняя граница (окна пересекаются)
        },
    }


def main() -> None:
    if not HISTORY_FILE.exists():
        raise SystemExit("traffic_history.json not found")

    history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    if not history:
        raise SystemExit("traffic_history.json is empty")

    all_ = summarize(history)
    month = summarize(history, days=30)
    week = summarize(history, days=7)
    today = date.today().isoformat()

    def fmt(s: dict | None) -> str:
        if s is None:
            return "  (нет данных за период)"
        v, c = s["views"], s["clones"]
        return (
            f"  срезов: {s['samples']} ({s['start']}…{s['end']})\n"
            f"  views : last {v['last_count']}/{v['last_uniques']} | max {v['max_count']}/{v['max_uniques']} | sum {v['sum_count']}\n"
            f"  clones: last {c['last_count']}/{c['last_uniques']} | max {c['max_count']}/{c['max_uniques']} | sum {c['sum_count']}"
        )

    print(f"=== Аналитика unique-visitors-badge ({today}) ===")
    print(f"Всё время:")
    print(fmt(all_))
    print(f"Последние 30 дней:")
    print(fmt(month))
    print(f"Последние 7 дней:")
    print(fmt(week))

    print("\nТренд (дата -> views uniques / clones uniques):")
    for d in sorted(history):
        r = history[d]
        print(f"  {d}: {r['views_uniques']} / {r['clones_uniques']}")

    print("\nПояснение: sum_count — верхняя граница (каждый хит попадает в ~14 срезов).")
    print("max_uniques — максимум уникальных в 14-дневном окне за период (оценка охвата).")
    print("Точных «уникальных за месяц» GitHub не хранит — это ограничение API.")

    analytics = {
        "generated": today,
        "period": {
            "start": all_["start"],
            "end": all_["end"],
            "samples": all_["samples"],
        },
        "all": all_,
        "last_30d": month,
        "last_7d": week,
        "trend": [
            {"date": d, "views_uniques": r["views_uniques"], "clones_uniques": r["clones_uniques"]}
            for d, r in sorted(history.items())
        ],
    }
    ANALYTICS_FILE.write_text(
        json.dumps(analytics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nanalytics.json -> {ANALYTICS_FILE.name} ({ANALYTICS_FILE.stat().st_size} B)")


if __name__ == "__main__":
    main()
