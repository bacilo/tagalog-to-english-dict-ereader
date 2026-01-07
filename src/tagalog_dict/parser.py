"""
Dictionary JSON parsing and data models.

Handles loading the scraped dictionary data from JSON format.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True)
class RawEntry:
    """
    A single entry from the scraped dictionary JSON.

    Attributes:
        word: The Tagalog word
        definition: The full definition text (may include conjugations, POS, etc.)
        link: URL to the original source
        language: Language of the entry (always "Tagalog" in this dataset)
    """

    word: str
    definition: str
    link: str
    language: str


def load_dictionary(path: Path) -> Iterator[RawEntry]:
    """
    Load dictionary entries from JSON file.

    Yields entries one at a time to support streaming processing
    of large files if needed in the future.

    Args:
        path: Path to the JSON dictionary file

    Yields:
        RawEntry objects for each dictionary entry

    Raises:
        FileNotFoundError: If the JSON file doesn't exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for entry in data:
        yield RawEntry(
            word=entry["word"],
            definition=entry["definition"],
            link=entry.get("link", ""),
            language=entry.get("language", "Tagalog"),
        )


def load_dictionary_list(path: Path) -> list[RawEntry]:
    """
    Load all dictionary entries into a list.

    Convenience function when you need all entries in memory.

    Args:
        path: Path to the JSON dictionary file

    Returns:
        List of all RawEntry objects
    """
    return list(load_dictionary(path))
