# stactools-amazonia-1

[![PyPI](https://img.shields.io/pypi/v/stactools-amazonia-1)](https://pypi.org/project/stactools-amazonia-1/)

- Name: amazonia-1
- Package: `stactools.amazonia_1`
- [stactools-amazonia-1 on PyPI](https://pypi.org/project/stactools-amazonia-1/)
- Owner: @fredliporace
- [Dataset homepage](https://aws.amazon.com/marketplace/pp/prodview-khrlpmr36l66s)
- STAC extensions used:
  - [eo](https://github.com/stac-extensions/eo)
  - [item-assets](https://github.com/stac-extensions/item-assets)
  - [proj](https://github.com/stac-extensions/projection/)
  - [sat](https://github.com/stac-extensions/sat)
  - [view](https://github.com/stac-extensions/view)
- Extra fields:
  - `amazonia:data_type`: Product level: L2 stands for system geometric
  correction (equivalent to Landast L1GS), L4 for ortho.
  - `amazonia:path`: Path in Amazonia-1 reference grid.
  - `amazonia:row`: Row in Amazonia-1 reference grid.
- [Browse the example in human-readable form](https://radiantearth.github.io/stac-browser/#/external/raw.githubusercontent.com/stactools-packages/amazonia-1/main/examples/collection.json)

Create Amazonia-1 STAC items from INPE's original metadata format,
using assets stored on AWS.

## STAC Examples

- [Collection](examples/collection.json)
- [Item](examples/AMAZONIA_1_WFI_20220810_033_018.json)

## Installation

```shell
pip install stactools-amazonia-1
```

## Command-line Usage

Creating a STAC item from INPE's XML file:

```shell
stac amazonia1 create-item SOURCE DESTINATION
```

Use `stac amazonia1 --help` to see all subcommands and options.

Creating the Amazonia-1 WFI collection:

```shell
stac amazonia1 create-collection DESTINATION
```

Use `stac amazonia1 create-collection --help` to see all subcommands and options.

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
