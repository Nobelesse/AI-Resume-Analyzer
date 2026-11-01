"""Private Supabase Storage operations: server-side only, no public file URLs.

A server-side secret key is required; use never from client-side JavaScript.
Permission and ownership MUST be checked by the caller before GET/DELETE.
"""
from __future__ import annotations
import os
import re
import urllib.error
import urllib.parse
import urllib.request

BUCKET = "resume-documents"
NAME = re.compile(r"^[a-f0-9]{32}\.(pdf|docx|txt|rtf|odt)$")


class StorageError(RuntimeError):
    pass


def _settings():
    url = os.environ.get("ARA_SUPABASE_URL", "").strip().rstrip("/")
    key = os.environ.get("ARA_SUPABASE_SERVICE_KEY", "").strip()
    if not re.fullmatch(r"https://[a-z0-9-]+\.supabase\.co", url):
        raise StorageError("Configure ARA_SUPABASE_URL as the Supabase project HTTPS URL")
    if not key:
        raise StorageError("ARA_SUPABASE_SERVICE_KEY is not configured")
    return url, key


def _object_path(storage_name: str) -> str:
    if not NAME.fullmatch(storage_name):
        raise ValueError("Storage name must be a generated UUID hex basename and valid document suffix")
    return urllib.parse.quote(storage_name, safe="")


def _request(method: str, storage_name: str, *, data=None, mime=None):
    url, key = _settings()
    path = _object_path(storage_name)
    # Private bucket. No unauthenticated URLs or signed public links are created.
    endpoint = f"{url}/storage/v1/object/{BUCKET}/{path}"
    headers = {"Authorization": f"Bearer {key}", "apikey": key}
    if mime:
        headers["Content-Type"] = mime
        headers["x-upsert"] = "false"
    request = urllib.request.Request(endpoint, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as result:
            return result.read(10_000_001)
    except urllib.error.HTTPError as exc:
        raise StorageError(f"Private storage {method} failed (HTTP {exc.code})") from None
    except urllib.error.URLError:
        raise StorageError("Private storage service unavailable") from None


def put_private(storage_name: str, data: bytes, mime: str):
    if not isinstance(data, bytes) or not (0 < len(data) <= 10_000_000):
        raise ValueError("Document must be between 1 and 10,000,000 bytes")
    if mime not in {
        "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain", "application/rtf", "application/vnd.oasis.opendocument.text"
    }:
        raise ValueError("Unsupported document MIME type")
    return _request("POST", storage_name, data=data, mime=mime)


def remove_private(storage_name: str):
    return _request("DELETE", storage_name)


def get_private(storage_name: str):
    """ONLY call after confirming document ownership/administrator authorization."""
    return _request("GET", storage_name)
