"""Shared pytest fixtures for the test suite."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def snapshots_dir() -> Path:
    """Return the snapshots directory."""
    return Path(__file__).parent / "snapshots"


@pytest.fixture
def sample_entries() -> list[dict[str, Any]]:
    """Sample dictionary entries for testing."""
    return [
        {
            "word": "abahin",
            "definition": "abahin (inaaba, inaba, aabahin) v., inf. notify; pay attention to",
            "link": "https://tagalog.pinoydictionary.com/word/abahin/",
            "language": "Tagalog",
        },
        {
            "word": "aba",
            "definition": "aba adj. poor; humble; subservient",
            "link": "https://tagalog.pinoydictionary.com/word/aba/",
            "language": "Tagalog",
        },
        {
            "word": "aba",
            "definition": "aba! intrj. Well; Hi!",
            "link": "https://tagalog.pinoydictionary.com/word/aba/",
            "language": "Tagalog",
        },
    ]
