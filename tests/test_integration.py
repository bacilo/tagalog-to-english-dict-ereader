"""
Full pipeline integration tests.

These tests verify the entire conversion process produces correct output.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tagalog_dict.pipeline import ConversionStats, convert


class TestFullPipeline:
    """Tests for the complete conversion pipeline."""

    def test_produces_valid_kindle_structure(self, tmp_path: Path) -> None:
        """Test that output contains required Kindle elements."""
        # Create minimal test input
        sample_json = tmp_path / "input.json"
        sample_json.write_text(
            """[
            {"word": "abahin", "definition": "abahin (inaaba, inaba, aabahin) v., inf. notify", "link": "", "language": "Tagalog"}
        ]"""
        )

        output_html = tmp_path / "output.html"
        stats = convert(sample_json, output_html)

        html = output_html.read_text()

        # Required Kindle dictionary elements
        assert "xmlns:idx=" in html
        assert "<idx:entry" in html
        assert "<idx:orth" in html
        assert "<mbp:frameset>" in html

    def test_verb_inflections_included(self, tmp_path: Path) -> None:
        """Test that verb conjugations generate inflection XML."""
        sample_json = tmp_path / "input.json"
        sample_json.write_text(
            """[
            {"word": "abahin", "definition": "abahin (inaaba, inaba, aabahin) v., inf. notify", "link": "", "language": "Tagalog"}
        ]"""
        )

        output_html = tmp_path / "output.html"
        convert(sample_json, output_html)

        html = output_html.read_text()
        assert 'inflgrp="verb"' in html
        assert 'value="inaaba"' in html  # progressive
        assert 'value="inaba"' in html  # completed
        assert 'value="aabahin"' in html  # contemplated

    def test_duplicate_words_merged(self, tmp_path: Path) -> None:
        """Test that multiple entries for same word get A), B) labels."""
        sample_json = tmp_path / "input.json"
        sample_json.write_text(
            """[
            {"word": "aba", "definition": "aba adj. poor", "link": "", "language": "Tagalog"},
            {"word": "aba", "definition": "aba! intrj. Well!", "link": "", "language": "Tagalog"}
        ]"""
        )

        output_html = tmp_path / "output.html"
        stats = convert(sample_json, output_html)

        html = output_html.read_text()
        assert stats.unique_words == 1
        assert stats.total_raw_entries == 2
        assert "A) aba adj. poor" in html
        assert "B) aba! intrj. Well!" in html

    def test_ligature_inflections_for_vowel_ending(self, tmp_path: Path) -> None:
        """Test that words ending in vowels get ligature forms."""
        sample_json = tmp_path / "input.json"
        sample_json.write_text(
            """[
            {"word": "bata", "definition": "bata n. child", "link": "", "language": "Tagalog"}
        ]"""
        )

        output_html = tmp_path / "output.html"
        convert(sample_json, output_html)

        html = output_html.read_text()
        assert 'value="batang"' in html  # ligature form

    def test_html_escaping(self, tmp_path: Path) -> None:
        """Test that special characters are properly escaped."""
        sample_json = tmp_path / "input.json"
        sample_json.write_text(
            """[
            {"word": "test", "definition": "meaning with <brackets> & ampersand", "link": "", "language": "Tagalog"}
        ]"""
        )

        output_html = tmp_path / "output.html"
        convert(sample_json, output_html)

        html = output_html.read_text()
        assert "&lt;brackets&gt;" in html
        assert "&amp; ampersand" in html

    def test_stats_returned(self, tmp_path: Path) -> None:
        """Test that conversion returns useful statistics."""
        sample_json = tmp_path / "input.json"
        sample_json.write_text(
            """[
            {"word": "abahin", "definition": "abahin (inaaba, inaba, aabahin) v., inf. notify", "link": "", "language": "Tagalog"},
            {"word": "aba", "definition": "aba adj. poor", "link": "", "language": "Tagalog"}
        ]"""
        )

        output_html = tmp_path / "output.html"
        stats = convert(sample_json, output_html)

        assert isinstance(stats, ConversionStats)
        assert stats.total_raw_entries == 2
        assert stats.unique_words == 2
        assert stats.verbs_with_conjugations == 1


class TestProductionRegression:
    """Regression tests against the actual production dictionary."""

    @pytest.fixture
    def production_dict(self) -> Path:
        """Path to production dictionary."""
        return Path(__file__).parent.parent / "data" / "tagalog_dict.json"

    @pytest.fixture
    def production_html(self) -> Path:
        """Path to production HTML output."""
        return Path(__file__).parent.parent / "dist" / "dictionary.html"

    @pytest.mark.slow
    def test_production_entry_counts(
        self, production_dict: Path, tmp_path: Path
    ) -> None:
        """Ensure we produce the correct number of entries."""
        if not production_dict.exists():
            pytest.skip("Production data not available")

        output_html = tmp_path / "output.html"
        stats = convert(production_dict, output_html)

        # These numbers come from analysis of the actual data
        assert stats.total_raw_entries == 45831, "Raw entry count changed"
        assert stats.unique_words == 42730, "Unique word count changed"

    @pytest.mark.slow
    def test_production_verb_count(
        self, production_dict: Path, tmp_path: Path
    ) -> None:
        """Verify verb conjugation detection count."""
        if not production_dict.exists():
            pytest.skip("Production data not available")

        output_html = tmp_path / "output.html"
        stats = convert(production_dict, output_html)

        # 14,252 conjugation matches from snapshot
        assert stats.verbs_with_conjugations == 14252, "Verb conjugation count changed"

    @pytest.mark.slow
    def test_production_output_structure(
        self, production_dict: Path, tmp_path: Path
    ) -> None:
        """Verify production output has correct structure."""
        if not production_dict.exists():
            pytest.skip("Production data not available")

        output_html = tmp_path / "output.html"
        convert(production_dict, output_html)

        html = output_html.read_text()

        # Verify key counts by counting occurrences
        entry_count = html.count("<idx:entry")
        assert entry_count == 42730, f"Entry count: {entry_count}"

        # Should have at least as many idx:orth as entries
        orth_count = html.count("<idx:orth")
        assert orth_count >= 42730, f"Orth count: {orth_count}"


class TestCLI:
    """Tests for the command-line interface."""

    def test_cli_help(self) -> None:
        """Test that help works."""
        from tagalog_dict.cli import main

        # Help should exit with code 0
        with pytest.raises(SystemExit) as excinfo:
            main(["--help"])
        assert excinfo.value.code == 0

    def test_cli_missing_file(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test error handling for missing input file."""
        from tagalog_dict.cli import main

        result = main([str(tmp_path / "nonexistent.json"), str(tmp_path / "out.html")])
        assert result == 1

        captured = capsys.readouterr()
        assert "not found" in captured.err

    def test_cli_successful_conversion(self, tmp_path: Path) -> None:
        """Test successful conversion via CLI."""
        from tagalog_dict.cli import main

        # Create test input
        input_file = tmp_path / "input.json"
        input_file.write_text('[{"word": "test", "definition": "a test", "link": "", "language": "Tagalog"}]')
        output_file = tmp_path / "output.html"

        result = main([str(input_file), str(output_file)])
        assert result == 0
        assert output_file.exists()

    def test_cli_verbose_output(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test verbose flag outputs statistics."""
        from tagalog_dict.cli import main

        input_file = tmp_path / "input.json"
        input_file.write_text('[{"word": "test", "definition": "a test", "link": "", "language": "Tagalog"}]')
        output_file = tmp_path / "output.html"

        result = main(["-v", str(input_file), str(output_file)])
        assert result == 0

        captured = capsys.readouterr()
        assert "Raw entries read" in captured.out
        assert "Unique words" in captured.out
