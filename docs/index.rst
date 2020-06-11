.. pDESy documentation master file, created by
   sphinx-quickstart on Thu Jun  4 15:37:26 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pDESy: Discrete-Event Simulator in Python
==========================================

pDESy is a Python package of Discrete-Event Simulator (DES).
It aims to be the fundamental high-level building block for doing practical, real world engineering project management by using DES and other DES modeling tools.
pDESy has only the function of discrete-event simulation, does not include the function of visual modeling.

.. image:: https://github.com/mitsuyukiLab/pDESy/workflows/test/badge.svg

.. image:: https://codecov.io/gh/mitsuyukiLab/pDESy/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/mitsuyukiLab/pDESy


Install
--------

.. code-block::

   pip install git+https://git@github.com/mitsuyukiLab/pDESy.git


If you are trouble to install pDESy, please try the following code.

.. code-block::

   pip uninstall -y pDESy 
   pip uninstall -y typing #https://github.com/ethereum/eth-abi/issues/131
   pip install -U poetry
   pip install git+https://git@github.com/mitsuyukiLab/pDESy.git


How to use pDESy?
------------------

Example code of pDESy is `here <https://nbviewer.jupyter.org/gist/taiga4112/5af01bc433d204d676a0ef3e95062b5f>`_ .

We will introduce case study of academic research project by using pDESy soon...

If you want to implement more complex models for describling a real engineering project, you can create new model by inheriting base models.


.. toctree::
   :maxdepth: 4
   :caption: Contents:

   pDESy


Indices and tables
-------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
