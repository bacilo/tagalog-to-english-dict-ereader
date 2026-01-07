"""Tests for the dictionary parser module."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tagalog_dict.parser import RawEntry, load_dictionary, load_dictionary_list


class TestRawEntry:
    """Tests for the RawEntry dataclass."""

    def test_create_entry(self) -> None:
        """Test basic entry creation."""
        entry = RawEntry(
            word="test",
            definition="a test word",
            link="http://example.com",
            language="Tagalog",
        )
        assert entry.word == "test"
        assert entry.definition == "a test word"
        assert entry.link == "http://example.com"
        assert entry.language == "Tagalog"

    def test_entry_is_frozen(self) -> None:
        """Entries should be immutable."""
        entry = RawEntry(
            word="test", definition="test", link="", language="Tagalog"
        )
        with pytest.raises(AttributeError):
            entry.word = "changed"  # type: ignore


class TestLoadDictionary:
    """Tests for loading dictionary JSON files."""

    def test_load_single_entry(self, tmp_path: Path) -> None:
        """Test loading a file with a single entry."""
        sample = [
            {
                "word": "aba",
                "definition": "aba adj. poor",
                "link": "http://example.com",
                "language": "Tagalog",
            }
        ]
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(sample))

        entries = list(load_dictionary(json_file))
        assert len(entries) == 1
        assert entries[0].word == "aba"
        assert entries[0].definition == "aba adj. poor"

    def test_load_multiple_entries(self, tmp_path: Path) -> None:
        """Test loading multiple entries."""
        sample = [
            {"word": "a", "definition": "def a", "link": "", "language": "Tagalog"},
            {"word": "b", "definition": "def b", "link": "", "language": "Tagalog"},
            {"word": "c", "definition": "def c", "link": "", "language": "Tagalog"},
        ]
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(sample))

        entries = list(load_dictionary(json_file))
        assert len(entries) == 3
        assert [e.word for e in entries] == ["a", "b", "c"]

    def test_missing_optional_fields(self, tmp_path: Path) -> None:
        """Test that missing optional fields get defaults."""
        sample = [{"word": "test", "definition": "a test"}]
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(sample))

        entries = list(load_dictionary(json_file))
        assert entries[0].link == ""
        assert entries[0].language == "Tagalog"

    def test_file_not_found(self) -> None:
        """Test error handling for missing files."""
        with pytest.raises(FileNotFoundError):
            list(load_dictionary(Path("/nonexistent/path.json")))

    def test_invalid_json(self, tmp_path: Path) -> None:
        """Test error handling for invalid JSON."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("not valid json")

        with pytest.raises(json.JSONDecodeError):
            list(load_dictionary(json_file))


class TestLoadDictionaryList:
    """Tests for the convenience list loader."""

    def test_returns_list(self, tmp_path: Path) -> None:
        """Test that load_dictionary_list returns a list."""
        sample = [
            {"word": "a", "definition": "def", "link": "", "language": "Tagalog"},
            {"word": "b", "definition": "def", "link": "", "language": "Tagalog"},
        ]
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(sample))

        result = load_dictionary_list(json_file)
        assert isinstance(result, list)
        assert len(result) == 2


class TestProductionData:
    """Tests against the actual production dictionary."""

    @pytest.fixture
    def production_dict(self) -> Path:
        """Path to production dictionary."""
        return Path(__file__).parent.parent / "data" / "tagalog_dict.json"

    @pytest.mark.slow
    def test_production_entry_count(self, production_dict: Path) -> None:
        """Verify production dictionary has expected entries."""
        if not production_dict.exists():
            pytest.skip("Production data not available")

        entries = load_dictionary_list(production_dict)
        assert len(entries) == 45831  # Known count

    @pytest.mark.slow
    def test_production_all_entries_valid(self, production_dict: Path) -> None:
        """Verify all production entries have required fields."""
        if not production_dict.exists():
            pytest.skip("Production data not available")

        for entry in load_dictionary(production_dict):
            assert entry.word, "Entry missing word"
            assert entry.definition, "Entry missing definition"
