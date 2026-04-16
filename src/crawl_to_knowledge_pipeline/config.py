from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    provider_mode: str = "deterministic"
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_api_version: str = "2025-04-01-preview"
    azure_openai_extract_deployment: str = "gpt-5-mini"
    azure_openai_reasoning_deployment: str = "gpt-5.4"
    fetch_timeout_seconds: float = 20.0
    max_urls_per_source: int = 6

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            provider_mode=os.getenv(
                "CRAWL_TO_KNOWLEDGE_PROVIDER",
                os.getenv("KNOWLEDGE_PIPELINE_PROVIDER", "deterministic"),
            )
            .strip()
            .lower(),
            azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("AZURE_API_KEY"),
            azure_openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview"),
            azure_openai_extract_deployment=os.getenv(
                "AZURE_OPENAI_EXTRACT_DEPLOYMENT",
                "gpt-5-mini",
            ),
            azure_openai_reasoning_deployment=os.getenv(
                "AZURE_OPENAI_REASONING_DEPLOYMENT",
                "gpt-5.4",
            ),
            fetch_timeout_seconds=float(os.getenv("CRAWL_FETCH_TIMEOUT_SECONDS", "20")),
            max_urls_per_source=int(os.getenv("CRAWL_MAX_URLS_PER_SOURCE", "6")),
        )

    @property
    def live_provider_enabled(self) -> bool:
        return self.provider_mode == "azure"

    def validate_for_live_mode(self) -> None:
        missing = []
        if not self.azure_openai_endpoint:
            missing.append("AZURE_OPENAI_ENDPOINT")
        if not self.azure_openai_api_key:
            missing.append("AZURE_OPENAI_API_KEY")
        if missing:
            raise RuntimeError(
                "Live crawl mode is enabled but missing environment variables: "
                + ", ".join(missing)
            )
