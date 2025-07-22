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

## Deprecated Params used in real-world Examples 
Deprecated-params is now used with two of my own libraries by default. 

- [aiothreading (up until 0.1.6)](https://github.com/Vizonex/aiothreading)
  - Originally aiothreading had it's own wrapper but I split it off to this library along with a rewrite after finding out that
    parameter names were not showing up ides such as vs-code. The rewrite felt a bit bigger and knowing that users would want to utilize
    this concept in other places was how this library ultimately got started.
  - Lots of interior changes were made and with many arguments being suddenly dropped to increase the performance, the best solution was to warn
    developers to stop using certain parameters as they will be deleted in the future.
  - It is planned to be dropped as many of the things we wanted to remove have been slowly removed from the library which means this library will
    be removed from it but that doesn't mean I won't keep maintaining it, it is invented for short-use cases and can be added and removed freely
    without needing additional dependencies. 

- [aiocallback (mainly used in version 1.6)](https://github.com/Vizonex/aiocallback)
  - Same situation as aiothreading but I decided to buy users more time due to how fast some releases were going and it also allowed
  - Currently I removed deprecated-params from aiocallback since it wasn't needed anymore but this is what deprecated-param's purpose 
    was for, being there only when its need. I desired nothing more or less.

If you would like to add examples of your own libraries that have used this library feel free to throw me an issue or send me a pull request.

