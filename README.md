# Enterprise UI Automation Framework — Books to Scrape

A production-ready UI automation framework built with Playwright and Pytest,
targeting [books.toscrape.com](https://books.toscrape.com). Implements Page
Object Model, OOP, SOLID, and DRY principles with HTML and Allure reporting,
plus full GitHub Actions CI/CD.

Covers homepage integrity, random book navigation, cross-page data
consistency, broken link detection, and product image validation across
paginated results.

---

## Features

- Page Object Model design pattern
- Five automated test cases covering all acceptance criteria
- Random book selection for realistic test coverage
- Screenshot, video, and trace capture on failure
- Allure HTML report with steps and attachments + self-contained pytest-html report
- GitHub Actions CI/CD, triggers on push and pull request
- No hardcoded waits — all synchronization via Playwright's built-in strategies

## Tech Stack

| Layer              | Technology          |
|--------------------|----------------------|
| Language           | Python 3.11+        |
| Browser Automation | Playwright 1.44     |
| Test Runner        | Pytest 8.2          |
| HTML Report        | pytest-html 4.1     |
| Allure Report      | allure-pytest 2.13  |
| HTTP Validation    | requests 2.32       |
| CI/CD              | GitHub Actions      |

---

## Setup

**Prerequisites:** Python 3.10+, Git, pip

```bash
git clone https://github.com/tamim-cste/books-automation-Farman-Arefin-Tamim.git
cd books-automation-Farman-Arefin-Tamim

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python -m playwright install chromium
```

## Running Tests

```bash
pytest -v                              # full suite

pytest tests/test_01_homepage.py -v    # single file

pytest -m smoke -v                     # by marker
pytest -m regression -v
pytest -m navigation -v
pytest -m images -v

HEADLESS=false pytest -v               # with browser visible
```

Configuration is handled through environment variables with sensible
defaults — create a `.env` file in the project root to override any of them.

## Test Case Coverage

| ID    | Test Case              | Description                                        | Markers                |
|-------|-------------------------|-----------------------------------------------------|--------------------------|
| TC-01 | Homepage Validation     | URL, title, headings, and books section            | smoke, ui              |
| TC-02 | Random Book Navigation  | Open 5 random books, verify detail page title      | regression, navigation |
| TC-03 | Data Consistency        | Compare title/price on homepage vs. detail page    | regression, data       |
| TC-04 | Broken Link Validation  | Check all hrefs return HTTP 200                    | regression, links      |
| TC-05 | Image Validation        | Verify src, alt, class attributes across 5 pages   | regression, images     |

---

## Reports

**HTML** — generated automatically at `reports/report.html` on every run.
```bash
xdg-open reports/report.html
```

**Allure** — requires the Allure CLI (`sudo apt-get install -y allure` on
Ubuntu/Debian, `brew install allure` on macOS).
```bash
pytest --alluredir=allure-results
allure serve allure-results            # opens report directly

# or generate a static version:
allure generate allure-results --clean -o allure-report
python3 -m http.server 8080 --directory allure-report
```

## GitHub Actions CI/CD

Workflow: `.github/workflows/playwright.yml`
**Triggers:** push/PR to `main` or `dev`, or manual `workflow_dispatch`.

**Pipeline:** checkout → install dependencies → install Playwright/Chromium →
run pytest suite → generate Allure report → upload artifacts
(`html-report`, `allure-results`, `allure-report`, `screenshots`, `videos`,
`traces`; 30-day retention).

To view artifacts: **Actions tab → latest run → Artifacts** section. For the
Allure report artifact, run `python3 -m http.server 8080` inside the
unzipped folder and open `http://localhost:8080`.

---

## Design Decisions

| Decision                     | Reason                                                   |
|-------------------------------|------------------------------------------------------------|
| Page Object Model             | Separates selectors from test logic, reduces duplication |
| `BasePage` class              | Single place for all browser interactions                |
| `BookCard` dataclass           | Clean data transfer between page objects and tests        |
| Session-scoped browser        | One browser launch per run, faster execution              |
| Function-scoped context       | Each test gets a fresh, isolated context                  |
| `normalize_price` utility     | Handles encoding differences when comparing prices        |
| `verify=False` for link checks| books.toscrape.com has SSL issues on some machines         |
| `continue-on-error` in CI     | Artifacts upload even when tests fail                      |
| No `time.sleep()` anywhere    | All waits use Playwright `networkidle`/`wait_for_selector`|

## Known Limitations

- Broken link test may run slowly on low-bandwidth connections
- Video recording slightly increases test execution time
- Allure CLI must be installed separately to view the report locally
- Tests run sequentially; parallel execution is not configured
- SSL verification is disabled for HTTP link checks due to certificate issues on the target site

---

Built following industry automation best practices: OOP, SOLID, DRY, and Page Object Model.