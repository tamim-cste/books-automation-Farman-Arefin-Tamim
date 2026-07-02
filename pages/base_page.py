"""
BasePage encapsulates behavior that is common to every page object in the
framework (navigation, waiting strategies, generic element queries).

Every concrete page object inherits from this class so that synchronization
logic and low-level Playwright calls live in exactly one place (DRY) and so
that page objects only need to express *what* to do, not *how* Playwright
does it (Single Responsibility).
"""
from __future__ import annotations

import logging
from typing import List

from playwright.sync_api import Page, Locator, expect

from config.settings import settings

logger = logging.getLogger(__name__)


class BasePage:
    """Common functionality shared by all page objects."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.base_url = settings.BASE_URL

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def goto(self, path: str = "") -> None:
        """Navigate to a path relative to the base URL and wait for load."""
        url = f"{self.base_url}{path}" if path else self.base_url
        logger.info("Navigating to %s", url)
        self.page.goto(url, wait_until="domcontentloaded")

    def goto_url(self, url: str) -> None:
        """Navigate directly to a fully-qualified URL."""
        logger.info("Navigating to %s", url)
        self.page.goto(url, wait_until="domcontentloaded")

    def go_back(self) -> None:
        """Navigate back in browser history and wait for the page to settle."""
        self.page.go_back(wait_until="domcontentloaded")

    @property
    def current_url(self) -> str:
        return self.page.url

    @property
    def title(self) -> str:
        return self.page.title()

    # ------------------------------------------------------------------
    # Generic, reusable element helpers (no hardcoded sleeps anywhere)
    # ------------------------------------------------------------------
    def is_visible(self, locator: Locator, timeout: int = None) -> bool:
        """Return True if the locator becomes visible within the timeout."""
        try:
            locator.first.wait_for(
                state="visible", timeout=timeout or settings.DEFAULT_TIMEOUT
            )
            return True
        except Exception:
            return False

    def wait_for_visible(self, locator: Locator, timeout: int = None) -> Locator:
        """Wait until the locator is visible, then return it for chaining."""
        locator.first.wait_for(
            state="visible", timeout=timeout or settings.DEFAULT_TIMEOUT
        )
        return locator

    def get_all_texts(self, locator: Locator) -> List[str]:
        """Return stripped, non-empty text content for every matched element."""
        raw_texts = locator.all_text_contents()
        return [text.strip() for text in raw_texts]

    def count(self, locator: Locator) -> int:
        return locator.count()

    def wait_for_load(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
