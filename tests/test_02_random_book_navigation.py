"""
Test Case 2: Random Book Navigation Validation

Verifies that randomly selected books open the correct details page, and
that the H1 title and book information render correctly on each.
"""
import allure
import pytest

from pages.book_details_page import BookDetailsPage
from pages.home_page import HomePage
from utils.text_helpers import truncated_title_matches


@allure.feature("Navigation")
@allure.story("Random Book Navigation Validation")
class TestRandomBookNavigation:
    """Validates that randomly selected books navigate to a correct, fully
    rendered details page."""

    @pytest.mark.regression
    @pytest.mark.navigation
    @allure.title("Randomly selected books open the correct details page")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_random_books_navigate_correctly(
        self, home_page: HomePage, book_details_page: BookDetailsPage
    ):
        with allure.step("Collect a random sample of books from the homepage"):
            random_books = home_page.get_random_books()
            allure.attach(
                "\n".join(b.title for b in random_books),
                name="Selected Books",
                attachment_type=allure.attachment_type.TEXT,
            )

        failures = []

        for index, book in enumerate(random_books, start=1):
            with allure.step(f"[{index}] Navigate to details page for '{book.title}'"):
                home_page.open_book(book)

            with allure.step(f"[{index}] Verify the details page loaded successfully"):
                if not book_details_page.is_loaded():
                    failures.append(f"Details page did not load for '{book.title}'")
                    continue

            with allure.step(f"[{index}] Verify H1 title matches the selected book title"):
                actual_title = book_details_page.get_title()
                if not truncated_title_matches(book.title, actual_title):
                    failures.append(
                        f"Title mismatch: expected '{book.title}', got '{actual_title}'"
                    )

            with allure.step(f"[{index}] Verify book information is visible"):
                if not book_details_page.is_visible(book_details_page.product_info_table):
                    failures.append(
                        f"Product information table not visible for '{book.title}'"
                    )
                if not book_details_page.is_visible(book_details_page.availability_locator):
                    failures.append(
                        f"Availability info not visible for '{book.title}'"
                    )

            with allure.step(f"[{index}] Navigate back to the homepage"):
                home_page.load()

        assert not failures, "Navigation validation failures:\n" + "\n".join(failures)
