"""
Main conversion pipeline orchestrating all modules.

This is the core logic that converts dictionary JSON to Kindle HTML.
"""
from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Dict

from .conjugation import extract_conjugations
from .formatter import ProcessedEntry, format_entry_html, wrap_in_kindle_html
from .inflections import format_base_inflections_xml, format_verb_inflections_xml
from .parser import load_dictionary


@dataclass
class ConversionStats:
    """
    Statistics from the conversion process.

    Useful for validation and debugging.
    """

    total_raw_entries: int = 0
    unique_words: int = 0
    verbs_with_conjugations: int = 0
    total_inflections: int = 0


def convert(input_path: Path, output_path: Path) -> ConversionStats:
    """
    Convert dictionary JSON to Kindle HTML.

    This is the main entry point that orchestrates:
    1. Loading JSON entries
    2. Merging duplicate words
    3. Extracting verb conjugations
    4. Generating inflections
    5. Formatting Kindle HTML

    Args:
        input_path: Path to the input JSON dictionary file
        output_path: Path to write the output HTML file

    Returns:
        ConversionStats with counts from the conversion

    Raises:
        FileNotFoundError: If input file doesn't exist
        json.JSONDecodeError: If input is not valid JSON
    """
    stats = ConversionStats()
    entries_by_word: Dict[str, ProcessedEntry] = {}

    for raw_entry in load_dictionary(input_path):
        stats.total_raw_entries += 1
        word = escape(raw_entry.word)
        definition = escape(raw_entry.definition)

        if word not in entries_by_word:
            entry = ProcessedEntry(word=word)
            entries_by_word[word] = entry

            # Add ligature inflection for the word itself
            base_infl = format_base_inflections_xml(word)
            if base_infl:
                entry.inflection_xml_blocks.append(base_infl)
                stats.total_inflections += 1

        entry = entries_by_word[word]
        entry.definitions.append(definition)

        # Extract and add verb conjugations
        conj = extract_conjugations(definition)
        if conj:
            stats.verbs_with_conjugations += 1
            verb_infl = format_verb_inflections_xml(conj)
            entry.inflection_xml_blocks.append(verb_infl)
            # Count: 3 verb forms + up to 3 ligatures
            stats.total_inflections += 3  # Base verb forms

    stats.unique_words = len(entries_by_word)

    # Generate HTML
    entries_html = "\n".join(
        format_entry_html(entry) for entry in entries_by_word.values()
    )
    full_html = wrap_in_kindle_html(entries_html)

    output_path.write_text(full_html, encoding="utf-8")

    return stats
