"""Race submission wrapper for the canonical Stage 1.5 implementation."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "contracts"))
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "shared_utils"))
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "extraction"))

from doramagic_extraction.stage15_agentic import *  # noqa: F401,F403,E402
