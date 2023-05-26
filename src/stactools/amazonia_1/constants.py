"""Constants"""

import re
from typing import Any, Dict

TIF_XML_REGEX = re.compile(
    r"(?P<satellite>\w+)_(?P<mission>\w+)_(?P<camera>\w+)_"
    r"(?P<date>\d{8})_(?P<path>\d{3})_(?P<row>\d{3})_"
    r"(?P<level>[^\W_]+)(?P<optics>_LEFT|_RIGHT)?_"
    r"BAND(?P<band>\d+)\.(tif|xml)"
)

COG_TYPE = "image/tiff; application=geotiff; profile=cloud-optimized"

# CBERS and Amazonia-1 general missions definitions
CBERS_AM_MISSIONS: Dict[str, Any] = {
    "CBERS-4": {
        "interval": [["2014-12-08T00:00:00Z", None]],
        "quicklook": {"extension": "jpg", "type": "jpeg"},
        "instruments": ["MUX", "AWFI", "PAN5M", "PAN10M"],
        "band": {
            "B1": {"common_name": "pan"},
            "B2": {"common_name": "green"},
            "B3": {"common_name": "red"},
            "B4": {"common_name": "nir"},
            "B5": {"common_name": "blue"},
            "B6": {"common_name": "green"},
            "B7": {"common_name": "red"},
            "B8": {"common_name": "nir"},
            "B13": {"common_name": "blue"},
            "B14": {"common_name": "green"},
            "B15": {"common_name": "red"},
            "B16": {"common_name": "nir"},
        },
        "international_designator": "2014-079A",
        "MUX": {"meta_band": 6},
        "AWFI": {"meta_band": 14},
        "PAN5M": {"meta_band": 1},
        "PAN10M": {"meta_band": 4},
        "providers": [
            {
                "name": "Instituto Nacional de Pesquisas Espaciais, INPE",
                "roles": ["producer"],
                "url": "http://www.cbers.inpe.br",
            },
            {
                "name": "AMS Kepler",
                "roles": ["processor"],
                "description": "Convert INPE's original TIFF to COG "
                "and copy to Amazon Web Services",
                "url": "https://github.com/fredliporace/cbers-on-aws",
            },
            {
                "name": "Amazon Web Services",
                "roles": ["host"],
                "url": "https://registry.opendata.aws/cbers/",
            },
        ],
    },
    "CBERS-4A": {
        "interval": [["2019-12-20T00:00:00Z", None]],
        "quicklook": {"extension": "png", "type": "png"},
        "instruments": ["WPM", "MUX", "WFI"],
        "band": {
            "B0": {
                "common_name": "pan",
            },
            "B1": {
                # gsd is only defined for values greater than
                # what is defined at collection level
                "common_name": "blue",
                "gsd": 8.0,
            },
            "B2": {"common_name": "green", "gsd": 8.0},
            "B3": {"common_name": "red", "gsd": 8.0},
            "B4": {"common_name": "nir", "gsd": 8.0},
            "B5": {"common_name": "blue"},
            "B6": {"common_name": "green"},
            "B7": {"common_name": "red"},
            "B8": {"common_name": "nir"},
            "B13": {"common_name": "blue"},
            "B14": {"common_name": "green"},
            "B15": {"common_name": "red"},
            "B16": {"common_name": "nir"},
        },
        "international_designator": "2019-093E",
        "WPM": {"meta_band": 2},
        "MUX": {"meta_band": 6},
        "WFI": {"meta_band": 14},
        "providers": [
            {
                "name": "Instituto Nacional de Pesquisas Espaciais, INPE",
                "roles": ["producer"],
                "url": "http://www.cbers.inpe.br",
            },
            {
                "name": "AMS Kepler",
                "roles": ["processor"],
                "description": "Convert INPE's original TIFF to COG "
                "and copy to Amazon Web Services",
                "url": "https://github.com/fredliporace/cbers-on-aws",
            },
            {
                "name": "Amazon Web Services",
                "roles": ["host"],
                "url": "https://registry.opendata.aws/cbers/",
            },
        ],
    },
    "AMAZONIA-1": {
        "interval": [["2021-02-28T00:00:00Z", None]],
        "quicklook": {"extension": "png", "type": "png"},
        "instruments": ["WFI"],
        "band": {
            "B1": {"common_name": "blue"},
            "B2": {"common_name": "green"},
            "B3": {"common_name": "red"},
            "B4": {"common_name": "nir"},
        },
        "international_designator": "2021-015A",
        "WFI": {"meta_band": 2},
        "providers": [
            {
                "name": "Instituto Nacional de Pesquisas Espaciais, INPE",
                "roles": ["producer"],
                "url": "http://www.inpe.br/amazonia1",
            },
            {
                "name": "AMS Kepler",
                "roles": ["processor"],
                "description": "Convert INPE's original TIFF to COG "
                "and copy to Amazon Web Services",
                "url": "https://amskepler.com",
            },
            {
                "name": "Amazon Web Services",
                "roles": ["host"],
                "url": "https://registry.opendata.aws/amazonia",
            },
        ],
    },
}

BASE_CAMERA: Dict[str, Any] = {
    "CBERS-4": {
        "MUX": {
            "summaries": {
                "gsd": [20.0],
                "sat:platform_international_designator": [
                    CBERS_AM_MISSIONS["CBERS-4"]["international_designator"]
                ],
            },
            "item_assets": {
                "thumbnail": {"title": "Thumbnail", "type": "image/jpeg"},
                "metadata": {"title": "INPE original metadata", "type": "text/xml"},
                "B5": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B5", "common_name": "blue"}],
                },
                "B6": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B6", "common_name": "green"}],
                },
                "B7": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B7", "common_name": "red"}],
                },
                "B8": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B8", "common_name": "nir"}],
                },
            },
        },
        "AWFI": {
            "summaries": {
                "gsd": [64.0],
                "sat:platform_international_designator": [
                    CBERS_AM_MISSIONS["CBERS-4"]["international_designator"]
                ],
            },
            "item_assets": {
                "thumbnail": {"title": "Thumbnail", "type": "image/jpeg"},
                "metadata": {"title": "INPE original metadata", "type": "text/xml"},
                "B13": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B13", "common_name": "blue"}],
                },
                "B14": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B14", "common_name": "green"}],
                },
                "B15": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B15", "common_name": "red"}],
                },
                "B16": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B16", "common_name": "nir"}],
                },
            },
        },
        "PAN5M": {
            "summaries": {
                "gsd": [5.0],
                "sat:platform_international_designator": [
                    CBERS_AM_MISSIONS["CBERS-4"]["international_designator"]
                ],
            },
            "item_assets": {
                "thumbnail": {"title": "Thumbnail", "type": "image/jpeg"},
                "metadata": {"title": "INPE original metadata", "type": "text/xml"},
                "B1": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B1", "common_name": "pan"}],
                },
            },
        },
        "PAN10M": {
            "summaries": {
                "gsd": [10.0],
                "sat:platform_international_designator": [
                    CBERS_AM_MISSIONS["CBERS-4"]["international_designator"]
                ],
            },
            "item_assets": {
                "thumbnail": {"title": "Thumbnail", "type": "image/jpeg"},
                "metadata": {"title": "INPE original metadata", "type": "text/xml"},
                "B2": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B2", "common_name": "green"}],
                },
                "B3": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B3", "common_name": "red"}],
                },
                "B4": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B4", "common_name": "nir"}],
                },
            },
        },
    },
    "CBERS-4A": {
        "MUX": {
            "summaries": {
                "gsd": [16.5],
                "sat:platform_international_designator": [
                    CBERS_AM_MISSIONS["CBERS-4A"]["international_designator"]
                ],
            },
            "item_assets": {
                "thumbnail": {"title": "Thumbnail", "type": "image/png"},
                "metadata": {"title": "INPE original metadata", "type": "text/xml"},
                "B5": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B5", "common_name": "blue"}],
                },
                "B6": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B6", "common_name": "green"}],
                },
                "B7": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B7", "common_name": "red"}],
                },
                "B8": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B8", "common_name": "nir"}],
                },
            },
        },
        "WFI": {
            "summaries": {
                "gsd": [55.0],
                "sat:platform_international_designator": [
                    CBERS_AM_MISSIONS["CBERS-4A"]["international_designator"]
                ],
            },
            "item_assets": {
                "thumbnail": {"title": "Thumbnail", "type": "image/png"},
                "metadata": {"title": "INPE original metadata", "type": "text/xml"},
                "B13": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B13", "common_name": "blue"}],
                },
                "B14": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B14", "common_name": "green"}],
                },
                "B15": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B15", "common_name": "red"}],
                },
                "B16": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B16", "common_name": "nir"}],
                },
            },
        },
        "WPM": {
            # First GSD should be the smaller
            "summaries": {
                "gsd": [2.0, 8.0],
                "sat:platform_international_designator": [
                    CBERS_AM_MISSIONS["CBERS-4A"]["international_designator"]
                ],
            },
            "item_assets": {
                "thumbnail": {"title": "Thumbnail", "type": "image/png"},
                "metadata": {"title": "INPE original metadata", "type": "text/xml"},
                "B0": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B0", "common_name": "pan"}],
                },
                "B1": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B1", "common_name": "blue"}],
                },
                "B2": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B2", "common_name": "green"}],
                },
                "B3": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B3", "common_name": "red"}],
                },
                "B4": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B4", "common_name": "nir"}],
                },
            },
        },
    },
    "AMAZONIA-1": {
        "WFI": {
            "summaries": {
                "gsd": [64.0],
                "sat:platform_international_designator": [
                    CBERS_AM_MISSIONS["AMAZONIA-1"]["international_designator"]
                ],
            },
            "item_assets": {
                "thumbnail": {"title": "Thumbnail", "type": "image/png"},
                "metadata": {"title": "INPE original metadata", "type": "text/xml"},
                "B1": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B1", "common_name": "blue"}],
                },
                "B2": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B2", "common_name": "green"}],
                },
                "B3": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B3", "common_name": "red"}],
                },
                "B4": {
                    "type": COG_TYPE,
                    "eo:bands": [{"name": "B4", "common_name": "nir"}],
                },
            },
        },
    },
}

BASE_COLLECTION: Dict[str, Any] = {
    "stac_extensions": [
        "https://stac-extensions.github.io/item-assets/v1.0.0/schema.json"
    ],
    "license": "CC-BY-SA-3.0",
    "providers": None,
    "extent": {
        "spatial": {
            "bbox": [[-180.0, -83.0, 180.0, 83.0]],
        },
        "temporal": {"interval": None},
    },
    "summaries": {
        "gsd": None,
        "sat:platform_international_designator": None,
        "sat:orbit_state": ["ascending", "descending"],
    },
    "links": None,
    "item_assets": None,
}
