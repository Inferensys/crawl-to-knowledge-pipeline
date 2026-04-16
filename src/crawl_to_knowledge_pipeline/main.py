from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .config import Settings
from .models import ExportRequest, ExportResponse, SourceManifest
from .service import CrawlService, RunNotFoundError
from .store import InMemoryCrawlStore


def create_app() -> FastAPI:
    app = FastAPI(title="crawl-to-knowledge-pipeline", version="0.1.0")
    settings = Settings.from_env()
    service = CrawlService(InMemoryCrawlStore(), settings=settings)
    app.state.crawl_service = service

    @app.get("/healthz")
    def healthz():
        return {"ok": True, "provider_mode": settings.provider_mode}

    @app.post("/api/crawls")
    def create_run(manifest: SourceManifest):
        return service.create_run(manifest)

    @app.get("/api/crawls/{run_id}")
    def get_run(run_id: str):
        try:
            return service.get_run(run_id)
        except RunNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/api/sources")
    def list_sources():
        return service.list_sources()

    @app.post("/api/exports/build", response_model=ExportResponse)
    def build_export(request: ExportRequest) -> ExportResponse:
        try:
            return service.build_export(request.run_id)
        except RunNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return app


app = create_app()
