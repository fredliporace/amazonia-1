from stactools.amazonia_1 import stac


def test_create_collection() -> None:
    # Write tests for each for the creation of a STAC Collection
    # Create the STAC Collection...
    collection = stac.create_collection()
    collection.set_self_href("")

    # Check that it has some required attributes
    assert collection.id == "my-collection-id"
    # self.assertEqual(collection.other_attr...

    # Validate
    collection.validate()


def test_create_item() -> None:
    # Write tests for each for the creation of STAC Items
    # Create the STAC Item...
    item = stac.create_item(
        "tests/fixtures/AMAZONIA_1_WFI_20220811_036_018_L4_BAND2.xml"
    )

    # Check that it has some required attributes
    assert item.id == "AMAZONIA_1_WFI_20220811_036_018_L4"
    # self.assertEqual(item.other_attr...

    # Validate
    item.validate()
