from __future__ import annotations

from decimal import Decimal

from app.models.enums import DayOfWeek

# Russian day names, matching the sample plan ("Среда (Crossfit)").
DAY_NAMES_RU: dict[DayOfWeek, str] = {
    DayOfWeek.MON: "Понедельник",
    DayOfWeek.TUE: "Вторник",
    DayOfWeek.WED: "Среда",
    DayOfWeek.THU: "Четверг",
    DayOfWeek.FRI: "Пятница",
    DayOfWeek.SAT: "Суббота",
    DayOfWeek.SUN: "Воскресенье",
}


def day_name(day: DayOfWeek) -> str:
    return DAY_NAMES_RU.get(day, day.value)


def plural_ru(n: int, one: str, few: str, many: str) -> str:
    """Russian pluralization (1 серия, 2 серии, 5 серий)."""
    n = abs(n)
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


def sets_label(sets: int) -> str:
    return f"{sets} {plural_ru(sets, 'серия', 'серии', 'серий')}"


def format_weight(weight: Decimal) -> str:
    """Render 8.00 -> '8', 7.50 -> '7.5'."""
    normalized = weight.normalize()
    text = format(normalized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"
