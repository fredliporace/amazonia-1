# stactools-amazonia-1

[![PyPI](https://img.shields.io/pypi/v/stactools-amazonia-1)](https://pypi.org/project/stactools-amazonia-1/)

- Name: amazonia-1
- Package: `stactools.amazonia_1`
- [stactools-amazonia-1 on PyPI](https://pypi.org/project/stactools-amazonia-1/)
- Owner: @githubusername
- [Dataset homepage](http://example.com)
- STAC extensions used:
  - [proj](https://github.com/stac-extensions/projection/)
- Extra fields:
  - `amazonia-1:custom`: A custom attribute
- [Browse the example in human-readable form](https://radiantearth.github.io/stac-browser/#/external/raw.githubusercontent.com/stactools-packages/amazonia-1/main/examples/collection.json)

A short description of the package and its usage.

## STAC Examples

- [Collection](examples/collection.json)
- [Item](examples/item/item.json)

## Installation

```shell
pip install stactools-amazonia-1
```

## Command-line Usage

Description of the command line functions

```shell
stac amazonia-1 create-item source destination
```

Use `stac amazonia-1 --help` to see all subcommands and options.

## Contributing

We use [pre-commit](https://pre-commit.com/) to check any changes.
To set up your development environment:

```shell
pip install -e .
pip install -r requirements-dev.txt
pre-commit install
```

To check all files:

```shell
pre-commit run --all-files
```

To run the tests:

```shell
pytest -vv
```
