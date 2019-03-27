from collections import OrderedDict

import requests

from intake.catalog import Catalog
from intake.catalog.local import LocalCatalogEntry


class DCATCatalog(Catalog):
    name: str = "dcat"
    url: str

    def __init__(self, url, metadata=None):
        self.url = url
        super().__init__(metadata)

    def _load(self):
        resp = requests.get(self.url)
        catalog = resp.json()
        self._entries = {
            entry["identifier"]: _construct_entry(entry)
            for entry in catalog["dataset"]
            if _should_include_entry(entry)
        }

def _get_relevant_distribution(dcat_entry):
    """
    Given a DCAT entry, find the most relevant distribution
    for the intake catalog. In general, we choose the more specific
    formats over the less specific formats. At present, they
    are ranked in the following order:

        GeoJSON
        CSV

    If none of these are found, None.
    If there are no distributions, it returns None.
    """
    mediaTypes = ["application/vnd.geo+json", "text/csv"]
    distributions = dcat_entry.get("distribution")

    if not distributions or not len(distributions):
        return None
    for key in mediaTypes:
        for distribution in distributions:
                return distribution
    return None


def _should_include_entry(dcat_entry):
    return _get_relevant_distribution(dcat_entry) != None


def _construct_entry(dcat_entry):
    driver_map = {
        "application/vnd.geo+json": "geojson",
        "text/csv": "csv",
    }
    kwargs_map = {
        "text/csv": {
            "csv_kwargs": {
                "blocksize": None,
                "sample": False
            }
        }
    }

    name = dcat_entry["identifier"]
    distribution = _get_relevant_distribution(dcat_entry)
    mediaType = distribution["mediaType"]
    url = distribution["downloadURL"]
    args = {
        "urlpath": url,
        **(kwargs_map.get(mediaType) or {})
    }
    description = f"## {dcat_entry['title']}\n\n{dcat_entry['description']}"
    driver = driver_map[mediaType]
    return LocalCatalogEntry(name, description, driver, True, args=args, metadata=dcat_entry)
