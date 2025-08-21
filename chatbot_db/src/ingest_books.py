from __future__ import annotations

import os
import sys
import hashlib
import logging
from pathlib import Path
from typing import Iterable, List, Dict, Any

from dotenv import load_dotenv

# Ensure absolute imports work when running as a script
THIS_DIR = Path(__file__).resolve().parent
PROJECT_SRC = THIS_DIR
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from data.iterators.book_iterator import BooksDataIterator  # noqa: E402
from models.book import Book  # noqa: E402

import chromadb  # noqa: E402
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction  # noqa: E402


# Helpers for normalization and IDs
def _flatten(seq: Iterable[str]) -> str:
    return ", ".join(s.strip() for s in seq if s and s.strip())


def _canonical_id(title: str, authors: Iterable[str], categories: Iterable[str]) -> str:
    return f"{title.strip().lower()}|{_flatten(authors).lower()}|{_flatten(categories).lower()}"


def _hash_id(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def main() -> None:
    load_dotenv()

    # Config
    chroma_host = os.getenv("CHROMA_HOST", "127.0.0.1")
    chroma_port = int(os.getenv("CHROMA_PORT", "8000"))
    chroma_collection = os.getenv("CHROMA_COLLECTION", "books")
    csv_path = Path(os.getenv("CSV_PATH", "/app/src/data/BooksDatasetClean.csv"))
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    force_reingest = os.getenv("FORCE_REINGEST", "0") == "1"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found at: {csv_path}")

    logging.info("Connecting to Chroma at %s:%s ...", chroma_host, chroma_port)
    client = chromadb.HttpClient(host=chroma_host, port=chroma_port)

    # Optional: drop collection if forced
    if force_reingest:
        try:
            client.delete_collection(name=chroma_collection)
            logging.info("Deleted collection '%s' due to FORCE_REINGEST=1.", chroma_collection)
        except Exception as e:
            logging.warning("Delete collection failed or did not exist: %s", e)

    # Create or connect to the collection with OpenAI embedding fn
    embedding_fn = OpenAIEmbeddingFunction(
        api_key=openai_api_key,
        model_name=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
    )

    collection = client.get_or_create_collection(
        name=chroma_collection,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )

    count_before = collection.count()
    logging.info("Collection '%s' current count: %d", chroma_collection, count_before)

    # Ingest only if empty
    if count_before > 0 and not force_reingest:
        logging.info("Collection is not empty. Skipping ingestion.")
        return

    logging.info("Starting ingestion from CSV: %s", csv_path)
    iterator = BooksDataIterator(csv_path)

    batch_ids: List[str] = []
    batch_docs: List[str] = []
    batch_metas: List[Dict[str, Any]] = []

    batch_size = int(os.getenv("INGEST_BATCH_SIZE", "128"))
    added = 0
    skipped_dups = 0
    seen_ids: set[str] = set()

    def _flush_batch() -> None:
        nonlocal batch_ids, batch_docs, batch_metas, added
        if not batch_ids:
            return
        collection.add(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_metas,
        )
        added += len(batch_ids)
        logging.info("Added %d docs (total: %d)", len(batch_ids), added)
        batch_ids.clear()
        batch_docs.clear()
        batch_metas.clear()

    for book in iterator:
        book_id = _hash_id(_canonical_id(book.title, book.authors, book.categories))
        _id, doc, meta = book.to_chroma(book_id)
        if _id in seen_ids:
            skipped_dups += 1
            continue
        seen_ids.add(_id)
        batch_ids.append(_id)
        batch_docs.append(doc)
        batch_metas.append(meta)

        if len(batch_ids) >= batch_size:
            _flush_batch()

    _flush_batch()

    if skipped_dups:
        logging.info("Skipped %d duplicate items based on canonical ID.", skipped_dups)

    logging.info("Ingestion finished. New collection count: %d", collection.count())


if __name__ == "__main__":
    main()
