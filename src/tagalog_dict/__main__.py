"""
Entry point for running as a module.

Usage:
    python -m tagalog_dict data/tagalog_dict.json dist/dictionary.html
"""
from __future__ import annotations

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
