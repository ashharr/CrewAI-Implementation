#!/usr/bin/env python3
"""
Setup script for CrewAI Platform.

This provides traditional setuptools installation for users who prefer
pip install over UV package manager.
"""

from setuptools import setup, find_packages
import os
import re

# Read version from src/__init__.py
def get_version():
    version_file = os.path.join("src", "__init__.py")
    with open(version_file, "r", encoding="utf-8") as f:
        content = f.read()
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")

# Read long description from README
def get_long_description():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# Read requirements from requirements.txt
def get_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Development requirements
dev_requirements = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.7.0",
    "pre-commit>=3.5.0",
    "bandit>=1.7.5",
    "safety>=2.3.0",
]

# Documentation requirements
docs_requirements = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.4.0",
    "mkdocstrings[python]>=0.23.0",
]

# Monitoring requirements
monitoring_requirements = [
    "prometheus-client>=0.19.0",
    "grafana-api>=1.0.3",
]

setup(
    name="crewai-platform",
    version=get_version(),
    author="CrewAI Platform Contributors",
    author_email="contributors@crewai-platform.com",
    description="A comprehensive, extensible ecosystem for AI agent workflows",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/crewai-platform",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/crewai-platform/issues",
        "Source": "https://github.com/yourusername/crewai-platform",
        "Documentation": "https://crewai-platform.readthedocs.io/",
        "Discord": "https://discord.gg/crewai-platform",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business :: Groupware",
    ],
    python_requires=">=3.10",
    install_requires=get_requirements(),
    extras_require={
        "dev": dev_requirements,
        "docs": docs_requirements,
        "monitoring": monitoring_requirements,
        "all": dev_requirements + docs_requirements + monitoring_requirements,
    },
    entry_points={
        "console_scripts": [
            "crewai-platform=src.core.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yml", "*.yaml", "*.json", "*.md", "*.txt"],
    },
    zip_safe=False,
    keywords=[
        "ai", "agents", "automation", "workflow", "crewai", 
        "multi-agent", "orchestration", "llm", "chatgpt", "openai"
    ],
) 