#!/usr/bin/env python3
"""
Setup script for IPv9 Scanner
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="ipv9tool",
    version="1.0.0",
    description="IPv9 Scanner - Exploration and Discovery Tool for China's Decimal Network",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="IPv9 Research Team",
    author_email="research@example.com",
    url="https://github.com/yourusername/ipv9-scanner",
    license="MIT",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'ipv9tool=ipv9tool.cli.commands:main',
            'ipv9scan=ipv9tool.tui.main:main',
            'ipv9api=ipv9tool.api.server:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet",
        "Topic :: System :: Networking",
        "Topic :: Security",
    ],
    keywords="ipv9 dns scanning network security china decimal-network",
    project_urls={
        "Documentation": "https://github.com/yourusername/ipv9-scanner/blob/main/docs/GUIDE.md",
        "Source": "https://github.com/yourusername/ipv9-scanner",
        "Bug Reports": "https://github.com/yourusername/ipv9-scanner/issues",
    },
    include_package_data=True,
    zip_safe=False,
)
