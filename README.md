# crawl-to-knowledge-pipeline

Reference repository for maintaining a live knowledge graph from web and docs sources using crawl manifests, canonicalization, and delta snapshots.

Primary output of this project is not a chatbot. It is a reproducible crawl data product with strict freshness metadata.

## Design Principles

- manifest-driven sources and schedules
- deterministic URL canonicalization
- incremental recrawl with diff snapshots
- explicit source trust and extraction policy
- export format optimized for retrieval/indexing systems

## Runtime Model

```text
Source Registry -> Frontier Builder -> Fetchers -> Content Normalizer -> Delta Detector -> Knowledge Export
```

Architecture details: [`docs/architecture.md`](./docs/architecture.md)

## First Pass

Walk the repository in this order:

1. Open [`examples/source-manifest.json`](./examples/source-manifest.json) to see how source policy, rate limits, and canonicalization are pinned.
2. Inspect [`examples/crawl-run.json`](./examples/crawl-run.json) for run-level counters and failure accounting.
3. Inspect [`examples/knowledge-record.json`](./examples/knowledge-record.json) for the retrieval-ready export shape.
4. Use [`docs/runbook.md`](./docs/runbook.md) to reason about cadence, retries, and partial-run handling.

## Contracts

- source manifest schema: [`schemas/source-manifest.schema.json`](./schemas/source-manifest.schema.json)
- crawl run metadata schema: [`schemas/crawl-run.schema.json`](./schemas/crawl-run.schema.json)
- knowledge record schema: [`schemas/knowledge-record.schema.json`](./schemas/knowledge-record.schema.json)

Example artifacts:

- [`examples/source-manifest.json`](./examples/source-manifest.json)
- [`examples/crawl-run.json`](./examples/crawl-run.json)
- [`examples/knowledge-record.json`](./examples/knowledge-record.json)

## API / Worker Surface

- `POST /api/crawls` create crawl run from manifest revision
- `GET /api/crawls/{run_id}` crawl status, counters, and failure set
- `POST /api/freshness/check` compare current snapshot with prior run
- `POST /api/exports/build` emit retrieval-ready knowledge package
- `GET /api/sources` list source definitions and policy tags

## Operational Notes

- Use separate queues for `seed-discovery` and `content-fetch`.
- Enforce per-domain rate limits and robots policy checks at fetch time.
- Keep raw fetch payloads for reproducible extraction and parser regression tests.

Detailed runbook notes are in [`docs/runbook.md`](./docs/runbook.md).

## Demo Assets

Screenshot and recording guidance is in [`assets/README.md`](./assets/README.md).
