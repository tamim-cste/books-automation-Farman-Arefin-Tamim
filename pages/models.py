"""
Lightweight data models used to pass book information between page objects
and tests without relying on loosely-typed dictionaries.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class BookSummary:
    """Represents a book entry as seen on a listing page (homepage/catalogue)."""

    title: str
    price: str
    detail_url: str
    availability: str = ""

    def __str__(self) -> str:
        return f"BookSummary(title={self.title!r}, price={self.price!r})"


@dataclass(frozen=True)
class BookDetail:
    """Represents a book's information as seen on its details page."""

    title: str
    price: str
    availability: str
    upc: str = ""
    product_type: str = ""

    def __str__(self) -> str:
        return f"BookDetail(title={self.title!r}, price={self.price!r})"
