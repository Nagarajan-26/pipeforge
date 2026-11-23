from pipeforge import __version__
from pipeforge.config import (
    DATASET_DIR,
    PRODUCT_NAME,
    PROJECT_NAME,
    REPORT_DIR,
)


def test_package_version_exists():
    assert __version__ == "0.1.0"


def test_project_identity():
    assert PROJECT_NAME == "PipeForge"
    assert PRODUCT_NAME == "PipeSight Ops"


def test_project_directories_are_configured():
    assert DATASET_DIR.name == "generated"
    assert REPORT_DIR.name == "reports"
