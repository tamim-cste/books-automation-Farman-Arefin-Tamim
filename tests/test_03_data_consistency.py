# Third party imports
import allure
import pytest
from playwright.sync_api import Page

# Internal imports
from pages.home_page import HomePage, BookCard
from pages.book_detail_page import BookDetailPage
from utils.config import Config
from utils.helpers import pick_random_items, normalize_price


@allure.feature("Data Consistency")
@allure.story("TC-03: Book Data Consistency")
@pytest.mark.regression
@pytest.mark.data
class TestBookDataConsistency:
    """
    Test suite for verifying data consistency between homepage and detail page.
    """

    @allure.title("Homepage and detail page data match for 5 random books")
    def test_book_data_consistency(self, page: Page) -> None:
        """
        Check that title and price match between homepage card and detail page.
        """
        home_page = HomePage(page).open()

        with allure.step("Collect all book cards"):
            book_cards = home_page.get_all_book_cards()
            assert book_cards, "No books found on the homepage"

        with allure.step(f"Randomly select {Config.RANDOM_BOOK_COUNT} books"):
            selected_book_cards: list[BookCard] = pick_random_items(book_cards, Config.RANDOM_BOOK_COUNT)

        book_detail_page = BookDetailPage(page)
        failures = []

        for book_card in selected_book_cards:
            with allure.step(f"Checking data for: '{book_card.book_title}'"):

                homepage_title = book_card.book_title
                homepage_price = normalize_price(book_card.book_price)

                with allure.step("Open detail page"):
                    home_page.click_book_by_index(book_card.book_index)

                with allure.step("Capture detail page title and price"):
                    detail_title = book_detail_page.get_title()
                    detail_price = normalize_price(book_detail_page.get_price())

                title_ok = homepage_title == detail_title
                price_ok = homepage_price == detail_price

                if not title_ok or not price_ok:
                    failures.append(
                        f"Book '{homepage_title}':\n"
                        f"  Title  — homepage='{homepage_title}'  detail='{detail_title}'  match={title_ok}\n"
                        f"  Price  — homepage='{homepage_price}'  detail='{detail_price}'  match={price_ok}"
                    )

                allure.attach(
                    (
                        f"Homepage title : {homepage_title}\n"
                        f"Detail title   : {detail_title}\n"
                        f"Title match    : {title_ok}\n\n"
                        f"Homepage price : {homepage_price}\n"
                        f"Detail price   : {detail_price}\n"
                        f"Price match    : {price_ok}"
                    ),
                    name=f"Comparison — {homepage_title[:30]}",
                    attachment_type=allure.attachment_type.TEXT,
                )

                with allure.step("Navigate back to homepage"):
                    book_detail_page.go_to_homepage()
                    home_page = HomePage(page)

        assert not failures, (
            f"{len(failures)} data inconsistency/ies found:\n"
            + "\n\n".join(failures)
        )