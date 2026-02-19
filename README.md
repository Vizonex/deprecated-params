# Deprecated Params 
[![PyPI version](https://badge.fury.io/py/deprecated-params.svg)](https://badge.fury.io/py/deprecated-params)
![PyPI - Downloads](https://img.shields.io/pypi/dm/deprecated-params)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: Appache-2.0](https://img.shields.io/badge/License-Appache-yellow.svg)](https://opensource.org/licenses/Appache-2-0)


Inspired after python's warning.deprecated wrapper, deprecated_params is made to serve the single purpose of deprecating parameter names to warn users
about incoming changes as well as retaining typehinting.



## How to Deprecate Parameters
Parameters should be keyword arguments, not positional, Reason
for this implementation is that in theory you should've already 
planned an alternative approach to an argument you wish 
to deprecate. Most of the times these arguments will most 
likely be one of 3 cases.
- misspellings
- better functionality that replaces old arguments with better ones.
- removed parameters but you want to warn developers
  to move without being aggressive about it.


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

## Why I wrote Deprecated Params
I got tired of throwing random warnings in my code and wanted something cleaner that didn't 
interfere with a function's actual code and didn't blind anybody trying to go through it. 
Contributors and Reviewers should be able to utilize a library that saves them from these problems
while improving the readability of a function. After figuring out that the functionality I was 
looking for didn't exist I took the opportunity to implement it.

## Goals With this library
- Keep up to date and maintained until sometime around __2040__ or when something new obsoletes the need for it
  - Example: If the standard python library were to introduce it's own adaptation of `deprecated-params`
- Remain tiny or as a single module with no additonal dependencies unless needed for backwards compatable versions of python example: `typing-extensions`.

