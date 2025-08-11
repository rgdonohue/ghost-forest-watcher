"""
Smoke test to ensure streamlit pages module imports and exposes expected callables.
"""

def test_streamlit_pages_imports():
    from ghost_forest_watcher.src import streamlit_pages as sp

    assert hasattr(sp, "show_map_page")
    assert hasattr(sp, "show_analysis_page")
    assert hasattr(sp, "show_explorer_page")
    assert hasattr(sp, "show_export_page")
    assert hasattr(sp, "show_about_page")
