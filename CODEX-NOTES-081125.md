# Ghost Forest Watcher - Code Review Notes
*August 11, 2025*

## Executive Summary

**Strong concept with timely value**: Post-wildfire forest recovery monitoring backed by NDVI and SAM, plus a Streamlit UI.

**Codebase status**: Reasonably organized with helpful docs, but several claims in README oversell current maturity.

**Implementation**: Core implementation is present; however, there are key functional gaps (SAM handling, test mismatches, cloud pipeline return values) and repo hygiene issues (vendored venv, large model in repo).

**Feasibility**: Feasible as a niche demo and baseline research tool; production claims (stability, scaling guarantees) are not yet supported by tests or architecture.

## Project Value

- **Environmental impact**: Visualizes and communicates vegetation recovery; aligns with climate and land management needs
- **Technical interest**: Combines remote sensing, basic geospatial processing, and a modern web UI
- **Differentiation**: Including "scalable processing" and a cloud pipeline design (GEE) is attractive, though presently partial

## Architecture & Quality

### Structure
- Clean package layout (`ghost_forest_watcher/app.py` + `src/` helpers)
- CLI wrapper (`main.py`) and Makefile conform to conventions

### Documentation
- README and docs are polished and descriptive with concrete workflows
- **Warning**: Several badges/claims look aspirational (placeholders and "Stable/100% success" language)

### Testing
- Two test modules only; some tests do not align with current code interfaces
- CI workflow exists and is sound on paper

### Code Style
- Mostly consistent docstrings and readable functions
- Uses Streamlit caching and separation of Streamlit pages into `src/streamlit_pages.py`

## Key Functional Components

### `src/data_manager.py`
- Caching, GeoTIFF loading, stats, Folium overlays, export helpers
- Includes synthetic data fallback via `GF_SYNTHETIC_FALLBACK=1`
- Generally solid, but tightly couples to Streamlit (e.g., `st.error`) which complicates headless use

### `src/sam_processor.py`
Provides NDVI-to-RGB, prompt point generation, SAM segmentation, health classification, visualization.

**Important caveats:**
- Uses SAM on a color-mapped NDVI image. This is unconventional; SAM isn't trained for semantic classification of NDVI-derived imagery. Expect unpredictable masks and fragile results.
- If `segment_anything` is not installed, `SAM_AVAILABLE=False`, but `load_model()` still references `sam_model_registry` unguarded (will error). Data manager catches exceptions, but it means the "AI" path is effectively disabled without the dependency.

### `src/scalable_processor.py`
Tiling and multiprocessing pipeline with per-process SAM initialization.

**Thoughtful API, but:**
- Heavy SAM initialization in each child process is expensive; GPU support across processes is non-trivial
- File ends mid-example; core class methods are present, but the example `main()` is truncated

### `src/cloud_pipeline.py`
GEE-based processing design reads well; however:

**Issues:**
- `process_fire_area_cloud()` returns a dict without `task_id` or `fire_name`, but `main()` prints them — will error at runtime
- GEE auth and usage included, but these flows are untested in repo; several values are placeholders

### `app.py` and `src/streamlit_pages.py`
- Pages render, caching is applied, and UI is cohesive
- **Issue**: `app.py` contains duplicated "_local_*" page functions, diverging from the extracted `streamlit_pages.py` and increasing maintenance risk

## Tests & CI Reality

### Unit Tests
`tests/test_app.py` includes mismatches:

- `GhostForestDataManager.get_vegetation_health_stats()` expects a dict with a `statistics` key and returns a normalized dict. Test passes raw mask arrays and expects keys like `healthy` in the returned dict. This will not pass as written.
- Streamlit `set_page_config` is patched and asserted on import; this is fragile but acceptable.

### Integration Tests
`tests/test_web.py` requires a running Streamlit server; guarded by `GF_RUN_INTEGRATION=1`. Reasonable design.

### CI
Workflow file is in place and modern. But with current test mismatches and optional heavy deps (SAM, GEE), unit stage could fail unless the code or tests are aligned and extras are mocked/optionalized.

## Feasibility

### Demo Feasibility
**High**. Safe mode and synthetic fallback enable a smooth demo experience without heavy ML deps.

### SAM Feasibility
**Moderate**. Running SAM headless (CPU) will be slow; requiring model weights and segment-anything install. Using SAM on colorized NDVI is not best-practice for vegetation health and may not be reliable.

### Scaling
**Conceptually OK** (tiling + multiprocessing). Practically, SAM per-process load is expensive; memory and GPU limits require more careful design (model server, shared memory, batching).

### Cloud
**Concept plausible** with GEE; but the provided code is not production-complete.

## Critical Issues

### SAM Handling
- `ForestSAMProcessor.load_model()` references `sam_model_registry` even when `segment_anything` import failed; this will raise errors
- **File**: `ghost_forest_watcher/src/sam_processor.py`
- **Impact**: Data manager swallows this and returns `{}`, so app will degrade — but "AI analysis" won't work unless the package is installed and reachable

### Cloud Pipeline Return Mismatch
- `process_fire_area_cloud()` returns no `task_id`/`fire_name`, but `main()` prints them. Will raise KeyError
- **File**: `ghost_forest_watcher/src/cloud_pipeline.py`

### Test Misalignment
- `get_vegetation_health_stats()` contract vs tests diverge; tests expect a different shape
- **File**: `tests/test_app.py` vs `src/data_manager.py`

### Repository Hygiene/Security
- Vendored `venv/` committed to repo
- Large model file tracked: `models/sam_vit_b.pth` contradicts README guidance to avoid committing weights
- `ghost_forest_watcher.egg-info/` and `.DS_Store` committed; unnecessary

### Overstated Claims
- README states "Stable," "100% success," "Automated tests pass" and a CI badge referencing `yourusername` which is a placeholder
- **Impact**: This can damage credibility if not actually true

## Moderate Issues

### Duplicated Page Implementations
- `_local_show_*` functions in `app.py` overlap with `src/streamlit_pages.py`; risk of drift and bugs

### Robustness
- Many UI code paths assume present files and ideal NDVI; more robust error messages and fallbacks would help

### Coupling to Streamlit
- Data manager logs via Streamlit functions; consider separating domain logic from UI for better testing

### Performance Assumptions
- Tiling + multiprocessing with SAM doesn't address the heavy model load cost; may need lazy init and reuse, or a microservice model inference approach

## What's Working Well

- Clean organization and thoughtful UX with multi-page Streamlit
- Caching and synthetic fallback to demo without data
- Tiling design and GEE pipeline are clearly documented with reasonable interfaces
- Makefile, setup, pyproject, and CI workflow exist and are coherent

## Recommended Next Steps

### Fix Critical Correctness
- **SAM Guards**: Guard all SAM references behind `SAM_AVAILABLE` and raise a clear error if missing; in `load_model()`, return early or raise informative exception when dependency is absent
- **Cloud Pipeline**: Add `task_id` and `fire_name` (and potentially task state polling info) to `process_fire_area_cloud()` return dict

### Align Tests and Code
- **Update Test**: Update `tests/test_app.py::test_get_vegetation_health_stats` to pass a classification dict with a `statistics` sub-dict (or adjust `get_vegetation_health_stats()` to accept raw masks and compute stats consistently)
- **SAM Testing**: Consider marking SAM-dependent tests to skip when SAM isn't installed; or mock SAM behavior

### Repository Hygiene
- **Remove**: `venv/`, `*.egg-info/`, `models/sam_vit_b.pth`, `.DS_Store` from git; add guardrails to `.gitignore`
- **Documentation**: Document how to fetch model weights out-of-band

### Clarify README
- **Replace**: Placeholder badges/links and tone down claims (e.g., "Stable" → "Beta")
- **Describe**: Safe-mode expectations and that AI features require additional setup

### Architectural Improvements
- **SAM Usage**: Consider alternative approaches (NDVI thresholding or supervised classifiers trained for vegetation health) or use SAM only with meaningful prompts on true-color imagery
- **Scaling**: Use a single model init per worker with a proper life-cycle and ensure GPU constraints are honored. Evaluate moving inference into a service to avoid multi-process GPU contention

### Add Missing Tests
- **Unit Tests**: For `scalable_processor._aggregate_tile_statistics()` and `calculate_optimal_tiling()`
- **Smoke Test**: For `cloud_pipeline.process_fire_area_cloud()` in skip-init mode (`skip_ee_init=True`) to validate return shapes

## Feasibility Outlook

- **Short term**: Fully feasible as a demo and educational tool with safe mode and synthetic data; light polish needed to avoid runtime surprises
- **Medium term**: Feasible to run SAM locally on small tiles, but results quality should be validated; consider pivoting to standard remote-sensing classification for credible metrics
- **Long term**: GEE pipeline can deliver real scalability; needs authentication, quotas management, and robust export orchestration

## Risk Summary

### High Risk
- Dependency brittleness around SAM
- Claims in docs vs actual robustness
- Repository hygiene with committed binaries/venv

### Medium Risk
- Test misalignment
- Cloud pipeline result mismatch
- Duplicated UI logic

### Low Risk
- Performance assumptions and metrics in README are illustrative but could be misinterpreted as measured

## Available Actions

If you want, I can:
- Patch the SAM guards and cloud pipeline return dict
- Align or update the failing test to the current contract
- Remove committed venv/model artifacts and tighten .gitignore
- Tone down and correct README claims and badges
