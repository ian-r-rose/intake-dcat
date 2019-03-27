from collections import OrderedDict

import requests

from intake.catalog import Catalog
from intake.catalog.local import LocalCatalogEntry

from .distributions import get_relevant_distribution

class DCATCatalog(Catalog):
    name: str
    url: str

    def __init__(self, url, name, metadata=None, **kwargs):
        self.url = url
        self.name = name
        super().__init__(name=name, metadata=metadata, **kwargs)

    def _load(self):
        resp = requests.get(self.url)
        catalog = resp.json()
        self._entries = {
            entry["identifier"]: construct_entry(entry)
            for entry in catalog["dataset"]
            if should_include_entry(entry)
        }

def should_include_entry(dcat_entry):
    return get_relevant_distribution(dcat_entry) != None


def construct_entry(dcat_entry):
    driver, args = get_relevant_distribution(dcat_entry)
    name = dcat_entry["identifier"]
    description = f"## {dcat_entry['title']}\n\n{dcat_entry['description']}"
    return LocalCatalogEntry(name, description, driver, True, args=args, metadata=dcat_entry)
