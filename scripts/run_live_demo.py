from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT / "demo" / "input"
OUTPUT_DIR = ROOT / "demo" / "output"


def main() -> None:
    os.environ.setdefault("CRAWL_TO_KNOWLEDGE_PROVIDER", "azure")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    from crawl_to_knowledge_pipeline.main import create_app

    client = TestClient(create_app())

    manifests = [
        ("v1", _read_json(INPUT_DIR / "manifest-v1.json")),
        ("v2", _read_json(INPUT_DIR / "manifest-v2.json")),
    ]

    summary: list[dict[str, object]] = []
    for name, manifest in manifests:
        print(f"[{name}] creating crawl run for manifest {manifest['manifest_id']} rev={manifest['revision']}")
        create_response = client.post("/api/crawls", json=manifest)
        create_response.raise_for_status()
        run = create_response.json()
        _write_json(OUTPUT_DIR / f"run-{name}.json", run)

        print(f"[{name}] building export package for run_id={run['run_id']}")
        export_response = client.post("/api/exports/build", json={"run_id": run["run_id"]})
        export_response.raise_for_status()
        export_payload = export_response.json()
        _write_json(OUTPUT_DIR / f"export-{name}.json", export_payload)

        summary.append(
            {
                "name": name,
                "manifest_id": manifest["manifest_id"],
                "run_id": run["run_id"],
                "status": run["status"],
                "provider_mode": os.environ.get("CRAWL_TO_KNOWLEDGE_PROVIDER", "deterministic"),
                "extract_model": os.environ.get("AZURE_OPENAI_EXTRACT_DEPLOYMENT", "gpt-5-mini"),
                "duration_seconds": _duration_seconds(run["started_at"], run["ended_at"]),
                "fetched": run["counters"]["fetched"],
                "new": run["counters"]["new"],
                "updated": run["counters"]["updated"],
                "unchanged": run["counters"]["unchanged"],
                "errors": run["counters"]["errors"],
                "record_urls": [record["canonical_url"] for record in export_payload["records"]],
            }
        )
        print(
            f"[{name}] fetched={run['counters']['fetched']} "
            f"new={run['counters']['new']} unchanged={run['counters']['unchanged']} "
            f"errors={run['counters']['errors']}"
        )

    _write_json(OUTPUT_DIR / "demo-summary.json", summary)
    print(f"wrote live demo artifacts to {OUTPUT_DIR}")


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _duration_seconds(started_at: str, ended_at: str) -> float:
    start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    end = datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
    return round((end - start).total_seconds(), 3)


if __name__ == "__main__":
    main()
