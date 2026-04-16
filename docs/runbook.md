# Runbook

## Choosing Provider Mode

Use deterministic mode when you need:

- fast local development
- stable tests
- API contract work
- canonicalization debugging

Use Azure mode when you need:

- dense export text instead of clipped local extracts
- retrieval-ready record content
- realistic demo artifacts

Switch with:

```bash
export CRAWL_TO_KNOWLEDGE_PROVIDER=deterministic
```

or:

```bash
export CRAWL_TO_KNOWLEDGE_PROVIDER=azure
```

## Source Admission Rules

Before adding a source:

- make the frontier explicit in `allowed_prefixes`
- choose the extractor deliberately: `html_main`, `markdown_native`, or `api_json`
- verify that the pages are fetchable without interactive auth
- keep the manifest small enough that one run still tells a coherent story

If you need large-scale discovery, build that upstream and feed this service resolved URLs.

## Reading Run Counters

- `new`: canonical URL did not exist in the previous snapshot
- `updated`: canonical URL existed and the stable local content hash changed
- `unchanged`: canonical URL existed and the stable local content hash matched
- `deleted`: reserved for future manifests that explicitly drop prior URLs
- `errors`: fetch or extraction failures that were isolated without failing the full run

In Azure mode, `updated` is still based on the local hash, not on the model text.

## Latency Expectations

The live extractor path is network-bound and model-bound.

Observed on the checked-in MCP demo:

- 2-page run: about 77 seconds
- 3-page run: about 122 seconds

Treat the live path as a quality path, not a high-throughput crawler. If throughput matters:

- pre-expand the frontier elsewhere
- batch work outside the request thread
- cache fetch bodies and model outputs
- move export text generation to an async stage

## Failure Handling

Current behavior:

- fetch and extraction errors increment `errors`
- the run still completes if at least part of the frontier succeeded
- the final run status becomes `completed_with_errors` when `errors > 0`

Recommended next production steps:

- persist raw fetch payloads for replay
- record structured error reasons per URL
- retry transient 5xx and timeout paths outside the request lifecycle
- emit metrics for error rate and crawl duration

## Regenerating The Demo

```bash
export CRAWL_TO_KNOWLEDGE_PROVIDER=azure
export AZURE_OPENAI_ENDPOINT="https://<resource>.openai.azure.com/"
export AZURE_OPENAI_API_KEY="<key>"
export AZURE_OPENAI_EXTRACT_DEPLOYMENT="gpt-5-mini"

uv run python scripts/run_live_demo.py
```

Artifacts land in `demo/output/`.
