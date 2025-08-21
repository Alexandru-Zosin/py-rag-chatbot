from typing import Iterator
from pathlib import Path
import csv
from models.book import Book


class BooksDataIterator:
    def __init__(self, path: Path):
        self._path = path

    def __iter__(self, ) -> Iterator[Book]:
        # iterate through all books in the dataframe and bring one book obj. at a time
        with self._path.open("r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)

            for row in reader:
                if not row:
                    continue

                title = (row.get("Title") or "").strip()
                authors = [a for a in (row.get("Authors") or " ").split(
                    ",") if a.strip()] or []
                summary = (row.get("Description") or "").strip()
                categories = [c for c in (row.get("Category") or " ").split(
                    ",") if c.strip()] or []

                if not title or not summary:
                    continue

                yield Book(title, authors, summary, categories)
