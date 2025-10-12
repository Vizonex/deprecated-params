.. deprecated-params documentation master file, created by
   sphinx-quickstart on Tue Aug 12 16:13:23 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

deprecated-params documentation
===============================

Based off python's `warnings.deprecated(...)` wrapper `PEP 702 <https://peps.python.org/pep-0702/>`_

**deprecated-params** was made for solving the problems of warning users that certain parameters will
not be used anymore and that better ones exist. **deprecated-params** was made with the intent of being.
Tiny, easy to use & disposable later from any python library. Although libraries that may be similar to this 
one do exist it was my goal to give a simplsitic name for install with a simplsitic interface. 
3 of my own libraries either have already used it and been removed after deprecation or currently have it inplace.
**deprecated-params** should retain typehinting at all-times and should be able to retain type typehints of 
anything you can wrap to a function under the sun including 
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

