#!/usr/bin/env bash
# Generates an Allure HTML report from allure-results/ and serves it locally.
#
# Prerequisite: Allure commandline must be installed.
#   - macOS:   brew install allure
#   - npm:     npm install -g allure-commandline
#   - manual:  https://allurereport.org/docs/install/
#
# Usage:
#   ./scripts/generate_allure_report.sh

set -e

RESULTS_DIR="allure-results"
REPORT_DIR="allure-report"

if ! command -v allure &> /dev/null; then
    echo "Error: 'allure' command not found."
    echo "Install it with: npm install -g allure-commandline"
    exit 1
fi

if [ ! -d "$RESULTS_DIR" ] || [ -z "$(ls -A "$RESULTS_DIR" 2>/dev/null)" ]; then
    echo "Error: '$RESULTS_DIR' is empty. Run the tests first: pytest"
    exit 1
fi

echo "Generating Allure report from $RESULTS_DIR ..."
allure generate "$RESULTS_DIR" --clean -o "$REPORT_DIR"

echo "Opening Allure report in browser..."
allure open "$REPORT_DIR"
