from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class TimePeriod:
    name: str
    start: date | None
    end: date | None


@dataclass(frozen=True)
class PipelineConfig:
    input_file: Path
    author_id_column: str
    input_has_header: bool
    time_periods: list[TimePeriod]
    citation_start_year: int
    identifier_priority: list[str]
    output_directory: Path
    output_basename: str
    output_formats: list[str]
    max_authors: int | None


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _parse_periods(raw_periods: list[dict[str, Any]]) -> list[TimePeriod]:
    if not raw_periods:
        raise ValueError("At least one time period is required.")

    periods: list[TimePeriod] = []
    for item in raw_periods:
        name = item.get("name")
        if not name:
            raise ValueError("Each time period must have a name.")

        start = _parse_date(item["start"]) if "start" in item else None
        end = _parse_date(item["end"]) if "end" in item else None
        if start is None and end is None:
            raise ValueError(f"Period '{name}' must define start and/or end.")

        periods.append(TimePeriod(name=name, start=start, end=end))

    return periods


def load_config(path: str | Path) -> PipelineConfig:
    config_path = Path(path)
    with config_path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    input_cfg = raw.get("input", {})
    citation_cfg = raw.get("citation", {})
    output_cfg = raw.get("output", {})

    input_file = Path(input_cfg.get("file", "data/sample_author_ids.csv"))
    if not input_file.is_absolute():
        input_file = (config_path.parent / input_file).resolve()

    output_directory = Path(output_cfg.get("directory", "outputs"))
    if not output_directory.is_absolute():
        output_directory = (config_path.parent / output_directory).resolve()

    identifier_priority = citation_cfg.get("identifier_priority", ["doi", "pubmed_id"])
    allowed = {"doi", "pubmed_id"}
    unknown = set(identifier_priority) - allowed
    if unknown:
        raise ValueError(f"Unsupported citation identifiers: {sorted(unknown)}")

    return PipelineConfig(
        input_file=input_file,
        author_id_column=input_cfg.get("author_id_column", "scopus_id"),
        input_has_header=bool(input_cfg.get("has_header", True)),
        time_periods=_parse_periods(raw.get("time_periods", [])),
        citation_start_year=int(citation_cfg.get("start_year", 2000)),
        identifier_priority=identifier_priority,
        output_directory=output_directory,
        output_basename=output_cfg.get("basename", "author_metrics"),
        output_formats=[fmt.lower() for fmt in output_cfg.get("formats", ["csv", "json"])],
        max_authors=raw.get("max_authors"),
    )
