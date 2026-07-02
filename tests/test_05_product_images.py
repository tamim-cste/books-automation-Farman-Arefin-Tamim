"""
Test Case 5: Product Image Validation

Verifies that product images render correctly with required attributes
(visible, non-empty src/alt, 'thumbnail' class) across up to 5 paginated
listing pages.
"""
import allure
import pytest

from config.settings import settings
from pages.home_page import HomePage


@allure.feature("UI Validation")
@allure.story("Product Image Validation")
class TestProductImages:
    """Validates product image rendering and pagination across listing pages."""

    @pytest.mark.regression
    @pytest.mark.images
    @allure.title("Product images render correctly across paginated listing pages")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_images_valid_across_pages(self, home_page: HomePage):
        max_pages = settings.MAX_PAGINATION_PAGES
        all_failures = []
        pages_visited = 0

        for page_number in range(1, max_pages + 1):
            pages_visited = page_number
            with allure.step(f"Validate product images on page {page_number}"):
                page_failures = self._validate_images_on_current_page(
                    home_page, page_number
                )
                all_failures.extend(page_failures)

            with allure.step(f"Check pagination after page {page_number}"):
                if page_number == max_pages or not home_page.has_next_page():
                    break
                home_page.go_to_next_page()

        allure.attach(
            f"Pages visited: {pages_visited}",
            name="Pagination Summary",
            attachment_type=allure.attachment_type.TEXT,
        )

        if all_failures:
            allure.attach(
                "\n".join(all_failures),
                name="Image Validation Failures",
                attachment_type=allure.attachment_type.TEXT,
            )

        assert not all_failures, (
            f"Image validation failed with {len(all_failures)} issue(s):\n"
            + "\n".join(all_failures)
        )

    @staticmethod
    def _validate_images_on_current_page(home_page: HomePage, page_number: int) -> list:
        """Validate every product image on the currently loaded page.

        Returns a list of human-readable failure descriptions (empty if none).
        """
        failures = []
        images = home_page.product_images
        image_count = images.count()

        if image_count == 0:
            failures.append(f"Page {page_number}: no product images found")
            return failures

        for i in range(image_count):
            image = images.nth(i)
            label = f"Page {page_number}, image {i + 1}"

            if not home_page.is_visible(image):
                failures.append(f"{label}: image is not visible")
                continue

            src = image.get_attribute("src")
            if not src:
                failures.append(f"{label}: missing or empty 'src' attribute")

            alt = image.get_attribute("alt")
            if not alt:
                failures.append(f"{label}: missing or empty 'alt' attribute")

            css_class = image.get_attribute("class") or ""
            if "thumbnail" not in css_class:
                failures.append(
                    f"{label}: expected 'thumbnail' in class attribute, got '{css_class}'"
                )

        return failures
