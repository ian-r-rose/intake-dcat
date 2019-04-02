# intake-dcat

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
Future formats could include plain JSON and ESRI Shapefiles.

## Requirements
```
intake >= 4.3
intake_geopandas
```
## Installation

Currently a work in progress, requires some unpublished versions of packages.
You can test the functionality by creating a conda enviromnent and then opening the example notebook:
```bash
conda env create -f environment.yml
jupyter lab
```

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

You can then list the items in the catalog
```python
for entry_id in catalog:
    print(entry_id, catalog[entry_id].description)
```

### Loading a dataset
Once you have identified a dataset, you can load it into a dataframe using `read()`:

```python
df = catalog[entry_id].read()
```

This will automatically load that dataset into a Pandas dataframe, or a GeoDataFrame, depending on the source format.

