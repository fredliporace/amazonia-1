import stactools.core
from stactools.cli.registry import Registry

from stactools.amazonia_1.stac import create_collection, create_item

__all__ = ["create_collection", "create_item"]

stactools.core.use_fsspec()


def register_plugin(registry: Registry) -> None:
    from stactools.amazonia_1 import commands

    registry.register_subcommand(commands.create_amazonia1_command)


__version__ = "0.1.1"
