"""
Small, pure helper functions for normalizing text and price strings before
comparison. Centralizing this avoids duplicated `.strip()` / `.replace()`
chains scattered across multiple test files (DRY).
"""
from __future__ import annotations

import re


def normalize_text(text: str) -> str:
    """Collapse whitespace and strip leading/trailing spaces from a string."""
    if text is None:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def normalize_price(price_text: str) -> str:
    """
    Normalize a price string for reliable comparison.

    Strips whitespace and any non-numeric/non-currency-symbol noise while
    preserving the currency symbol and decimal value, e.g. "  £51.77 " -> "£51.77".
    """
    cleaned = normalize_text(price_text)
    match = re.search(r"[£$€]\s?\d+(?:\.\d{1,2})?", cleaned)
    return match.group(0).replace(" ", "") if match else cleaned


def truncated_title_matches(short_title: str, full_title: str) -> bool:
    """
    Compare a possibly truncated listing-page title (ending in '...') against
    the full title shown on the details page.
    """
    short = normalize_text(short_title)
    full = normalize_text(full_title)

    if short == full:
        return True

    if short.endswith("..."):
        prefix = short[:-3].strip()
        return full.startswith(prefix)

    return False
