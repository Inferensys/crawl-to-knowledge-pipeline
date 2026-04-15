# Implementation Plan

## Objective

Build a runnable crawl control plane that exercises manifest parsing, canonicalization, run counters, delta classification, and export generation without requiring a real crawler.

## v1 Scope

- FastAPI service with in-memory manifests, runs, and generated records
- deterministic record generation from manifest inputs
- URL canonicalization and previous-run diffing
- run, sources, and export endpoints
- API tests covering canonicalization-driven dedupe, update classification, and export assembly

## Module split

- `models.py`: manifests, runs, counters, records, and export contracts
- `canonicalize.py`: URL normalization rules
- `simulator.py`: synthetic fetch/extract pipeline and delta classification
- `store.py`: in-memory persistence
- `service.py`: run orchestration and export assembly
- `main.py`: HTTP endpoints and error mapping

