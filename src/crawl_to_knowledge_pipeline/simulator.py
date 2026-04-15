from __future__ import annotations

import hashlib
from typing import Dict, List, Tuple

from .canonicalize import canonicalize_url
from .models import DeltaClass, KnowledgeRecord, SourceManifest


def simulate_manifest_records(manifest: SourceManifest, run_id: str, as_of) -> List[KnowledgeRecord]:
    records: List[KnowledgeRecord] = []
    for source in manifest.sources:
        generated_urls = _source_urls(source.source_id, source.allowed_prefixes)
        for ordinal, url in enumerate(generated_urls, start=1):
            canonical_url = canonicalize_url(url)
            title = _title_for(source.source_id, ordinal)
            content = _content_for(source.source_id, manifest.revision, ordinal)
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            record_id = hashlib.sha256(
                f"{manifest.manifest_id}:{canonical_url}".encode("utf-8")
            ).hexdigest()[:12]
            section_path = _section_for(source.source_id, ordinal)
            records.append(
                KnowledgeRecord(
                    record_id=f"kr_{record_id}",
                    run_id=run_id,
                    canonical_url=canonical_url,
                    source_id=source.source_id,
                    title=title,
                    content=content,
                    section_path=section_path,
                    as_of=as_of,
                    content_hash_sha256=content_hash,
                    delta_class=DeltaClass.NEW,
                )
            )
    return records


def classify_delta(
    current_records: List[KnowledgeRecord],
    previous_records: List[KnowledgeRecord],
) -> Tuple[List[KnowledgeRecord], Dict[str, int]]:
    previous_by_url = {str(record.canonical_url): record for record in previous_records}
    current_by_url = {str(record.canonical_url): record for record in current_records}
    counters = {"new": 0, "updated": 0, "deleted": 0, "unchanged": 0}

    classified: List[KnowledgeRecord] = []
    for record in current_records:
        previous = previous_by_url.get(str(record.canonical_url))
        if previous is None:
            record.delta_class = DeltaClass.NEW
            counters["new"] += 1
        elif previous.content_hash_sha256 != record.content_hash_sha256:
            record.delta_class = DeltaClass.UPDATED
            counters["updated"] += 1
        else:
            record.delta_class = DeltaClass.UNCHANGED
            counters["unchanged"] += 1
        classified.append(record)

    for previous in previous_records:
        if str(previous.canonical_url) not in current_by_url:
            counters["deleted"] += 1

    return classified, counters


def _source_urls(source_id: str, prefixes: List[str]) -> List[str]:
    urls: List[str] = []
    if not prefixes:
        return urls
    first_prefix = prefixes[0].rstrip("/") + "/"
    urls.append(first_prefix)
    urls.append(first_prefix + "service-accounts?utm_source=ops")
    if len(prefixes) > 1:
        second_prefix = prefixes[1].rstrip("/") + "/"
        urls.append(second_prefix + "rate-limits#limits")
    return urls


def _title_for(source_id: str, ordinal: int) -> str:
    if source_id == "docs" and ordinal == 1:
        return "Service Accounts"
    if source_id == "docs" and ordinal == 2:
        return "Rotation Policy"
    if source_id == "changelog":
        return "Platform Changelog"
    return f"{source_id.title()} Entry {ordinal}"


def _content_for(source_id: str, revision: int, ordinal: int) -> str:
    base = {
        ("docs", 1): "Service accounts can be provisioned using the admin API. Tokens are scoped by project and support rotation.",
        ("docs", 2): "Rotation policy describes how keys are retired and reissued across production environments.",
        ("docs", 3): "Rate limits apply per project and per token family with regional overrides.",
        ("changelog", 1): "Release log entries describe public API changes and migration notes.",
    }.get((source_id, ordinal), f"Knowledge record for {source_id} #{ordinal}.")
    if ordinal == 1:
        return f"{base} Revision {revision}."
    return base


def _section_for(source_id: str, ordinal: int) -> str:
    if source_id == "docs" and ordinal == 1:
        return "Guides/Authentication/Service Accounts"
    if source_id == "docs" and ordinal == 2:
        return "Guides/Security/Rotation Policy"
    if source_id == "docs" and ordinal == 3:
        return "API/Quotas/Rate Limits"
    return f"{source_id.title()}/Entry {ordinal}"

