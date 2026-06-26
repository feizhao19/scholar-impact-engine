from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd
from tqdm import tqdm

from .author import compute_author_metrics_safe
from .config import PipelineConfig, load_config

logger = logging.getLogger(__name__)


def read_author_ids(config: PipelineConfig) -> list[int]:
    if config.input_has_header:
        frame = pd.read_csv(config.input_file)
        id_column = config.author_id_column
    else:
        frame = pd.read_csv(
            config.input_file,
            header=None,
            names=[config.author_id_column],
        )
        id_column = config.author_id_column

    if id_column not in frame.columns:
        raise ValueError(
            f"Column '{id_column}' not found in {config.input_file}. "
            f"Available columns: {list(frame.columns)}"
        )

    author_ids = []
    for value in frame[id_column].dropna().tolist():
        author_ids.append(int(value))

    if config.max_authors is not None:
        author_ids = author_ids[: config.max_authors]

    if not author_ids:
        raise ValueError(f"No author IDs found in {config.input_file}")

    return author_ids


def run_pipeline(config: PipelineConfig) -> list[dict[str, Any]]:
    author_ids = read_author_ids(config)
    results: list[dict[str, Any]] = []

    for author_id in tqdm(author_ids, desc="Processing authors"):
        results.append(compute_author_metrics_safe(author_id, config))

    return results


def run_pipeline_from_config_path(config_path: str | Path) -> list[dict[str, Any]]:
    config = load_config(config_path)
    return run_pipeline(config)
