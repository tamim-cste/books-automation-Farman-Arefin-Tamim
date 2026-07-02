"""
Utility for validating that a collection of URLs returns successful HTTP
responses. Kept separate from page objects/tests since it performs plain
HTTP requests rather than browser-driven navigation, and is reused only by
the broken-link test.
"""
from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List

import certifi
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LinkCheckResult:
    """Result of checking a single URL."""

    url: str
    status_code: int | None
    is_success: bool
    error: str | None = None


def _build_session() -> requests.Session:
    """
    Build a requests Session configured for reliable checks against
    books.toscrape.com (and similar small/free-tier hosted sites).

    Two real-world issues this addresses:
      1. Some local Python/OpenSSL installs ship a stale or misconfigured
         certificate store, causing SSLCertVerificationError even though the
         target site's certificate is valid. Pointing verify at certifi's
         bundle (kept up to date via pip) avoids relying on the OS store.
      2. Hosting platforms used by small demo sites (e.g. Heroku free tier)
         will reset connections (ConnectionResetError) under a burst of
         concurrent requests. A retry policy with backoff smooths over
         transient resets instead of failing the whole link-check test.
    """
    session = requests.Session()
    session.verify = certifi.where()

    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


class LinkChecker:
    """Performs concurrent HTTP HEAD/GET checks against a list of URLs."""

    def __init__(self, timeout: int = None, max_workers: int = None) -> None:
        self.timeout = timeout or settings.LINK_CHECK_TIMEOUT
        # Default lowered from 10 -> 5: books.toscrape.com is a small,
        # free-tier hosted site and resets connections under heavier
        # concurrency. 5 workers comfortably checks 60+ unique URLs without
        # tripping the host's connection limits.
        self.max_workers = max_workers or min(settings.LINK_CHECK_WORKERS, 5)
        self._session = _build_session()

    def check_url(self, url: str, attempt: int = 1) -> LinkCheckResult:
        """Check a single URL, falling back to GET if HEAD is not allowed."""
        try:
            response = self._session.head(
                url, timeout=self.timeout, allow_redirects=True
            )
            # Some servers don't implement HEAD properly; fall back to GET.
            if response.status_code in (405, 403, 501):
                response = self._session.get(
                    url, timeout=self.timeout, allow_redirects=True, stream=True
                )
            return LinkCheckResult(
                url=url,
                status_code=response.status_code,
                is_success=response.status_code == 200,
            )
        except (requests.exceptions.ConnectionError, requests.exceptions.SSLError) as exc:
            # One extra manual retry with a short pause for connection-level
            # failures (reset/refused) that the urllib3 Retry adapter does
            # not cover, since those happen at the connection layer before
            # a response/status code ever exists.
            if attempt < 2:
                time.sleep(0.75)
                return self.check_url(url, attempt=attempt + 1)
            logger.warning("Request failed for %s: %s", url, exc)
            return LinkCheckResult(
                url=url, status_code=None, is_success=False, error=str(exc)
            )
        except requests.RequestException as exc:
            logger.warning("Request failed for %s: %s", url, exc)
            return LinkCheckResult(
                url=url, status_code=None, is_success=False, error=str(exc)
            )

    def check_all(self, urls: List[str]) -> List[LinkCheckResult]:
        """Check all given URLs concurrently and return their results."""
        unique_urls = sorted(set(urls))
        results: List[LinkCheckResult] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self.check_url, url): url for url in unique_urls
            }
            for future in as_completed(future_to_url):
                results.append(future.result())

        return results

    @staticmethod
    def get_broken_links(results: List[LinkCheckResult]) -> List[LinkCheckResult]:
        return [r for r in results if not r.is_success]
