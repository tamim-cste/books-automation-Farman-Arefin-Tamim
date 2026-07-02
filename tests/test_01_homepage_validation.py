"""
Test Case 1: Homepage Validation

Verifies that the homepage loads successfully and displays the expected
content: correct URL/title, visible non-empty headings, and a populated
books section.
"""
import allure
import pytest

from config.settings import settings
from pages.home_page import HomePage


@allure.feature("Homepage")
@allure.story("Homepage Validation")
class TestHomepageValidation:
    """Validates core homepage load behavior and visible content."""

    @pytest.mark.smoke
    @pytest.mark.ui
    @allure.title("Homepage loads with the correct URL")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_homepage_url_is_correct(self, home_page: HomePage):
        with allure.step("Verify the current URL matches the expected homepage URL"):
            assert home_page.current_url == settings.home_url, (
                f"Expected URL '{settings.home_url}' but got "
                f"'{home_page.current_url}'"
            )

    @pytest.mark.smoke
    @pytest.mark.ui
    @allure.title("Homepage loads with the correct page title")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_title_is_correct(self, home_page: HomePage):
        with allure.step("Verify the page title matches the expected value"):
            expected_title_fragment = "All products"
            assert expected_title_fragment in home_page.title, (
                f"Expected title to contain '{expected_title_fragment}' but got "
                f"'{home_page.title}'"
            )

    @pytest.mark.smoke
    @pytest.mark.ui
    @allure.title("All visible headings are displayed with non-empty text")
    @allure.severity(allure.severity_level.NORMAL)
    def test_all_headings_visible_and_non_empty(self, home_page: HomePage):
        with allure.step("Collect all visible heading texts (h1-h6)"):
            heading_texts = home_page.get_visible_heading_texts()
            allure.attach(
                "\n".join(heading_texts),
                name="Visible Headings",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("Verify at least one heading is visible"):
            assert len(heading_texts) > 0, "No visible headings found on the homepage"

        with allure.step("Verify every visible heading contains non-empty text"):
            empty_headings = [i for i, text in enumerate(heading_texts) if not text]
            assert not empty_headings, (
                f"Found {len(empty_headings)} visible heading(s) with empty text "
                f"at positions {empty_headings}"
            )

    @pytest.mark.smoke
    @pytest.mark.ui
    @allure.title("Books section is visible on the homepage")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_books_section_is_visible(self, home_page: HomePage):
        with allure.step("Verify the books section container is visible"):
            assert home_page.is_visible(home_page.books_section), (
                "Books section is not visible on the homepage"
            )

    @pytest.mark.smoke
    @pytest.mark.ui
    @allure.title("Books section contains at least one book item")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_books_section_has_book_items(self, home_page: HomePage):
        with allure.step("Count the number of book items in the books section"):
            book_count = home_page.get_book_count()
            allure.attach(
                str(book_count), name="Book Count", attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Verify the book list is not empty"):
            assert book_count > 0, "Expected at least one book item, found none"
