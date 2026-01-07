"""
Command-line interface for the dictionary converter.

Usage:
    python -m tagalog_dict data/tagalog_dict.json dist/dictionary.html
    tagalog-dict data/tagalog_dict.json dist/dictionary.html  # if installed
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .pipeline import convert


def main(argv: list[str] | None = None) -> int:
    """
    Main CLI entry point.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = argparse.ArgumentParser(
        description="Convert Tagalog dictionary JSON to Kindle HTML format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data/tagalog_dict.json dist/dictionary.html
  %(prog)s -v data/tagalog_dict.json dist/dictionary.html

After generating the HTML, use kindlegen or Kindle Previewer to create
the .mobi file:
  kindlegen res/dictionary.opf -o dictionary.mobi

Data Attribution:
  Dictionary data from Luis Ligunas' pinoy-dictionary-scraper
  https://github.com/luisligunas/pinoy-dictionary-scraper
        """,
    )
    parser.add_argument("input", type=Path, help="Input JSON dictionary file")
    parser.add_argument("output", type=Path, help="Output HTML file")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print conversion statistics"
    )

    args = parser.parse_args(argv)

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    try:
        stats = convert(args.input, args.output)
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        return 1

    if args.verbose:
        print("Conversion complete:")
        print(f"  Raw entries read: {stats.total_raw_entries}")
        print(f"  Unique words: {stats.unique_words}")
        print(f"  Verbs with conjugations: {stats.verbs_with_conjugations}")
        print(f"  Total inflections: {stats.total_inflections}")
        print(f"  Output written to: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
