from fastapi.testclient import TestClient

from crawl_to_knowledge_pipeline.main import create_app


def _manifest(revision: int = 7):
    return {
        "manifest_id": "support-docs-primary",
        "revision": revision,
        "sources": [
            {
                "source_id": "docs",
                "seed_url": "https://docs.example.com/",
                "allowed_prefixes": [
                    "https://docs.example.com/guides/",
                    "https://docs.example.com/api/",
                ],
                "extractor": "html_main",
                "priority_tier": 1,
                "rate_limit_rps": 2,
            }
        ],
    }


def test_create_run_and_export_records():
    client = TestClient(create_app())

    create = client.post("/api/crawls", json=_manifest())
    assert create.status_code == 200
    run = create.json()
    assert run["status"] == "completed"
    assert run["counters"]["fetched"] >= 2
    assert run["counters"]["new"] >= 1

    export = client.post("/api/exports/build", json={"run_id": run["run_id"]})
    assert export.status_code == 200
    payload = export.json()
    assert payload["run"]["run_id"] == run["run_id"]
    assert len(payload["records"]) >= 2


def test_second_run_classifies_updates_and_unchanged():
    client = TestClient(create_app())

    first = client.post("/api/crawls", json=_manifest(revision=7)).json()
    second = client.post("/api/crawls", json=_manifest(revision=8)).json()

    assert first["counters"]["new"] >= 1
    assert second["counters"]["updated"] >= 1
    assert second["counters"]["unchanged"] >= 1


def test_sources_list_contains_manifest_metadata():
    client = TestClient(create_app())
    client.post("/api/crawls", json=_manifest())

    response = client.get("/api/sources")
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["manifest_id"] == "support-docs-primary"
    assert payload[0]["sources"][0]["source_id"] == "docs"

