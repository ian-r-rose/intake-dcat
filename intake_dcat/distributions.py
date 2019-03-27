import re


def get_relevant_distribution(dcat_entry):
    """
    Given a DCAT entry, find the most relevant distribution
    for the intake catalog. Returns a tuple of
    (intake_driver_name, distribution). In general,
    we choose the more specific formats over the less specific
    formats. At present, they are ranked in the following order:

        GeoJSON
        Shapefile
        CSV

    If none of these are found, None.
    If there are no distributions, it returns None.
    """
    distributions = dcat_entry.get("distribution")
    if not distributions or not len(distributions):
        return None

    for d in distributions:
        if test_geojson(d):
            return "geojson", geojson_driver_args(d)
    for d in distributions:
        if test_shapefile(d):
            return "shapefile", shapefile_driver_args(d)
    for d in distributions:
        if test_csv(d):
            return "csv", csv_driver_args(d)

    return None


def test_geojson(distribution):
    """
    Test if a DCAT:distribution is GeoJSON.
    """
    return distribution.get("mediaType") == "application/vnd.geo+json"


def test_csv(distribution):
    """
    Test if a DCAT:distribution is CSV.
    """
    return distribution.get("mediaType") == "text/csv"


def test_shapefile(distribution):
    """
    Test if a DCAT:distribution is a Shapefile.
    """
    # TODO: can there be a more robust test here?
    url = distribution.get("downloadURL") or ""
    title = distribution.get("title") or ""
    return (
        title.lower() == "shapefile"
        or re.search("format=shapefile", url, re.I) is not None
    )


def geojson_driver_args(distribution):
    """
    Construct driver args for a GeoJSON distribution.
    """
    url = distribution["downloadURL"]
    return {"urlpath": url}


def csv_driver_args(distribution):
    """
    Construct driver args for a GeoJSON distribution.
    """
    url = distribution["downloadURL"]
    return {"urlpath": url, "csv_kwargs": {"blocksize": None, "sample": False}}


def shapefile_driver_args(distribution):
    """
    Construct driver args for a GeoJSON distribution.
    """
    url = distribution["downloadURL"]
    args = {"urlpath": url, "geopandas_kwargs": {}}
    if distribution["mediaType"] == "application/zip":
        args["geopandas_kwargs"]["compression"] = "zip"
    return args
