from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from pybliometrics.scopus import CitationOverview

from .config import PipelineConfig
from .periods import assign_year, zero_period_counts

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DocumentIdentifiers:
    doi: str | None
    pii: str | None
    pubmed_id: str | None
    title: str | None


def extract_identifiers(document: Any) -> DocumentIdentifiers:
    return DocumentIdentifiers(
        doi=getattr(document, "doi", None),
        pii=getattr(document, "pii", None),
        pubmed_id=getattr(document, "pubmed_id", None),
        title=getattr(document, "title", None),
    )


def choose_identifier(
    identifiers: DocumentIdentifiers,
    priority: list[str],
) -> tuple[str, str] | None:
    mapping = {
        "doi": identifiers.doi,
        "pubmed_id": identifiers.pubmed_id,
    }
    for key in priority:
        value = mapping.get(key)
        if value:
            return value, key
    return None


def fetch_yearly_citations(
    identifier: str,
    id_type: str,
    start_year: int,
) -> list[tuple[int, int]]:
    overview = CitationOverview([identifier], start=start_year, id_type=id_type)
    if not overview.cc:
        return []
    return [(int(year), int(count)) for year, count in overview.cc[0]]


def accumulate_citations_by_period(
    document: Any,
    config: PipelineConfig,
    citation_counts: dict[str, int],
    missing_titles: list[str],
) -> None:
    identifiers = extract_identifiers(document)
    chosen = choose_identifier(identifiers, config.identifier_priority)

    if chosen is None:
        if identifiers.title:
            missing_titles.append(identifiers.title)
        logger.debug(
            "Skipping citation lookup; no supported identifier for title=%s pii=%s",
            identifiers.title,
            identifiers.pii,
        )
        return

    identifier, id_type = chosen
    try:
        yearly = fetch_yearly_citations(
            identifier,
            id_type=id_type,
            start_year=config.citation_start_year,
        )
    except Exception as exc:  # noqa: BLE001 - API errors should not stop the batch
        logger.warning(
            "Citation lookup failed for %s (%s): %s",
            identifier,
            id_type,
            exc,
        )
        return

    for year, count in yearly:
        period_name = assign_year(year, config.time_periods)
        if period_name is not None:
            citation_counts[period_name] += count
