#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = []
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                requirements.append(line)
        return requirements

setup(
    name="lightime",
    version="1.0.0",
    author="Lightime Team",
    author_email="lightime@example.com",
    description="Lightweight Pomodoro timer for Linux desktops",
    long_description=read_readme() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/lightime/lightime",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Utilities",
        "Environment :: X11 Desktop Applications",
        "Environment :: Wayland",
    ],
    python_requires=">=3.11",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest-xvfb>=3.0.0",
            "python-dbusmock>=0.31.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lightime=lightime.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "lightime": [
            "config/*.yaml",
        ],
    },
    zip_safe=False,
    keywords="pomodoro timer productivity linux gtk",
    project_urls={
        "Bug Reports": "https://github.com/lightime/lightime/issues",
        "Source": "https://github.com/lightime/lightime",
        "Documentation": "https://github.com/lightime/lightime/wiki",
    },
)