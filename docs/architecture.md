# Architecture: Crawl to Knowledge Pipeline

## System Objectives

- Keep retrieval corpus synchronized with mutable source content.
- Minimize recrawl cost through delta-aware scheduling.
- Preserve source traceability from fetched page to exported record.

## Core Services

- `source-registry`: stores manifest revisions and policy tags.
- `scheduler`: computes crawl frontier by priority and recency SLA.
- `fetch-workers`: perform HTTP fetch with robots and rate-limit controls.
- `normalizer`: converts HTML/Markdown/API payloads into canonical text units.
- `delta-engine`: compares canonical URL + content hash vs prior snapshot.
- `export-writer`: emits versioned knowledge package for downstream systems.

## Queue Topology

- `q.discovery`: seed URLs and sitemap expansion.
- `q.fetch`: concrete URL fetch jobs with retry state.
- `q.normalize`: extraction and canonicalization.
- `q.delta`: change classification and snapshot merge.
- `q.export`: package build and publication.

## Snapshot Model

Each successful run produces:

- run metadata (`run_id`, `manifest_revision`, `as_of`)
- per-URL crawl result
- delta classification
- exported knowledge records

Snapshots are append-only. Rebuilds should derive from snapshot history, not mutable latest-only tables.

## Recommended Metrics

- `frontier_backlog_count`
- `urls_fetched_per_minute`
- `fetch_error_rate_by_domain`
- `delta_change_ratio`
- `export_record_count`
- `snapshot_lag_minutes`
