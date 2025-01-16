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

## Officially Supported Method: Using pipx

We recommend using [pipx] for the installation of `phosphorus` as it provides
an isolated environment for the package, preventing any dependency conflicts.

To install `phosphorus` using pipx, run the following command in your terminal:

```console
$ pipx install phosphorus
```

## Alternative Method: Using pip

As an alternative, you can use [pip] to install `phosphorus`.
However, this method does not provide an isolated environment for the package,
which may lead to dependency conflicts or leave your system in an inconsistent state.
Therefore, this method is not recommended or supported.

To install `phosphorus` using pip, run the following command in your terminal:

```console
$ pip install --user phosphorus
```

## Python Version Requirement

Please note that `phosphorus` requires Python 3.9 or higher. Please ensure
that your system is using the correct Python version. If not,
consider using a tool like [pyenv] to create a shell with the required Python version.

[uv]: https://github.com/astral-sh/uv
[PEP 621]: https://peps.python.org/pep-0621/
[pip]: https://pip.pypa.io/en/stable/
[pipx]: https://pypa.github.io/pipx/
[pyenv]: https://github.com/pyenv/pyenv
