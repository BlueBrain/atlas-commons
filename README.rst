Overview
=========

This project contains the common functions used in the context of brain atlases.
It is used by the projects:

* https://github.com/BlueBrain/atlas-densities
* https://github.com/BlueBrain/atlas-direction-vectors
* https://github.com/BlueBrain/atlas-placement-hints
* https://github.com/BlueBrain/atlas-splitter

Installation
============

.. code-block:: bash

    git clone https://github.com/BlueBrain/atlas-commons
    cd atlas-commons
    pip install -e .

Examples
========

Create a mask for the region defined by `query`
-----------------------------------------------

.. code-block:: python

    from atlas_commons import utils
    from voxcell.nexus.voxelbrain import Atlas

    # see voxcell documentation for more more information
    atlas = Atlas.open('.')
    annotation = atlas.load_data('brain_regions')
    region_map = atlas.load_region_map()

    region = {
        "query": "Isocortex",
        "attribute": "acronym",
        "with_descendants": True,
    }
    mask = utils.query_region_mask(region, annotation, region_map)

Split input 3D volume into two halves using the middle plane orthogonal to the z-axis
-------------------------------------------------------------------------------------

.. code-block:: python

    from atlas_commons import utils
    import numpy as np

    volume = np.array(
        [
            [[0, 1, 2], [2, 3, 4]],
            [[4, 5, 6], [7, 8, 9]],
        ],
        dtype=np.int64,
    )
    halves = utils.split_into_halves(volume)


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
