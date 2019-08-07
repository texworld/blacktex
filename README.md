<p align="center">
  <a href="https://github.com/nschloe/blacktex"><img alt="blacktex" src="https://nschloe.github.io/blacktex/logo.svg" width="60%"></a>
  <p align="center">Clean up your LaTeX files.</p>
</p>

[![CircleCI](https://img.shields.io/circleci/project/github/nschloe/blacktex/master.svg)](https://circleci.com/gh/nschloe/blacktex/tree/master)
[![codecov](https://img.shields.io/codecov/c/github/nschloe/blacktex.svg)](https://codecov.io/gh/nschloe/blacktex)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![PyPi Version](https://img.shields.io/pypi/v/blacktex.svg)](https://pypi.python.org/pypi/blacktex)
[![GitHub stars](https://img.shields.io/github/stars/nschloe/blacktex.svg?logo=github&label=Stars&logoColor=white)](https://github.com/nschloe/blacktex)

blacktex is a little tool, helping with the article editing for LaTeX. It removes all
comments from a given file and corrects [some common
anti-patterns](http://mirrors.ctan.org/info/l2tabu/english/l2tabuen.pdf). For example,
with
```
blacktex in.tex out.tex
```
the input file
```latex
Because   of $$a+b=c$$ ({\it Pythogoras}),
% @johnny remember to insert name
and $y=2^ng$ with $n=1,...,10$, we have ${\Gamma \over 2}=8.$
```
is converted to
```latex
Because of
\[
a+b = c
\]
(\textit{Pythogoras}),
and $y = 2^n g$ with $n = 1,\dots,10$, we have $\frac{\Gamma}{2} = 8$.
```

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

### License
blacktex is published under the [MIT license](https://en.wikipedia.org/wiki/MIT_License).
