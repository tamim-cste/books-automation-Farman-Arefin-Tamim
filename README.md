# Enterprise UI Automation Framework — Books to Scrape

A production-ready UI automation framework built with **Playwright + Pytest**
that validates the functionality, data consistency, UI elements, and
navigation behavior of [books.toscrape.com](https://books.toscrape.com/index.html).

The framework follows the **Page Object Model (POM)**, OOP/SOLID/DRY
principles, and integrates **HTML + Allure reporting** with a **GitHub
Actions CI/CD pipeline**.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation Guide](#installation-guide)
- [Environment Setup](#environment-setup)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Test Case Coverage](#test-case-coverage)
- [Report Generation Guide](#report-generation-guide)
	- [HTML Report Guide](#html-report-guide)
	- [Allure Report Guide](#allure-report-guide)
- [GitHub Actions Setup](#github-actions-setup)
- [Design Decisions](#design-decisions)
- [Known Limitations](#known-limitations)

---

## Project Overview

This project is an end-to-end UI test automation suite for the **Books to
Scrape** sandbox site. It exercises five core scenarios — homepage
validation, random book navigation, cross-page data consistency, broken-link
detection, and product image/pagination validation — using a maintainable,
reusable automation architecture that is safe to extend with new pages and
tests.

The suite runs identically on a local machine and inside GitHub Actions,
producing both an **HTML report** (via `pytest-html`) and an **Allure
report** on every run, with screenshots, videos, and traces captured
automatically on failure.



## Tech Stack

| Category            | Technology                           |
|----------------------|---------------------------------------|
| Language             | Python 3.11+                         |
| Browser automation   | Playwright (Python, sync API)        |
| Test framework       | Pytest + `pytest-playwright`         |
| HTML reporting       | `pytest-html`                        |
| Allure reporting     | `allure-pytest` + Allure commandline |
| HTTP requests        | `requests` (broken link checks)      |
| CI/CD                | GitHub Actions                       |
| Flaky-test handling  | `pytest-rerunfailures`               |

## Installation Guide

### Prerequisites

- Python 3.11 or later
- `pip`
- Node.js (only required locally to install the Allure commandline tool)
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/tamim-cste/books-automation-Farman-Arefin-Tamim.git
cd books-automation-Farman-Arefin-Tamim

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # on windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers (and OS-level dependencies)
playwright install chromium
```

### Installing Allure (for local report viewing)

```bash
# Option A: via npm
npm install -g allure-commandline

# Option B: via Homebrew (macOS)
brew install allure

# Option C: manual install
# https://allurereport.org/docs/install/
```

## Environment Setup

All configuration is centralized in [`config/settings.py`](config/settings.py)
and can be overridden via environment variables — no code changes are needed
to point the suite at a different environment.

| Variable                  | Default                       | Description                                  |
|----------------------------|--------------------------------|------------------------------------------------|
| `BASE_URL`                 | `https://books.toscrape.com`  | Base URL of the application under test        |
| `BROWSER`                  | `chromium`                    | Browser engine to use                          |
| `HEADLESS`                  | `true`                        | Run browser in headless mode                   |
| `SLOW_MO`                  | `0`                            | Slow down actions by N ms (debugging)          |
| `DEFAULT_TIMEOUT`          | `10000`                        | Default Playwright action timeout (ms)         |
| `NAVIGATION_TIMEOUT`       | `15000`                        | Navigation timeout (ms)                        |
| `RANDOM_BOOK_SAMPLE_SIZE`  | `5`                             | Number of random books sampled per test        |
| `MAX_PAGINATION_PAGES`     | `5`                             | Max listing pages visited during image checks  |
| `LINK_CHECK_TIMEOUT`       | `10`                            | Per-request timeout for link checks (seconds)  |
| `LINK_CHECK_WORKERS`       | `10`                            | Thread pool size for concurrent link checks    |

Export variables directly in your shell as needed, for example:

```bash
export HEADLESS=false
export SLOW_MO=250
```

## Running Tests

```bash
# Run the entire suite (headless, chromium)
pytest

# Run with a visible browser
HEADLESS=false pytest

# Run a specific test file
pytest tests/test_01_homepage_validation.py

# Run by marker
pytest -m smoke
pytest -m regression
pytest -m "navigation or data_consistency"

# Run in parallel (requires pytest-xdist, already included)
pytest -n auto

# Run with a specific browser engine
pytest --browser firefox
```

Test execution automatically produces:
- `test-results/report.html` — standalone HTML report
- `allure-results/` — raw Allure result files
- `screenshots/`, `videos/`, `traces/` — captured on failure

## Project Structure

```
books-automation/
├── .github/
│   └── workflows/
│       └── playwright.yml          # CI/CD pipeline definition
├── config/
│   └── settings.py                 # Centralized, env-driven configuration
├── pages/                          # Page Object Model layer
│   ├── base_page.py                # Shared navigation/wait helpers
│   ├── home_page.py                # Homepage / listing page object
│   ├── book_details_page.py        # Book details page object
│   └── models.py                   # BookSummary / BookDetail data models
├── tests/                          # Test suite (one file per test case)
│   ├── test_01_homepage_validation.py
│   ├── test_02_random_book_navigation.py
│   ├── test_03_book_data_consistency.py
│   ├── test_04_broken_links.py
│   └── test_05_product_images.py
├── utils/                          # Reusable, non-Playwright utilities
│   ├── link_checker.py             # Concurrent HTTP link validation
│   └── text_helpers.py             # Text/price normalization helpers
├── scripts/
│   └── generate_allure_report.sh   # Local Allure report helper script
├── conftest.py                     # Fixtures: browser config, POM, artifacts
├── pytest.ini                      # Pytest configuration & markers
├── requirements.txt                # Python dependencies
├── .gitignore
└── README.md
```


## Report Generation Guide

### HTML Report Guide

Generated automatically on every `pytest` run (configured in `pytest.ini`):

```bash
pytest
# Report written to: test-results/report.html
```

Open it directly in a browser:

```bash
# macOS
open test-results/report.html

# Linux
xdg-open test-results/report.html

# Windows
start test-results/report.html
```

The report is self-contained (`--self-contained-html`), so it can be shared
as a single file without broken asset links.

### Allure Report Guide

Allure results are written to `allure-results/` on every run. Generate and
view the interactive report with:

```bash
# Using the helper script
./scripts/generate_allure_report.sh

# Or manually
allure generate allure-results --clean -o allure-report
allure open allure-report
```

The Allure report includes step-by-step breakdowns (via `allure.step`),
severity levels, feature/story grouping, and automatically attached failure
screenshots.

## GitHub Actions Setup

The workflow is defined in [`.github/workflows/playwright.yml`](.github/workflows/playwright.yml)
and triggers automatically on:
- `push` to `main`/`master`
- `pull_request` targeting `main`/`master`
- manual `workflow_dispatch`

### Pipeline steps

1. Checkout the repository
2. Set up Python 3.11 with pip caching
3. Install Python dependencies from `requirements.txt`
4. Install Playwright's Chromium browser (with OS dependencies)
5. Run the full Pytest suite
6. Generate the Allure HTML report from raw results
7. Upload artifacts: HTML report, raw Allure results, generated Allure
	 report, screenshots, videos, and traces

### Viewing CI results

After a workflow run completes, go to the **Actions** tab → select the run →
scroll to **Artifacts** to download:
- `html-report`
- `allure-results`
- `allure-report`
- `screenshots` / `videos` / `traces` (only present if a test failed)

> **Tip:** GitHub Pages can be configured separately to publish the Allure
> report automatically; this is not enabled by default to keep the pipeline
> dependency-free for first-time setup.

