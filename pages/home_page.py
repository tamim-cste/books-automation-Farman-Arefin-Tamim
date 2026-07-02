"""
Page object for the homepage / book listing (catalogue) pages.

Encapsulates every locator and interaction needed for:
 - Heading validation
 - Book listing retrieval
 - Random book selection
 - Pagination ("Next" button) handling
 - Product image retrieval

Locators are defined once as properties so that if the site markup changes,
only this file needs to be updated (Open/Closed-friendly design).
"""
from __future__ import annotations

import logging
import random
from typing import List
from urllib.parse import urljoin

from playwright.sync_api import Page, Locator

from config.settings import settings
from pages.base_page import BasePage
from pages.models import BookSummary

logger = logging.getLogger(__name__)


class HomePage(BasePage):
    """Page object representing the Books to Scrape homepage / listing pages."""

    # ------------------------------------------------------------------
    # Locators (centralized so selectors are never duplicated elsewhere)
    # ------------------------------------------------------------------
    HEADINGS_SELECTOR = "h1, h2, h3, h4, h5, h6"
    BOOKS_SECTION_SELECTOR = "section"
    BOOK_ITEM_SELECTOR = "article.product_pod"
    BOOK_TITLE_LINK_SELECTOR = "h3 a"
    BOOK_PRICE_SELECTOR = "p.price_color"
    BOOK_IMAGE_SELECTOR = "div.image_container img"
    NEXT_BUTTON_SELECTOR = "li.next a"
    ALL_LINKS_SELECTOR = "a"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def load(self) -> "HomePage":
        """Navigate to the homepage."""
        self.goto(settings.HOME_PATH)
        return self

    # ------------------------------------------------------------------
    # Heading validation helpers
    # ------------------------------------------------------------------
    @property
    def headings_locator(self) -> Locator:
        return self.page.locator(self.HEADINGS_SELECTOR)

    def get_visible_heading_texts(self) -> List[str]:
        """Return text content of every *visible* heading element on the page."""
        all_headings = self.headings_locator
        visible_texts: List[str] = []
        for i in range(all_headings.count()):
            heading = all_headings.nth(i)
            if heading.is_visible():
                visible_texts.append(heading.text_content().strip())
        return visible_texts

    # ------------------------------------------------------------------
    # Books section helpers
    # ------------------------------------------------------------------
    @property
    def books_section(self) -> Locator:
        return self.page.locator(self.BOOKS_SECTION_SELECTOR)

    @property
    def book_items(self) -> Locator:
        return self.page.locator(self.BOOK_ITEM_SELECTOR)

    def get_book_count(self) -> int:
        return self.book_items.count()

    def get_all_books(self) -> List[BookSummary]:
        """Extract title, price and detail URL for every book on the current page."""
        books: List[BookSummary] = []
        items = self.book_items
        item_count = items.count()

        for i in range(item_count):
            item = items.nth(i)
            title_link = item.locator(self.BOOK_TITLE_LINK_SELECTOR)
            title = title_link.get_attribute("title") or title_link.text_content()
            price = item.locator(self.BOOK_PRICE_SELECTOR).text_content()
            href = title_link.get_attribute("href")
            detail_url = self._resolve_url(href)

            books.append(
                BookSummary(
                    title=title.strip(),
                    price=price.strip(),
                    detail_url=detail_url,
                )
            )
        return books

    def get_random_books(self, sample_size: int = None) -> List[BookSummary]:
        """Return a random, non-repeating sample of books from the homepage."""
        sample_size = sample_size or settings.RANDOM_BOOK_SAMPLE_SIZE
        all_books = self.get_all_books()
        actual_sample_size = min(sample_size, len(all_books))
        selected = random.sample(all_books, actual_sample_size)
        logger.info(
            "Randomly selected %d books: %s",
            len(selected),
            [b.title for b in selected],
        )
        return selected

    def open_book(self, book: BookSummary) -> None:
        """Navigate directly to a book's details page via its captured URL."""
        self.goto_url(book.detail_url)

    # ------------------------------------------------------------------
    # Link collection (for broken-link validation)
    # ------------------------------------------------------------------
    def get_all_hrefs(self) -> List[str]:
        """Collect every non-empty href on the current page as an absolute URL."""
        anchors = self.page.locator(self.ALL_LINKS_SELECTOR)
        hrefs: List[str] = []
        count = anchors.count()
        for i in range(count):
            href = anchors.nth(i).get_attribute("href")
            if href and not href.startswith("javascript:") and not href.startswith("#"):
                hrefs.append(self._resolve_url(href))
        return hrefs

    # ------------------------------------------------------------------
    # Image validation helpers
    # ------------------------------------------------------------------
    @property
    def product_images(self) -> Locator:
        return self.page.locator(self.BOOK_IMAGE_SELECTOR)

    def get_image_count(self) -> int:
        return self.product_images.count()

    # ------------------------------------------------------------------
    # Pagination helpers
    # ------------------------------------------------------------------
    @property
    def next_button(self) -> Locator:
        return self.page.locator(self.NEXT_BUTTON_SELECTOR)

    def has_next_page(self) -> bool:
        return self.next_button.count() > 0

    def go_to_next_page(self) -> None:
        """Click the pagination 'Next' button and wait for the new page to load."""
        self.next_button.first.click()
        self.wait_for_load()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _resolve_url(self, href: str) -> str:
        """Resolve a possibly-relative href against the current page URL."""
        return urljoin(self.page.url, href)
