#!/usr/bin/env python3
"""
Genesis Enhanced Assistants - Test Runner

Run this script to test all enhanced assistants and generate reports.

Usage:
    python run_assistant_tests.py [--open]

Options:
    --open    Open the HTML report in browser after completion
"""

import sys
import os
from pathlib import Path

# Add genesis to path
genesis_path = Path(__file__).parent / "genesis"
sys.path.insert(0, str(genesis_path))

from tests.test_assistants import run_tests


def main():
    report = run_tests()

    # Check if we should open the report
    if "--open" in sys.argv:
        report_path = Path(__file__).parent / "test_results" / "assistant_test_report.html"
        if report_path.exists():
            import webbrowser
            webbrowser.open(f"file://{report_path.absolute()}")

    # Return non-zero if there were failures
    if report.total_failed > 0 or report.total_errors > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
