from dataclasses import dataclass
from typing import List
from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.config import Config


@dataclass
class BookCard:
    """Represents a single book item on the homepage."""
    book_title: str
    book_price: str
    book_index: int


class HomePage(BasePage):
    """Page object for the Books to Scrape homepage."""

    _BOOKS_SECTION = "section"
    _BOOK_ITEMS = "article.product_pod"
    _BOOK_TITLE = "h3 > a"
    _BOOK_PRICE = "p.price_color"
    _HEADINGS = "h1, h2, h3, h4, h5, h6"
    _NEXT_BUTTON = "li.next > a"
    _PRODUCT_IMAGES = "article.product_pod img"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def open(self) -> "HomePage":
        self.navigate(Config.BASE_URL)
        return self

    def get_url(self) -> str:
        return self.current_url

    def get_page_title(self) -> str:
        return self.title

    def get_all_headings(self) -> List[str]:
        heading_locators = self._page.locator(self._HEADINGS).all()
        return [h.inner_text().strip() for h in heading_locators if h.is_visible()]

    def is_books_section_visible(self) -> bool:
        return self.is_visible(self._BOOKS_SECTION)

    def get_book_count(self) -> int:
        return len(self._page.locator(self._BOOK_ITEMS).all())

    def get_all_book_cards(self) -> List[BookCard]:
        book_item_elements = self._page.locator(self._BOOK_ITEMS).all()
        book_cards: List[BookCard] = []
        for card_index, book_element in enumerate(book_item_elements):
            title_element = book_element.locator(self._BOOK_TITLE)
            price_element = book_element.locator(self._BOOK_PRICE)
            book_title = title_element.get_attribute("title") or title_element.inner_text().strip()
            book_price = price_element.inner_text().strip()
            book_cards.append(
                BookCard(
                    book_title=book_title,
                    book_price=book_price,
                    book_index=card_index,
                )
            )
        return book_cards

    def click_book_by_index(self, index: int) -> None:
        self._page.locator(self._BOOK_ITEMS).nth(index).locator(self._BOOK_TITLE).click()
        self._page.wait_for_load_state("networkidle")

    def has_next_page(self) -> bool:
        return self._page.locator(self._NEXT_BUTTON).count() > 0

    def click_next_page(self) -> None:
        self._page.locator(self._NEXT_BUTTON).click()
        self._page.wait_for_load_state("networkidle")

    def get_product_images(self) -> list:
        return self._page.locator(self._PRODUCT_IMAGES).all()

    def get_all_hrefs(self) -> List[str]:
        anchor_elements = self._page.locator("a[href]").all()
        href_set = set()
        for anchor_element in anchor_elements:
            href = anchor_element.get_attribute("href")
            if href and href.strip():
                href_set.add(href.strip())
        return list(href_set)