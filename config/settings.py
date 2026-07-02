"""
Central configuration module for the automation framework.

All environment-specific and run-specific settings are sourced from here so
that no test or page object ever hardcodes a URL, timeout, or path.
"""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Immutable settings object for the test run."""

    # --- Application under test ---
    BASE_URL: str = os.getenv("BASE_URL", "https://books.toscrape.com")
    HOME_PATH: str = "/index.html"

    # --- Browser / execution settings ---
    BROWSER: str = os.getenv("BROWSER", "chromium")
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
    SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))

    # --- Timeouts (milliseconds) ---
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "10000"))
    NAVIGATION_TIMEOUT: int = int(os.getenv("NAVIGATION_TIMEOUT", "15000"))

    # --- Test data sizing ---
    RANDOM_BOOK_SAMPLE_SIZE: int = int(os.getenv("RANDOM_BOOK_SAMPLE_SIZE", "5"))
    MAX_PAGINATION_PAGES: int = int(os.getenv("MAX_PAGINATION_PAGES", "5"))

    # --- Link-checking ---
    LINK_CHECK_TIMEOUT: int = int(os.getenv("LINK_CHECK_TIMEOUT", "10"))
    LINK_CHECK_WORKERS: int = int(os.getenv("LINK_CHECK_WORKERS", "10"))

    # --- Artifact directories ---
    SCREENSHOTS_DIR: str = "screenshots"
    VIDEOS_DIR: str = "videos"
    TRACES_DIR: str = "traces"

    @property
    def home_url(self) -> str:
        return f"{self.BASE_URL}{self.HOME_PATH}"


settings = Settings()
