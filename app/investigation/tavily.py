"""
Tavily research provider for Shadow Files.

This module provides the first real external research connection for
Shadow Files.

Design goals:
- Use Tavily's normal API-key endpoint.
- Use the free/basic search mode only.
- Use Python's standard library HTTP client.
- Never use Tavily's paid x402 endpoint.
- Never silently retry a failed request.
- Return source URLs and retrieved content for later evidence handling.
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from shadow_core.providers import (
    ProviderError,
    ResearchProvider,
)


TAVILY_SEARCH_URL = "https://api.tavily.com/search"


@dataclass(frozen=True)
class TavilyResearchResult:
    """One source returned by Tavily."""

    title: str
    url: str
    content: str
    score: float | None
    published_date: str | None


class TavilyResearchProvider(ResearchProvider):
    """
    Real Tavily HTTP implementation of ResearchProvider.

    The provider intentionally uses Tavily's basic search mode because
    basic search is the lowest-cost API search mode and is appropriate
    for the initial zero-dollar Shadow Files integration.
    """

    def __init__(
        self,
        api_key: str | None = None,
        timeout: int = 30,
    ) -> None:
        self._api_key = (
            api_key
            or os.getenv("TAVILY_API_KEY")
        )

        if not self._api_key:
            raise ProviderError(
                "TAVILY_API_KEY is not configured."
            )

        if timeout <= 0:
            raise ProviderError(
                "Tavily timeout must be greater than zero."
            )

        self._timeout = timeout

    def search(
        self,
        query: str,
    ) -> list[TavilyResearchResult]:
        """
        Execute one real Tavily search request.

        No automatic retry is performed. This prevents an HTTP failure
        from silently generating additional API usage.
        """

        if not query or not query.strip():
            raise ProviderError(
                "Research query cannot be empty."
            )

        payload = {
            "query": query.strip(),
            "search_depth": "basic",
            "max_results": 10,
            "include_answer": False,
            "include_raw_content": False,
        }

        request = Request(
            TAVILY_SEARCH_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": (
                    f"Bearer {self._api_key}"
                ),
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Shadow-Files/1.0",
            },
            method="POST",
        )

        retrieved_at = datetime.now(
            timezone.utc
        ).isoformat()

        try:
            with urlopen(
                request,
                timeout=self._timeout,
            ) as response:
                raw_body = response.read().decode(
                    "utf-8"
                )

        except HTTPError as exc:
            if exc.code == 401:
                raise ProviderError(
                    "Tavily authentication failed. "
                    "Check TAVILY_API_KEY."
                ) from exc

            if exc.code == 429:
                raise ProviderError(
                    "Tavily rate or usage limit reached."
                ) from exc

            raise ProviderError(
                f"Tavily HTTP error: {exc.code}."
            ) from exc

        except URLError as exc:
            raise ProviderError(
                f"Tavily connection failed: {exc.reason}"
            ) from exc

        except TimeoutError as exc:
            raise ProviderError(
                "Tavily request timed out."
            ) from exc

        except OSError as exc:
            raise ProviderError(
                f"Tavily network error: {exc}"
            ) from exc

        try:
            response_data = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise ProviderError(
                "Tavily returned invalid JSON."
            ) from exc

        results = response_data.get(
            "results",
            [],
        )

        if not isinstance(results, list):
            raise ProviderError(
                "Tavily returned an invalid results payload."
            )

        normalized: list[TavilyResearchResult] = []

        for item in results:
            if not isinstance(item, dict):
                continue

            url = str(
                item.get("url", "")
            ).strip()

            if not url:
                continue

            score_value = item.get("score")

            score: float | None

            try:
                score = (
                    float(score_value)
                    if score_value is not None
                    else None
                )
            except (TypeError, ValueError):
                score = None

            normalized.append(
                TavilyResearchResult(
                    title=str(
                        item.get("title", "")
                    ).strip(),
                    url=url,
                    content=str(
                        item.get("content", "")
                    ).strip(),
                    score=score,
                    published_date=(
                        str(
                            item.get(
                                "published_date"
                            )
                        ).strip()
                        if item.get(
                            "published_date"
                        )
                        else None
                    ),
                )
            )

        return normalized
