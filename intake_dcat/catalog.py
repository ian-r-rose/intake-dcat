from collections import OrderedDict

import requests

from intake.catalog import Catalog
from intake.catalog.local import LocalCatalogEntry

class DCATCatalog(Catalog):
    name: str = 'dcat'
    url: str

    def __init__(self, url, metadata=None):
        self.url = url
        super().__init__(metadata)

    def _load(self):
        resp = requests.get(self.url)
        catalog = resp.json()
        self._entries = {
            entry['identifier']: _construct_entry(entry)
            for entry in catalog['dataset'] if _should_include_entry(entry)
        }
        

_container_map = {
    'application/vnd.geo+json': 'dataframe',
    'text/csv': 'dataframe',
    'application/json': 'dataframe',
}

def _should_include_entry(dcat_entry):
    return dcat_entry.get('distribution') != None

def _construct_entry(dcat_entry):
    name = dcat_entry['identifier']
    distribution = dcat_entry['distribution']
    args = { 'urlpath': distribution[0]['downloadURL'] }
    description = dcat_entry['description']
    driver = 'text'
    return LocalCatalogEntry(
            name,
            description,
            driver,
            True,
            metadata=dcat_entry
    )
