# Demo Assets

Use this directory for operational screenshots tied to crawler behavior.

## Suggested Captures

- `frontier-queue-health.png`
  - queue depth by crawl stage (`discovery`, `fetch`, `normalize`, `delta`)
- `delta-summary-run.png`
  - per-run counts for `new`, `updated`, `deleted`, `unchanged`
- `canonicalization-debug.png`
  - raw URL -> canonical URL transform examples

## Capture Guidelines

- Prefer dashboards with absolute timestamps visible.
- Keep one capture set per manifest revision.
- Remove any private hostnames or credentials from request traces.
