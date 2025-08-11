# Repository Guidelines

## Project Structure & Module Organization
- Source: `ghost_forest_watcher/` (Streamlit app in `app.py` and helpers in `src/`)
  - Key modules: `src/data_manager.py`, `src/sam_processor.py`, `src/scalable_processor.py`, `src/streamlit_pages.py`
- Entrypoints: `main.py` (CLI wrapper), `scripts/run_app.py` (launcher)
- Tests: `tests/` (unit + integration)
- Assets/data: `data/`, `models/` (not versioned), results in `outputs/`
- Docs and ops: `docs/`, `.github/`, `Makefile`, `pyproject.toml`

## Build, Test, and Development Commands
- `make install`: Install runtime deps from `requirements.txt`.
- `make dev-install`: Editable install with dev extras (`pip install -e .[dev]`).
- `make run` / `python main.py`: Launch the app. Use `--safe` to skip AI models.
- `streamlit run ghost_forest_watcher/app.py`: Direct Streamlit entry.
- `make test` / `pytest -q`: Run unit tests. `pytest -m "not integration"` to skip integration.
- `pytest -m integration`: Run integration tests (enable if needed).
- `make lint`: Run `flake8` and `pylint` (limited warnings).
- `make format` / `make check-format`: Apply/check `black` and `isort`.
- `make build`: Build sdist/wheel. `make clean`: Remove artifacts.

## Coding Style & Naming Conventions
- Python 3.11, `black` line length 100; `isort` profile `black`.
- Indentation 4 spaces; UTF-8; one public class/function per concern.
- Naming: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE`.
- Run `pre-commit install` to enable `black`, `isort`, `flake8`, and safety hooks.

## Testing Guidelines
- Framework: `pytest` (tests can use `unittest`). Files: `tests/test_*.py`.
- Mark longer browser/web flows with `@pytest.mark.integration`; keep unit tests fast.
- Recommended: `pytest --cov=ghost_forest_watcher` for coverage (if `pytest-cov` installed).

## Commit & Pull Request Guidelines
- Commit style mirrors history: prefixes like `Fix:`, `Docs:`, `CI:`, `Build:`, `Tests:`, `Chore:`, `Ops:`; imperative, concise subject (<72 chars). Emojis allowed but optional.
- Before PR: `make check-format && make lint && make test`.
- PRs include: clear description, linked issues, screenshots/GIFs for UI, and notes on data/model requirements.

## Security & Configuration Tips
- Large data and SAM weights aren’t tracked; avoid committing binaries. `.gitignore` is configured.
- Useful env vars: `GF_SYNTHETIC_FALLBACK=1` (demo data), `GFW_BIND_ADDRESS=localhost` (server bind).
- Secrets: never commit keys; pre-commit includes `detect-private-key`.
