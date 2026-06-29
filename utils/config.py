"""
Centralised configuration for the automation framework.
All environment-specific values live here  no hardcoded values in tests.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Site under test
    BASE_URL: str = os.getenv("BASE_URL", "https://books.toscrape.com/index.html")
    BASE_DOMAIN: str = "https://books.toscrape.com"

    # Browser settings
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
    SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))

    # Timeouts in milliseconds
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
    NAVIGATION_TIMEOUT: int = int(os.getenv("NAVIGATION_TIMEOUT", "60000"))

    # Test behaviour
    RANDOM_BOOK_COUNT: int = int(os.getenv("RANDOM_BOOK_COUNT", "5"))
    MAX_PAGES_IMAGE_CHECK: int = int(os.getenv("MAX_PAGES_IMAGE_CHECK", "5"))

    # Artifact output paths
    SCREENSHOT_DIR: str = os.getenv("SCREENSHOT_DIR", "screenshots")
    VIDEO_DIR: str = os.getenv("VIDEO_DIR", "videos")
    TRACE_DIR: str = os.getenv("TRACE_DIR", "traces")
    REPORT_DIR: str = os.getenv("REPORT_DIR", "reports")
    RECORD_VIDEO: bool = os.getenv("RECORD_VIDEO", "true").lower() == "true"

    # HTTP link check timeout in seconds
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "15"))