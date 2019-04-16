import copy
import os

import requests
import yaml

from dask.utils import tmpfile
import s3fs

from .catalog import DCATCatalog

# TODO: should we allow the user to pass in a s3fs session here?
fs = s3fs.S3FileSystem()


def mirror_data(manifest_file, upload=True, name=None, version=None):
    """
    Given a path the a manifest.yml file, download the relevant data,
    upload it to the specified bucket, and return a new catalog
    pointing at the data.

    Parameters
    ----------
    manifest_file: str
        A path to a manifest file.

    upload: boolean
        Whether to upload the datasets to the indicated bucket. Defaults to
        True, but can be set to false to perform a dry run.

    Returns
    -------
    A dictionary containing data for the new catalog.
    """
    new_catalog = {"metadata": {"name": name, "version": version}, "sources": {}}
    with open(manifest_file) as f:
        manifest = yaml.safe_load(f)
        for catalog_name, catalog_data in manifest.items():
            catalog = DCATCatalog(catalog_data["url"], name=catalog_name)
            bucket_uri = catalog_data["bucket_uri"]
            items = catalog_data["items"]
            for name, id in items.items():
                entry = yaml.safe_load(catalog[id].yaml())["sources"][id]
                new_entry = _construct_remote_entry(
                    bucket_uri, entry, name, upload=upload
                )
                new_catalog["sources"][name] = new_entry

    return new_catalog


def _upload_remote_data(old_uri, new_uri, dir=None):
    r = requests.get(old_uri)
    with tmpfile(dir=dir) as filename:
        with open(filename, "wb") as outfile:
            outfile.write(r.content)
        fs.put(filename, new_uri)


def _construct_remote_entry(bucket_uri, entry, name, directory="", upload=True):
    new_entry = copy.deepcopy(entry)
    old_uri = entry["args"]["urlpath"]
    new_uri = _construct_remote_uri(bucket_uri, entry, name, directory)
    new_entry["args"]["urlpath"] = new_uri
    if upload:
        _upload_remote_data(old_uri, new_uri)
    return new_entry


def _construct_remote_uri(bucket_uri, entry, name, directory=""):
    urlpath = entry["args"].get("urlpath")
    _, ext = os.path.splitext(urlpath)
    key = f"{directory.strip('/')}/{name}{ext}" if directory else f"{name}{ext}"
    return f"{bucket_uri.strip('/')}/{key}"
