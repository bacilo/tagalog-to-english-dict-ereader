"""Tests for the HTML formatter module."""
from __future__ import annotations

import pytest

from tagalog_dict.formatter import (
    ProcessedEntry,
    format_entry_html,
    wrap_in_kindle_html,
)


class TestProcessedEntry:
    """Tests for the ProcessedEntry dataclass."""

    def test_create_empty_entry(self) -> None:
        """Test creating an entry with defaults."""
        entry = ProcessedEntry(word="test")
        assert entry.word == "test"
        assert entry.definitions == []
        assert entry.inflection_xml_blocks == []

    def test_create_full_entry(self) -> None:
        """Test creating a fully populated entry."""
        entry = ProcessedEntry(
            word="aba",
            definitions=["def 1", "def 2"],
            inflection_xml_blocks=["<xml>1</xml>", "<xml>2</xml>"],
        )
        assert entry.word == "aba"
        assert len(entry.definitions) == 2
        assert len(entry.inflection_xml_blocks) == 2


class TestFormatEntryHtml:
    """Tests for the entry HTML formatter."""

    def test_single_definition(self) -> None:
        """Test formatting a single definition."""
        entry = ProcessedEntry(word="test", definitions=["meaning one"])
        html = format_entry_html(entry)

        assert "idx:entry" in html
        assert 'name="default"' in html
        assert 'scriptable="yes"' in html
        assert "A) meaning one" in html
        assert "B)" not in html

    def test_multiple_definitions_labeled(self) -> None:
        """Test that multiple definitions get A, B, C labels."""
        entry = ProcessedEntry(
            word="test", definitions=["first", "second", "third"]
        )
        html = format_entry_html(entry)

        assert "A) first" in html
        assert "B) second" in html
        assert "C) third" in html

    def test_word_with_space_gets_underscore_id(self) -> None:
        """Test that spaces in words are converted to underscores in IDs."""
        entry = ProcessedEntry(word="my word", definitions=["def"])
        html = format_entry_html(entry)

        assert 'value="my_word"' in html
        assert ">my word" in html  # Display name keeps space

    def test_includes_inflections(self) -> None:
        """Test that inflection blocks are included."""
        entry = ProcessedEntry(
            word="test",
            definitions=["def"],
            inflection_xml_blocks=['<idx:infl inflgrp="verb">content</idx:infl>'],
        )
        html = format_entry_html(entry)

        assert 'inflgrp="verb"' in html

    def test_required_kindle_elements(self) -> None:
        """Test that all required Kindle elements are present."""
        entry = ProcessedEntry(word="test", definitions=["def"])
        html = format_entry_html(entry)

        assert "<idx:entry" in html
        assert "<idx:orth" in html
        assert "</idx:orth>" in html
        assert "<h5>" in html
        assert "<dt>" in html
        assert "<dd>" in html
        assert "<hr/>" in html


class TestWrapInKindleHtml:
    """Tests for the full document wrapper."""

    def test_includes_namespace(self) -> None:
        """Test that the idx namespace is declared."""
        html = wrap_in_kindle_html("<content>")
        assert 'xmlns:idx=' in html

    def test_includes_charset(self) -> None:
        """Test UTF-8 charset is specified."""
        html = wrap_in_kindle_html("<content>")
        assert 'charset="utf-8"' in html

    def test_includes_mbp_frameset(self) -> None:
        """Test that mbp:frameset wrapper is present."""
        html = wrap_in_kindle_html("<content>")
        assert "<mbp:frameset>" in html
        assert "</mbp:frameset>" in html

    def test_content_is_embedded(self) -> None:
        """Test that the content is properly embedded."""
        html = wrap_in_kindle_html("<idx:entry>test</idx:entry>")
        assert "<idx:entry>test</idx:entry>" in html

    def test_is_valid_html_structure(self) -> None:
        """Test that the output has proper HTML structure."""
        html = wrap_in_kindle_html("<content>")
        assert html.startswith("<html")
        assert "<head>" in html
        assert "</head>" in html
        assert "<body>" in html
        assert "</body>" in html
        assert "</html>" in html
