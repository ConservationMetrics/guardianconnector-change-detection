# GuardianConnector Change Detection

A Python script which processes a GeoJSON input and generates several outputs for rendering on satellite imagery maps. In addition, it prepares offline map resources to load the data in data collection applications such as Kobo/ODK Collect and Mapeo.

## Prerequisites

With `pip` (or your package manager of choice):
```
pip install -r requirements.txt
```

You will also need to install `tippecanoe` per the instructions in the [Github repo](https://github.com/mapbox/tippecanoe).

## Configure

1. Create a `.env` file using the provided example as a template.
2. Set your Mapbox access token in the `.env` file. This is essential as the HTML map won't load without it. Additional Mapbox map properties are optional.
3. (Optional) Define the maximum zoom for your satellite imagery offline map in the `.env` file. By default, it uses a zoom level of 14 if no value is given.

## Run the script

Execute the script using the command:

```
python ./script.py --input [FILENAME].geojson --output [OUTPUT].geojson
```

The `--output` flag is optional. If omitted, the script will employ the input filename for outputs.

## Outputs

Once the script is run, it populates the `/outputs` directory with:

* **GeoJSON**: a duplicate of the input GeoJSON.
* **HTML map**: A preview of the GeoJSON overlayed on a Mapbox satellite imagery + streets map. The map renders each kind of GeoJSON geometry (Point, Polygon, LineString) and zooms to the maximum extent of the data. The map also adds a label for fields with key `type_of_alert`.
* **XYZ tiles**:  Imagery tiles derived from Bing maps satellite that overlap with the input GeoJSON's bounding box.
* **Vector MBTiles**: MBTiles format of the GeoJSON, intended for map stylesheets in data collection apps.
* **Raster MBTiles**: MBTiles format of the Bing satellite imagery tiles.
* **Fonts and sprites**: font and sprite glyph resources required to load a Mapbox map.
* **Stylesheet**: A `style.json` file which overlays the MBTiles on top of Bing satellite imagery.

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

 **Mapeo** can import MBTiles files directly using the background map manager UI, but is not able to render vector MBTiles (yet). Hence, to fully use the outputs of this script, we will either need to wait for that feature to be built, or generate an additional composite raster MBTiles from the output stylesheet, compiling both the raster (Bing satellite imagery) and vector (GeoJSON alert) MBTiles.