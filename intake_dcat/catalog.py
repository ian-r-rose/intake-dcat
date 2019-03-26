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


_container_map = {
    "application/vnd.geo+json": "dataframe",
    "text/csv": "dataframe",
    "application/json": "dataframe",
}

_driver_map = {
    "application/vnd.geo+json": "geojson",
    "text/csv": "csv",
    "application/json": "json",
}

_kwargs_map = {
    "text/csv": {
        "csv_kwargs": {
            "blocksize": None,
            "sample": False
        }
    }
}


def _get_relevant_distribution(distributions):
    if not distributions or not len(distributions):
        return None
    for key in _container_map:
        for distribution in distributions:
            if distribution.get("mediaType") == key:
                return distribution
    return distributions[0]


def _should_include_entry(dcat_entry):
    return dcat_entry.get("distribution") != None


def _construct_entry(dcat_entry):
    name = dcat_entry["identifier"]
    distribution = _get_relevant_distribution(dcat_entry["distribution"])
    args = {
        "urlpath": distribution["downloadURL"],
        **(_kwargs_map.get(distribution["mediaType"]) or {})
    }
    description = dcat_entry["description"]
    driver = "csv"
    return LocalCatalogEntry(name, description, driver, True, args=args, metadata=dcat_entry)
