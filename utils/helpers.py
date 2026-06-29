import random
from typing import List, TypeVar

T = TypeVar("T")


def pick_random_items(items: List[T], count: int) -> List[T]:
    """Pick random items from a list without repetition."""
    return random.sample(items, min(count, len(items)))


def normalize_price(price_text: str) -> str:
    """Strip currency symbol and whitespace from price string."""
    return price_text.replace("£", "").replace("Â", "").strip()


def build_absolute_url(base: str, href: str) -> str:
    """Convert relative href to absolute URL."""
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return base + href
    return base + "/" + href