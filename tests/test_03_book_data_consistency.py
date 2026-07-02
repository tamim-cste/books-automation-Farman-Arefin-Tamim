"""
Test Case 3: Book Data Consistency Validation

Verifies that book title and price information displayed on the homepage
matches the information displayed on the corresponding details page.
"""
import allure
import pytest

from pages.book_details_page import BookDetailsPage
from pages.home_page import HomePage
from utils.text_helpers import normalize_price, truncated_title_matches


@allure.feature("Data Consistency")
@allure.story("Book Data Consistency Validation")
class TestBookDataConsistency:
    """Validates that homepage and details-page data for the same book agree."""

    @pytest.mark.regression
    @pytest.mark.data_consistency
    @allure.title("Homepage and details page data are consistent for random books")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_and_details_data_match(
        self, home_page: HomePage, book_details_page: BookDetailsPage
    ):
        with allure.step("Collect a random sample of books from the homepage"):
            random_books = home_page.get_random_books()

        mismatches = []

        for index, homepage_book in enumerate(random_books, start=1):
            with allure.step(
                f"[{index}] Open details page for '{homepage_book.title}'"
            ):
                home_page.open_book(homepage_book)

            with allure.step(f"[{index}] Capture details page title and price"):
                details_title = book_details_page.get_title()
                details_price = book_details_page.get_price()

            with allure.step(f"[{index}] Compare titles"):
                if not truncated_title_matches(homepage_book.title, details_title):
                    mismatches.append(
                        f"Title mismatch for book {index}: "
                        f"homepage='{homepage_book.title}' details='{details_title}'"
                    )

            with allure.step(f"[{index}] Compare prices"):
                homepage_price = normalize_price(homepage_book.price)
                details_price_norm = normalize_price(details_price)
                if homepage_price != details_price_norm:
                    mismatches.append(
                        f"Price mismatch for book {index} ('{homepage_book.title}'): "
                        f"homepage='{homepage_price}' details='{details_price_norm}'"
                    )

            with allure.step(f"[{index}] Navigate back to the homepage"):
                home_page.load()

        if mismatches:
            allure.attach(
                "\n".join(mismatches),
                name="Data Inconsistencies",
                attachment_type=allure.attachment_type.TEXT,
            )

        assert not mismatches, "Data consistency failures:\n" + "\n".join(mismatches)
