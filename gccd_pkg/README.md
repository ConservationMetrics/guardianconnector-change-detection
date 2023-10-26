# gccd Python library

## Run

### Prerequisites
Build and install the library in one of two ways:

```
# Install in your current virtual env
cd gccd_pkg
pip install -e .
```

or

```
# Install in a isolated environment that lives at `gccd_pkg/.tox/py310/`
cd gccd_pkg
tox --notest
```

You will also need to install:

* `tippecanoe` according to the instructions in the [Github repo](https://github.com/mapbox/tippecanoe).

### Tests
Tox will both rebuild the package and run tests.

```
cd gccd_pkg
tox
```


### Execute
In the virtual environment where you installed gccd, execute the driver script `main.py`.

For development, you are likely to store your environment variables in an `.env` files,
so use `dotenv run` to slurp them up into Python's environment:

```
dotenv run -- main.py --input [FILENAME].geojson --output [OUTPUT]
```

If the necessary environment variables are already set (e.g. in production),
omit the `dotenv run --`.

The `--output` flag is optional and can be used to name the directory and any files like MBTiles differently than your input file. If omitted, the script will employ the input filename for outputs.

## Outputs

Once the script is run, it populates the `/outputs` directory with:

* **GeoJSON**: a duplicate of the input GeoJSON.
* **HTML map**: A preview of the GeoJSON overlayed on a Mapbox satellite imagery + streets map. The map renders each kind of GeoJSON geometry (Point, Polygon, LineString) and zooms to the maximum extent of the data. The map also adds a label for fields with key `type_of_alert`.
* **MBTiles**: A raster tileset which styles and overlays the input GeoJSON on top of satellite imagery, downloaded to the extent of the bounding box of the GeoJSON (or higher per the `RASTER_BUFFER_SIZE` env var).
