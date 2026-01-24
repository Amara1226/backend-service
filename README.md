# Project Aether (AQMS Backend)

A configuration-driven Air Quality Monitoring System backend for the Netherlands built with FastAPI, pandas, and Plotly using Clean Architecture + dependency injection.

## Quickstart

```bash
pip install -r requirements.txt

./run.sh
```

Open:
- Welcome page: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`

## Tests

```bash
python -m pytest -q
```

## Architecture

- `domain/` plain Python domain models (no Pydantic validation)
- `dto/` Pydantic models for API boundary validation
- `services/` business logic + pandas cleaning
- `persistence/` JSON storage and CSV repository
- `visualization/` Plotly HTML creators
- `dependencies.py` DI providers + init/reset
- `main.py` routes only (thin controllers)
