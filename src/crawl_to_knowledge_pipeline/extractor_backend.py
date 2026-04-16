from __future__ import annotations

import json
import re
from dataclasses import dataclass
from html import unescape
from typing import Protocol
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .config import Settings
from .models import Extractor


@dataclass(frozen=True)
class ExtractionResult:
    title: str
    content: str
    section_path: str


@dataclass(frozen=True)
class FetchPayload:
    url: str
    source_id: str
    extractor: Extractor
    content_type: str
    body: str


class ExtractionBackend(Protocol):
    def extract(self, payload: FetchPayload) -> ExtractionResult:
        ...


class DeterministicExtractionBackend:
    def extract(self, payload: FetchPayload) -> ExtractionResult:
        return _extract_locally(payload)


def build_extraction_backend(settings: Settings) -> ExtractionBackend:
    if settings.live_provider_enabled:
        from .azure_extractor import AzureExtractionBackend

        return AzureExtractionBackend(settings)
    return DeterministicExtractionBackend()


def _extract_locally(payload: FetchPayload) -> ExtractionResult:
    if payload.extractor == Extractor.API_JSON:
        return _extract_json(payload)
    if payload.extractor == Extractor.MARKDOWN_NATIVE:
        return _extract_markdown(payload)
    return _extract_html(payload)


def _extract_html(payload: FetchPayload) -> ExtractionResult:
    soup = BeautifulSoup(payload.body, "html.parser")
    for tag_name in ("script", "style", "noscript", "svg"):
        for node in soup.find_all(tag_name):
            node.decompose()

    root = soup.find("main") or soup.find("article") or soup.body or soup
    title = _clean_text(
        (
            root.find(["h1", "title"]).get_text(" ", strip=True)
            if root.find(["h1", "title"])
            else soup.title.get_text(" ", strip=True) if soup.title else payload.url
        )
    )
    text = _clean_text(root.get_text("\n", strip=True))
    content = _summarize_text(text, max_chars=2400)
    return ExtractionResult(
        title=title,
        content=content,
        section_path=_section_path_from_url(payload.url, title),
    )


def _extract_markdown(payload: FetchPayload) -> ExtractionResult:
    lines = [line.strip() for line in payload.body.splitlines() if line.strip()]
    title = payload.url
    for line in lines:
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            break
    text = _clean_text("\n".join(lines))
    return ExtractionResult(
        title=title,
        content=_summarize_text(text, max_chars=2400),
        section_path=_section_path_from_url(payload.url, title),
    )


def _extract_json(payload: FetchPayload) -> ExtractionResult:
    try:
        parsed = json.loads(payload.body)
        pretty = json.dumps(parsed, indent=2, sort_keys=True, ensure_ascii=True)
    except json.JSONDecodeError:
        pretty = payload.body
    title = f"{payload.source_id} API payload"
    return ExtractionResult(
        title=title,
        content=_summarize_text(pretty, max_chars=2400),
        section_path=_section_path_from_url(payload.url, title),
    )


def _clean_text(value: str) -> str:
    cleaned = unescape(value)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _summarize_text(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    clipped = value[:max_chars].rsplit(" ", 1)[0].strip()
    return clipped + " ..."


def _section_path_from_url(url: str, title: str) -> str:
    path_parts = [part for part in urlparse(url).path.split("/") if part]
    if not path_parts:
        return title
    normalized = [part.replace("-", " ").replace("_", " ").title() for part in path_parts]
    return "/".join(normalized)
