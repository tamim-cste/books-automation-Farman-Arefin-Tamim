from playwright.sync_api import Page, Locator
from utils.config import Config


class BasePage:
    """Base class for all page objects. Handles common browser interactions."""

    def __init__(self, page: Page) -> None:
        self._page = page
        self._page.set_default_timeout(Config.DEFAULT_TIMEOUT)

    # Navigation
    def navigate(self, url: str) -> None:
        self._page.goto(url, wait_until="networkidle", timeout=Config.NAVIGATION_TIMEOUT)

    def go_back(self) -> None:
        self._page.go_back(wait_until="networkidle", timeout=Config.NAVIGATION_TIMEOUT)

    # Page info
    @property
    def current_url(self) -> str:
        return self._page.url

    @property
    def title(self) -> str:
        return self._page.title()

    # Element interactions
    def find(self, selector: str) -> Locator:
        return self._page.locator(selector)

    def find_all(self, selector: str) -> list:
        return self._page.locator(selector).all()

    def is_visible(self, selector: str) -> bool:
        return self._page.locator(selector).is_visible()

    def get_text(self, selector: str) -> str:
        return self._page.locator(selector).inner_text().strip()

    def click(self, selector: str) -> None:
        self._page.locator(selector).click()
        self._page.wait_for_load_state("networkidle")

    def wait_for_selector(self, selector: str) -> None:
        self._page.wait_for_selector(selector, timeout=Config.DEFAULT_TIMEOUT)

    def take_screenshot(self, path: str) -> None:
        self._page.screenshot(path=path, full_page=True)