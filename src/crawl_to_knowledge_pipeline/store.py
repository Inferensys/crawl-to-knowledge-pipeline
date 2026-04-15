from __future__ import annotations

from threading import Lock
from typing import Dict, List, Optional

from .models import CrawlRun, KnowledgeRecord, SourceManifest


class InMemoryCrawlStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._manifests: Dict[str, SourceManifest] = {}
        self._runs: Dict[str, CrawlRun] = {}
        self._records_by_run: Dict[str, List[KnowledgeRecord]] = {}
        self._latest_run_by_manifest: Dict[str, str] = {}

    def save_manifest(self, manifest: SourceManifest) -> None:
        with self._lock:
            self._manifests[manifest.manifest_id] = manifest

    def list_manifests(self) -> List[SourceManifest]:
        with self._lock:
            return list(self._manifests.values())

    def save_run(self, run: CrawlRun, records: List[KnowledgeRecord]) -> None:
        with self._lock:
            self._runs[run.run_id] = run
            self._records_by_run[run.run_id] = records
            self._latest_run_by_manifest[run.manifest_id] = run.run_id

    def get_run(self, run_id: str) -> Optional[CrawlRun]:
        with self._lock:
            return self._runs.get(run_id)

    def get_records(self, run_id: str) -> List[KnowledgeRecord]:
        with self._lock:
            return list(self._records_by_run.get(run_id, []))

    def get_previous_records(self, manifest_id: str) -> List[KnowledgeRecord]:
        with self._lock:
            previous_run_id = self._latest_run_by_manifest.get(manifest_id)
            if previous_run_id is None:
                return []
            return list(self._records_by_run.get(previous_run_id, []))

