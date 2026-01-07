"""
Tests for the SACRED conjugation regex.

CRITICAL: These tests document the exact behavior of the regex.
If any test fails after a regex change, the change MUST be reviewed carefully.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tagalog_dict.conjugation import (
    CONJUGATION_PATTERN,
    VerbConjugation,
    extract_conjugations,
)

SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"


class TestConjugationSnapshot:
    """Golden master tests - regex must match exactly these patterns."""

    @pytest.fixture
    def known_matches(self) -> list[dict]:
        """Load snapshot of all definitions that should match."""
        snapshot_file = SNAPSHOTS_DIR / "conjugation_matches.json"
        return json.loads(snapshot_file.read_text())

    def test_all_known_matches_still_match(self, known_matches: list[dict]) -> None:
        """CRITICAL: Ensure regex still matches all previously-matched patterns."""
        failures = []
        for entry in known_matches:
            result = extract_conjugations(entry["definition"])
            if result is None:
                failures.append(f"No longer matches: {entry['definition'][:80]}")
            elif (
                result.progressive,
                result.completed,
                result.contemplated,
            ) != tuple(entry["expected"]):
                failures.append(f"Different result for: {entry['definition'][:80]}")

        assert not failures, (
            f"Regex regression! {len(failures)} failures:\n" + "\n".join(failures[:10])
        )

    def test_match_count_unchanged(self, known_matches: list[dict]) -> None:
        """Ensure we're not losing or gaining matches unexpectedly."""
        # 14,252 conjugation matches as of initial snapshot
        expected_count = 14252
        assert len(known_matches) == expected_count, (
            f"Snapshot count changed! Expected {expected_count}, got {len(known_matches)}"
        )


class TestConjugationEdgeCases:
    """Explicit tests for known edge cases the regex handles."""

    @pytest.mark.parametrize(
        "definition,expected",
        [
            # Standard format: word followed by conjugations
            (
                "abahin (inaaba, inaba, aabahin) v., inf. notify",
                ("inaaba", "inaba", "aabahin"),
            ),
            # No word prefix, starts with parenthesis
            (
                "(inaaba, inaba, aabain) v., inf. look down upon",
                ("inaaba", "inaba", "aabain"),
            ),
            # Optional comma after v.
            (
                "word (prog, comp, cont) v. inf. meaning",
                ("prog", "comp", "cont"),
            ),
            # Case insensitivity
            (
                "word (prog, comp, cont) V., INF. meaning",
                ("prog", "comp", "cont"),
            ),
        ],
    )
    def test_known_patterns(
        self, definition: str, expected: tuple[str, str, str]
    ) -> None:
        result = extract_conjugations(definition)
        assert result is not None
        assert (result.progressive, result.completed, result.contemplated) == expected

    def test_non_verb_returns_none(self) -> None:
        """Non-verb definitions should return None."""
        assert extract_conjugations("abaka n. abaka hemp") is None
        assert extract_conjugations("aba adj. poor; humble") is None
        assert extract_conjugations("random text without verbs") is None

    def test_result_is_dataclass(self) -> None:
        """Verify the result is a proper VerbConjugation dataclass."""
        result = extract_conjugations("word (a, b, c) v., inf. test")
        assert result is not None
        assert isinstance(result, VerbConjugation)
        assert result.raw_match == "a, b, c"


class TestConjugationPatternIntegrity:
    """Tests to ensure we don't accidentally modify the regex."""

    def test_pattern_string_unchanged(self) -> None:
        """
        CRITICAL: This test fails if the regex pattern is modified.
        If you need to change the regex, update this test AND run full regression.
        """
        expected_pattern = (
            r"\(+((?:\([^)]+\)|[^),])+?(?:,\s*(?:\([^)]+\)|[^),])+?){2})\)"
            r"(\s*\d+\.)?\s*v\.,?\s*inf\."
        )
        assert CONJUGATION_PATTERN.pattern == expected_pattern

    def test_pattern_flags_unchanged(self) -> None:
        """Ensure the regex flags haven't changed."""
        assert CONJUGATION_PATTERN.flags == re.IGNORECASE | re.UNICODE
