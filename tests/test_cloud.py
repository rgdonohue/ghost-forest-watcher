"""
Smoke tests for cloud pipeline that do not require earthengine-api.
This test injects a minimal stub 'ee' module so the cloud module can import.
"""
import sys
from types import SimpleNamespace


def _inject_ee_stub():
    # Minimal 'ee' stub for import-time and type annotations
    ee_stub = SimpleNamespace(Geometry=object)
    sys.modules.setdefault("ee", ee_stub)


def test_cloud_pipeline_smoke_without_ee():
    _inject_ee_stub()
    from ghost_forest_watcher.src.cloud_pipeline import CloudOptimizedPipeline, FireBoundary

    # Instantiate without initializing Earth Engine
    pipeline = CloudOptimizedPipeline(skip_ee_init=True)

    # Create a minimal FireBoundary; geometry is not used by estimate_processing_resources
    fb = FireBoundary(
        name="Test Fire",
        year=2020,
        geometry=object(),
        total_area_ha=12345.0,
        fire_start_date="2020-01-01",
        fire_end_date="2020-02-01",
    )

    resources = pipeline.estimate_processing_resources(fb)
    # Basic shape checks
    assert resources["fire_name"] == "Test Fire"
    assert "area_km2" in resources
    assert "estimated_output_size_gb" in resources
    assert "estimated_processing_time_minutes" in resources
