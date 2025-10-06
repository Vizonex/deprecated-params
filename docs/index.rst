.. deprecated-params documentation master file, created by
   sphinx-quickstart on Tue Aug 12 16:13:23 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

deprecated-params documentation
===============================

Based off python's `warnings.deprecated(...)` wrapper `PEP 702 <https://peps.python.org/pep-0702/>`_

**deprecated-params** was made for solving the problems of warning users that certain parameters will
not be used anymore and that better ones exist. **deprecated-params** was made with the intent of being,
tiny, easy to use & disposable later from any python library. Although libraries that may be similar to this 
one that do exist it was my goal to give a simplsitic name for install with a simplsitic interface and fast performance. 
many of my own libraries that are maintained by me either have already used it and been removed 
after deprecation or currently have it inplace. **deprecated-params** should retain typehinting at all-times and 
should be able to retain typehints of anything you can wrap to a function under the sun including 
functions like ``__init__``, ``__init_subclass__`` & ``__new__`` all of which will retain Parameter data 
with ides & code editors such as **Visual-Studio-Code** with the pyright extension, **PyCharm** and many more.

Examples of libraries that currently used or dropped deprecated-params:

- `cyares <https://github.com/Vizonex/cyares>`_ DNS Resolver replacement for pycares without resorting to weird cleanups 
    and has aggressive systems inplace to prevent unwanted or new vulnerabilities. It includes trio and asyncio wrappers as well as an experimental 
    aiohttp extension that is injectable.

- `aiothreading <https://github.com/Vizonex/aiothreading>`_ The Heart where deprecated-params originated off of. It is currently still in use.

- `aiocallback <https://github.com/Vizonex/aiocallback>`_ Another project that sparked deprecated-params's seperation from aiothreading. It was dropped
    a while ago when certain arguments were no longer in use...


Addintionaly for a little bit of additional speed it can be compiled in Cython simillar to how `yarl <https://yarl.aio-libs.org/en/latest/>`_
and `propcache <https://propcache.aio-libs.org/en/latest/>`_ both work, one of them I've contributed my work to (propcache).



Installation
------------

.. code-block:: bash

   $ pip install deprecated-params

The library requires Python 3.9 or newer.

API
---

.. class::MissingKeywordsError()
      Raised when Missing a keyword for an argument

.. class::InvalidParametersError()
      Raised when Parameters were positional arguments without defaults or keyword arguments


.. class:: deprecated_params(params: Sequence[str] | Iterable[str] | str, message: str | Mapping[str, str] = "is deprecated", /, *, default_message: str | None = None, category: type[Warning] | None = DeprecationWarning, stacklevel: int = 3, display_kw: bool = True, removed_in: str | Sequence[int] | Mapping[str, str | Sequence[int]] | None = None)
         A Wrapper inspired by python's wrapper deprecated from 3.13 and is used to deprecate parameters that are transformed into keyword arguments
         
         :param params: A Sequence of keyword parameters of single keyword parameter to deprecate and warn the removal of.
         :param message: A single message for to assign to each parameter to be deprecated otherwise
            you can deprecate multiple under different reasons::

                @deprecated_params(
                    ['mispel', 'x'],
                    message={
                        'mispel': 'mispel was deprecated due to misspelling the word',
                        'x':'you get the idea...'
                    }
                )
                def mispelled_func(misspelling = None, *, mispel:str, x:int): ...

         :param category:     Used to warrant a custom warning category if required or needed to specify what
               Deprecation warning should appear.
         :param stacklevel:   What level should this wanring appear at? Default: 3
         :param default_message:    When a parameter doesn't have a warning message try using this message instead
         :param display_kw:   Displays which parameter is deprecated in the warning message under "Parameter "%s" ..."  followed by the rest of the message
         :param removed_in:   Displays which version of your library's program will remove this keyword parameter 
            in::

                   @deprecated_params(
                       ['mispel', 'x'],
                       removed_in={
                           'mispel':'0.1.4',
                           'x':(0, 1, 3)
                       } # sequences of numbers are also allowed if preferred.
                   )

                   def mispelled_func(misspelling = None, *, mispel:str, x:int): ...

            you can also say that all parameters will be removed in one version::

                   @deprecated_params(
                       ['mispel', 'x'],
                       removed_in='0.1.5' # or (0, 1, 5)
                   )
                   def mispelled_func(misspelling = None, *, mispel:str, x:int): ...

      


.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. _GitHub: https://github.com/Vizonex/deprecated-params

