from __future__ import annotations

import json
from typing import Any, Dict

from openai import AzureOpenAI

from .config import Settings
from .extractor_backend import (
    DeterministicExtractionBackend,
    ExtractionResult,
    FetchPayload,
)


class AzureExtractionBackend:
    def __init__(self, settings: Settings) -> None:
        settings.validate_for_live_mode()
        self._settings = settings
        self._fallback = DeterministicExtractionBackend()
        self._client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
            max_retries=2,
            timeout=90.0,
        )

    def extract(self, payload: FetchPayload) -> ExtractionResult:
        local = self._fallback.extract(payload)
        response = self._client.chat.completions.create(
            model=self._settings.azure_openai_extract_deployment,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You normalize fetched technical documents into retrieval-ready knowledge records. "
                        "Preserve concrete facts, APIs, limits, and operational details. "
                        "Do not add commentary. "
                        "Return a compact title, a slash-delimited section path, and a dense content block "
                        "that can be embedded directly into a knowledge index."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "url": payload.url,
                            "source_id": payload.source_id,
                            "content_type": payload.content_type,
                            "local_title": local.title,
                            "local_section_path": local.section_path,
                            "local_content_excerpt": local.content,
                        },
                        ensure_ascii=True,
                    ),
                },
            ],
            tools=[_extract_schema()],
            tool_choice={"type": "function", "function": {"name": "emit_knowledge_record"}},
        )
        tool_calls = response.choices[0].message.tool_calls or []
        if not tool_calls:
            raise RuntimeError(f"Azure extractor returned no tool call for {payload.url}")
        args = json.loads(tool_calls[0].function.arguments)
        return ExtractionResult(
            title=str(args["title"]).strip() or local.title,
            content=str(args["content"]).strip() or local.content,
            section_path=str(args["section_path"]).strip() or local.section_path,
        )


def _extract_schema() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "emit_knowledge_record",
            "description": "Return a normalized knowledge record extracted from a fetched page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "section_path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["title", "section_path", "content"],
                "additionalProperties": False,
            },
        },
    }
