"""Central project configuration."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = PROJECT_ROOT / "datasets" / "generated"
REPORT_DIR = PROJECT_ROOT / "reports"
SCHEMA_DIR = PROJECT_ROOT / "schemas"

PROJECT_NAME = "PipeForge"
PRODUCT_NAME = "PipeSight Ops"
