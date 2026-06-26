from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .config import load_config
from .export import export_results
from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scholar-impact-engine",
        description=(
            "Scholar Impact Engine — measure time-stratified scholarly impact "
            "for a cohort of Scopus authors."
        ),
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to YAML configuration file (default: config.yaml)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    config_path = Path(args.config)
    if not config_path.exists():
        logging.error("Config file not found: %s", config_path)
        logging.error("Copy config.example.yaml to config.yaml and edit it.")
        return 1

    config = load_config(config_path)
    results = run_pipeline(config)
    written = export_results(results, config)

    for fmt, path in written.items():
        logging.info("Wrote %s output to %s", fmt.upper(), path)

    failures = [row for row in results if "error" in row]
    if failures:
        logging.warning("%s author(s) failed; see error column in output.", len(failures))

    return 0


if __name__ == "__main__":
    sys.exit(main())
