"""
Load design content from .env — raises clearly if a required key is missing.
Import this instead of reading os.environ directly in design scripts.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


def _require(key: str) -> str:
    val = os.environ.get(key, "").strip()
    if not val:
        raise RuntimeError(f"Missing required .env key: {key}")
    return val


# PHRASE_A — 4-word grid/kufic phrase
PHRASE_A_W1 = _require("PHRASE_A_W1")
PHRASE_A_W2 = _require("PHRASE_A_W2")
PHRASE_A_W3 = _require("PHRASE_A_W3")
PHRASE_A_W4 = _require("PHRASE_A_W4")

# PHRASE_B — calligraphic/water phrase variants
PHRASE_B_SINGLE  = _require("PHRASE_B_SINGLE")
PHRASE_B_VEC_L1  = _require("PHRASE_B_VEC_L1")
PHRASE_B_VEC_L2  = _require("PHRASE_B_VEC_L2")
PHRASE_B_VEC_L3  = _require("PHRASE_B_VEC_L3")
PHRASE_B_TAK_L1  = _require("PHRASE_B_TAK_L1")
PHRASE_B_TAK_L2  = _require("PHRASE_B_TAK_L2")
PHRASE_B_TAK_L3  = _require("PHRASE_B_TAK_L3")

# LABEL_C / NUMBER_C — jersey design
LABEL_C  = _require("LABEL_C")
NUMBER_C  = _require("NUMBER_C")

# LATIN_D — Latin wordmark
LATIN_D  = _require("LATIN_D")
