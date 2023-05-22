"""Create Amazonia-1 stac items and collection."""
import logging
import os
import re
import statistics
import typing
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, Optional

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
from pystac.extensions.projection import ProjectionExtension

logger = logging.getLogger(__name__)

TIF_XML_REGEX = re.compile(
    r"(?P<satellite>\w+)_(?P<mission>\w+)_(?P<camera>\w+)_"
    r"(?P<date>\d{8})_(?P<path>\d{3})_(?P<row>\d{3})_"
    r"(?P<level>[^\W_]+)(?P<optics>_LEFT|_RIGHT)?_"
    r"BAND(?P<band>\d+)\.(tif|xml)"
)


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

    properties = {
        "title": "A dummy STAC Item",
        "description": "Used for demonstration purposes",
    }

    demo_geom = {
        "type": "Polygon",
        "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]],
    }

    # Time must be in UTC
    demo_time = datetime.now(tz=timezone.utc)

    item = Item(
        id=(
            "%s_%s_%s_%s_%03d_%03d_L%s"
            % (
                cbers_am["mission"],
                cbers_am["number"],
                cbers_am["sensor"],
                cbers_am["acquisition_day"].replace("-", ""),
                int(cbers_am["path"]),
                int(cbers_am["row"]),
                cbers_am["processing_level"],
            )
        ),
        properties=properties,
        geometry=demo_geom,
        bbox=[-180, 90, 180, -90],
        datetime=demo_time,
        stac_extensions=[],
    )

    # It is a good idea to include proj attributes to optimize for libs like stac-vrt
    proj_attrs = ProjectionExtension.ext(item, add_if_missing=True)
    proj_attrs.epsg = 4326
    proj_attrs.bbox = [-180, 90, 180, -90]
    proj_attrs.shape = [1, 1]  # Raster shape
    proj_attrs.transform = [-180, 360, 0, 90, 0, 180]  # Raster GeoTransform

    # Add an asset to the item (COG for example)
    item.add_asset(
        "image",
        Asset(
            href=asset_href,
            media_type=MediaType.COG,
            roles=["data"],
            title="A dummy STAC Item COG",
        ),
    )

    return item
