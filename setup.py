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
            "ghost-forest-watcher=scripts.run_app:main",
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