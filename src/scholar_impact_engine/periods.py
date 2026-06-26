from __future__ import annotations

from datetime import date

from .config import TimePeriod


def parse_cover_date(cover_date: str) -> date:
    """Parse Scopus coverDate values such as 2018-05-02."""
    return date.fromisoformat(cover_date)


def assign_date(value: date, periods: list[TimePeriod]) -> str | None:
    for period in periods:
        if period.start and value < period.start:
            continue
        if period.end and value > period.end:
            continue
        return period.name
    return None


def assign_year(year: int, periods: list[TimePeriod]) -> str | None:
    # CitationOverview returns yearly counts; mid-year is a stable assignment rule.
    return assign_date(date(year, 6, 15), periods)


def zero_period_counts(periods: list[TimePeriod]) -> dict[str, int]:
    return {period.name: 0 for period in periods}
