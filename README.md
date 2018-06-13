# tidytex

Cleans up your LaTeX files.

[![CircleCI](https://img.shields.io/circleci/project/github/nschloe/tidytex/master.svg)](https://circleci.com/gh/nschloe/tidytex/tree/master)
[![codecov](https://img.shields.io/codecov/c/github/nschloe/tidytex.svg)](https://codecov.io/gh/nschloe/tidytex)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![PyPi Version](https://img.shields.io/pypi/v/tidytex.svg)](https://pypi.python.org/pypi/tidytex)
[![GitHub stars](https://img.shields.io/github/stars/nschloe/tidytex.svg?logo=github&label=Stars)](https://github.com/nschloe/tidytex)

tidytex converts your input file
```
| A | 1.34|-214.1
|CCCC | 55.534|   1131.1|
```
into
```
| A    |  1.34  | -214.1 |
| CCCC | 55.534 | 1131.1 |
```
Column widths are unified across the table, decimal dots are aligned, and
tidytex tries to be smart about column separators. Works for CSV, LaTeX,
Markdown etc.

### Usage from vim

Simply mark the table, and type
```
:'<,'>:!tidytex
```

![](https://nschloe.github.io/tidytex/tty-capture.gif)

### Installation

tidytex is [available from the Python Package Index](https://pypi.python.org/pypi/tidytex/), so with
```
pip install -U tidytex
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
tidytex is published under the [MIT license](https://en.wikipedia.org/wiki/MIT_License).
