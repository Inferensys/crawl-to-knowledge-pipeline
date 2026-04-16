from crawl_to_knowledge_pipeline.extractor_backend import (
    DeterministicExtractionBackend,
    FetchPayload,
)
from crawl_to_knowledge_pipeline.live_crawler import _source_urls
from crawl_to_knowledge_pipeline.models import Extractor


def test_html_extraction_prefers_main_content() -> None:
    backend = DeterministicExtractionBackend()
    payload = FetchPayload(
        url="https://docs.example.com/guides/authentication/service-accounts",
        source_id="docs",
        extractor=Extractor.HTML_MAIN,
        content_type="text/html",
        body="""
        <html>
          <head><title>Fallback Title</title></head>
          <body>
            <nav>Ignored Nav</nav>
            <main>
              <h1>Service Accounts</h1>
              <p>Provision service accounts through the admin API.</p>
              <p>Tokens are scoped by project and support rotation.</p>
            </main>
          </body>
        </html>
        """,
    )

    result = backend.extract(payload)

    assert result.title == "Service Accounts"
    assert "Provision service accounts through the admin API." in result.content
    assert "Ignored Nav" not in result.content
    assert result.section_path == "Guides/Authentication/Service Accounts"


def test_source_urls_are_bounded_and_deduped() -> None:
    urls = _source_urls(
        "https://docs.example.com/root",
        [
            "https://docs.example.com/root",
            "https://docs.example.com/guide-a",
            "https://docs.example.com/guide-b",
        ],
        limit=3,
    )

    assert urls == [
        "https://docs.example.com/root",
        "https://docs.example.com/guide-a",
        "https://docs.example.com/guide-b",
    ]
