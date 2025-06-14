# Deprecated Params 
[![PyPI version](https://badge.fury.io/py/deprecated-params.svg)](https://badge.fury.io/py/deprecated-params)
![PyPI - Downloads](https://img.shields.io/pypi/dm/deprecated-params)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Inspired after python's warning.deprecated wrapper, deprecated_params is made to serve the single purpose of deprecating parameter names to warn users
about incoming changes as well as retaining typehinting.



## How to Deprecate Parameters
Parameters should be keyword arguments, not positional, Reason
for this implementation is that in theory you should've already 
planned an alternative approch to an argument you wish 
to deprecate.

```python
from deprecated_params import deprecated_params

@deprecated_params(['x'])
def func(y, *, x:int = 0):
    pass

# DeprecationWarning: Parameter "x" is deprecated
func(None, x=20)

# NOTE: **kw is accepted but also you could put down more than one 
# parameter if needed...
@deprecated_params(['foo'], {"foo":"foo was removed in ... don't use it"}, display_kw=False)
class MyClass:
    def __init__(self, spam:object, **kw):
        self.spam = spam
        self.foo = kw.get("foo", None)

# DeprecationWarning: foo was removed in ... don't use it
mc = MyClass("spam", foo="X")
```
