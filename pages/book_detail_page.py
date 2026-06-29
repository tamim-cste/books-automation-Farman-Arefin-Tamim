from playwright.sync_api import Page
from pages.base_page import BasePage


class BookDetailPage(BasePage):
    """Page object for individual book detail page."""

    _TITLE_SELECTOR = "article.product_page h1"
    _PRICE_SELECTOR = "p.price_color"
    _PRODUCT_INFO_SELECTOR = "table.table-striped"
    _PRODUCT_IMAGE_SELECTOR = "div.item.active img"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def get_title(self) -> str:
        self.wait_for_selector(self._TITLE_SELECTOR)
        return self.get_text(self._TITLE_SELECTOR)

    def get_price(self) -> str:
        self.wait_for_selector(self._PRICE_SELECTOR)
        return self._page.locator(self._PRICE_SELECTOR).first.inner_text().strip()

    def is_product_info_visible(self) -> bool:
        return self.is_visible(self._PRODUCT_INFO_SELECTOR)

    def is_image_visible(self) -> bool:
        return self.is_visible(self._PRODUCT_IMAGE_SELECTOR)

    def go_to_homepage(self) -> None:
        self.go_back()