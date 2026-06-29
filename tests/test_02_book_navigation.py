# Third-party imports
import allure
import pytest
from playwright.sync_api import Page

# Internal imports
from pages.home_page import HomePage, BookCard
from pages.book_detail_page import BookDetailPage
from utils.config import Config
from utils.helpers import pick_random_items


@allure.feature("Book Navigation")
@allure.story("TC-02: Random Book Navigation")
@pytest.mark.regression
@pytest.mark.navigation
class TestRandomBookNavigation:
    """Test suite for random book selection and detail page validation."""

    @allure.title("5 randomly selected books open correct detail pages")
    def test_random_book_navigation(self, page: Page) -> None:
        """Click 5 random books and verify the detail page title and product info."""
        home_page = HomePage(page).open()

        with allure.step("Collect all book cards from homepage"):
            book_cards = home_page.get_all_book_cards()
            assert book_cards, "No books found on the homepage"

        with allure.step(f"Randomly select {Config.RANDOM_BOOK_COUNT} books"):
            selected_book_cards: list[BookCard] = pick_random_items(book_cards, Config.RANDOM_BOOK_COUNT)
            allure.attach(
                "\n".join([book_card.book_title for book_card in selected_book_cards]),
                name="Selected Book Titles",
                attachment_type=allure.attachment_type.TEXT,
            )

        book_detail_page = BookDetailPage(page)

        for book_card in selected_book_cards:
            with allure.step(f"Validate book: '{book_card.book_title}'"):

                with allure.step("Click the book on homepage"):
                    home_page.click_book_by_index(book_card.book_index)

                with allure.step("Verify detail page H1 title matches"):
                    detail_title = book_detail_page.get_title()
                    assert detail_title == book_card.book_title, (
                        f"Title mismatch!\n"
                        f"  Homepage : '{book_card.book_title}'\n"
                        f"  Detail   : '{detail_title}'"
                    )

                with allure.step("Verify product information table is visible"):
                    assert book_detail_page.is_product_info_visible(), (
                        f"Product info table not visible for book '{book_card.book_title}'"
                    )

                with allure.step("Navigate back to homepage"):
                    book_detail_page.go_to_homepage()
                    home_page = HomePage(page)