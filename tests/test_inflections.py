"""Tests for the inflections module."""
from __future__ import annotations

import pytest

from tagalog_dict.conjugation import VerbConjugation
from tagalog_dict.inflections import (
    VOWELS,
    format_base_inflections_xml,
    format_ligature_inflection_xml,
    format_verb_inflections_xml,
    ligature_inflection,
)


class TestLigatureInflection:
    """Tests for the ligature form generation."""

    @pytest.mark.parametrize(
        "word,expected",
        [
            # Vowel endings get -ng
            ("bata", "batang"),
            ("aso", "asong"),
            ("ube", "ubeng"),
            ("sili", "siling"),
            ("puto", "putong"),
            ("babaU", "babaUng"),  # uppercase vowel at end
            # N ending gets -g
            ("akin", "aking"),
            ("niyan", "niyang"),
            ("saan", "saang"),
            # Other consonant endings return None
            ("bahay", None),
            ("kapit", None),
            ("liwas", None),
            ("bukas", None),
            # Edge cases
            ("", None),
            ("a", "ang"),
            ("n", "ng"),
        ],
    )
    def test_ligature_rules(self, word: str, expected: str | None) -> None:
        assert ligature_inflection(word) == expected

    def test_vowels_constant_complete(self) -> None:
        """Verify all vowels are in the VOWELS set."""
        assert "a" in VOWELS
        assert "e" in VOWELS
        assert "i" in VOWELS
        assert "o" in VOWELS
        assert "u" in VOWELS
        assert "A" in VOWELS
        assert "E" in VOWELS
        assert "I" in VOWELS
        assert "O" in VOWELS
        assert "U" in VOWELS


class TestFormatLigatureInflectionXml:
    """Tests for ligature XML generation."""

    def test_generates_xml_for_vowel_ending(self) -> None:
        xml = format_ligature_inflection_xml("bata")
        assert xml == '<idx:iform value="batang" />'

    def test_generates_xml_for_n_ending(self) -> None:
        xml = format_ligature_inflection_xml("akin")
        assert xml == '<idx:iform value="aking" />'

    def test_empty_for_consonant_ending(self) -> None:
        xml = format_ligature_inflection_xml("bahay")
        assert xml == ""

    def test_empty_for_empty_string(self) -> None:
        xml = format_ligature_inflection_xml("")
        assert xml == ""


class TestFormatBaseInflectionsXml:
    """Tests for the base inflection block generation."""

    def test_generates_block_for_vowel_ending(self) -> None:
        xml = format_base_inflections_xml("bata")
        assert "idx:infl" in xml
        assert 'inflgrp="other"' in xml
        assert 'value="batang"' in xml

    def test_empty_for_consonant_ending(self) -> None:
        xml = format_base_inflections_xml("bahay")
        assert xml == ""


class TestFormatVerbInflectionsXml:
    """Tests for verb inflection XML generation."""

    def test_generates_all_three_aspects(self) -> None:
        conj = VerbConjugation(
            progressive="inaaba",
            completed="inaba",
            contemplated="aabahin",
            raw_match="inaaba, inaba, aabahin",
        )
        xml = format_verb_inflections_xml(conj)

        assert 'inflgrp="verb"' in xml
        assert 'name="progressive" value="inaaba"' in xml
        assert 'name="completed" value="inaba"' in xml
        assert 'name="contemplated" value="aabahin"' in xml

    def test_includes_ligature_forms(self) -> None:
        """Verb forms ending in vowels should have ligature inflections."""
        conj = VerbConjugation(
            progressive="inaaba",  # ends in a -> inaabang
            completed="inaba",  # ends in a -> inabang
            contemplated="aabahin",  # ends in n -> aabahig
            raw_match="test",
        )
        xml = format_verb_inflections_xml(conj)

        assert 'value="inaabang"' in xml
        assert 'value="inabang"' in xml
        assert 'value="aabahing"' in xml

    def test_no_ligature_for_consonant_ending(self) -> None:
        """Verb forms ending in consonants shouldn't have extra ligatures."""
        conj = VerbConjugation(
            progressive="nag-aral",  # ends in l
            completed="nag-aral",
            contemplated="mag-aaral",
            raw_match="test",
        )
        xml = format_verb_inflections_xml(conj)

        # Should not have ligature forms for these
        assert 'value="nag-aralng"' not in xml
        assert 'value="nag-aralg"' not in xml
