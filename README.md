# pacopy

[![PyPi Version](https://img.shields.io/pypi/v/pacopy.svg?style=flat-square)](https://pypi.org/project/pacopy/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/pacopy.svg?style=flat-square)](https://pypi.org/project/pacopy/)
[![GitHub stars](https://img.shields.io/github/stars/nschloe/pacopy.svg?style=flat-square&logo=github&label=Stars&logoColor=white)](https://github.com/nschloe/pacopy)
[![PyPi downloads](https://img.shields.io/pypi/dm/pacopy.svg?style=flat-square)](https://pypistats.org/packages/pacopy)

[![Discord](https://img.shields.io/static/v1?logo=discord&logoColor=white&label=chat&message=on%20discord&color=7289da&style=flat-square)](https://discord.gg/hnTJ5MRX2Y)

[![gh-actions](https://img.shields.io/github/workflow/status/nschloe/pacopy/ci?style=flat-square)](https://github.com/nschloe/pacopy/actions?query=workflow%3Aci)
[![codecov](https://img.shields.io/codecov/c/github/nschloe/pacopy.svg?style=flat-square)](https://app.codecov.io/gh/nschloe/pacopy)
[![LGTM](https://img.shields.io/lgtm/grade/python/github/nschloe/pacopy.svg?style=flat-square)](https://lgtm.com/projects/g/nschloe/pacopy)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

pacopy provides various algorithms of [numerical parameter
continuation](https://en.wikipedia.org/wiki/Numerical_continuation) for ODEs and PDEs in
Python.

pacopy is backend-agnostic, so it doesn't matter if your problem is formulated with
[NumPy](https://numpy.org/), [SciPy](https://scipy.org/),
[FEniCS](https://fenicsproject.org/), [pyfvm](https://github.com/nschloe/pyfvm), or any
other Python package. The only thing the user must provide is a class with some simple
methods, e.g., a function evaluation `f(u, lmbda)`, a Jacobian a solver
`jacobian_solver(u, lmbda, rhs)` etc.

Install with

```
pip install pacopy
```
To get started, take a look at the examples below.

Some pacopy documentation is available
[here](https://pacopy.readthedocs.io/en/latest/?badge=latest).

### Examples

#### Basic scalar example

<img src="https://nschloe.github.io/pacopy/simple.svg" width="30%">

Let's start off with a problem where the solution space is scalar. We try to
solve `sin(x) - lambda` for different values of `lambda`, starting at 0.

```python
import math
import matplotlib.pyplot as plt
import pacopy


class SimpleScalarProblem:
    def inner(self, a, b):
        """The inner product in the problem domain. For scalars, this is just a
        multiplication.
        """
        return a * b

    def norm2_r(self, a):
        """The norm in the range space; used to determine if a solution has been found."""
        return a**2

    def f(self, u, lmbda):
        """The evaluation of the function to be solved"""
        return math.sin(u) - lmbda

    def df_dlmbda(self, u, lmbda):
        """The function's derivative with respect to the parameter. Used in Euler-Newton
        continuation.
        """
        return -1.0

    def jacobian_solver(self, u, lmbda, rhs):
        """A solver for the Jacobian problem. For scalars, this is just a division."""
        return rhs / math.cos(u)


problem = SimpleScalarProblem()

lmbda_list = []
values_list = []


def callback(k, lmbda, sol):
    # Use the callback for plotting, writing data to files etc.
    lmbda_list.append(lmbda)
    values_list.append(sol)


pacopy.euler_newton(
    problem,
    u0=0.0,
    lmbda0=0.0,
    callback=callback,
    max_steps=20,
    newton_tol=1.0e-10,
    verbose=False,
)

# plot solution
plt.plot(values_list, lmbda_list, ".-")
plt.xlabel("$u_1$")
plt.ylabel("$\\lambda$")
plt.show()
```

#### Simple 2D problem

<img src="https://nschloe.github.io/pacopy/simple2d.svg" width="30%">

A similarly simple example with two unknowns and a parameter. The inner product and
Jacobian solver are getting more interesting.

```python
import matplotlib.pyplot as plt
import numpy as np
import pacopy
import scipy
from mpl_toolkits.mplot3d import Axes3D


class SimpleProblem2D:
    def inner(self, a, b):
        return np.dot(a, b)

    def norm2_r(self, a):
        return np.dot(a, a)

    def f(self, u, lmbda):
        return np.array(
            [
                np.sin(u[0]) - lmbda - u[1] ** 2,
                np.cos(u[1]) * u[1] - lmbda,
            ]
        )

    def df_dlmbda(self, u, lmbda):
        return -np.ones_like(u)

    def jacobian_solver(self, u, lmbda, rhs):
        A = np.array(
            [
                [np.cos(u[0]), -2 * u[1]],
                [0.0, np.cos(u[1]) - np.sin(u[1]) * u[1]],
            ]
        )
        return np.linalg.solve(A, rhs)


problem = SimpleProblem2D()
# Initial guess and initial parameter value
u0 = np.zeros(2)
lmbda0 = 0.0

# Init lists
lmbda_list = []
values_list = []


def callback(k, lmbda, sol):
    lmbda_list.append(lmbda)
    values_list.append(sol)


pacopy.euler_newton(problem, u0, lmbda0, callback, max_steps=50, newton_tol=1.0e-10)

# plot solution
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
ax.plot(*np.array(values_list).T, lmbda_list, ".-")
ax.set_xlabel("$u_1$")
ax.set_ylabel("$u_2$")
ax.set_zlabel("$\\lambda$")
# plt.show()
plt.savefig("simple2d.svg", transparent=True, bbox_inches="tight")
plt.close()
```

#### Bratu

<img src="https://nschloe.github.io/pacopy/bratu1d.png" width="30%">

Let's deal with an actual PDE, the classical [Bratu
problem](https://en.wikipedia.org/wiki/Liouville%E2%80%93Bratu%E2%80%93Gelfand_equation)
in 1D with Dirichlet boundary conditions. Now, the solution space isn't scalar, but a
vector of length `n` (the values of the solution at given points on the 1D interval).
We now need numpy and scipy, the inner product and Jacobian solver are more complicated.

```python
import matplotlib.pyplot as plt
import numpy as np
import pacopy
import scipy.sparse
import scipy.sparse.linalg


# This is the classical finite-difference approximation
class Bratu1d:
    def __init__(self, n):
        self.n = n
        h = 1.0 / (self.n - 1)

        self.H = np.full(self.n, h)
        self.H[0] = h / 2
        self.H[-1] = h / 2

        self.A = (
            scipy.sparse.diags([-1.0, 2.0, -1.0], [-1, 0, 1], shape=(self.n, self.n))
            / h**2
        )

    def inner(self, a, b):
        """The inner product of the problem. Can be np.dot(a, b), but factoring in
        the mesh width stays true to the PDE.
        """
        return np.dot(a, self.H * b)

    def norm2_r(self, a):
        """The norm in the range space; used to determine if a solution has been found."""
        return np.dot(a, a)

    def f(self, u, lmbda):
        """The evaluation of the function to be solved"""
        out = self.A.dot(u) - lmbda * np.exp(u)
        out[0] = u[0]
        out[-1] = u[-1]
        return out

    def df_dlmbda(self, u, lmbda):
        """The function's derivative with respect to the parameter. Used in Euler-Newton
        continuation.
        """
        out = -np.exp(u)
        out[0] = 0.0
        out[-1] = 0.0
        return out

    def jacobian_solver(self, u, lmbda, rhs):
        """A solver for the Jacobian problem."""
        M = self.A.copy()
        d = M.diagonal().copy()
        d -= lmbda * np.exp(u)
        M.setdiag(d)
        # Dirichlet conditions
        M.data[0][self.n - 2] = 0.0
        M.data[1][0] = 1.0
        M.data[1][self.n - 1] = 1.0
        M.data[2][1] = 0.0
        return scipy.sparse.linalg.spsolve(M.tocsr(), rhs)


problem = Bratu1d(51)
# Initial guess and parameter value
u0 = np.zeros(problem.n)
lmbda0 = 0.0

lmbda_list = []
values_list = []


def callback(k, lmbda, sol):
    # Use the callback for plotting, writing data to files etc.
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.set_xlabel("$\\lambda$")
    ax1.set_ylabel("$||u||_2$")
    ax1.grid()

    lmbda_list.append(lmbda)
    # use the norm of the currentsolution for plotting on the y-axis
    values_list.append(np.sqrt(problem.inner(sol, sol)))

    ax1.plot(lmbda_list, values_list, "-x", color="C0")
    ax1.set_xlim(0.0, 4.0)
    ax1.set_ylim(0.0, 6.0)
    plt.close()


# Natural parameter continuation
# pacopy.natural(problem, u0, lmbda0, callback, max_steps=100)

pacopy.euler_newton(
    problem, u0, lmbda0, callback, max_steps=500, max_num_retries=10, newton_tol=1.0e-10
)
```

#### Ginzburg–Landau

https://user-images.githubusercontent.com/181628/146639709-90b6e6aa-48ba-418d-9aa4-ec5754f95b93.mp4

The [Ginzburg-Landau
equations](https://en.wikipedia.org/wiki/Ginzburg%E2%80%93Landau_theory) model
the behavior of extreme type-II superconductors under a magnetic field. The
above example (to be found in full detail
[here](tests/test_ginzburg_landau.py)) shows parameter continuation in the
strength of the magnetic field. The plot on the right-hand side shows the
complex-valued solution using [cplot](https://github.com/nschloe/cplot).


### License

This software is published under the [GPLv3
license](https://www.gnu.org/licenses/gpl-3.0.en.html).
