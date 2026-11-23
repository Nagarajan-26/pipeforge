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
