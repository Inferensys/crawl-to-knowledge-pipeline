# Crawl Operations Runbook

This document captures execution policy for recurring crawl runs and knowledge snapshot generation.

## Crawl Cadence

- Tier 0 sources (release notes, incident docs): every 15 minutes
- Tier 1 sources (product docs, API refs): every 2 hours
- Tier 2 sources (blogs, long-form articles): daily

Crawl cadence must be configured per source manifest, not as a global setting.

## Source Admission Checklist

Before adding a new source:

- verify robots policy and legal terms
- choose extractor policy (`html_main`, `markdown_native`, `api_json`)
- set canonical domain and allowed path prefixes
- configure priority tier and rate limit

## Freshness and Diff Policy

For each crawl run:

1. Compute normalized content hash per canonical URL.
2. Compare against last successful run.
3. Emit change class:
   - `new`
   - `updated`
   - `deleted`
   - `unchanged`
4. Push only delta set to downstream indexing jobs.

## Canonicalization Rules

- force lowercase scheme + host
- strip known tracking query params (`utm_*`, `gclid`, `fbclid`)
- trim trailing slash except root
- fragment identifiers are ignored for dedupe

Canonicalization must be deterministic and versioned. If rules change, bump `canonicalizer_version`.

## Failure Budget and Retry

- network timeout retry: 2 attempts with exponential backoff
- 4xx responses: no retry, mark as terminal
- 5xx responses: retry until budget limit
- parser failures: isolate URL and continue run

Run status should become `completed_with_errors` when errors remain under threshold.

## Export Integrity

Before publishing a knowledge package:

- assert manifest revision pin
- assert full source coverage or emit explicit partial-run flag
- attach crawl watermark timestamp (`as_of`)
- include checksum for each exported record payload
