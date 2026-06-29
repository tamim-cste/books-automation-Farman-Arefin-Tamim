# Third party imports
import allure
import pytest
import requests
from playwright.sync_api import Page
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Internal imports
from pages.home_page import HomePage
from utils.config import Config
from utils.helpers import build_absolute_url


@allure.feature("Link Validation")
@allure.story("TC-04: Broken Link Detection")
@pytest.mark.regression
@pytest.mark.links
class TestBrokenLinks:
    """ 
    Test suite for detecting broken hyperlinks on the homepage.
    """

    @allure.title("All homepage hyperlinks return HTTP 200")
    def test_no_broken_links(self, page: Page) -> None:
        """
        Send HTTP GET to every unique href and check for successful response.
        """
        home = HomePage(page).open()

        with allure.step("Collect all anchor hrefs from homepage"):
            raw_hrefs = home.get_all_hrefs()
            assert raw_hrefs, "No hrefs found on the homepage"

        with allure.step("Build absolute URLs"):
            urls = list({
                build_absolute_url(Config.BASE_DOMAIN, href)
                for href in raw_hrefs
                if not href.startswith("javascript:")
                and not href.startswith("mailto:")
                and not href.startswith("#")
            })
            allure.attach(
                "\n".join(sorted(urls)),
                name=f"URLs to check ({len(urls)})",
                attachment_type=allure.attachment_type.TEXT,
            )

        broken: list[str] = []
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (BooksTestBot/1.0)"})

        for url in urls:
            with allure.step(f"GET {url}"):
                try:
                    response = session.get(url, timeout=Config.REQUEST_TIMEOUT, allow_redirects=True, verify=False)
                    status = response.status_code
                    if status not in (200, 301, 302):
                        broken.append(f"{url} → HTTP {status}")
                except requests.RequestException as exc:
                    broken.append(f"{url} → ERROR: {exc}")

        if broken:
            allure.attach(
                "\n".join(broken),
                name="Broken Links",
                attachment_type=allure.attachment_type.TEXT,
            )

        assert not broken, (
            f"{len(broken)} broken link(s) found:\n" + "\n".join(broken)
        )