
# Package initialization
for dir in \
  src/pipeforge \
  src/pipeforge/generator \
  src/pipeforge/renderer \
  src/pipeforge/questions \
  src/pipeforge/oracle \
  src/pipeforge/validation \
  src/pipeforge/twins \
  src/pipeforge/evaluation \
  src/pipeforge/reporting
do
  echo '"""PipeForge module."""' > "$dir/__init__.py"
done

cat > src/pipeforge/__init__.py <<'EOF'
"""PipeForge package."""

__version__ = "0.1.0"
EOF

cat > src/pipeforge/config.py <<'EOF'
"""Central project configuration."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = PROJECT_ROOT / "datasets" / "generated"
REPORT_DIR = PROJECT_ROOT / "reports"
SCHEMA_DIR = PROJECT_ROOT / "schemas"

PROJECT_NAME = "PipeForge"
PRODUCT_NAME = "PipeSight Ops"
EOF

# Python project configuration
cat > pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=75", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "pipeforge"
version = "0.1.0"
description = "Visual benchmark factory for enterprise data-pipeline incident reasoning."
readme = "README.md"
requires-python = ">=3.14"
dependencies = [
    "networkx>=3.7",
    "matplotlib>=3.10",
    "pandas>=2.3",
    "pydantic>=2.10",
    "Pillow>=11.0",
    "streamlit>=1.50",
    "python-dotenv>=1.0",
    "jsonschema>=4.23"
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3",
    "pytest-cov>=6.0",
    "ruff>=0.11"
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-ra"

[tool.ruff]
line-length = 100
target-version = "py314"
src = ["src", "tests"

]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
EOF

# Requirements
cat > requirements.txt <<'EOF'
-e .[dev]
EOF

# Streamlit application
cat > app/streamlit_app.py <<'EOF'
import streamlit as st

from pipeforge import __version__
from pipeforge.config import PRODUCT_NAME

st.set_page_config(
    page_title=PRODUCT_NAME,
    page_icon="🔬",
    layout="wide",
)

st.title("PipeForge")
st.subheader(PRODUCT_NAME)

st.caption(
    f"Visual AI Benchmarking for Enterprise Data Operations · v{__version__}"
)

st.info(
    "The benchmark factory is under construction. "
    "Our first milestone is deterministic incident generation and validation."
)

col1, col2, col3 = st.columns(3)

col1.metric("Incident categories", "4", "Planned")
col2.metric("Pipeline topologies", "3", "Planned")
col3.metric("Benchmark tasks", "0", "Not generated yet")

st.markdown("### Development milestones")
st.markdown(
    """
    - [ ] Scenario generation
    - [ ] Incident board rendering
    - [ ] Question and ground-truth generation
    - [ ] Independent validation
    - [ ] Incident Twin Challenge
    - [ ] Multimodal model evaluation
    """
)
EOF

# Smoke tests
cat > tests/test_smoke.py <<'EOF'
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
EOF

# README
cat > README.md <<'EOF'
# PipeForge

**Product:** PipeSight Ops

**Tagline:** We don't just test what AI sees. We test how AI reasons.

PipeForge is a reproducible visual benchmark factory for evaluating
multimodal AI reasoning over enterprise data-pipeline incidents.

## Core capabilities

- Deterministic incident scenario generation
- Visual pipeline incident boards
- Question and ground-truth generation
- Independent task validation
- Causal, evidence-removal and distractor twins
- Multimodal model evaluation and reporting

## Development setup

Requires Python 3.14+.

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Run tests

```bash
pytest -v
```

## Launch the prototype

```bash
streamlit run app/streamlit_app.py
```
EOF

# Environment template
cat > .env.example <<'EOF'
# Never commit real API keys.
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
EOF

# Git ignore
cat > .gitignore <<'EOF'
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/
.env
.streamlit/secrets.toml
datasets/generated/*
!datasets/generated/.gitkeep
reports/*
!reports/.gitkeep
.DS_Store
Thumbs.db
EOF

touch datasets/generated/.gitkeep reports/.gitkeep

# GitHub Actions
cat > .github/workflows/tests.yml <<'EOF'
name: PipeForge tests

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.14"
      - run: python -m pip install --upgrade pip
      - run: pip install -e ".[dev]"
      - run: pytest
      - run: ruff check .
EOF

echo "PipeForge project files created successfully."
