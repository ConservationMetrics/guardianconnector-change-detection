# GuardianConnector Change Detection

A Dockerized Python script which processes a GeoJSON input and generates several outputs for rendering on satellite imagery maps. In addition, it prepares offline map resources to load the data in data collection applications such as Kobo/ODK Collect and Mapeo.

You can execute this script using Docker or directly with Python (note that the latter option will require installing some dependencies).

## Steps

The `main.py` script follows these steps:

1. Copy GeoJSON file to outputs directory
2. Get bounding box for GeoJSON (all features)
3. Generate HTML Mapbox map for previewing change detection alert
4. Generate vector MBTiles from GeoJSON
5. Generate raster XYZ tiles from satellite imagery and bounding box
6. Convert raster XYZ directory to MBTiles
7. Generate stylesheet with both raster and vector MBTiles files
8. Download and copy over fonts and glyphs (needed for map style)
9. Generate overlay map HTML map (to preview style)
10. Serve maps using `tileserver-gl`
11. Generate composite MBTiles from `tileserver-gl` map loading the style

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

## Run the script with Docker

Execute the script using the command:

```
./run.sh --input [FILENAME].geojson --output [OUTPUT]
```

The `--output` flag is optional and can be used to name the directory and any files like MBTiles differently than your input file. If omitted, the script will employ the input filename for outputs.

## Run the script with Python

### Prerequisites
With `pip` (or your package manager of choice):
```
pip install -r requirements.txt
```

You will also need to install:

* `tippecanoe` according to the instructions in the [Github repo](https://github.com/mapbox/tippecanoe).

### Execute 
Execute the script using the command:

```
python ./main.py --input [FILENAME].geojson --output [OUTPUT]
```

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

## How to use the outputs

For **ODK/Kobo Collect**, you can use the final raster tileset as a background map for any geo fields by [transferring them to your device](https://docs.getodk.org/collect-offline-maps/). This process is still somewhat cumbersome, involving either the use of a USB cable or `adb` (see link). Also, while ODK/Kobo Collect can render the vector MBTiles, it is done without styling; each feature is displayed in a different color picked by the applications. 

 **Mapeo** can import raster MBTiles files directly using the background map manager UI. In the future, Mapeo will be able to render vector MBTiles too, and we can then retool this script (using the outputs in the `mapbox-map/` directory) to generate a file that conforms to the expected input from Mapeo.

![Raster mbtiles generated by this script loaded in Mapeo](images/mapeo.jpg)

*Raster mbtiles generated by this script loaded in Mapeo*