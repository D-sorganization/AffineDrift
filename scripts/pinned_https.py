"""Fetch from one named https host, and nothing else.

``urllib.request.urlopen`` also opens ``file:``, ``ftp:`` and plain ``http:`` URLs. A check
that builds its URL from repository data (a pinned commit, say) must not be steerable into
reading a local file or another host, so the scheme and the host are checked here, in one
place, before any request is made.
"""

from __future__ import annotations

import re
import urllib.parse
import urllib.request

GITHUB_RAW_HOST = "raw.githubusercontent.com"
_COMMIT_SHA = re.compile(r"[0-9a-f]{40}")


def require_commit_sha(commit: str) -> str:
    """Return ``commit`` when it is a full lowercase git SHA; raise ``ValueError`` otherwise."""
    if not isinstance(commit, str) or not _COMMIT_SHA.fullmatch(commit):
        raise ValueError(f"not a 40-character commit SHA: {commit!r}")
    return commit


def read_pinned_https(url: str, *, host: str, timeout: float = 60.0) -> bytes:
    """Return the body of ``url``.

    Pre: ``url`` is ``https://<host>/...`` with no user, password or port.
    Raises ``ValueError`` before any request when it is not.
    """
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != host:
        raise ValueError(f"refusing to fetch {url!r}: only https://{host}/ is allowed")
    # Scheme and host are pinned immediately above, so this is not an open-ended urlopen.
    with urllib.request.urlopen(url, timeout=timeout) as response:  # nosec B310
        return response.read()
