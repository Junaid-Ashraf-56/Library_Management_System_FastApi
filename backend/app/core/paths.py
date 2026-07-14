import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
GENERATED_DIR = Path(
    os.getenv("GENERATED_DIR", PROJECT_ROOT / "generated")
).resolve()
RECEIPTS_DIR = GENERATED_DIR / "receipts"
