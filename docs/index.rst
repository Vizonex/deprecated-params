.. deprecated-params documentation master file, created by
   sphinx-quickstart on Tue Aug 12 16:13:23 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

deprecated-params documentation
===============================

Based off python's `warnings.deprecated(...)` wrapper `PEP 702 <https://peps.python.org/pep-0702/>`_

**deprecated-params** was made for solving the problems of warning users that certain parameters will
not be used anymore and that better ones exist. The library's intent is to be lazy yet readable,
tiny, easy to use & disposable later from any python library as it's aim is to be used temporarily until no longer required. 
Although libraries may have similar characteristics to this one, it was my goal to give a simplsitic package name with a simplsitic 
interface meant to be something small and easy to maintain over longer periods of time and hopes to be maintainable for many 
years to come. I have used it with my other pypi packages that I maintain already or it stilly currently has this library it inplace.
**deprecated-params** should retain typehinting at all-times and should be able to retain type typehints of 
anything you can wrap to any function or class under the sun including 
functions like ``__init__``, ``__init_subclass__`` & ``__new__`` all of which will retain Parameter data with ides 
such as **Visual-Studio-Code**, **PyCharm** and many more.


Installation
------------

.. code-block:: bash

   $ pip install deprecated-params

The library requires Python 3.9 or newer.

API
---

.. automodule:: deprecated_params
    :members:
    :special-members: __call__, __init__


.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. _GitHub: https://github.com/Vizonex/deprecated-params

