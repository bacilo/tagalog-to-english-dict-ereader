"""
Generate Kindle inflection forms for dictionary entries.

Handles:
- Tagalog ligature forms (-ng, -g suffixes)
- Verb conjugation inflections (progressive, completed, contemplated)
"""
from __future__ import annotations

from typing import Optional

from .conjugation import VerbConjugation

# Tagalog vowels for ligature detection
VOWELS = frozenset("aeiouAEIOU")


def ligature_inflection(word: str) -> Optional[str]:
    """
    Generate Tagalog ligature form.

    The Tagalog ligature "na" connects modifiers to the words they modify.
    It contracts based on the ending of the first word:
    - Words ending in vowels: append 'ng' (e.g., 'bata' -> 'batang')
    - Words ending in 'n': append 'g' (e.g., 'akin' -> 'aking')
    - Otherwise: no contraction (use separate 'na')

    Args:
        word: The word to generate ligature form for

    Returns:
        The ligature form, or None if no contraction applies

    Examples:
        >>> ligature_inflection("bata")
        'batang'
        >>> ligature_inflection("akin")
        'aking'
        >>> ligature_inflection("bahay")
        None
    """
    if not word:
        return None

    last_char = word[-1].lower()

    if last_char in VOWELS:
        return f"{word}ng"
    if last_char == "n":
        return f"{word}g"
    return None


def format_ligature_inflection_xml(word: str) -> str:
    """
    Generate idx:iform XML for ligature, empty string if none applies.

    Args:
        word: The word to generate ligature inflection for

    Returns:
        XML string for the inflection, or empty string
    """
    lig = ligature_inflection(word)
    if lig is None:
        return ""
    return f'<idx:iform value="{lig}" />'


def format_base_inflections_xml(word: str) -> str:
    """
    Generate the base inflection block for a word (ligature form only).

    Args:
        word: The dictionary headword

    Returns:
        Complete idx:infl XML block, or empty string if no inflections
    """
    lig_xml = format_ligature_inflection_xml(word)
    if not lig_xml:
        return ""
    return f"""
        <idx:infl inflgrp="other">
        {lig_xml}
        </idx:infl>
        """


def format_verb_inflections_xml(conj: VerbConjugation) -> str:
    """
    Generate full verb inflection XML block.

    Creates inflection entries for all three verb aspects plus their
    ligature forms (if applicable).

    Args:
        conj: The extracted verb conjugation

    Returns:
        Complete idx:infl XML block for verb forms
    """
    parts = []

    for name, value in [
        ("progressive", conj.progressive),
        ("completed", conj.completed),
        ("contemplated", conj.contemplated),
    ]:
        parts.append(f'<idx:iform name="{name}" value="{value}" />')
        lig_xml = format_ligature_inflection_xml(value)
        if lig_xml:
            parts.append(lig_xml)

    return f"""
    <idx:infl inflgrp="verb">
    {chr(10).join(parts)}
    </idx:infl>
    """
