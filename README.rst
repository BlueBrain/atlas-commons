Overview
=========

This project contains the common functions used in the context of brain atlases.

Installation
============

.. code-block:: bash

    git clone https://github.com/BlueBrain/atlas-commons
    cd atlas-commons
    pip install -e .


Instructions for developers
===========================

Run the following commands before submitting your code for review:

.. code-block:: bash

    cd atlas-commons
    isort -l 100 --profile black atlas_commons tests setup.py
    black -l 100 atlas_commons tests setup.py

These formatting operations will help you pass the linting check `testenv:lint` defined in `tox.ini`.

Acknowledgements
================

The development of this software was supported by funding to the Blue Brain Project, a research center of the École polytechnique fédérale de Lausanne (EPFL), from the Swiss government’s ETH Board of the Swiss Federal Institutes of Technology.

For license and authors, see LICENSE.txt and AUTHORS.txt respectively.

Copyright © 2022 Blue Brain Project/EPFL
