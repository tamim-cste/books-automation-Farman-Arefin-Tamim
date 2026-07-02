"""
Root pytest configuration: fixtures shared across the entire test suite.

Responsibilities:
 - Configure Playwright browser context (viewport, video, tracing).
 - Provide ready-to-use page object fixtures (homepage, book details page).
 - Automatically capture a screenshot, video, and trace on test failure.
 - Attach failure screenshots to the Allure report automatically.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

import allure
import pytest
from playwright.sync_api import Page

from config.settings import settings
from pages.home_page import HomePage
from pages.book_details_page import BookDetailsPage

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Directory setup
# ----------------------------------------------------------------------
def _ensure_dirs() -> None:
    for directory in (
        settings.SCREENSHOTS_DIR,
        settings.VIDEOS_DIR,
        settings.TRACES_DIR,
        "test-results",
        "allure-results",
    ):
        Path(directory).mkdir(parents=True, exist_ok=True)


_ensure_dirs()


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    """
    Re-create required output directories right before the session starts.

    Module-level directory creation (above) only runs once, at import time.
    If a directory is removed between reruns (pytest-rerunfailures) or by an
    external cleanup step, pytest-html's writer will fail with
    FileNotFoundError when it tries to write test-results/report.html.
    This hook guarantees the directories exist no matter how/when pytest
    is invoked, relative to whatever the current working directory is.
    """
    _ensure_dirs()


# ----------------------------------------------------------------------
# Playwright browser/context configuration
# ----------------------------------------------------------------------
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Extend default Playwright launch args with project-level settings."""
    return {
        **browser_type_launch_args,
        "headless": settings.HEADLESS,
        "slow_mo": settings.SLOW_MO,
    }


@pytest.fixture(scope="function")
def browser_context_args(browser_context_args, request):
    """Extend default browser context args with video recording and viewport."""
    return {
        **browser_context_args,
        "viewport": {"width": 1440, "height": 900},
        "record_video_dir": settings.VIDEOS_DIR,
        "accept_downloads": True,
    }


@pytest.fixture(scope="function", autouse=True)
def _tracing(context, request):
    """Start/stop Playwright tracing for every test, saving a trace on failure."""
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield
    test_failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
    trace_name = f"{request.node.name}_trace.zip"
    trace_path = os.path.join(settings.TRACES_DIR, trace_name)
    if test_failed:
        context.tracing.stop(path=trace_path)
    else:
        context.tracing.stop()


# ----------------------------------------------------------------------
# Test result hook — needed so fixtures can know pass/fail status
# ----------------------------------------------------------------------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(scope="function", autouse=True)
def _capture_on_failure(page: Page, request):
    """Capture a screenshot and attach it to Allure whenever a test fails."""
    yield
    failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed
    if failed:
        screenshot_name = f"{request.node.name}.png"
        screenshot_path = os.path.join(settings.SCREENSHOTS_DIR, screenshot_name)
        try:
            page.screenshot(path=screenshot_path, full_page=True)
            allure.attach.file(
                screenshot_path,
                name="failure_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
            logger.error("Test failed. Screenshot saved to %s", screenshot_path)
        except Exception as exc:
            logger.warning("Could not capture failure screenshot: %s", exc)


# ----------------------------------------------------------------------
# Page object fixtures
# ----------------------------------------------------------------------
@pytest.fixture
def home_page(page: Page) -> HomePage:
    """Provides a HomePage object, already navigated to the homepage."""
    home = HomePage(page)
    home.load()
    return home


@pytest.fixture
def book_details_page(page: Page) -> BookDetailsPage:
    """Provides an unnavigated BookDetailsPage; tests navigate explicitly."""
    return BookDetailsPage(page)


# ----------------------------------------------------------------------
# Misc
# ----------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _set_default_timeout(page: Page):
    """Apply the project's default action/navigation timeouts to every page."""
    page.set_default_timeout(settings.DEFAULT_TIMEOUT)
    page.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT)
    yield
