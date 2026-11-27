"""
Utilities to simplify interaction with tmt and rpm/spec files.
"""

from __future__ import annotations

from .results import Result
from .test_env import TestEnv

__all__ = [
    "Result",
    "TestEnv",
]
