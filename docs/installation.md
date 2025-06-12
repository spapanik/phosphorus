# Installation

# Install as a build backend

`phosphorus` is a [PEP 621] compliant build backend. As such, you don't need to install it,
in order to use it in your project. You can specify `phosphorus` as your build system
in the project's `pyproject.toml` file:

```toml
[build-system]
requires = [
    "phosphorus>=0.10",
]
build-backend = "phosphorus.construction.api"
```

Your build front-end (we strongly recommend [uv] as it's fast and compliant) will take care
ot the rest.

# Install as a cli tool

In case you want to actually install `phosphorus` in your system, so you can use its cli
interface to build your project you can:

# Using uv

We recommend using uv for the installation of `phosphorus` as it provides
an isolated environment for the package, preventing any dependency conflicts.

The minimum python version needed is `3.10` but as uv is used, version 3.13
is preferred.

To install `phosphorus` using uv, run the following command in your terminal:

```console
$ uv tool install --python 3.13 cloninator
```

[uv]: https://github.com/astral-sh/uv
[PEP 621]: https://peps.python.org/pep-0621/
