from __future__ import annotations

from typing import List, Optional
from .utils import Bookmark


def check_liveness(bookmarks: List[Bookmark], *, enabled: bool) -> None:
    # MVP: mark as 'unknown' if disabled; skip network operations.
    status = "unknown" if not enabled else "unchecked"
    for b in bookmarks:
        if b.url:
            b.liveness = status


def extract_text_from_html(html: str, max_chars: int = 2000) -> str:
    # Light-weight text extraction using BeautifulSoup
    try:
        from bs4 import BeautifulSoup
    except Exception:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    # Normalize whitespace
    import re

    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_chars:
        text = text[:max_chars]
    return text


async def _fetch_one(
    session, url: str, *, timeout: int, ua: str
) -> Optional[str]:  # pragma: no cover - network
    try:
        async with session.get(url, timeout=timeout, headers={"User-Agent": ua}) as resp:
            if resp.status >= 200 and resp.status < 400:
                return await resp.text(errors="ignore")
    except Exception:
        return None
    return None


def enrich_with_content(  # pragma: no cover - network path is not covered in tests
    bookmarks: List[Bookmark],
    *,
    enabled: bool,
    timeout_sec: int,
    concurrent: int,
    user_agent: str,
    max_chars: int,
) -> None:
    if not enabled:
        return
    try:
        import asyncio
        import aiohttp
    except Exception:
        return
    urls = [(i, b.url) for i, b in enumerate(bookmarks) if b.url]
    if not urls:
        return

    async def runner():  # pragma: no cover - network
        conn = aiohttp.TCPConnector(limit=concurrent, ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            tasks = [
                _fetch_one(session, url, timeout=timeout_sec, ua=user_agent) for _, url in urls
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for (idx, _), html in zip(urls, results):
                if isinstance(html, str) and html:
                    snippet = extract_text_from_html(html, max_chars=max_chars)
                    if snippet:
                        bookmarks[idx].content_snippet = snippet

    try:  # pragma: no cover - network
        asyncio.run(runner())
    except RuntimeError:  # pragma: no cover - network
        # In case of nested event loop (rare in CLI), create a new loop
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(runner())
        finally:
            loop.close()
