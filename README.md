# intake-dcat

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/CityOfLosAngeles/intake-dcat/master?urlpath=lab%2Ftree%2Fexamples%2Fdemo.ipynb)

This is an [intake](https://intake.readthedocs.io/en/latest)
data source for [DCAT](https://www.w3.org/TR/vocab-dcat) catalogs.

These catalogs are a standardized format for describing metadata and access information
for public datasets, as described [here](https://project-open-data.cio.gov/v1.1/schema).
Many Socrata and ESRI data portals publish `data.json` files in this format describing their catalogs.
Two examples of thes can be found at

https://data.lacity.org/data.json

http://geohub.lacity.org/data.json

This project provides an opinionated way for users to load datasets from these catalogs into the scientific Python ecosystem.
At the moment it loads CSVs into Pandas dataframes and GeoJSON files into GeoDataFrames, and ESRI Shapefiles into GeoDataFrames.
Future formats could include plain JSON and Parquet.

## Requirements
```
intake >= 0.4.4
intake_geopandas >= 0.2.2
geopandas >= 0.5.0
```
## Installation

`intake-dcat` is published on PyPI.
You can install it by running the following in your terminal:
```bash
pip install intake-dcat
```

You can test the functionality by opening the example notebooks in the `examples/` directory:

### Usage

The package can be imported using
```python
from intake_dcat import DCATCatalog
```

### Loading a catalog

You can load data from a DCAT catalog by providing the URL to the `data.json` file:
```python
catalog = DCATCatalog('http://geohub.lacity.org/data.json', name='geohub')
len(list(catalog))
```

You can display the items in the catalog
```python
for entry_id, entry in catalog.items():
    display(entry)
```

If the catalog has too many entries to comfortably print all at once,
you can narrow it by searching for a term (e.g. 'district'):
```python
for entry_id, entry in catalog.search('district').items():
  display(entry)
```

### Loading a dataset
Once you have identified a dataset, you can load it into a dataframe using `read()`:

```python
df = entry.read()
```

This will automatically load that dataset into a Pandas dataframe, or a GeoDataFrame, depending on the source format.

### Command Line Interface

`intake-dcat` provides a small command line interface for some common operations.
These are invoked using `intake-dcat <subcommand> <options>`

#### The `mirror` command

This command loads a manifest file that lists a set of DCAT entries,
uploads them to a specified s3 bucket, and outputs a new catalog with identical entries
pointing to the bucket.

An example manifest is given by
```yml
# Name of the LA open data portal
la-open-data:
  # URL to the open data portal catalog
  url: https://data.lacity.org/data.json
  # The s3 bucket to upload the data to
  bucket_uri: s3://my-bucket
  # A list of data resources to mirror
  items:
    lapd_metrics: https://data.lacity.org/api/views/t6kt-2yic
# Name of the LA GeoHub data portal
la-geohub:
  # URL to the open data portal catalog
  url: http://geohub.lacity.org/data.json
  # The s3 bucket to upload the data to
  bucket_uri: s3://my-bucket
  # A list of data resources to mirror
  items:
    bikeways: http://geohub.lacity.org/datasets/2602345a7a8549518e8e3c873368c1d9_0 
    city_boundary: http://geohub.lacity.org/datasets/09f503229d37414a8e67a7b6ceb9ec43_7
```

This can be mirrored using the command

```bash
intake-dcat mirror manifest.yml > new-catalog.yml
```

This command uses the `boto3` library and assumes it can find AWS credentials.
For more information see [this documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html).

#### The `create` command

This command creates a new intake catalog from a DCAT catalog, and outputs it to standard out.
An example command is given by

```bash
intake-dcat create data.lacity.org/data.json > catalog.yml
```
