import requests
import yaml

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
            entry["identifier"]: DCATEntry(entry)
            for entry in catalog["dataset"]
            if should_include_entry(entry)
        }

    def serialize(self):
        """
        Serialize the catalog to yaml.

        Returns
        -------
        A string with the yaml-formatted catalog.
        """
        output = {"metadata": self.metadata, "sources": {}}
        for key, entry in self.items():
            output["sources"][key] = yaml.safe_load(entry.yaml())["sources"][key]
        return yaml.dump(output)


class DCATEntry(LocalCatalogEntry):
    """
    A class representign a DCAT catalog entry, which knows how to pretty-print itself.
    """

    def __init__(self, dcat_entry):
        """
        Construct an Intake catalog entry from a DCAT catalog entry.
        """
        driver, args = get_relevant_distribution(dcat_entry)
        name = dcat_entry["identifier"]
        description = f"## {dcat_entry['title']}\n\n{dcat_entry['description']}"
        metadata = {"dcat": dcat_entry}
        super().__init__(name, description, driver, True, args=args, metadata=metadata)

    def _ipython_display_(self):
        """
        Print an HTML repr for the entry
        """
        dcat = self.metadata["dcat"]
        title = dcat.get("title") or "unknown"
        entry_id = dcat.get("identifier")
        description = dcat.get("description")
        issued = dcat.get("issued") or "unknown"
        modified = dcat.get("modified") or "unknown"
        license = dcat.get("license") or "unknown"
        organization = dcat.get("publisher")
        publisher = organization.get("name") or "unknown" if organization else "unknown"
        download = self._open_args.get("urlpath") or "unknown"

        info = f"""
            <p style="margin-bottom: 0.5em"><b>ID:</b><a href="{entry_id}"> {entry_id}</a></p>
            <p style="margin-bottom: 0.5em"><b>Issued:</b> {issued}</p>
            <p style="margin-bottom: 0.5em"><b>Last Modified:</b> {modified}</p>
            <p style="margin-bottom: 0.5em"><b>Publisher:</b> {publisher}</p>
            <p style="margin-bottom: 0.5em"><b>License:</b> {license}</p>
            <p style="margin-bottom: 0.5em"><b>Download URL:</b><a href="{download}"> {download}</a></p>
        """
        html = f"""
        <h3>{title}</h3>
        <div style="display: flex; flex-direction: row; flex-wrap: wrap; height:256px">
            <div style="flex: 0 0 256px; padding-right: 24px">
                {info}
            </div>
            <div style="flex: 1 1 0; height: 100%; overflow: auto">
                <p>
                    {description}
                </p>
            </div>
        </div>
        """

        return display({
            "text/html": html,
            "text/plain": "\n".join([entry_id, title, description]),
        }, raw=True)


def should_include_entry(dcat_entry):
    """
    Return if a given DCAT entry should be included in the dataset.
    Returns True if we can find a driver to load it (GeoJSON,
    Shapefile, CSV), False otherwise.
    """
    return get_relevant_distribution(dcat_entry) != None
