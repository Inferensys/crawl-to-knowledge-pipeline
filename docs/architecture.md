# Architecture

This service has one job: turn a declared document set into stable knowledge exports.

It does not try to discover the whole web. It does not execute JavaScript. It does not let the model decide whether a page changed.

## Flow

```text
SourceManifest
  -> bounded URL set
  -> HTTP fetch
  -> deterministic local extraction
  -> optional model rewrite for export text
  -> stable content hash
  -> delta classification against previous run
  -> export package
```

## Boundary Decisions

- Frontier: bounded to `seed_url` plus `allowed_prefixes`. No recursive link walking.
- Canonicalization: app-owned and deterministic in `canonicalize.py`.
- Change detection: app-owned and hash-based in `simulator.py` and `service.py`.
- Record text: provider-owned in live mode through `ExtractionBackend`.
- Persistence: in-memory for this slice so the API stays inspectable and the tests stay fast.

## Why Two Extractors Run In Live Mode

`live_crawler.py` calls both extractors:

- `DeterministicExtractionBackend` produces the stable text used for `content_hash_sha256`
- `AzureExtractionBackend` produces the export text seen by downstream retrieval systems

That split is deliberate. The local extractor gives stable diffs. The model gives denser technical summaries. Mixing those responsibilities would create false `updated` runs whenever the model paraphrases.

## Record Identity

Each exported record is keyed from:

- `manifest_id`
- canonical URL

The record payload also carries:

- `as_of`
- `content_hash_sha256`
- `delta_class`
- `source_id`
- model-normalized `title`, `content`, and `section_path`

That is enough for downstream systems to:

- rebuild an index incrementally
- trace each record back to source
- discard or reprocess only the changed set

## Current Limits

- no robots.txt evaluation
- no concurrency pool
- no persistent store
- no sitemap expansion
- no browser render path
- no downstream embedding or index writer

Those are extension points, not oversights. The repo is intentionally centered on manifest discipline, stable delta behavior, and provider-swappable extraction.
