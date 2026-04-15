from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from .models import (
    CrawlCounters,
    CrawlRun,
    DeltaClass,
    ExportResponse,
    RunStatus,
    SourceManifest,
    SourceSummary,
)
from .simulator import classify_delta, simulate_manifest_records
from .store import InMemoryCrawlStore


class RunNotFoundError(RuntimeError):
    pass


class CrawlService:
    def __init__(self, store: InMemoryCrawlStore) -> None:
        self._store = store

    def create_run(self, manifest: SourceManifest) -> CrawlRun:
        started_at = datetime.now(timezone.utc)
        run = CrawlRun(
            run_id=f"crawl_{uuid4().hex[:12]}",
            manifest_id=manifest.manifest_id,
            manifest_revision=manifest.revision,
            status=RunStatus.RUNNING,
            started_at=started_at,
            counters=CrawlCounters(),
        )
        self._store.save_manifest(manifest)

        previous_records = self._store.get_previous_records(manifest.manifest_id)
        current_records = simulate_manifest_records(manifest, run.run_id, started_at)
        classified, delta_counts = classify_delta(current_records, previous_records)

        run.counters = CrawlCounters(
            fetched=len(classified),
            new=delta_counts["new"],
            updated=delta_counts["updated"],
            deleted=delta_counts["deleted"],
            unchanged=delta_counts["unchanged"],
            errors=0,
        )
        run.ended_at = datetime.now(timezone.utc)
        run.status = (
            RunStatus.COMPLETED_WITH_ERRORS if run.counters.errors > 0 else RunStatus.COMPLETED
        )
        self._store.save_run(run, classified)
        return run

    def get_run(self, run_id: str) -> CrawlRun:
        run = self._store.get_run(run_id)
        if run is None:
            raise RunNotFoundError(run_id)
        return run

    def list_sources(self) -> list[SourceSummary]:
        manifests = self._store.list_manifests()
        return [
            SourceSummary(
                manifest_id=manifest.manifest_id,
                revision=manifest.revision,
                sources=manifest.sources,
            )
            for manifest in manifests
        ]

    def build_export(self, run_id: str) -> ExportResponse:
        run = self.get_run(run_id)
        return ExportResponse(run=run, records=self._store.get_records(run_id))

