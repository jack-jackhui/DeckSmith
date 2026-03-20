"""Tests for vector database module."""

import os
import sys
import tempfile
from unittest.mock import patch

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestVectorDBOperations:
    """Tests for basic vector database operations."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {
                'FAISS_INDEX_PATH': os.path.join(tmpdir, 'test_index.bin'),
                'TEXTS_PATH': os.path.join(tmpdir, 'test_texts.pkl')
            }):
                import importlib
                import vector_db
                importlib.reload(vector_db)

                from vector_db import clear_vector_db
                clear_vector_db(auto_save=False)

                yield tmpdir

    def test_add_to_vector_db(self):
        """Test adding text to vector database."""
        from vector_db import add_to_vector_db, get_index_size

        initial_size = get_index_size()
        add_to_vector_db("Test document content", auto_save=False)
        assert get_index_size() == initial_size + 1

    def test_add_empty_text_skipped(self):
        """Test that empty text is not added."""
        from vector_db import add_to_vector_db, get_index_size

        initial_size = get_index_size()
        add_to_vector_db("", auto_save=False)
        add_to_vector_db("   ", auto_save=False)
        assert get_index_size() == initial_size

    def test_search_empty_db_returns_empty(self):
        """Test searching an empty database returns empty list."""
        from vector_db import clear_vector_db, search_vector_db

        clear_vector_db(auto_save=False)
        results = search_vector_db("test query")
        assert results == []

    def test_search_returns_relevant_text(self):
        """Test that search returns relevant documents."""
        from vector_db import add_to_vector_db, search_vector_db

        add_to_vector_db("Python programming language", auto_save=False)
        add_to_vector_db("JavaScript web development", auto_save=False)
        add_to_vector_db("Machine learning with Python", auto_save=False)

        results = search_vector_db("Python coding")
        assert len(results) > 0
        assert any("Python" in r for r in results)

    def test_search_respects_top_k(self):
        """Test that search respects top_k parameter."""
        from vector_db import add_to_vector_db, search_vector_db

        for i in range(10):
            add_to_vector_db(f"Document number {i}", auto_save=False)

        results = search_vector_db("document", top_k=3)
        assert len(results) <= 3

    def test_clear_vector_db(self):
        """Test clearing the vector database."""
        from vector_db import add_to_vector_db, clear_vector_db, get_index_size

        add_to_vector_db("Test content", auto_save=False)
        assert get_index_size() > 0

        clear_vector_db(auto_save=False)
        assert get_index_size() == 0


class TestVectorDBPersistence:
    """Tests for vector database persistence."""

    def test_save_and_load_index(self):
        """Test saving and loading the index."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = os.path.join(tmpdir, 'test_index.bin')
            texts_path = os.path.join(tmpdir, 'test_texts.pkl')

            with patch.dict(os.environ, {
                'FAISS_INDEX_PATH': index_path,
                'TEXTS_PATH': texts_path
            }):
                import importlib
                import vector_db
                importlib.reload(vector_db)

                from vector_db import add_to_vector_db, clear_vector_db, save_index

                clear_vector_db(auto_save=False)
                add_to_vector_db("Persistent test content", auto_save=False)
                save_index()

                assert os.path.exists(index_path)
                assert os.path.exists(texts_path)


class TestVectorDBConstants:
    """Tests for vector database constants."""

    def test_embedding_dimension(self):
        """Test embedding dimension constant."""
        from constants import EMBEDDING_DIMENSION
        assert EMBEDDING_DIMENSION == 384

    def test_search_top_k(self):
        """Test default search top_k."""
        from constants import VECTOR_SEARCH_TOP_K
        assert VECTOR_SEARCH_TOP_K == 5

    def test_embedding_model_name(self):
        """Test embedding model name."""
        from constants import EMBEDDING_MODEL_NAME
        assert EMBEDDING_MODEL_NAME == "all-MiniLM-L6-v2"


class TestToolsValidation:
    """Tests for email validation in tools module."""

    def test_validate_email_valid(self):
        """Test valid email addresses."""
        from tools import validate_email

        assert validate_email("test@example.com") is True
        assert validate_email("user.name@domain.org") is True
        assert validate_email("user+tag@example.co.uk") is True

    def test_validate_email_invalid(self):
        """Test invalid email addresses."""
        from tools import validate_email

        assert validate_email("invalid") is False
        assert validate_email("@example.com") is False
        assert validate_email("test@") is False
        assert validate_email("") is False
        assert validate_email(None) is False

    def test_sanitize_subject_removes_newlines(self):
        """Test that subject sanitization removes newlines."""
        from tools import sanitize_subject

        result = sanitize_subject("Test\nSubject\rLine")
        assert "\n" not in result
        assert "\r" not in result

    def test_sanitize_subject_truncates(self):
        """Test that subject is truncated to max length."""
        from tools import sanitize_subject

        long_subject = "A" * 500
        result = sanitize_subject(long_subject)
        assert len(result) <= 255


class TestValidationModule:
    """Tests for validation module."""

    def test_sanitize_input_removes_control_chars(self):
        """Test that control characters are removed."""
        from validation import sanitize_input

        result = sanitize_input("Test\x00\x1fContent")
        assert "\x00" not in result
        assert "\x1f" not in result

    def test_sanitize_input_handles_empty(self):
        """Test handling of empty input."""
        from validation import sanitize_input

        assert sanitize_input("") == ""
        assert sanitize_input(None) == ""

    def test_sanitize_input_strips_whitespace(self):
        """Test that whitespace is stripped."""
        from validation import sanitize_input

        result = sanitize_input("  test  ")
        assert result == "test"
