# GuardianConnector Change Detection

A Python script which processes a GeoJSON input and generates several outputs for rendering on satellite imagery maps. In addition, it prepares offline map resources to load the data in data collection applications such as Kobo/ODK Collect and Mapeo.

## Prerequisites

With `pip` (or your package manager of choice):
```
pip install -r requirements.txt
```

You will also need to install `tippecanoe` per the instructions in the [Github repo](https://github.com/mapbox/tippecanoe).

## Configure

Create a `.env` file using the provided example as a template. The variables represent the following:

* `MAPBOX_ACCESS_TOKEN` (Mandatory): Access token for your Mapbox account, required for your HTML map to work.
* `MAPBOX_STYLE`: The background style used for your HTML map. Defaults to mapbox://styles/mapbox/satellite-streets-v11 if not provided.
* `MAPBOX_ZOOM`: Default zoom level for your HTML map. Defaults to 1 if not provided.
* `MAPBOX_CENTER_LONGITUDE`: Default center longitude for your HTML map. Defaults to 0 if not provided.
* `MAPBOX_CENTER_LATITUDE`: Default center latitude for your HTML map. Defaults to 0 if not provided.
* `RASTER_IMAGERY_URL` (Mandatory): URL for the source of your satellite imagery tiles that will be downloaded for offline usage. Note that if an API token is required that it must be appended to this URL. (If need be, the script can be expanded to handle this differently.)
* `RASTER_IMAGERY_ATTRIBUTION`: Attribution for your satellite imagery source. Currently this is added to the metadata of the raster MBTiles file.
* `RASTER_MBTILES_MAX_ZOOM`: Maximum zoom level up until which imagery tiles will be downloaded. Defaults to 14 if not provided.
* `RASTER_BUFFER_SIZE`: A buffer (in kilometers) to expand the imagery download beyond the bounding box of your GeoJSON file. Defaults to 0 if not provided.

## Run the script

Execute the script using the command:

```
python ./main.py --input [FILENAME].geojson --output [OUTPUT].geojson
```

The `--output` flag is optional. If omitted, the script will employ the input filename for outputs.

## Outputs

Once the script is run, it populates the `/outputs` directory with:

* **GeoJSON**: a duplicate of the input GeoJSON.
* **HTML map**: A preview of the GeoJSON overlayed on a Mapbox satellite imagery + streets map. The map renders each kind of GeoJSON geometry (Point, Polygon, LineString) and zooms to the maximum extent of the data. The map also adds a label for fields with key `type_of_alert`.
* **XYZ tiles**:  Satellite imagery tiles that overlap with the input GeoJSON's bounding box.
* **Vector MBTiles**: MBTiles format of the GeoJSON, intended for map stylesheets in data collection apps.
* **Raster MBTiles**: MBTiles format of the satellite imagery tiles.
* **Fonts and sprites**: font and sprite glyph resources required to load a Mapbox map.
* **Stylesheet**: A `style.json` file which overlays the MBTiles on top of satellite imagery.

Outputs are systematically organized as follows:

```
example/
├── example.geojson
├── example.html
├── mapbox-map/
│   ├── style.json
│   ├── index.html
│   ├── fonts/
│   │   ├── ... (font files)
│   ├── sprites/
│   │   ├── ... (sprite image files)
│   └── tiles/
│       ├── example-raster.mbtiles
│       └── example-vector.mbtiles
│       └── xyz/
│           ├── ... metadata.json
│           ├── ... (XYZ tile files) 
```

## How to use the outputs

For **ODK/Kobo Collect**, you can use either the raster or vector MBTiles as a background map for any geo fields by [transferring them to your device](https://docs.getodk.org/collect-offline-maps/). This process is still somewhat cumbersome, involving either the use of a USB cable or `adb` (see link). Also, while ODK/Kobo Collect can render the vector MBTiles, it is done without styling; each feature is displayed in a different color picked by the applications. 

 **Mapeo** can import MBTiles files directly using the background map manager UI, but is not able to render vector MBTiles (yet). Hence, to fully use the outputs of this script, we will either need to wait for that feature to be built, or generate an additional composite raster MBTiles from the output stylesheet, compiling both the raster (satellite imagery) and vector (GeoJSON alert) MBTiles.