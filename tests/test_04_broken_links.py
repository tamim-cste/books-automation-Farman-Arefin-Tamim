"""
Test Case 4: Broken Link Validation

Collects every hyperlink on the homepage, deduplicates them, and verifies
that each one returns a successful (HTTP 200) response.
"""
import allure
import pytest

from pages.home_page import HomePage
from utils.link_checker import LinkChecker


@allure.feature("Link Integrity")
@allure.story("Broken Link Validation")
class TestBrokenLinks:
    """Validates that all hyperlinks on the homepage are reachable and return HTTP 200."""

    @pytest.mark.regression
    @pytest.mark.links
    @allure.title("All homepage hyperlinks return HTTP 200")
    @allure.severity(allure.severity_level.NORMAL)
    def test_no_broken_links_on_homepage(self, home_page: HomePage):
        with allure.step("Collect all anchor href values from the homepage"):
            hrefs = home_page.get_all_hrefs()
            unique_hrefs = sorted(set(hrefs))
            allure.attach(
                "\n".join(unique_hrefs),
                name="Unique URLs Checked",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step(f"Send requests to all {len(unique_hrefs)} unique URLs"):
            checker = LinkChecker()
            results = checker.check_all(unique_hrefs)

        with allure.step("Verify every URL returned HTTP 200"):
            broken = checker.get_broken_links(results)
            if broken:
                report_lines = [
                    f"{r.url} -> status={r.status_code} error={r.error}"
                    for r in broken
                ]
                allure.attach(
                    "\n".join(report_lines),
                    name="Broken Links",
                    attachment_type=allure.attachment_type.TEXT,
                )
            assert not broken, (
                f"Found {len(broken)} broken link(s):\n"
                + "\n".join(f"{r.url} -> {r.status_code}" for r in broken)
            )
