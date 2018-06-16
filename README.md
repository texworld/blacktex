# blacktex

Cleans up your LaTeX files.

[![CircleCI](https://img.shields.io/circleci/project/github/nschloe/blacktex/master.svg)](https://circleci.com/gh/nschloe/blacktex/tree/master)
[![codecov](https://img.shields.io/codecov/c/github/nschloe/blacktex.svg)](https://codecov.io/gh/nschloe/blacktex)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![PyPi Version](https://img.shields.io/pypi/v/blacktex.svg)](https://pypi.python.org/pypi/blacktex)
[![GitHub stars](https://img.shields.io/github/stars/nschloe/blacktex.svg?logo=github&label=Stars)](https://github.com/nschloe/blacktex)

### Installation

blacktex is [available from the Python Package Index](https://pypi.python.org/pypi/blacktex/), so with
```
pip install -U blacktex
```
you can install/upgrade.

### Testing

To run the tests, simply check out this repository and run
```
pytest
```

### Distribution

To create a new release

1. bump the `__version__` number,

2. publish to PyPi and GitHub:
    ```
    $ make publish
    ```

### License
blacktex is published under the [MIT license](https://en.wikipedia.org/wiki/MIT_License).
