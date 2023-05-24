"""test_stac."""

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

    # Create the STAC Item...
    item = stac.create_item(
        "tests/fixtures/AMAZONIA_1_WFI_20220811_036_018_L4_BAND2.xml"
    )

    assert item.id == "AMAZONIA_1_WFI_20220811_036_018_L4"
    # todo: check Z
    assert item.datetime is not None
    assert item.datetime.isoformat() == "2022-08-11T14:01:37"

    assert item.properties["platform"] == "amazonia-1"
    assert item.properties["instruments"] == ["WFI"]
    assert item.properties["gsd"] == 64

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

    # meta = get_keys_from_cbers_am(
    #     "test/fixtures/AMAZONIA_1_WFI_20220811_036_018_L4_BAND2.xml"
    # )
    # buckets = {"metadata": "cbers-meta-pds", "cog": "cbers-pds", "stac": "cbers-stac"}
    # smeta = build_stac_item_keys(meta, buckets)

    # # bbox
    # assert len(smeta["bbox"]) == 4

    # # properties:proj
    # assert smeta["properties"]["proj:epsg"] == 32722

    # # properties:amazonia
    # assert smeta["properties"]["amazonia:data_type"] == "L4"
    # assert smeta["properties"]["amazonia:path"] == 36
    # assert smeta["properties"]["amazonia:row"] == 18

    # # assets
    # assert (
    #     smeta["assets"]["thumbnail"]["href"]
    #     == "https://s3.amazonaws.com/cbers-meta-pds/AMAZONIA1/WFI/036/018/"
    #     "AMAZONIA_1_WFI_20220811_036_018_L4/AMAZONIA_1_WFI_20220811_036_018.png"
    # )
    # assert (
    #     smeta["assets"]["metadata"]["href"]
    #     == "s3://cbers-pds/AMAZONIA1/WFI/036/018/AMAZONIA_1_WFI_20220811_036_018_L4/"
    #     "AMAZONIA_1_WFI_20220811_036_018_L4_BAND2.xml"
    # )
    # assert (
    #     smeta["assets"]["B2"]["href"]
    #     == "s3://cbers-pds/AMAZONIA1/WFI/036/018/AMAZONIA_1_WFI_20220811_036_018_L4/"
    #     "AMAZONIA_1_WFI_20220811_036_018_L4_BAND2.tif"
    # )

    # # LEFT case
    # meta = get_keys_from_cbers_am(
    #     "test/fixtures/AMAZONIA_1_WFI_20220810_033_018_L4_LEFT_BAND2.xml"
    # )
    # buckets = {"metadata": "cbers-meta-pds", "cog": "cbers-pds", "stac": "cbers-stac"}
    # smeta = build_stac_item_keys(meta, buckets)

    # # id
    # assert smeta["id"] == "AMAZONIA_1_WFI_20220810_033_018_L4"

    # # bbox
    # assert len(smeta["bbox"]) == 4

    # # geometry is built like other cameras, correct computation
    # # is checked in test_get_keys_from_cbers4a

    # # properties
    # assert smeta["properties"]["datetime"] == "2022-08-10T13:01:35Z"

    # # properties:view
    # assert smeta["properties"]["view:sun_elevation"] == 48.9478
    # assert smeta["properties"]["view:sun_azimuth"] == 38.3485
    # assert smeta["properties"]["view:off_nadir"] == 0.000120206

    # # properties:proj
    # assert smeta["properties"]["proj:epsg"] == 32724

    # # properties:amazonia
    # assert smeta["properties"]["amazonia:data_type"] == "L4"
    # assert smeta["properties"]["amazonia:path"] == 33
    # assert smeta["properties"]["amazonia:row"] == 18

    # # assets
    # assert (
    #     smeta["assets"]["thumbnail"]["href"]
    #     == "https://s3.amazonaws.com/cbers-meta-pds/AMAZONIA1/WFI/033/018/"
    #     "AMAZONIA_1_WFI_20220810_033_018_L4/AMAZONIA_1_WFI_20220810_033_018.png"
    # )
    # assert (
    #     smeta["assets"]["metadata"]["href"]
    #     == "s3://cbers-pds/AMAZONIA1/WFI/033/018/AMAZONIA_1_WFI_20220810_033_018_L4/"
    #     "AMAZONIA_1_WFI_20220810_033_018_L4_LEFT_BAND2.xml"
    # )
    # assert (
    #     smeta["assets"]["B2"]["href"]
    #     == "s3://cbers-pds/AMAZONIA1/WFI/033/018/AMAZONIA_1_WFI_20220810_033_018_L4/"
    #     "AMAZONIA_1_WFI_20220810_033_018_L4_LEFT_BAND2.tif"
    # )

    # Validate
    item.validate()
