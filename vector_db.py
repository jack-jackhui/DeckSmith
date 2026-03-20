"""Vector database module for document storage and retrieval using FAISS."""

import logging
import os
import pickle
from typing import List, Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from constants import (
    DEFAULT_DATA_DIR,
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL_NAME,
    FAISS_INDEX_FILENAME,
    TEXTS_FILENAME,
    VECTOR_SEARCH_TOP_K,
)

logger = logging.getLogger(__name__)

model = SentenceTransformer(EMBEDDING_MODEL_NAME)
index: faiss.IndexFlatL2 = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
texts: List[str] = []

FAISS_INDEX_PATH: str = os.getenv(
    "FAISS_INDEX_PATH",
    os.path.join(DEFAULT_DATA_DIR, FAISS_INDEX_FILENAME)
)
TEXTS_PATH: str = os.getenv(
    "TEXTS_PATH",
    os.path.join(DEFAULT_DATA_DIR, TEXTS_FILENAME)
)


def ensure_data_dir() -> None:
    """Ensure the data directory exists."""
    data_dir = os.path.dirname(FAISS_INDEX_PATH)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        logger.info("Created data directory: %s", data_dir)


def load_index() -> bool:
    """Load FAISS index and texts from disk if they exist.

    Returns:
        True if index was loaded successfully, False otherwise.
    """
    global index, texts

    if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(TEXTS_PATH):
        logger.info("No existing index found. Starting with empty index.")
        return False

    try:
        index = faiss.read_index(FAISS_INDEX_PATH)

        with open(TEXTS_PATH, 'rb') as f:
            texts = pickle.load(f)

        logger.info("Loaded index with %d entries from disk.", len(texts))
        return True
    except Exception as e:
        logger.error("Failed to load index from disk: %s", e)
        index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
        texts = []
        return False


def save_index() -> bool:
    """Save FAISS index and texts to disk.

    Returns:
        True if index was saved successfully, False otherwise.
    """
    ensure_data_dir()

    try:
        faiss.write_index(index, FAISS_INDEX_PATH)

        with open(TEXTS_PATH, 'wb') as f:
            pickle.dump(texts, f)

        logger.info("Saved index with %d entries to disk.", len(texts))
        return True
    except Exception as e:
        logger.error("Failed to save index to disk: %s", e)
        return False


def add_to_vector_db(text: str, auto_save: bool = True) -> None:
    """Add text to the vector database.

    Args:
        text: The text to add to the database.
        auto_save: Whether to automatically save to disk after adding.
    """
    if not text or not text.strip():
        logger.warning("Attempted to add empty text to vector DB. Skipping.")
        return

    embeddings = model.encode([text])
    index.add(np.array(embeddings))
    texts.append(text)
    logger.info("Added text to vector DB. Total texts: %d", len(texts))

    if auto_save:
        save_index()


def search_vector_db(query: str, top_k: Optional[int] = None) -> List[str]:
    """Search the vector database for similar texts.

    Args:
        query: The search query.
        top_k: Number of results to return. Defaults to VECTOR_SEARCH_TOP_K.

    Returns:
        A list of matching text strings.
    """
    if top_k is None:
        top_k = VECTOR_SEARCH_TOP_K

    if len(texts) == 0:
        logger.debug("Vector DB is empty. Returning no results.")
        return []

    query_embedding = model.encode([query])
    D, I = index.search(np.array(query_embedding), k=min(top_k, len(texts)))

    logger.debug("Search distances: %s", D)
    logger.debug("Search indices: %s", I)

    if I.size == 0 or len(I[0]) == 0:
        logger.debug("No results found in vector DB.")
        return []

    valid_indices = [i for i in I[0] if 0 <= i < len(texts)]
    logger.debug("Valid indices: %s", valid_indices)

    if not valid_indices:
        logger.debug("No valid indices found.")
        return []

    return [texts[i] for i in valid_indices]


def clear_vector_db(auto_save: bool = True) -> None:
    """Clear all entries from the vector database.

    Args:
        auto_save: Whether to automatically save to disk after clearing.
    """
    global index, texts
    index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
    texts = []
    logger.info("Cleared vector DB.")

    if auto_save:
        save_index()


def get_index_size() -> int:
    """Get the number of entries in the vector database.

    Returns:
        The number of text entries stored.
    """
    return len(texts)


load_index()
