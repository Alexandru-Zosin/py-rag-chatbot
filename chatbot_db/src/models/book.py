from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence, Any


@dataclass
class Book:
    title: str
    authors: Sequence[str]
    summary: str
    categories: Sequence[str]

    def to_chroma(self, book_id: str) -> tuple[str, str, dict[str, Any]]:
        doc = (
            f"Title: {self.title}\n"
            f"Authors: {', '.join(self.authors)}\n"
            f"Categories: {', '.join(self.categories)}\n"
            f"Summary: {self.summary}"
        )
        meta: dict[str, Any] = {
            "title": self.title,
            "authors": ", ".join(self.authors),       # flatten
            "categories": ", ".join(self.categories)  # flatten
        }
        return (book_id, doc, meta)
