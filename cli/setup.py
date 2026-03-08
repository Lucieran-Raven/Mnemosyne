# Mnemosyne CLI
# Automation tool for managing Mnemosyne infrastructure

from setuptools import setup, find_packages

setup(
    name="mnemosyne-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "requests>=2.28.0",
        "pyyaml>=6.0",
        "google-cloud-run>=1.0.0",
        "google-cloud-tasks>=2.0.0",
        "google-cloud-logging>=3.0.0",
        "colorama>=0.4.6",
        "rich>=13.0.0",
        "tabulate>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "mnemosyne=mnemosyne_cli.cli:main",
        ],
    },
    python_requires=">=3.9",
    author="Mnemosyne Team",
    description="CLI for managing Mnemosyne AI Memory Layer",
)
