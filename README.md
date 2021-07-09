<p align="center">
  <a href="https://github.com/nschloe/blacktex"><img alt="blacktex" src="https://nschloe.github.io/blacktex/logo.svg" width="60%"></a>
  <p align="center">Clean up your LaTeX files.</p>
</p>

[![PyPi Version](https://img.shields.io/pypi/v/blacktex.svg?style=flat-square)](https://pypi.org/project/blacktex/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/blacktex.svg?style=flat-square)](https://pypi.org/project/blacktex/)
[![GitHub stars](https://img.shields.io/github/stars/nschloe/blacktex.svg?style=flat-square&logo=github&label=Stars&logoColor=white)](https://github.com/nschloe/blacktex)
[![PyPi downloads](https://img.shields.io/pypi/dm/blacktex.svg?style=flat-square)](https://pypistats.org/packages/blacktex)

[![gh-actions](https://img.shields.io/github/workflow/status/nschloe/blacktex/ci?style=flat-square)](https://github.com/nschloe/blacktex/actions?query=workflow%3Aci)
[![codecov](https://img.shields.io/codecov/c/github/nschloe/blacktex.svg?style=flat-square)](https://codecov.io/gh/nschloe/blacktex)
[![LGTM](https://img.shields.io/lgtm/grade/python/github/nschloe/blacktex.svg?style=flat-square)](https://lgtm.com/projects/g/nschloe/blacktex)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

blacktex is a little tool, helping with the article editing for LaTeX. It removes all
comments from a given file and corrects [some common
anti-patterns](http://mirrors.ctan.org/info/l2tabu/english/l2tabuen.pdf). For example,
with
```
blacktex in.tex > out.tex
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
and \(y = 2^n g\) with \(n = 1,\dots,10\), we have \(\frac{\Gamma}{2} = 8\).
```
You can use
```
blacktex -i in0.tex in1.tex ...
```
to modify files in-place. See `blacktex -h` for all options.

### Installation

blacktex is [available from the Python Package Index](https://pypi.org/project/blacktex/), so with
```
pip install -U blacktex
```
you can install/upgrade.

### License
This software is published under the [GPLv3 license](https://www.gnu.org/licenses/gpl-3.0.en.html).
