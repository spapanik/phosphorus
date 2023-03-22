from pathlib import Path

package_cache = Path.home().joinpath(".cache/phosphorus/packages/")
pypi_cache = package_cache.joinpath("PyPI")
