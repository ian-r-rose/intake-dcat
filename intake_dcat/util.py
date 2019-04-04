import copy
import os
from functools import reduce

import requests
import yaml

from dask.utils import tmpfile
import s3fs

from .catalog import DCATCatalog


fs = s3fs.S3FileSystem()


def mirror_data(manifest_file):
    new_catalog = {"sources": {}}
    with open(manifest_file) as f:
        manifest = yaml.safe_load(f)
        dcat = manifest.get("dcat")
        bucket_uri = manifest["bucket_uri"]
        if dcat:
            for catalog_name, catalog_data in dcat.items():
                catalog = DCATCatalog(catalog_data["url"], name=catalog_name)
                items = catalog_data["items"]
                for item in items:
                    entry = yaml.safe_load(catalog[item["id"]].yaml())["sources"][
                        item["id"]
                    ]
                    name = item["name"]
                    print(f"Mirroring {name}")
                    new_entry = _construct_remote_entry(bucket_uri, entry, name)
                    new_catalog["sources"][name] = new_entry

    return new_catalog


def _upload_data(old_uri, new_uri, dir=None):
    r = requests.get(old_uri)
    with tmpfile(dir=dir) as filename:
        with open(filename, "wb") as outfile:
            outfile.write(r.content)
        fs.put(filename, new_uri)


def _construct_remote_entry(bucket_uri, entry, name, directory=""):
    new_entry = copy.deepcopy(entry)
    old_uri = entry["args"]["urlpath"]
    new_uri = _construct_remote_uri(bucket_uri, entry, name, directory)
    new_entry["args"]["urlpath"] = new_uri
    _upload_data(old_uri, new_uri)
    return new_entry


def _construct_remote_uri(bucket_uri, entry, name, directory=""):
    urlpath = entry["args"].get("urlpath")
    _, ext = os.path.splitext(urlpath)
    key = f"{directory.strip('/')}/{name}{ext}" if directory else f"{name}{ext}"
    return f"{bucket_uri.strip('/')}/{key}"
