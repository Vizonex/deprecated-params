"""
Deprecated Params
-----------------

A Library dedicated for warning users about deprecated parameter
names and changes
"""

try:
    from ._helpers_c import (InvalidParametersError, MissingKeywordsError,
                             deprecated_params) 
except ModuleNotFoundError:
    from ._helpers_py import (InvalidParametersError, MissingKeywordsError,
                              deprecated_params)    


__all__ = (
    "InvalidParametersError",
    "MissingKeywordsError",
    "__author__",
    "__license__",
    "__version__",
    "deprecated_params",
)

__version__ = "0.1.7"
__license__ = "Apache 2.0 / MIT"
__author__ = "Vizonex"

