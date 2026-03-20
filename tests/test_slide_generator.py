"""Tests for slide deck generation module."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import (
    EXAMPLES_COUNT,
    MAX_SLIDES,
    RECOMMENDATIONS_KEY_POINTS,
    SLIDES_STRUCTURE,
)


class TestConstants:
    """Tests for slide generation constants."""

    def test_slides_structure_count(self):
        """Test that slides structure has expected number of slides."""
        assert len(SLIDES_STRUCTURE) == 12

    def test_slides_structure_has_titles(self):
        """Test that all slides have titles."""
        for slide in SLIDES_STRUCTURE:
            assert "title" in slide
            assert isinstance(slide["title"], str)
            assert len(slide["title"]) > 0

    def test_max_slides_matches_structure(self):
        """Test that MAX_SLIDES matches structure length."""
        assert MAX_SLIDES == len(SLIDES_STRUCTURE)

    def test_recommendations_key_points(self):
        """Test recommendations key points count."""
        assert RECOMMENDATIONS_KEY_POINTS == 3

    def test_examples_count(self):
        """Test examples count."""
        assert EXAMPLES_COUNT == 2


class TestSlideStructure:
    """Tests for slide structure content."""

    def test_front_page_is_first(self):
        """Test that front page is the first slide."""
        assert SLIDES_STRUCTURE[0]["title"] == "Front Page"

    def test_recommendations_at_correct_position(self):
        """Test that recommendations slide is at index 5."""
        assert SLIDES_STRUCTURE[5]["title"] == "Recommendations"

    def test_examples_at_correct_position(self):
        """Test that additional examples slide is at index 7."""
        assert SLIDES_STRUCTURE[7]["title"] == "Additional Examples"


class TestSlideContentGeneration:
    """Tests for content generation functions."""

    @patch('slide_deck_gen_v2.llm')
    def test_invoke_llm_returns_string(self, mock_llm):
        """Test that invoke_llm returns a string."""
        mock_response = MagicMock()
        mock_response.content = "Test content"
        mock_llm.invoke.return_value = mock_response

        from slide_deck_gen_v2 import invoke_llm

        result = invoke_llm("Test prompt")
        assert isinstance(result, str)
        assert result == "Test content"

    @patch('slide_deck_gen_v2.invoke_llm')
    def test_generate_slide_content_splits_by_marker(self, mock_invoke):
        """Test that content is split by [SLIDE] marker."""
        mock_content = "[SLIDE]".join(["Content " + str(i) for i in range(12)])
        mock_invoke.return_value = mock_content

        from slide_deck_gen_v2 import generate_slide_content

        result = generate_slide_content("Test description")
        assert len(result) == 12

    @patch('slide_deck_gen_v2.invoke_llm')
    def test_generate_slide_content_raises_on_wrong_count(self, mock_invoke):
        """Test that ValueError is raised when slide count doesn't match."""
        mock_content = "[SLIDE]".join(["Content " + str(i) for i in range(5)])
        mock_invoke.return_value = mock_content

        from slide_deck_gen_v2 import generate_slide_content

        with pytest.raises(ValueError, match="does not match"):
            generate_slide_content("Test description")


class TestRemoveUnwantedSlides:
    """Tests for slide removal function."""

    def test_remove_slides_sorts_indices(self):
        """Test that indices are sorted in descending order."""
        from slide_deck_gen_v2 import remove_unwanted_slides

        mock_prs = MagicMock()
        mock_prs.slides._sldIdLst = [MagicMock() for _ in range(5)]
        mock_prs.part.drop_rel = MagicMock()

        remove_unwanted_slides(mock_prs, [1, 3, 2])

        assert mock_prs.part.drop_rel.call_count == 3


class TestInsertContent:
    """Tests for content insertion function."""

    def test_insert_content_with_title(self):
        """Test inserting content with title."""
        from slide_deck_gen_v2 import insert_content

        mock_slide = MagicMock()
        mock_title = MagicMock()
        mock_slide.shapes.title = mock_title
        mock_slide.placeholders = []

        insert_content(mock_slide, "Test Title", "Test Content", 1)

        assert mock_title.text == "Test Title"

    def test_insert_content_moves_title_up(self):
        """Test that title is moved up when specified."""
        from slide_deck_gen_v2 import insert_content

        mock_slide = MagicMock()
        mock_title = MagicMock()
        mock_slide.shapes.title = mock_title
        mock_slide.placeholders = []

        insert_content(mock_slide, "Test Title", "Test Content", 1, move_title_up=True)

        assert mock_title.top is not None
