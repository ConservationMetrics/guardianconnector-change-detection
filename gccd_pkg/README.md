# gccd Python library

## Configure

Create a `.env` file using the provided example as a template. The variables represent the following:

* `MAPBOX_ACCESS_TOKEN` <span style="color:red">(required)</span>: Access token for your Mapbox account, required for your HTML map to work.
* `MAPBOX_STYLE`: The background style used for your HTML map. Defaults to mapbox://styles/mapbox/satellite-streets-v11 if not provided.
* `MAPBOX_ZOOM`: Default zoom level for your HTML map. Defaults to 1 if not provided.
* `MAPBOX_CENTER_LONGITUDE`: Default center longitude for your HTML map. Defaults to 0 if not provided.
* `MAPBOX_CENTER_LATITUDE`: Default center latitude for your HTML map. Defaults to 0 if not provided.
* `RASTER_IMAGERY_URL` <span style="color:red">(required)</span>: URL for the source of your satellite imagery tiles that will be downloaded for offline usage. Note that if an API token is required that it must be appended to this URL.
* `RASTER_IMAGERY_ATTRIBUTION`: Attribution for your satellite imagery source. Currently this is added to the metadata of the raster MBTiles file.
* `RASTER_MBTILES_MAX_ZOOM`: Maximum zoom level up until which imagery tiles will be downloaded. Defaults to 14 if not provided.
* `RASTER_BUFFER_SIZE`: A buffer (in kilometers) to expand the imagery download beyond the bounding box of your GeoJSON file. Defaults to 0 if not provided.
* `PORT`: If running the Python scripts outside of Docker, you may choose to specify a different port for `tileserver-gl` to run on. Defaults to 8080 if not specified.

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

The script also generates a `mapbox-map` directory with map resources placed in accordance to the Mapbox style spec:

* **XYZ tiles**:  Satellite imagery tiles that overlap with the input GeoJSON's bounding box. (These are used to generate the Raster MBTiles and could be deleted, but are kept here in case they are useful for a different purpose.)
* **Vector MBTiles**: MBTiles format of the GeoJSON, intended for map stylesheets in data collection apps.
* **Raster MBTiles**: MBTiles format of the satellite imagery tiles.
* **Fonts and sprites**: font and sprite glyph resources required to load a Mapbox map. Only Open Sans Regular is compiled (which is what is used in the style).
* **Stylesheet**: A `style.json` file which overlays the MBTiles on top of satellite imagery.

Outputs are systematically organized as follows (using `example` output):

```
example/
├── example.geojson
├── example.html
├── example.mbtiles
└── mapbox-map/
    ├── style.json
    ├── index.html
    ├── fonts/
    │   └── Open Sans Regular/
    │   │   ├── ... font glyphs
    ├── sprites/
    │   ├── ... (sprite image files)
    └── tiles/
        ├── example-raster.mbtiles
        └── example-vector.mbtiles
        └── xyz/
            ├── ... metadata.json
            ├── ... (XYZ tile files)
```