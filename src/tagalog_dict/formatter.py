"""
Kindle-compatible HTML generation.

Generates the idx:entry format required by Kindle dictionaries.
"""
from __future__ import annotations

import string
from dataclasses import dataclass, field


@dataclass
class ProcessedEntry:
    """
    A dictionary entry ready for HTML rendering.

    Attributes:
        word: The headword (already HTML-escaped)
        definitions: List of definition texts (already HTML-escaped)
        inflection_xml_blocks: List of idx:infl XML blocks
    """

    word: str
    definitions: list[str] = field(default_factory=list)
    inflection_xml_blocks: list[str] = field(default_factory=list)


def format_entry_html(entry: ProcessedEntry) -> str:
    """
    Generate idx:entry HTML for a single dictionary word.

    Multiple definitions are labeled with A), B), C), etc.

    Args:
        entry: The processed entry to format

    Returns:
        Complete idx:entry HTML block
    """
    # Format definitions with A), B), C) labels
    def_html = "".join(
        f"{label}) {defn}<br>"
        for label, defn in zip(string.ascii_uppercase, entry.definitions)
    )

    inflections = "".join(entry.inflection_xml_blocks)
    word_id = entry.word.replace(" ", "_")

    return f"""<idx:entry name="default" scriptable="yes" spell="yes">
              <h5><dt><idx:orth value="{word_id}">{entry.word}
                {inflections}
              </idx:orth></dt></h5>
              <dd>{def_html}</dd>
            </idx:entry>
            <hr/>"""


def wrap_in_kindle_html(entries_html: str) -> str:
    """
    Wrap entry HTML in complete Kindle dictionary structure.

    Args:
        entries_html: Concatenated idx:entry blocks

    Returns:
        Complete HTML document ready for kindlegen
    """
    return f"""<html xmlns:idx="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf">
      <head><meta charset="utf-8"></head>
      <body>
        <mbp:frameset>
          {entries_html}
        </mbp:frameset>
      </body>
    </html>"""
