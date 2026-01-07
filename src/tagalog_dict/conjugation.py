"""
Verb conjugation extraction from Tagalog dictionary definitions.

WARNING: THE REGEX PATTERN IN THIS FILE IS SACRED.
It captures edge cases discovered through extensive testing against 45,831 entries.
Any changes MUST be validated against the full snapshot test suite.

See tests/test_conjugation.py for the full test matrix.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

# SACRED REGEX - DO NOT MODIFY WITHOUT FULL REGRESSION TESTING
# Captures: (progressive, completed, contemplated) v., inf.
#
# Handles:
#   - Nested parentheses in conjugations
#   - Numbered definition prefixes (e.g., "1. v., inf.")
#   - Optional comma after "v."
#   - Case insensitivity
#   - Conjugations at start of definition: "(inaaba, inaba, aabain) v., inf."
#   - Conjugations after word: "abahin (inaaba, inaba, aabahin) v., inf."
#
# Pattern breakdown:
#   \(+                                    - One or more opening parentheses
#   ((?:\([^)]+\)|[^),])+?                 - First conjugation (may contain nested parens)
#   (?:,\s*(?:\([^)]+\)|[^),])+?){2}       - Two more comma-separated conjugations
#   \)                                     - Closing parenthesis
#   (\s*\d+\.)?                            - Optional numbered prefix (e.g., "1.")
#   \s*v\.,?\s*inf\.                       - "v., inf." or "v. inf."
#
CONJUGATION_PATTERN = re.compile(
    r"\(+((?:\([^)]+\)|[^),])+?(?:,\s*(?:\([^)]+\)|[^),])+?){2})\)"
    r"(\s*\d+\.)?\s*v\.,?\s*inf\.",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class VerbConjugation:
    """
    Represents extracted Tagalog verb tenses.

    Tagalog verbs have three aspects:
    - progressive: action in progress (e.g., "inaaba" - is notifying)
    - completed: action completed (e.g., "inaba" - notified)
    - contemplated: action planned/future (e.g., "aabahin" - will notify)
    """

    progressive: str
    completed: str
    contemplated: str
    raw_match: str  # Original matched string for debugging


def extract_conjugations(definition: str) -> Optional[VerbConjugation]:
    """
    Extract verb conjugations from a definition string.

    Args:
        definition: The full definition text, e.g.,
            "abahin (inaaba, inaba, aabahin) v., inf. notify"

    Returns:
        VerbConjugation if found, None otherwise.

    Examples:
        >>> result = extract_conjugations(
        ...     "abahin (inaaba, inaba, aabahin) v., inf. notify"
        ... )
        >>> result.progressive
        'inaaba'
        >>> result.completed
        'inaba'
        >>> result.contemplated
        'aabahin'
    """
    match = CONJUGATION_PATTERN.search(definition)
    if not match:
        return None

    raw = match.group(1).strip()
    parts = [p.strip() for p in raw.split(",")]

    if len(parts) != 3:
        return None  # Defensive: pattern should guarantee 3 parts

    return VerbConjugation(
        progressive=parts[0],
        completed=parts[1],
        contemplated=parts[2],
        raw_match=raw,
    )
