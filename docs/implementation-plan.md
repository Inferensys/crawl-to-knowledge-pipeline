# Extension Plan

The current repo is intentionally small. The next useful additions are obvious and separate.

## 1. Persist Runs

Replace `InMemoryCrawlStore` with a durable store that keeps:

- manifests by revision
- per-run metadata
- record snapshots by canonical URL
- per-URL error details

Without this, the API is useful for demos and tests but not for recurring jobs.

## 2. Move Crawl Execution Off The Request Thread

`POST /api/crawls` currently performs the whole run inline. That keeps the flow readable, but it is the wrong shape for larger frontiers.

Next step:

- accept the manifest
- enqueue the run
- stream progress through a run table or event log

## 3. Add Frontier Expansion

Keep the current bounded manifest mode, then add optional expansion stages for:

- sitemaps
- API pagination
- directory indexes

Do not mix expansion with diff logic. Expansion decides what to fetch. The delta engine decides what changed.

## 4. Publish Downstream

The export package is already shaped for downstream systems. The next adapters should be:

- embedding batch writer
- object storage snapshot publisher
- index sync worker

## 5. Add Provider Backends Without Touching The Delta Layer

The contract is already in `extractor_backend.py`.

Add:

- `OpenAIExtractionBackend`
- `VertexExtractionBackend`
- `AnthropicExtractionBackend`

Keep `content_hash_sha256` local and deterministic regardless of provider.
