import os
import pytest
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from utils.config import Config


@pytest.fixture(scope="session")
def browser_instance():
    """Launch a single Chromium browser for the entire test session."""
    with sync_playwright() as playwright:
        browser: Browser = playwright.chromium.launch(
            headless=Config.HEADLESS,
            slow_mo=Config.SLOW_MO,
        )
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def browser_context(browser_instance: Browser, request):
    """
    Create a fresh browser context for each test with video and tracing."""
    os.makedirs(Config.VIDEO_DIR, exist_ok=True)
    os.makedirs(Config.TRACE_DIR, exist_ok=True)

    context: BrowserContext = browser_instance.new_context(
        viewport={"width": 1280, "height": 720},
        record_video_dir=Config.VIDEO_DIR if Config.RECORD_VIDEO else None,
        record_video_size={"width": 1280, "height": 720},
    )

    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield context

    test_name = request.node.name.replace(" ", "_").replace("/", "_")
    trace_path = os.path.join(Config.TRACE_DIR, f"{test_name}.zip")
    context.tracing.stop(path=trace_path)
    context.close()


@pytest.fixture(scope="function")
def page(browser_context: BrowserContext, request):
    """Open a new page and capture screenshot on test failure."""
    os.makedirs(Config.SCREENSHOT_DIR, exist_ok=True)

    page: Page = browser_context.new_page()
    page.set_default_timeout(Config.DEFAULT_TIMEOUT)

    yield page

    page.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Capture screenshot and attach to Allure report on test failure.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

    if rep.when == "call" and rep.failed:
        page_fixture = item.funcargs.get("page")
        if page_fixture:
            os.makedirs(Config.SCREENSHOT_DIR, exist_ok=True)
            test_name = item.name.replace(" ", "_").replace("/", "_")
            screenshot_path = os.path.join(
                Config.SCREENSHOT_DIR, f"{test_name}_FAILED.png"
            )
            try:
                page_fixture.screenshot(path=screenshot_path, full_page=True)
                try:
                    import allure
                    with open(screenshot_path, "rb") as img:
                        allure.attach(
                            img.read(),
                            name=f"Failure Screenshot — {test_name}",
                            attachment_type=allure.attachment_type.PNG,
                        )
                except Exception:
                    pass
            except Exception:
                pass