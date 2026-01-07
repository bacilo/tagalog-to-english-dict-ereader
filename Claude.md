# Claude.md - Development Guidelines for Tagalog Dictionary Project

## Project Overview

This project converts scraped Tagalog dictionary data (JSON) into Kindle-compatible
.mobi dictionaries. The dictionary contains 45,831 entries (42,730 unique words)
with verb conjugation detection and ligature inflection support.

**Data Attribution**: Dictionary data from Luis Ligunas'
[pinoy-dictionary-scraper](https://github.com/luisligunas/pinoy-dictionary-scraper).

---

## CRITICAL: The Sacred Regex

The `CONJUGATION_PATTERN` regex in `src/tagalog_dict/conjugation.py` is the result
of extensive iteration to handle all edge cases in the dictionary data.

### DO NOT MODIFY THIS REGEX without:

1. **Running the full snapshot test suite**: `pytest tests/test_conjugation.py -v`
2. **Regenerating snapshots first** if intentionally changing behavior:
   ```bash
   python scripts/extract_conjugation_samples.py
   ```
3. **Reviewing the diff** of any snapshot changes
4. **Testing on the full dataset**: Generate dictionary.html and verify entry counts

### The regex handles these edge cases:
- Conjugations starting a definition: `(inaaba, inaba, aabain) v., inf.`
- Conjugations after a word: `abahin (inaaba, inaba, aabahin) v., inf.`
- Nested parentheses in conjugation forms
- Numbered definition prefixes: `(forms) 1. v., inf.`
- Optional comma: `v., inf.` and `v. inf.`

### Snapshot Test Details
- 14,252 verb conjugations are captured in `tests/snapshots/conjugation_matches.json`
- Any regex change must preserve all existing matches
- The snapshot test validates every single match against expected output

---

## Development Workflow

### Test-First Development

1. **Before any code change**, ensure tests pass: `pytest`
2. **Write a failing test** for the new behavior
3. **Implement the change** to make the test pass
4. **Run full regression**: `pytest -m "not slow"` (or full suite with `pytest`)

### Quick Commands

```bash
# Run fast tests
pytest -m "not slow"

# Run all tests including production regression
pytest

# Run only conjugation regex tests
pytest tests/test_conjugation.py -v

# Generate new dictionary
python -m tagalog_dict data/tagalog_dict.json dist/dictionary.html

# Verbose output with stats
python -m tagalog_dict -v data/tagalog_dict.json dist/dictionary.html
```

### Building the Dictionary

```bash
# Full build process
./scripts/build.sh

# Or manually:
python -m tagalog_dict data/tagalog_dict.json dist/dictionary.html
# Then use kindlegen or Kindle Previewer to create .mobi
```

### Validation

After generating output, verify:
- Entry count: `grep -c '<idx:entry' dist/dictionary.html` (should be 42,730)
- Test on actual Kindle device or Kindle Previewer

---

## Module Responsibilities

| Module | Purpose | Critical? |
|--------|---------|-----------|
| `conjugation.py` | Sacred regex, verb extraction | **YES** |
| `parser.py` | JSON loading | No |
| `inflections.py` | Ligature/verb XML | Medium |
| `formatter.py` | Kindle HTML structure | Medium |
| `pipeline.py` | Orchestration | No |
| `cli.py` | Command-line interface | No |

---

## Code Style

- Python 3.10+ with type hints on all public functions
- Use `dataclass` for data structures
- Use `pathlib.Path` over string paths
- Format with `black`, check with `mypy --strict`

---

## Gradual Refactoring Principles

1. **One module at a time**: Extract, test, verify output unchanged
2. **Snapshot everything**: Before touching regex, capture current behavior
3. **Compare outputs**: After any change, diff against known-good output
4. **Small commits**: Each commit should be individually revertible

---

## Common Pitfalls

### HTML Escaping
- Raw dictionary data may contain `<`, `>`, `&`
- Always use `html.escape()` on user-facing text
- But NOT on generated XML tags

### Kindle-Specific Quirks
- The `idx:` namespace URL is informational, not a real endpoint
- `mbp:frameset` is required for dictionary lookup to work
- Word IDs cannot contain spaces (use underscores)

### Character Encoding
- Source JSON is UTF-8
- Output HTML must be UTF-8
- Tagalog uses standard ASCII plus accented characters (rare)

---

## Project Structure

```
tagalog-to-english-dict-ereader/
├── Claude.md                  # This file
├── README.md                  # User documentation
├── pyproject.toml             # Package configuration
├── requirements-dev.txt       # Development dependencies
│
├── src/tagalog_dict/          # Main package
│   ├── __init__.py
│   ├── __main__.py            # python -m tagalog_dict
│   ├── cli.py                 # Command-line interface
│   ├── conjugation.py         # SACRED REGEX
│   ├── inflections.py         # Ligature/verb XML
│   ├── formatter.py           # Kindle HTML
│   ├── parser.py              # JSON loading
│   └── pipeline.py            # Orchestration
│
├── tests/
│   ├── snapshots/             # Golden master data
│   ├── test_conjugation.py    # CRITICAL
│   ├── test_*.py              # Other tests
│   └── conftest.py            # Fixtures
│
├── scripts/
│   ├── build.sh               # Full build
│   └── extract_conjugation_samples.py
│
├── data/tagalog_dict.json     # Source dictionary
├── res/dictionary.opf         # Kindle config
├── dist/                      # Generated output
└── src/archive/               # Old code for reference
```

---

## Expected Test Output

```
pytest -v
============================= test session starts ==============================
...
66 passed, 5 deselected in 0.22s (fast tests)
or
71 passed in 1.00s (all tests)
```

---

## Future Improvements (Not Yet Implemented)

- [ ] Better HTML formatting (bold part of speech, indentation)
- [ ] Pronunciation guides (if data available)
- [ ] Cross-references between related words
- [ ] Streaming processing for memory efficiency
