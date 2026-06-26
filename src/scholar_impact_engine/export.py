from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .config import PipelineConfig


def _prepare_dataframe(results: list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(results)
    if "publications_missing_identifier" in frame.columns:
        frame["publications_missing_identifier"] = frame[
            "publications_missing_identifier"
        ].apply(
            lambda value: json.dumps(value, ensure_ascii=False)
            if isinstance(value, list)
            else value
        )
    return frame


def export_results(
    results: list[dict[str, Any]],
    config: PipelineConfig,
) -> dict[str, Path]:
    config.output_directory.mkdir(parents=True, exist_ok=True)
    frame = _prepare_dataframe(results)
    written: dict[str, Path] = {}

    for fmt in config.output_formats:
        if fmt == "csv":
            path = config.output_directory / f"{config.output_basename}.csv"
            frame.to_csv(path, index=False)
            written["csv"] = path
        elif fmt == "json":
            path = config.output_directory / f"{config.output_basename}.json"
            with path.open("w", encoding="utf-8") as handle:
                json.dump(results, handle, indent=2, ensure_ascii=False)
            written["json"] = path
        elif fmt in {"xlsx", "excel"}:
            path = config.output_directory / f"{config.output_basename}.xlsx"
            frame.to_excel(path, index=False)
            written["xlsx"] = path
        else:
            raise ValueError(f"Unsupported output format: {fmt}")

    return written
