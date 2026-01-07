#!/bin/bash
# Build script for Tagalog-English Kindle Dictionary
#
# Generates the dictionary HTML and optionally creates the .mobi file.
#
# Usage:
#   ./scripts/build.sh           # Generate HTML only
#   ./scripts/build.sh --mobi    # Generate HTML and .mobi
#
# Requirements:
#   - Python 3.10+ with tagalog_dict package installed
#   - Calibre (for --mobi): https://calibre-ebook.com/download

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

INPUT_JSON="$PROJECT_DIR/data/tagalog_dict.json"
OUTPUT_HTML="$PROJECT_DIR/dist/dictionary.html"
OUTPUT_MOBI="$PROJECT_DIR/dist/dictionary.mobi"

# Find ebook-convert (Calibre)
find_ebook_convert() {
    # Check if in PATH
    if command -v ebook-convert &> /dev/null; then
        echo "ebook-convert"
        return 0
    fi

    # Check macOS app bundle location
    local macos_path="/Applications/calibre.app/Contents/MacOS/ebook-convert"
    if [ -x "$macos_path" ]; then
        echo "$macos_path"
        return 0
    fi

    return 1
}

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

    EBOOK_CONVERT=$(find_ebook_convert) || true

    if [ -n "$EBOOK_CONVERT" ]; then
        "$EBOOK_CONVERT" "$OUTPUT_HTML" "$OUTPUT_MOBI" \
            --output-profile kindle \
            --no-inline-toc \
            --mobi-file-type old \
            2>&1 | grep -E "(Output saved|error|Error)" || true

        if [ -f "$OUTPUT_MOBI" ]; then
            echo "Generated: $OUTPUT_MOBI"
            ls -lh "$OUTPUT_MOBI"
        else
            echo "Error: Failed to generate .mobi"
            exit 1
        fi
    else
        echo "Error: Calibre not found."
        echo ""
        echo "Install Calibre to generate .mobi files:"
        echo "  Download from: https://calibre-ebook.com/download"
        echo ""
        echo "Or add to PATH if already installed:"
        echo "  export PATH=\"\$PATH:/Applications/calibre.app/Contents/MacOS\""
        exit 1
    fi
fi

echo ""
echo "=== Build Complete ==="
