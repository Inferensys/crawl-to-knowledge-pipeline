# crawl-to-knowledge-pipeline

FastAPI service for maintaining a live knowledge graph from web and docs sources using crawl manifests, canonicalization, and delta snapshots.

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

## Current implementation

The first slice is a deterministic crawl simulator:

- `POST /api/crawls` accepts a manifest and creates a completed crawl run
- URLs are canonicalized before record generation and diffing
- generated records are compared against the previous run for the same manifest
- `GET /api/crawls/{run_id}` returns run metadata and counters
- `GET /api/sources` lists manifests observed by the service
- `POST /api/exports/build` returns the retrieval-ready knowledge package for a run

## Contracts

- source manifest schema: [`schemas/source-manifest.schema.json`](./schemas/source-manifest.schema.json)
- crawl run metadata schema: [`schemas/crawl-run.schema.json`](./schemas/crawl-run.schema.json)
- knowledge record schema: [`schemas/knowledge-record.schema.json`](./schemas/knowledge-record.schema.json)

Example artifacts:

- [`examples/source-manifest.json`](./examples/source-manifest.json)
- [`examples/crawl-run.json`](./examples/crawl-run.json)
- [`examples/knowledge-record.json`](./examples/knowledge-record.json)

## Project layout

```text
.
├── docs/
│   ├── architecture.md
│   ├── implementation-plan.md
│   └── runbook.md
├── src/crawl_to_knowledge_pipeline/
│   ├── canonicalize.py
│   ├── main.py
│   ├── models.py
│   ├── service.py
│   ├── simulator.py
│   └── store.py
├── tests/
│   └── test_api.py
├── schemas/
└── examples/
```

## Run locally

Prerequisites:

- Python 3.9
- `uv`

```bash
uv sync --extra dev
uv run uvicorn crawl_to_knowledge_pipeline.main:app --app-dir src --reload
```

## Test

```bash
uv run pytest -q
```

## Example flow

Create a run:

```bash
curl -X POST http://127.0.0.1:8000/api/crawls \
  -H "Content-Type: application/json" \
  -d @examples/source-manifest.json
```

Fetch run metadata:

```bash
curl http://127.0.0.1:8000/api/crawls/<run_id>
```

Build export:

```bash
curl -X POST http://127.0.0.1:8000/api/exports/build \
  -H "Content-Type: application/json" \
  -d '{"run_id":"<run_id>"}'
```

## Operational Notes

- Canonicalization strips `utm_*`, `gclid`, `fbclid`, fragments, and redundant trailing slashes.
- Revision changes can yield both `updated` and `unchanged` records in the same run.
- Storage is in-memory for this slice; restart clears manifests and run history.

Detailed runbook notes are in [`docs/runbook.md`](./docs/runbook.md).


## Demo Assets

Screenshot and recording guidance is in [`assets/README.md`](./assets/README.md).
