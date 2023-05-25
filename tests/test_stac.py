"""test_stac."""

import datetime

from stactools.amazonia_1 import stac


def test_create_collection() -> None:
    """test_create_collection."""

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
    """test_create_item."""

    # Create the STAC Item, combined (LEFT+RIGHT optics)
    item = stac.create_item(
        "tests/fixtures/AMAZONIA_1_WFI_20220811_036_018_L4_BAND2.xml"
    )

    assert item.id == "AMAZONIA_1_WFI_20220811_036_018_L4"
    assert item.datetime is not None
    assert item.datetime.isoformat() == "2022-08-11T14:01:37+00:00"
    assert item.datetime.tzinfo == datetime.timezone.utc

    assert item.common_metadata.platform == "amazonia-1"
    assert item.common_metadata.instruments == ["WFI"]
    assert item.common_metadata.gsd == 64

    assert item.geometry is not None
    assert item.geometry["coordinates"] == [
        [
            [
                (-58.40086, -20.559257),
                (-50.121331, -21.856167),
                (-48.698592, -15.04188),
                (-56.653807, -13.794569),
                (-58.40086, -20.559257),
            ]
        ]
    ]

    assert item.bbox == [-58.437218, -21.861746, -48.692586, -13.777946]

    # properties:view
    assert item.properties["view:sun_elevation"] == 50.042550000000006
    assert item.properties["view:sun_azimuth"] == 35.9219
    assert item.properties["view:off_nadir"] == 0.000416261

    # properties:sat
    assert item.properties["sat:platform_international_designator"] == "2021-015A"
    assert item.properties["sat:orbit_state"] == "descending"

    # properties:proj
    assert item.properties["proj:epsg"] == 32722

    # properties:amazonia
    assert item.properties["amazonia:data_type"] == "L4"
    assert item.properties["amazonia:path"] == 36
    assert item.properties["amazonia:row"] == 18

    # extensions schemas
    assert len(item.stac_extensions) == 4
    assert (
        "https://stac-extensions.github.io/view/v1.0.0/schema.json"
        in item.stac_extensions
    )
    assert (
        "https://stac-extensions.github.io/sat/v1.0.0/schema.json"
        in item.stac_extensions
    )
    assert (
        "https://stac-extensions.github.io/projection/v1.1.0/schema.json"
        in item.stac_extensions
    )
    assert (
        "https://stac-extensions.github.io/eo/v1.0.0/schema.json"
        in item.stac_extensions
    )

    # assets
    assert (
        item.assets["thumbnail"].href
        == "https://s3.amazonaws.com/amazonia-meta-pds/AMAZONIA1/WFI/036/018/"
        "AMAZONIA_1_WFI_20220811_036_018_L4/AMAZONIA_1_WFI_20220811_036_018.png"
    )
    assert (
        item.assets["metadata"].href
        == "s3://cbers-pds/AMAZONIA1/WFI/036/018/AMAZONIA_1_WFI_20220811_036_018_L4/"
        "AMAZONIA_1_WFI_20220811_036_018_L4_BAND2.xml"
    )
    assert (
        item.assets["B2"].href
        == "s3://cbers-pds/AMAZONIA1/WFI/036/018/AMAZONIA_1_WFI_20220811_036_018_L4/"
        "AMAZONIA_1_WFI_20220811_036_018_L4_BAND2.tif"
    )

    # Create the STAC Item, single optic (LEFT)
    item = stac.create_item(
        "tests/fixtures/AMAZONIA_1_WFI_20220810_033_018_L4_LEFT_BAND2.xml"
    )

    assert item.id == "AMAZONIA_1_WFI_20220810_033_018_L4"
    assert item.datetime is not None
    assert item.datetime.isoformat() == "2022-08-10T13:01:35+00:00"
    assert item.datetime.tzinfo == datetime.timezone.utc
    assert item.bbox == [-43.422677, -21.25324, -37.558733, -13.72715]

    # properties:view
    assert item.properties["view:sun_elevation"] == 48.9478
    assert item.properties["view:sun_azimuth"] == 38.3485
    assert item.properties["view:off_nadir"] == 0.000120206

    # properties:proj
    assert item.properties["proj:epsg"] == 32724

    # properties:amazonia
    assert item.properties["amazonia:data_type"] == "L4"
    assert item.properties["amazonia:path"] == 33
    assert item.properties["amazonia:row"] == 18

    # assets
    assert (
        item.assets["thumbnail"].href
        == "https://s3.amazonaws.com/amazonia-meta-pds/AMAZONIA1/WFI/033/018/"
        "AMAZONIA_1_WFI_20220810_033_018_L4/AMAZONIA_1_WFI_20220810_033_018.png"
    )
    assert (
        item.assets["metadata"].href
        == "s3://cbers-pds/AMAZONIA1/WFI/033/018/AMAZONIA_1_WFI_20220810_033_018_L4/"
        "AMAZONIA_1_WFI_20220810_033_018_L4_LEFT_BAND2.xml"
    )
    assert (
        item.assets["B2"].href
        == "s3://cbers-pds/AMAZONIA1/WFI/033/018/AMAZONIA_1_WFI_20220810_033_018_L4/"
        "AMAZONIA_1_WFI_20220810_033_018_L4_LEFT_BAND2.tif"
    )

    # Validate
    item.validate()
