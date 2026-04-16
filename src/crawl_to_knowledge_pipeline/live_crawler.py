from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import List

import httpx

from .canonicalize import canonicalize_url
from .config import Settings
from .extractor_backend import (
    DeterministicExtractionBackend,
    ExtractionBackend,
    FetchPayload,
)
from .models import DeltaClass, KnowledgeRecord, SourceManifest


@dataclass(frozen=True)
class CrawlResult:
    records: List[KnowledgeRecord]
    errors: int


def crawl_manifest_records(
    manifest: SourceManifest,
    run_id: str,
    as_of: datetime,
    settings: Settings,
    backend: ExtractionBackend,
) -> CrawlResult:
    records: List[KnowledgeRecord] = []
    errors = 0
    stable_backend = DeterministicExtractionBackend()
    client = httpx.Client(
        follow_redirects=True,
        timeout=settings.fetch_timeout_seconds,
        headers={"User-Agent": "crawl-to-knowledge-pipeline/0.1"},
    )
    try:
        for source in manifest.sources:
            urls = _source_urls(source.seed_url, source.allowed_prefixes, settings.max_urls_per_source)
            for url in urls:
                try:
                    response = client.get(url)
                    response.raise_for_status()
                    payload = FetchPayload(
                        url=str(response.url),
                        source_id=source.source_id,
                        extractor=source.extractor,
                        content_type=response.headers.get("content-type", ""),
                        body=response.text,
                    )
                    stable_extracted = stable_backend.extract(payload)
                    extracted = backend.extract(payload)
                except Exception:
                    errors += 1
                    continue

                canonical_url = canonicalize_url(str(response.url))
                # Delta classification must be stable across runs even when the model
                # rewrites the exported record text slightly differently.
                content_hash = hashlib.sha256(stable_extracted.content.encode("utf-8")).hexdigest()
                record_id = hashlib.sha256(
                    f"{manifest.manifest_id}:{canonical_url}".encode("utf-8")
                ).hexdigest()[:12]
                records.append(
                    KnowledgeRecord(
                        record_id=f"kr_{record_id}",
                        run_id=run_id,
                        canonical_url=canonical_url,
                        source_id=source.source_id,
                        title=extracted.title,
                        content=extracted.content,
                        section_path=extracted.section_path,
                        as_of=as_of,
                        content_hash_sha256=content_hash,
                        delta_class=DeltaClass.NEW,
                    )
                )
    finally:
        client.close()
    return CrawlResult(records=_dedupe_records(records), errors=errors)


def _source_urls(seed_url: str, allowed_prefixes: List[str], limit: int) -> List[str]:
    ordered: List[str] = []
    for candidate in [str(seed_url), *[str(prefix) for prefix in allowed_prefixes]]:
        if candidate not in ordered:
            ordered.append(candidate)
        if len(ordered) >= limit:
            break
    return ordered


def _dedupe_records(records: List[KnowledgeRecord]) -> List[KnowledgeRecord]:
    deduped: dict[str, KnowledgeRecord] = {}
    for record in records:
        deduped[str(record.canonical_url)] = record
    return list(deduped.values())
