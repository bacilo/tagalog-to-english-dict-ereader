#!/bin/bash
# Build script for Tagalog-English Kindle Dictionary
#
# Generates the dictionary HTML and optionally creates the .mobi file.
#
# Usage:
#   ./scripts/build.sh           # Generate HTML only
#   ./scripts/build.sh --mobi    # Generate HTML and .mobi

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

INPUT_JSON="$PROJECT_DIR/data/tagalog_dict.json"
OUTPUT_HTML="$PROJECT_DIR/dist/dictionary.html"
OUTPUT_MOBI="$PROJECT_DIR/dist/dictionary.mobi"
OPF_FILE="$PROJECT_DIR/res/dictionary.opf"

echo "=== Tagalog Dictionary Build ==="
echo ""

# Check input exists
if [ ! -f "$INPUT_JSON" ]; then
    echo "Error: Input file not found: $INPUT_JSON"
    exit 1
fi

# Generate HTML
echo "Generating HTML dictionary..."
python -m tagalog_dict -v "$INPUT_JSON" "$OUTPUT_HTML"

# Validate output
if [ -f "$OUTPUT_HTML" ]; then
    ENTRY_COUNT=$(grep -c '<idx:entry' "$OUTPUT_HTML" || true)
    echo ""
    echo "Validation:"
    echo "  idx:entry count: $ENTRY_COUNT (expected: 42730)"
else
    echo "Error: Failed to generate HTML"
    exit 1
fi

# Generate .mobi if requested
if [ "$1" = "--mobi" ]; then
    echo ""
    echo "Generating .mobi file..."

    if command -v kindlegen &> /dev/null; then
        # Copy HTML to res/ temporarily for kindlegen
        cp "$OUTPUT_HTML" "$PROJECT_DIR/res/dictionary.html"
        cd "$PROJECT_DIR/res"
        kindlegen dictionary.opf -o dictionary.mobi
        mv dictionary.mobi "$OUTPUT_MOBI"
        rm dictionary.html
        cd "$PROJECT_DIR"
        echo "Generated: $OUTPUT_MOBI"
    else
        echo "Warning: kindlegen not found. Install it or use Kindle Previewer to create .mobi"
        echo "Manual command: kindlegen $OPF_FILE -o dictionary.mobi"
    fi
fi

echo ""
echo "=== Build Complete ==="
