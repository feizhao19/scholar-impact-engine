from datetime import date

import pytest

from scholar_impact_engine.config import TimePeriod
from scholar_impact_engine.periods import assign_date, assign_year, parse_cover_date


PERIODS = [
    TimePeriod(name="before_2017", start=None, end=date(2016, 12, 31)),
    TimePeriod(
        name="period_2017_2021",
        start=date(2017, 1, 1),
        end=date(2021, 12, 31),
    ),
    TimePeriod(name="after_2021", start=date(2022, 1, 1), end=None),
]


def test_parse_cover_date():
    assert parse_cover_date("2018-05-02") == date(2018, 5, 2)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (date(2015, 1, 1), "before_2017"),
        (date(2016, 12, 31), "before_2017"),
        (date(2017, 1, 1), "period_2017_2021"),
        (date(2021, 12, 31), "period_2017_2021"),
        (date(2022, 1, 1), "after_2021"),
    ],
)
def test_assign_date(value, expected):
    assert assign_date(value, PERIODS) == expected


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (2016, "before_2017"),
        (2017, "period_2017_2021"),
        (2021, "period_2017_2021"),
        (2022, "after_2021"),
    ],
)
def test_assign_year(year, expected):
    assert assign_year(year, PERIODS) == expected
