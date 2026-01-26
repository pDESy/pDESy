.. pDESy documentation master file, created by
   sphinx-quickstart on Thu Jun  4 15:37:26 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pDESy: Discrete Time-Event Simulation in Python
================================================

pDESy is a Python package for Discrete Time-Event Simulation (DES).
It aims to be the fundamental high-level building block for practical, real-world engineering project management by using DES and other DES modeling tools.
pDESy focuses on Discrete Time-Event Simulation and does not include visual modeling tools.

.. image:: https://github.com/pDESy/pDESy/actions/workflows/test.yaml/badge.svg

.. image:: https://codecov.io/gh/pDESy/pDESy/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/pDESy/pDESy

.. image:: https://badge.fury.io/py/pDESy.svg
  :target: https://badge.fury.io/py/pDESy


Install
--------

Install the latest released version from the Python Package Index (PyPI):

.. code-block:: bash

   pip install pDESy
   # pip install git+ssh://git@github.com/pDESy/pDESy.git # INSTALL FROM GITHUB

Optional Dependencies
----------------------

Visualization (matplotlib, plotly): If you want to use visualization features
(Gantt charts, network diagrams), install with:

.. code-block:: bash

   pip install pDESy[vis]

or install the visualization libraries separately (kaleido is required for
static image export in plotly):

.. code-block:: bash

   pip install matplotlib plotly networkx kaleido

Note
-----

Starting from v0.8.0, visualization dependencies (matplotlib, plotly, kaleido,
networkx) are optional to avoid mandatory dependency on kaleido, which requires
Chrome for v1.0.0+. This keeps the core pDESy package lightweight for CI/CD and
production environments.

Documentation
--------------

API documentation is available at:
https://pDESy.github.io/pDESy/index.html

License
--------

MIT License: https://github.com/pDESy/pDESy/blob/master/LICENSE


How to use pDESy?
------------------

Example code of pDESy is `here <https://gist.github.com/taiga4112/278629844a14f7a61aa48763e3ceaa19>`_ .

If you want to implement more complex models for describing real engineering projects, you can create new models by inheriting the base models.

Background
-----------

pDESy is developed as part of the next-generation DES tool `pDES <https://github.com/pDESy/pDES>`_.

Citation
---------

Mitsuyuki, T., & Okubo, Y. (2024). pDESy: A Python Package for Discrete Time-Event Simulation to Engineering Project. Software Impacts, 19(100621). https://doi.org/10.1016/j.simpa.2024.100621

.. code-block:: bibtex

    @article{Mitsuyuki_pDESy_A_Python_2024,
        author = {Mitsuyuki, Taiga and Okubo, Yui},
        doi = {10.1016/j.simpa.2024.100621},
        journal = {Software Impacts},
        month = mar,
        number = {100621},
        title = {pDESy: A Python Package for Discrete Time-Event Simulation to Engineering Project},
        volume = {19},
        year = {2024}
    }


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   pDESy


Indices and tables
-------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
