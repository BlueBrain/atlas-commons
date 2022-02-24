#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="atlas-commons",
    author="Blue Brain Project, EPFL",
    description="Library containing common functions to build atlases",
    url="https://github.com/BlueBrain/atlas-commons",
    download_url="https://github.com/BlueBrain/atlas-commons",
    license='Apache-2',
    python_requires=">=3.7.0",
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

    use_scm_version={
        "local_scheme": "no-local-version",
        },
    setup_requires=[
        'setuptools_scm',
    ],

    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
