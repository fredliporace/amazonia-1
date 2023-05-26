"""test_commands."""

import os.path
from tempfile import TemporaryDirectory
from typing import Callable, List

import pystac
from click import Command, Group
from stactools.testing.cli_test import CliTestCase

from stactools.amazonia_1.commands import create_amazonia1_command


class CommandsTest(CliTestCase):
    """CommandsTest."""

    def create_subcommand_functions(self) -> List[Callable[[Group], Command]]:
        return [create_amazonia1_command]

    def test_create_collection(self) -> None:
        """test_create_collection."""
        with TemporaryDirectory() as tmp_dir:
            # Run your custom create-collection command and validate

            # Example:
            destination = os.path.join(tmp_dir, "collection.json")

            result = self.run_command(f"amazonia1 create-collection {destination}")

            assert result.exit_code == 0, f"\n{result.output}"

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            assert len(jsons) == 1

            collection = pystac.read_file(destination)
            assert collection.id == "AMAZONIA1-WFI"

            collection.validate()

    def test_create_item(self) -> None:
        """test_create_item."""
        with TemporaryDirectory() as tmp_dir:
            infile = "tests/fixtures/AMAZONIA_1_WFI_20220811_036_018_L4_BAND2.xml"

            destination = os.path.join(tmp_dir, "item.json")
            result = self.run_command(f"amazonia1 create-item {infile} {destination}")
            assert result.exit_code == 0, f"\n{result.output}"

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            assert len(jsons) == 1

            item = pystac.read_file(destination)
            assert item.id == "AMAZONIA_1_WFI_20220811_036_018_L4"

            item.validate()
