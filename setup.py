"""
ThreadSafe JSON Dict - setup.py
"""

from setuptools import setup, find_packages
from pathlib import Path

# README.mdから長い説明を読み込み
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="threadsafe-json-dict",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="diskcacheを使用したスレッドセーフなJSON保存機能付き辞書",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/threadsafe-json-dict",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: System :: Archiving",
    ],
    python_requires=">=3.7",
    install_requires=[
        "diskcache>=5.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    keywords="json dict cache threadsafe persistent storage",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/threadsafe-json-dict/issues",
        "Source": "https://github.com/yourusername/threadsafe-json-dict",
    },
) 