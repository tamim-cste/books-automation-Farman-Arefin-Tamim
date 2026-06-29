# Third-party imports
import allure
import pytest
from playwright.sync_api import Page

# Internal imports
from pages.home_page import HomePage
from utils.config import Config


@allure.feature("Homepage")
@allure.story("TC-01: Homepage Validation")
@pytest.mark.smoke
@pytest.mark.ui
class TestHomepageValidation:
    """Test suite for homepage load and content validation."""

    @allure.title("Homepage URL is correct")
    def test_page_url_is_correct(self, page: Page) -> None:
        """Check that the loaded URL matches the expected base URL."""
        home = HomePage(page).open()
        with allure.step("Verify page URL"):
            assert Config.BASE_URL in home.get_url(), (
                f"Expected URL to contain '{Config.BASE_URL}', got '{home.get_url()}'"
            )

    @allure.title("Homepage title is present and non-empty")
    def test_page_title_is_present(self, page: Page) -> None:
        """Check that the page has a non-empty browser title."""
        home = HomePage(page).open()
        with allure.step("Verify page title is not empty"):
            page_title = home.get_page_title()
            assert page_title, "Page title must not be empty"
            allure.attach(page_title, name="Page Title", attachment_type=allure.attachment_type.TEXT)

    @allure.title("All visible headings are non-empty")
    def test_all_headings_are_visible_and_non_empty(self, page: Page) -> None:
        """Check that every h1-h6 heading on the page contains text."""
        home = HomePage(page).open()
        with allure.step("Collect all headings"):
            headings = home.get_all_headings()
            assert headings, "No headings found on the homepage"
            allure.attach(
                "\n".join(headings),
                name="Heading Texts",
                attachment_type=allure.attachment_type.TEXT,
            )
        with allure.step("Assert each heading is non-empty"):
            for text in headings:
                assert text.strip(), f"Found a heading with empty text: '{text}'"

    @allure.title("Books section is visible on homepage")
    def test_books_section_is_visible(self, page: Page) -> None:
        """Check that the main books section is rendered on the page."""
        home = HomePage(page).open()
        with allure.step("Check books section visibility"):
            assert home.is_books_section_visible(), "Books section is not visible"

    @allure.title("Homepage contains at least one book item")
    def test_books_section_contains_books(self, page: Page) -> None:
        """Check that the books section has at least one book card."""
        home = HomePage(page).open()
        with allure.step("Count book items"):
            count = home.get_book_count()
            allure.attach(str(count), name="Book Count", attachment_type=allure.attachment_type.TEXT)
            assert count > 0, f"Expected books on homepage, found {count}"