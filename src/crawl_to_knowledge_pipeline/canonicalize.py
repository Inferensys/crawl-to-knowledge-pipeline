from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


TRACKING_KEYS = {"gclid", "fbclid"}


def canonicalize_url(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    scheme = parsed.scheme.lower()
    host = parsed.hostname.lower() if parsed.hostname else ""
    netloc = host
    if parsed.port and not _is_default_port(scheme, parsed.port):
        netloc = f"{host}:{parsed.port}"

    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/")

    filtered_query = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if key.startswith("utm_") or key in TRACKING_KEYS:
            continue
        filtered_query.append((key, value))
    query = urlencode(filtered_query, doseq=True)

    return urlunparse((scheme, netloc, path, "", query, ""))


def _is_default_port(scheme: str, port: int) -> bool:
    return (scheme == "http" and port == 80) or (scheme == "https" and port == 443)

