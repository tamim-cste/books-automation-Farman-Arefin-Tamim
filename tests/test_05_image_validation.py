# Third party imports
import allure
import pytest
from playwright.sync_api import Page, Locator

# Internal imports
from pages.home_page import HomePage
from utils.config import Config


@allure.feature("Image Validation")
@allure.story("TC-05: Product Image Attributes")
@pytest.mark.regression
@pytest.mark.images
class TestProductImageValidation:
    """
    Test suite for product image rendering and attribute validation.
    """

    @staticmethod
    def _validate_images_on_page(images: list[Locator], page_number: int) -> list[str]:
        """
        Check visibility, src, alt and class for every image on the page.
        """
        failures: list[str] = []

        for idx, img in enumerate(images, start=1):
            label = f"Page {page_number} | Image {idx}"

            if not img.is_visible():
                failures.append(f"{label}: Image is NOT visible")
                continue

            src = img.get_attribute("src") or ""
            if not src.strip():
                failures.append(f"{label}: 'src' attribute is empty or missing")

            alt = img.get_attribute("alt") or ""
            if not alt.strip():
                failures.append(f"{label}: 'alt' attribute is empty or missing")

            cls = img.get_attribute("class") or ""
            if "thumbnail" not in cls:
                failures.append(
                    f"{label}: 'class' does not contain 'thumbnail' (got: '{cls}')"
                )

        return failures

    @allure.title("Product images have correct attributes across up to 5 pages")
    def test_product_images_across_pages(self, page: Page) -> None:
        """
        Validate image src, alt and class attributes across paginated results.
        """
        home = HomePage(page).open()
        all_failures: list[str] = []
        current_page = 1

        while current_page <= Config.MAX_PAGES_IMAGE_CHECK:
            with allure.step(f"Validating images on page {current_page}"):
                images = home.get_product_images()
                assert images, f"No product images found on page {current_page}"

                allure.attach(
                    str(len(images)),
                    name=f"Image count — page {current_page}",
                    attachment_type=allure.attachment_type.TEXT,
                )

                page_failures = self._validate_images_on_page(images, current_page)
                all_failures.extend(page_failures)

            if not home.has_next_page():
                allure.attach(
                    f"Pagination ended after page {current_page}.",
                    name="Pagination Status",
                    attachment_type=allure.attachment_type.TEXT,
                )
                break

            with allure.step(f"Click Next → go to page {current_page + 1}"):
                home.click_next_page()
                current_page += 1

        if all_failures:
            allure.attach(
                "\n".join(all_failures),
                name="Image Validation Failures",
                attachment_type=allure.attachment_type.TEXT,
            )

        assert not all_failures, (
            f"{len(all_failures)} image issue(s) found:\n" + "\n".join(all_failures)
        )