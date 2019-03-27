import requests

from intake.catalog import Catalog
from intake.catalog.local import LocalCatalogEntry

from .distributions import get_relevant_distribution


class DCATCatalog(Catalog):
    """
    A Catalog that references a DCAT catalog at some URL
    and constructs an intake catalog from it, with opinionated
    choices about the drivers that will be used to load the datasets.
    In general, the drivers are in order of decreasing specificity:

    GeoJSON
    Shapefile
    CSV
    """
    name: str
    url: str

    def __init__(self, url, name, metadata=None, **kwargs):
        """
        Initialize the catalog.

        Parameters
        ----------
        url: str
            A URL pointing to a DCAT catalog, usually named data.json
        name: str
            A name for the catalog
        metadata: dict
            Additional information about the catalog
        """
        self.url = url
        self.name = name
        super().__init__(name=name, metadata=metadata, **kwargs)

    def _load(self):
        """
        Load the catalog from the remote data source.
        """
        resp = requests.get(self.url)
        catalog = resp.json()
        self._entries = {
            entry["identifier"]: construct_entry(entry)
            for entry in catalog["dataset"]
            if should_include_entry(entry)
        }


def should_include_entry(dcat_entry):
    """
    Return if a given DCAT entry should be included in the dataset.
    Returns True if we can find a driver to load it (GeoJSON,
    Shapefile, CSV), False otherwise.
    """
    return get_relevant_distribution(dcat_entry) != None


def construct_entry(dcat_entry):
    """
    Construct an Intake catalog entry from a DCAT catalog entry.
    """
    driver, args = get_relevant_distribution(dcat_entry)
    name = dcat_entry["identifier"]
    description = f"## {dcat_entry['title']}\n\n{dcat_entry['description']}"
    return LocalCatalogEntry(
        name, description, driver, True, args=args, metadata=dcat_entry
    )
