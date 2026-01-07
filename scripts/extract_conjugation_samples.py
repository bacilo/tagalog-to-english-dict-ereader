#!/usr/bin/env python3
"""
Extract all conjugation matches from the dictionary as a golden master snapshot.

Run this BEFORE any regex changes to establish the baseline.
The output file is used by tests/test_conjugation.py for regression testing.

Usage:
    python scripts/extract_conjugation_samples.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# The sacred regex - copied exactly from src/json-html.py
CONJUGATION_PATTERN = re.compile(
    r"\(+((?:\([^)]+\)|[^),])+?(?:,\s*(?:\([^)]+\)|[^),])+?){2})\)"
    r"(\s*\d+\.)?\s*v\.,?\s*inf\.",
    re.IGNORECASE,
)


def extract_conjugations(definition: str) -> tuple[str, list[str]] | tuple[None, list[str]]:
    """Safely extract verb aspects while preserving root."""
    match = CONJUGATION_PATTERN.search(definition)
    if match:
        raw = match.group(1).strip()
        return raw, [c.strip() for c in raw.split(",")]
    return None, []


def main() -> int:
    project_root = Path(__file__).parent.parent
    input_file = project_root / "data" / "tagalog_dict.json"
    output_file = project_root / "tests" / "snapshots" / "conjugation_matches.json"

    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        return 1

    print(f"Reading dictionary from: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    matches = []
    for entry in data:
        raw, conjugations = extract_conjugations(entry["definition"])
        if raw and len(conjugations) == 3:
            matches.append(
                {
                    "word": entry["word"],
                    "definition": entry["definition"],
                    "raw_match": raw,
                    "expected": conjugations,
                }
            )

    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(matches)} conjugation matches")
    print(f"Saved to: {output_file}")

    # Also print some statistics
    total_entries = len(data)
    unique_words = len(set(e["word"] for e in data))
    print(f"\nDictionary statistics:")
    print(f"  Total entries: {total_entries}")
    print(f"  Unique words: {unique_words}")
    print(f"  Verb conjugations found: {len(matches)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
