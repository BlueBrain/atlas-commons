Overview
=========

This project contains the common functions used in the context of brain atlases.

Installation
============

.. code-block:: bash

    git clone git@bbpgitlab.epfl.ch:nse/atlas-commons.git
    cd atlas-commons
    pip install -e .


Instructions for developers
===========================

Run the following commands before submitting your code for review:

.. code-block:: bash

    cd atlas-commons
    isort -l 100 --profile black atlas_commons tests setup.py
    black -l 100 atlas_commons tests setup.py

These formatting operations will help you pass the linting check `testenv:lint` defined in
`tox.ini`.
