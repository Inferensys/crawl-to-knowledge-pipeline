from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Extractor(str, Enum):
    HTML_MAIN = "html_main"
    MARKDOWN_NATIVE = "markdown_native"
    API_JSON = "api_json"


class RunStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"


class DeltaClass(str, Enum):
    NEW = "new"
    UPDATED = "updated"
    DELETED = "deleted"
    UNCHANGED = "unchanged"


class SourceDefinition(BaseModel):
    source_id: str
    seed_url: HttpUrl | str
    allowed_prefixes: List[str]
    extractor: Extractor
    priority_tier: int = Field(ge=0, le=2)
    rate_limit_rps: Optional[float] = Field(default=None, ge=0.1, le=20)


class SourceManifest(BaseModel):
    manifest_id: str = Field(pattern=r"^[a-zA-Z0-9._:-]{4,128}$")
    revision: int = Field(ge=1)
    sources: List[SourceDefinition] = Field(min_length=1)


class CrawlCounters(BaseModel):
    fetched: int = 0
    new: int = 0
    updated: int = 0
    deleted: int = 0
    unchanged: int = 0
    errors: int = 0


class CrawlRun(BaseModel):
    run_id: str
    manifest_id: str
    manifest_revision: int = Field(ge=1)
    status: RunStatus
    started_at: datetime
    ended_at: Optional[datetime] = None
    counters: CrawlCounters


class KnowledgeRecord(BaseModel):
    record_id: str
    run_id: str
    canonical_url: HttpUrl | str
    source_id: str
    title: str
    content: str = Field(min_length=1)
    section_path: str
    as_of: datetime
    content_hash_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    delta_class: DeltaClass


class FreshnessCheckRequest(BaseModel):
    manifest_id: str
    revision: int


class ExportRequest(BaseModel):
    run_id: str


class ExportResponse(BaseModel):
    run: CrawlRun
    records: List[KnowledgeRecord]


class SourceSummary(BaseModel):
    manifest_id: str
    revision: int
    sources: List[SourceDefinition]

