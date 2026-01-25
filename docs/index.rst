.. pDESy documentation master file, created by
   sphinx-quickstart on Thu Jun  4 15:37:26 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pDESy: Discrete-Event Simulator in Python
==========================================

pDESy is a Python package of Discrete-Event Simulator (DES).
It aims to be the fundamental high-level building block for doing practical, real world engineering project management by using DES and other DES modeling tools.
pDESy has only the function of discrete-event simulation, does not include the function of visual modeling.

.. image:: https://github.com/pDESy/pDESy/actions/workflows/test.yaml/badge.svg

.. image:: https://codecov.io/gh/pDESy/pDESy/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/pDESy/pDESy

.. image:: https://badge.fury.io/py/pDESy.svg
  :target: https://badge.fury.io/py/pDESy


Install
--------

.. code-block:: bash

   pip install pDESy
   # pip install git+ssh://git@github.com/pDESy/pDESy.git # INSTALL FROM GITHUB

Optional Dependencies
----------------------

If you want to use visualization features (Gantt charts, network diagrams),
install with the optional extra:

.. code-block:: bash

   pip install pDESy[vis]

Or install the visualization libraries separately:

.. code-block:: bash

   pip install matplotlib plotly networkx kaleido

Note
-----

Starting from v0.8.0, visualization dependencies (matplotlib, plotly, networkx, kaleido)
are optional to keep the core package lightweight. This avoids requiring Chrome
for kaleido v1.0.0+ in environments where visualization is not needed.

Documentation
--------------

API Documentation is available at:
https://pDESy.github.io/pDESy/index.html

License
--------

MIT License: https://github.com/pDESy/pDESy/blob/master/LICENSE


How to use pDESy?
------------------

Example code of pDESy is `here <https://gist.github.com/taiga4112/278629844a14f7a61aa48763e3ceaa19>`_ .

If you want to implement more complex models for describling a real engineering project, you can create new model by inheriting base models.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   pDESy


Indices and tables
-------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
