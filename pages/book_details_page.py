"""
Page object for an individual book's details page.

Encapsulates locators and extraction logic for the H1 title, price,
availability, and the "Product Information" table so that no test needs
to know the underlying DOM structure.
"""
from __future__ import annotations

from playwright.sync_api import Page, Locator

from pages.base_page import BasePage
from pages.models import BookDetail


class BookDetailsPage(BasePage):
    """Page object representing a single book's details page."""

    TITLE_SELECTOR = "div.product_main h1"
    PRICE_SELECTOR = "div.product_main p.price_color"
    AVAILABILITY_SELECTOR = "div.product_main p.availability"
    PRODUCT_INFO_TABLE_SELECTOR = "table.table-striped"
    PRODUCT_INFO_ROW_SELECTOR = "table.table-striped tr"
    BREADCRUMB_SELECTOR = "ul.breadcrumb"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ------------------------------------------------------------------
    # Core element accessors
    # ------------------------------------------------------------------
    @property
    def title_locator(self) -> Locator:
        return self.page.locator(self.TITLE_SELECTOR)

    @property
    def price_locator(self) -> Locator:
        return self.page.locator(self.PRICE_SELECTOR)

    @property
    def availability_locator(self) -> Locator:
        return self.page.locator(self.AVAILABILITY_SELECTOR)

    @property
    def product_info_table(self) -> Locator:
        return self.page.locator(self.PRODUCT_INFO_TABLE_SELECTOR)

    @property
    def breadcrumb(self) -> Locator:
        return self.page.locator(self.BREADCRUMB_SELECTOR)

    # ------------------------------------------------------------------
    # Convenience extraction methods used by tests
    # ------------------------------------------------------------------
    def get_title(self) -> str:
        return self.title_locator.text_content().strip()

    def get_price(self) -> str:
        return self.price_locator.text_content().strip()

    def get_availability(self) -> str:
        text = self.availability_locator.text_content()
        return " ".join(text.split())  # collapse internal whitespace/newlines

    def is_loaded(self) -> bool:
        """Confirm the details page has rendered its core elements."""
        return self.is_visible(self.title_locator) and self.is_visible(
            self.price_locator
        )

    def get_book_detail(self) -> BookDetail:
        """Extract a structured BookDetail object from the current page."""
        info = self._parse_product_info_table()
        return BookDetail(
            title=self.get_title(),
            price=self.get_price(),
            availability=self.get_availability(),
            upc=info.get("UPC", ""),
            product_type=info.get("Product Type", ""),
        )

    def _parse_product_info_table(self) -> dict:
        """Parse the 'Product Information' table into a {label: value} dict."""
        rows = self.page.locator(self.PRODUCT_INFO_ROW_SELECTOR)
        data = {}
        for i in range(rows.count()):
            row = rows.nth(i)
            label = row.locator("th").text_content().strip()
            value = row.locator("td").text_content().strip()
            data[label] = value
        return data
