from __future__ import annotations

import logging
from typing import Any

from pybliometrics.scopus import AuthorRetrieval

from .citations import accumulate_citations_by_period
from .config import PipelineConfig
from .periods import assign_date, parse_cover_date, zero_period_counts

logger = logging.getLogger(__name__)


def _affiliation_fields(author: AuthorRetrieval) -> tuple[str | None, str | None]:
    if not author.affiliation_current:
        return None, None

    affiliation = author.affiliation_current[0]
    preferred = affiliation[5] if len(affiliation) > 5 else None
    parent = affiliation[6] if len(affiliation) > 6 else None
    return preferred, parent


def compute_author_metrics(author_id: int, config: PipelineConfig) -> dict[str, Any]:
    author = AuthorRetrieval(author_id, view="ENHANCED")
    preferred_affiliation, parent_affiliation = _affiliation_fields(author)

    publication_counts = zero_period_counts(config.time_periods)
    citation_counts = zero_period_counts(config.time_periods)
    missing_identifiers: list[str] = []

    for document in author.get_documents():
        cover_date = parse_cover_date(document.coverDate)
        period_name = assign_date(cover_date, config.time_periods)
        if period_name is not None:
            publication_counts[period_name] += 1

        accumulate_citations_by_period(
            document,
            config,
            citation_counts,
            missing_identifiers,
        )

    total_citations = sum(citation_counts.values())

    row: dict[str, Any] = {
        "scopus_id": author_id,
        "last_name": author.surname,
        "first_name": author.given_name,
        "affiliation_current": preferred_affiliation,
        "affiliation_parent": parent_affiliation,
        "publications_total": author.document_count,
        "citations_total": total_citations,
        "h_index": author.h_index,
        "publications_missing_identifier": missing_identifiers,
    }

    for period in config.time_periods:
        row[f"publications_{period.name}"] = publication_counts[period.name]
        row[f"citations_{period.name}"] = citation_counts[period.name]

    return row


def compute_author_metrics_safe(
    author_id: int,
    config: PipelineConfig,
) -> dict[str, Any]:
    try:
        return compute_author_metrics(author_id, config)
    except Exception as exc:  # noqa: BLE001 - keep batch running on single-author failures
        logger.exception("Failed to process author %s", author_id)
        return {
            "scopus_id": author_id,
            "error": str(exc),
        }
