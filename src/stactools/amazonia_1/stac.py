"""Create Amazonia-1 stac items and collection."""
import logging
import os
import re
import statistics
import typing
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import utm
from pystac import (
    Asset,
    CatalogType,
    Collection,
    Extent,
    Item,
    MediaType,
    Provider,
    ProviderRole,
    SpatialExtent,
    TemporalExtent,
)
from pystac.extensions.eo import Band, EOExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.sat import OrbitState, SatExtension
from pystac.extensions.view import ViewExtension

from stactools.amazonia_1.constants import BASE_CAMERA, CBERS_AM_MISSIONS, TIF_XML_REGEX

logger = logging.getLogger(__name__)


def _epsg_from_utm_zone(zone: int) -> int:
    """
    Returns the WGS-84 EPSG for a given UTM zone.

    Args:
        zone: UTM zone
    Returns:
        WGS-84 EPSG code
    """

    if zone > 0:
        epsg = 32600 + zone
    else:
        epsg = 32700 - zone
    return epsg


def _build_collection_name(satellite: str, camera: str, mission: Optional[str]) -> str:
    """Build collection names.

    If mission is missing then we assume that it is already concatenated with satellite.

    Args:
        satellite: satellite id (CBERS, AMAZONIA, etc.)
        camera: camera id (WFI, MUX, etc.)
        mission: satellite mission (4, 4A, etc.)
    """
    if not mission:
        return f"{satellite}-{camera}"
    return f"{satellite}{mission}-{camera}"


@typing.no_type_check
def _get_keys_from_cbers_am(cb_am_metadata: str) -> Dict[str, Any]:
    """Extract keys from Amazonia-1 INPE's metadata.

    Args:
        cb_am_metadata: CBERS/AM metadata file location

    Returns:
        Item: STAC Item object
    """

    nsp = {"x": "http://www.gisplan.com.br/xmlsat"}
    metadata = {}

    match = TIF_XML_REGEX.match(cb_am_metadata.split("/")[-1])
    assert match, f"Can't match {cb_am_metadata}"

    tree = ET.parse(cb_am_metadata)
    original_root = tree.getroot()

    # satellite node information, checking for CBERS-04A/AMAZONIA1 WFI
    # special case
    left_root = original_root.find("x:leftCamera", nsp)
    if left_root:
        right_root = original_root.find("x:rightCamera", nsp)
        # We use the left camera for fields that are not camera
        # specific or are not used for STAC fields computation
        root = left_root
    else:
        root = original_root

    satellite = root.find("x:satellite", nsp)

    metadata["mission"] = satellite.find("x:name", nsp).text
    metadata["number"] = satellite.find("x:number", nsp).text
    metadata["sensor"] = satellite.find("x:instrument", nsp).text
    metadata["collection"] = _build_collection_name(
        satellite=metadata["mission"],
        mission=metadata["number"],
        camera=metadata["sensor"],
    )
    metadata["optics"] = (
        match.groupdict()["optics"] if match.groupdict()["optics"] else ""
    )

    # image node information
    image = root.find("x:image", nsp)
    metadata["path"] = image.find("x:path", nsp).text
    metadata["row"] = image.find("x:row", nsp).text
    metadata["processing_level"] = image.find("x:level", nsp).text
    metadata["vertical_pixel_size"] = image.find("x:verticalPixelSize", nsp).text
    metadata["horizontal_pixel_size"] = image.find("x:horizontalPixelSize", nsp).text
    metadata["projection_name"] = image.find("x:projectionName", nsp).text
    metadata["origin_latitude"] = image.find("x:originLatitude", nsp).text
    metadata["origin_longitude"] = image.find("x:originLongitude", nsp).text

    imagedata = image.find("x:imageData", nsp)
    metadata["ul_lat"] = imagedata.find("x:UL", nsp).find("x:latitude", nsp).text
    metadata["ul_lon"] = imagedata.find("x:UL", nsp).find("x:longitude", nsp).text
    metadata["ur_lat"] = imagedata.find("x:UR", nsp).find("x:latitude", nsp).text
    metadata["ur_lon"] = imagedata.find("x:UR", nsp).find("x:longitude", nsp).text
    metadata["lr_lat"] = imagedata.find("x:LR", nsp).find("x:latitude", nsp).text
    metadata["lr_lon"] = imagedata.find("x:LR", nsp).find("x:longitude", nsp).text
    metadata["ll_lat"] = imagedata.find("x:LL", nsp).find("x:latitude", nsp).text
    metadata["ll_lon"] = imagedata.find("x:LL", nsp).find("x:longitude", nsp).text
    metadata["ct_lat"] = imagedata.find("x:CT", nsp).find("x:latitude", nsp).text
    metadata["ct_lon"] = imagedata.find("x:CT", nsp).find("x:longitude", nsp).text

    boundingbox = image.find("x:boundingBox", nsp)
    metadata["bb_ul_lat"] = boundingbox.find("x:UL", nsp).find("x:latitude", nsp).text
    metadata["bb_ul_lon"] = boundingbox.find("x:UL", nsp).find("x:longitude", nsp).text
    metadata["bb_ur_lat"] = boundingbox.find("x:UR", nsp).find("x:latitude", nsp).text
    metadata["bb_ur_lon"] = boundingbox.find("x:UR", nsp).find("x:longitude", nsp).text
    metadata["bb_lr_lat"] = boundingbox.find("x:LR", nsp).find("x:latitude", nsp).text
    metadata["bb_lr_lon"] = boundingbox.find("x:LR", nsp).find("x:longitude", nsp).text
    metadata["bb_ll_lat"] = boundingbox.find("x:LL", nsp).find("x:latitude", nsp).text
    metadata["bb_ll_lon"] = boundingbox.find("x:LL", nsp).find("x:longitude", nsp).text

    sun_position = image.find("x:sunPosition", nsp)
    metadata["sun_elevation"] = sun_position.find("x:elevation", nsp).text
    metadata["sun_azimuth"] = sun_position.find("x:sunAzimuth", nsp).text

    if left_root:
        # Update fields for CB04A / AMAZONIA WFI special case
        lidata = left_root.find("x:image", nsp).find("x:imageData", nsp)
        ridata = right_root.find("x:image", nsp).find("x:imageData", nsp)
        metadata["ur_lat"] = ridata.find("x:UR", nsp).find("x:latitude", nsp).text
        metadata["ur_lon"] = ridata.find("x:UR", nsp).find("x:longitude", nsp).text
        metadata["lr_lat"] = ridata.find("x:LR", nsp).find("x:latitude", nsp).text
        metadata["lr_lon"] = ridata.find("x:LR", nsp).find("x:longitude", nsp).text
        metadata["ct_lat"] = str(
            statistics.mean(
                [
                    float(lidata.find("x:CT", nsp).find("x:latitude", nsp).text),
                    float(ridata.find("x:CT", nsp).find("x:latitude", nsp).text),
                ]
            )
        )
        metadata["ct_lon"] = str(
            statistics.mean(
                [
                    float(lidata.find("x:CT", nsp).find("x:longitude", nsp).text),
                    float(ridata.find("x:CT", nsp).find("x:longitude", nsp).text),
                ]
            )
        )

        spleft = left_root.find("x:image", nsp).find("x:sunPosition", nsp)
        spright = right_root.find("x:image", nsp).find("x:sunPosition", nsp)

        metadata["sun_elevation"] = str(
            statistics.mean(
                [
                    float(spleft.find("x:elevation", nsp).text),
                    float(spright.find("x:elevation", nsp).text),
                ]
            )
        )

        metadata["sun_azimuth"] = str(
            statistics.mean(
                [
                    float(spleft.find("x:sunAzimuth", nsp).text),
                    float(spright.find("x:sunAzimuth", nsp).text),
                ]
            )
        )

        bbleft = left_root.find("x:image", nsp).find("x:boundingBox", nsp)
        bbright = right_root.find("x:image", nsp).find("x:boundingBox", nsp)

        metadata["bb_ll_lat"] = str(
            min(
                float(bbleft.find("x:LL", nsp).find("x:latitude", nsp).text),
                float(bbright.find("x:LL", nsp).find("x:latitude", nsp).text),
            )
        )
        metadata["bb_ll_lon"] = str(
            min(
                float(bbleft.find("x:LL", nsp).find("x:longitude", nsp).text),
                float(bbright.find("x:LL", nsp).find("x:longitude", nsp).text),
            )
        )

        metadata["bb_ur_lat"] = str(
            max(
                float(bbleft.find("x:UR", nsp).find("x:latitude", nsp).text),
                float(bbright.find("x:UR", nsp).find("x:latitude", nsp).text),
            )
        )
        metadata["bb_ur_lon"] = str(
            max(
                float(bbleft.find("x:UR", nsp).find("x:longitude", nsp).text),
                float(bbright.find("x:UR", nsp).find("x:longitude", nsp).text),
            )
        )

    # attitude node information
    attitudes = image.find("x:attitudes", nsp)
    for attitude in attitudes.findall("x:attitude", nsp):
        metadata["roll"] = attitude.find("x:roll", nsp).text
        break

    # ephemeris node information
    ephemerides = image.find("x:ephemerides", nsp)
    for ephemeris in ephemerides.findall("x:ephemeris", nsp):
        metadata["vz"] = ephemeris.find("x:vz", nsp).text
        break

    # availableBands node information
    available_bands = root.find("x:availableBands", nsp)
    metadata["bands"] = []
    for band in available_bands.findall("x:band", nsp):
        metadata["bands"].append(band.text)
        key = f"band_{band.text}_gain"
        metadata[key] = band.attrib.get("gain")

    # viewing node information
    viewing = root.find("x:viewing", nsp)
    metadata["acquisition_date"] = viewing.find("x:center", nsp).text.replace("T", " ")
    metadata["acquisition_day"] = metadata["acquisition_date"].split(" ")[0]

    # derived fields
    metadata["no_level_id"] = (
        f"{metadata['mission']}_{metadata['number']}_{metadata['sensor']}_"
        f"{metadata['acquisition_day'].replace('-', '')}_"
        f"{int(metadata['path']):03d}_{int(metadata['row']):03d}"
    )

    # example: CBERS4/MUX/071/092/CBERS_4_MUX_20171105_071_092_L2
    metadata["download_url"] = (
        "%s%s/"
        "%s/"
        "%03d/%03d/"
        "%s"
        % (
            metadata["mission"],
            metadata["number"],
            metadata["sensor"],
            int(metadata["path"]),
            int(metadata["row"]),
            re.sub(
                r"(_LEFT|_RIGHT)?_BAND\d+.xml", "", os.path.basename(cb_am_metadata)
            ),
        )
    )
    metadata[
        "sat_sensor"
    ] = f"{metadata['mission']}{metadata['number']}/{metadata['sensor']}"
    metadata["sat_number"] = f"{metadata['mission']}-{metadata['number']}"
    metadata["meta_file"] = os.path.basename(cb_am_metadata)

    return metadata


def create_collection() -> Collection:
    """Create a STAC Collection

    This function includes logic to extract all relevant metadata from
    an asset describing the STAC collection and/or metadata coded into an
    accompanying constants.py file.

    See `Collection<https://pystac.readthedocs.io/en/latest/api.html#collection>`_.

    Returns:
        Collection: STAC Collection object
    """
    providers = [
        Provider(
            name="The OS Community",
            roles=[ProviderRole.PRODUCER, ProviderRole.PROCESSOR, ProviderRole.HOST],
            url="https://github.com/stac-utils/stactools",
        )
    ]

    # Time must be in UTC
    demo_time = datetime.now(tz=timezone.utc)

    extent = Extent(
        SpatialExtent([[-180.0, 90.0, 180.0, -90.0]]),
        TemporalExtent([[demo_time, None]]),
    )

    collection = Collection(
        id="my-collection-id",
        title="A dummy STAC Collection",
        description="Used for demonstration purposes",
        license="CC-0",
        providers=providers,
        extent=extent,
        catalog_type=CatalogType.RELATIVE_PUBLISHED,
    )

    return collection


# Original code from cbers_2_stac, will be removed as incorporated to
# create_item, create_collection

# # Collection
# stac_item["collection"] = cbers_am["collection"]

# # Links
# meta_prefix = f"https://s3.amazonaws.com/{buckets['metadata']}/"
# main_prefix = f"s3://{buckets['cog']}/"
# stac_prefix = f"https://{buckets['stac']}.s3.amazonaws.com/"
# # https://s3.amazonaws.com/cbers-meta-pds/CBERS4/MUX/066/096/
# # CBERS_4_MUX_20170522_066_096_L2/CBERS_4_MUX_20170522_066_096.jpg
# stac_item["links"] = []

# # links, self
# stac_item["links"].append(
#     build_link(
#         "self",
#         build_absolute_prefix(
#             buckets["stac"],
#             cbers_am["sat_sensor"],
#             int(cbers_am["path"]),
#             int(cbers_am["row"]),
#         )
#         + stac_item["id"]
#         + ".json",
#     )
# )

# # links, parent
# stac_item["links"].append(
#     build_link(
#         "parent",
#         build_absolute_prefix(
#             buckets["stac"],
#             cbers_am["sat_sensor"],
#             int(cbers_am["path"]),
#             int(cbers_am["row"]),
#         )
#         + "catalog.json",
#     )
# )

# # link, collection
# stac_item["links"].append(
#     build_link(
#         rel="collection",
#         href=stac_prefix
#         + cbers_am["mission"]
#         + cbers_am["number"]
#         + "/"
#         + cbers_am["sensor"]
#         + "/collection.json",
#     )
# )


def create_item(asset_href: str) -> Item:
    """Create a STAC Item

    This function should include logic to extract all relevant metadata from an
    asset, metadata asset, and/or a constants.py file.

    See `Item<https://pystac.readthedocs.io/en/latest/api.html#item>`_.

    Args:
        asset_href (str): The HREF pointing to an asset associated with the item

    Returns:
        Item: STAC Item object
    """

    cbers_am = _get_keys_from_cbers_am(asset_href)

    geom = {
        "type": "MultiPolygon",
        "coordinates": [
            [
                [
                    (float(cbers_am["ll_lon"]), float(cbers_am["ll_lat"])),
                    (float(cbers_am["lr_lon"]), float(cbers_am["lr_lat"])),
                    (float(cbers_am["ur_lon"]), float(cbers_am["ur_lat"])),
                    (float(cbers_am["ul_lon"]), float(cbers_am["ul_lat"])),
                    (float(cbers_am["ll_lon"]), float(cbers_am["ll_lat"])),
                ]
            ]
        ],
    }

    date_time = cbers_am["acquisition_date"].replace(" ", "T")
    # Remove microseconds info
    date_time = re.sub(r"\.\d+", "+00:00", date_time)

    item_id = "%s_%s_%s_%s_%03d_%03d_L%s" % (
        cbers_am["mission"],
        cbers_am["number"],
        cbers_am["sensor"],
        cbers_am["acquisition_day"].replace("-", ""),
        int(cbers_am["path"]),
        int(cbers_am["row"]),
        cbers_am["processing_level"],
    )

    item = Item(
        id=item_id,
        properties={},
        geometry=geom,
        # Order is lower left lon, lat; upper right lon, lat
        bbox=[
            float(cbers_am["bb_ll_lon"]),
            float(cbers_am["bb_ll_lat"]),
            float(cbers_am["bb_ur_lon"]),
            float(cbers_am["bb_ur_lat"]),
        ],
        datetime=datetime.fromisoformat(date_time),
    )

    item.common_metadata.platform = cbers_am["sat_number"].lower()
    item.common_metadata.instruments = [cbers_am["sensor"]]
    item.common_metadata.gsd = BASE_CAMERA[
        f"{cbers_am['mission']}{cbers_am['number']}"
    ][cbers_am["sensor"]]["summaries"]["gsd"][0]

    # view extension
    view = ViewExtension.ext(item, add_if_missing=True)
    view.sun_azimuth = float(cbers_am["sun_azimuth"])
    view.sun_elevation = float(cbers_am["sun_elevation"])
    view.off_nadir = abs(float(cbers_am["roll"]))

    # sat extension
    sat = SatExtension.ext(item, add_if_missing=True)
    sat.platform_international_designator = CBERS_AM_MISSIONS[cbers_am["sat_number"]][
        "international_designator"
    ]
    sat.orbit_state = (
        OrbitState.DESCENDING if float(cbers_am["vz"]) < 0 else OrbitState.ASCENDING
    )

    # proj extension
    proj = ProjectionExtension.ext(item, add_if_missing=True)
    assert cbers_am["projection_name"] == "UTM", (
        "Unsupported projection " + cbers_am["projection_name"]
    )
    utm_zone = int(
        utm.from_latlon(float(cbers_am["ct_lat"]), float(cbers_am["ct_lon"]))[2]
    )
    if float(cbers_am["ct_lat"]) < 0.0:
        utm_zone *= -1
    proj.epsg = _epsg_from_utm_zone(utm_zone)

    # cbers/amazonia section
    item.properties.update(
        {
            f"{cbers_am['mission'].lower()}:data_type": "L"
            + cbers_am["processing_level"],
            f"{cbers_am['mission'].lower()}:path": int(cbers_am["path"]),
            f"{cbers_am['mission'].lower()}:row": int(cbers_am["row"]),
        }
    )

    # Metadata bucket
    meta_prefix = "https://s3.amazonaws.com/amazonia-meta-pds/"
    # COG bucket
    main_prefix = "s3://cbers-pds/"

    # Thumbnail asset
    item.add_asset(
        key="thumbnail",
        asset=Asset.from_dict(
            {
                "href": meta_prefix
                + cbers_am["download_url"]
                + "/"
                + cbers_am["no_level_id"]
                + "."
                + CBERS_AM_MISSIONS[cbers_am["sat_number"]]["quicklook"]["extension"],
                "type": "image/"
                + CBERS_AM_MISSIONS[cbers_am["sat_number"]]["quicklook"]["type"],
            }
        ),
    )

    # INPE's metadata
    item.add_asset(
        key="metadata",
        asset=Asset(
            href=main_prefix + cbers_am["download_url"] + "/" + cbers_am["meta_file"],
            title="INPE original metadata",
            media_type=MediaType.XML,
        ),
    )

    # COGs
    for band in cbers_am["bands"]:
        band_id = "B" + band
        # Check gsd here, if not defined we use the collection's value.
        gsd = CBERS_AM_MISSIONS[cbers_am["sat_number"]]["band"][band_id].get("gsd")
        if gsd:
            properties = {"gsd": gsd}
        else:
            properties = {}
        asset = Asset.from_dict(
            {
                "href": main_prefix
                + cbers_am["download_url"]
                + "/"
                + item_id
                + cbers_am["optics"]
                + "_BAND"
                + band
                + ".tif",
                "type": "image/tiff; application=geotiff; " "profile=cloud-optimized",
            }
            | properties
        )
        item.add_asset(
            key=band_id,
            asset=asset,
        )
        optical_eo = EOExtension.ext(asset, add_if_missing=True)
        optical_eo.bands = [
            Band.create(
                name=band_id,
                common_name=CBERS_AM_MISSIONS[cbers_am["sat_number"]]["band"][band_id][
                    "common_name"
                ],
            )
        ]

    # Add an asset to the item (COG for example)
    # item.add_asset(
    #     "image",
    #     Asset(
    #         href=asset_href,
    #         media_type=MediaType.COG,
    #         roles=["data"],
    #         title="A dummy STAC Item COG",
    #     ),
    # )

    return item
