#!/usr/bin/env python

import importlib

from setuptools import find_packages, setup

VERSION = importlib.import_module("atlas_commons.version").__version__

setup(
    name="atlas-commons",
    author="BlueBrain NSE",
    author_email="bbp-ou-nse@groupes.epfl.ch",
    version=VERSION,
    description="Library containing common functions to build atlases",
    url="https://bbpgitlab.epfl.ch/nse/atlas-commons",
    download_url="git@bbpgitlab.epfl.ch:nse/atlas-commons.git",
    license="BBP-internal-confidential",
    python_requires=">=3.6.0",
    install_requires=[
        "click>=7.0",
        "numpy>=1.15.0",
        "voxcell>=3.0.0",
    ],
    extras_require={
        "tests": [
            "pytest>=4.4.0",
        ],
    },
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
