"""
Setup configuration for Ghost Forest Watcher
"""
from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ghost-forest-watcher",
    version="3.0.0",
    author="Ghost Forest Watcher Team",
    author_email="contact@ghostforestwatcher.com",
    description="AI-Powered Forest Recovery Monitoring System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ghost-forest-watcher",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/ghost-forest-watcher/issues",
        "Documentation": "https://github.com/yourusername/ghost-forest-watcher#readme",
        "Source": "https://github.com/yourusername/ghost-forest-watcher",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "core": [
            "streamlit==1.32.2",
            "streamlit-folium==0.20.0",
            "folium==0.15.1",
            "geopandas==0.14.3",
            "duckdb==0.10.2",
            "rasterio==1.3.9",
            "plotly==5.22.0",
            "numpy==1.26.4",
            "pandas==2.2.2",
            "matplotlib==3.8.3",
            "scikit-image==0.22.0",
            "scikit-learn==1.4.2",
            "pillow==10.3.0",
            "requests==2.31.0",
        ],
        "sam": [
            "torch==2.2.2",
            "torchvision==0.17.2",
            "opencv-python==4.9.0.80",
            "segment-anything @ git+https://github.com/facebookresearch/segment-anything.git@01ec64",
        ],
        "gee": [
            "earthengine-api==0.1.395",
            "google-api-python-client==2.125.0",
        ],
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
            "isort>=5.0",
        ],
        "docs": [
            "sphinx>=5.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ghost-forest-watcher=scripts.run_app:run_streamlit",
        ],
    },
    include_package_data=True,
    package_data={
        "ghost_forest_watcher": [
            "src/*.py",
            "*.py",
        ],
    },
    keywords=[
        "forest monitoring",
        "remote sensing",
        "AI",
        "satellite imagery",
        "environmental science",
        "GIS",
        "streamlit",
        "computer vision"
    ],
) 