# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to [Semantic Versioning].

## [Unreleased]

## [0.10.2] - 2025-01-16

### Fixed

-   Fixed adding no requirements at all

## [0.10.1] - 2025-01-16 [YANKED]

### Fixed

-   Fixed adding dev requirements to main

## [0.10.0] - 2025-01-16

### Removed

-   Dropped install, check, and lock in favour of [uv]

## [0.9.0] - 2025-01-13

### Changed

-   Use `dependency-groups` instead of `tool.phosphorus.dev-dependencies`

## [0.8.3] - 2024-12-14

### Fixed

-   Fixed universal resolver bug

## [0.8.2] - 2024-11-24

### Fixed

-   Fixed uploading errors for sdist

## [0.8.1] - 2024-11-14

### Fixed

-   Fixed a crash when UV returns non-zero exit code

## [0.8.0] - 2024-11-11

### Fixed

-   Fixed the env marker evaluation

## [0.7.0] - 2024-11-10

### Fixed

-   Fixed macOS tmpdir error

## [0.6.0] - 2024-11-03

### Changed

-   Dropped support for python 3.8

## [0.5.0] - 2024-09-06

### Added

-   Added a check for outdated packages

### Fixed

-   Fixed reporting of unknown groups

## [0.4.1] - 2024-07-16

### Fixed

-   Fixed hash when readme is missing

## [0.4.0] - 2024-07-15

### Changed

-   Changed license to BSD 3-Clause

### Fixed

-   Fixed python 3.8 compatibility issues
-   Fixed hashes, as they need to be independent of the installation path

## [0.3.0] - 2024-07-10

### Added

-   Added validation for trove classifiers

### Fixed

-   Fixed missing uv command
-   Fixed message when there are no packages to remove or update

## [0.2.1] - 2024-07-09

### Fixed

-   Fixed python 3.8 compatibility issues with missing BooleanOptionalAction
-   Fixed packages with different names than the project name

## [0.2.0] - 2024-07-08

### Added

-   Added support for python 3.8
-   Added support for python 3.9
-   Added support for python 3.10

## [0.1.3] - 2024-07-05

### Fixed

-   Fixed sdist file type, making it an actual tar.gz
-   Fixed installation subcommand, to install the project in editable mode

## [0.1.2] - 2024-07-04

### Fixed

-   Fixed status code after successful installations
-   Removed extra whitespace in METADATA

## [0.1.1] - 2024-07-04

### Added

-   Added a subcommand to build sdists and wheels
-   Added a subcommand to lock the dependencies
-   Added a subcommand to install the project
-   Added a subcommand to check if the lockfile is up to date

[Keep a Changelog]: https://keepachangelog.com/en/1.0.0/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html
[uv]: https://docs.astral.sh/uv/
[Unreleased]: https://github.com/spapanik/phosphorus/compare/v0.10.2...main
[0.10.1]: https://github.com/spapanik/phosphorus/compare/v0.10.1...v0.10.2
[0.10.1]: https://github.com/spapanik/phosphorus/compare/v0.10.0...v0.10.1
[0.10.0]: https://github.com/spapanik/phosphorus/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/spapanik/phosphorus/compare/v0.8.3...v0.9.0
[0.8.3]: https://github.com/spapanik/phosphorus/compare/v0.8.2...v0.8.3
[0.8.2]: https://github.com/spapanik/phosphorus/compare/v0.8.1...v0.8.2
[0.8.1]: https://github.com/spapanik/phosphorus/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/spapanik/phosphorus/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/spapanik/phosphorus/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/spapanik/phosphorus/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/spapanik/phosphorus/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/spapanik/phosphorus/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/spapanik/phosphorus/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/spapanik/phosphorus/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/spapanik/phosphorus/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/spapanik/phosphorus/compare/v0.1.3...v0.2.0
[0.1.3]: https://github.com/spapanik/eulertools/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/spapanik/eulertools/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/spapanik/eulertools/releases/tag/v0.1.1
