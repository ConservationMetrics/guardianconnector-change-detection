# GuardianConnector Change Detection

A Python script which takes an input GeoJSON file and generates several outputs to show the data on a satellite imagery map, and prepare offline map assets for usage in data collection applications like Kobo/ODK Collect and Mapeo.

## Prerequisites

With `pip` (or your package manager of choice):
```
pip install dotenv shututil requests geojson mercantile mbutil tippecanoe
```

## Configure

Create a `.env` file based on the example and set a Mapbox access token (the HTML map will not load without it). The other Mapbox map properties are optional.

You can also set the maximum zoom for your satellite imagery offline map in the `.env` file. If no value is provided, a default of 14 will be used.

## Run the script

The command to run the script is:

```
python ./script.py --input [FILENAME].geojson --output [OUTPUT].geojson
```

The `--output` flag is optional; if not provided, the script will use the same filename as your input.

## Outputs

Currently, the script generates the following outputs in the `/outputs` directory:

* **GeoJSON**: a copy of the GeoJSON file.
* **HTML map**: to preview the GeoJSON file on a Mapbox satellite imagery + streets map. The map shows the GeoJSON as a label and zooms to the maximum extent of the data. Currently, the template is only mapping Point GeoJSON data (and is labeling fields with key `type_of_alert`)
* **XYZ tiles**: Imagery tiles of Bing maps satellite imagery intersecting with the bounding box of the GeoJSON file in XYZ directory format. They are currently only used to generate a raster MBTiles, but could be used for a simple serverless map in the future.
* **Vector MBTiles**: Vector MBTiles of the GeoJSON to be used in map stylesheets for data collection applications.
* **Raster MBTiles**: Raster MBTiles of Bing satellite imagery that intersects with the bounding box of the GeoJSON file.
* **Fonts and sprites**: font and sprite glyph resources required to load a Mapbox map.
* **Stylesheet**: A `style.json` file which overlays the MBTiles on top of Bing satellite imagery. The reason for using Bing imagery is because Bing does not require access tokens, so we don't run into any issues with API token limits.

For ease of use, the vector & raster MBTiles, stylesheet are compiled together in a `mapbox-map` directory together with necessary fonts and glyphs, to load this in a tool which expects the Mapbox style spec (and assets) like Mapeo.

```
example/
├── example.geojson
├── example.html
├── mapbox-map/
│   ├── style.json
│   ├── fonts/
│   │   ├── ... (font files)
│   ├── sprites/
│   │   ├── ... (sprite image files)
│   └── tiles/
│       ├── example-raster.mbtiles
│       └── example-vector.mbtiles
└── xyz-tiles/
    ├── ... metadata.json
    ├── ... (XYZ tile files) 
```

## How to use the outputs

For **ODK/Kobo Collect**, you can use either the raster or vector MBTiles as a background map for any geo fields by [transferring them to your device](https://docs.getodk.org/collect-offline-maps/). This process is still somewhat cumbersome, involving either the use of a USB cable or `adb` (see link). Also, while ODK/Kobo Collect can render the vector MBTiles, it is done without styling; each feature is displayed in a different color picked by the applications. 

 **Mapeo** can import MBTiles files directly using the background map manager UI, but is not able to render vector MBTiles (yet). 
 Hence, to fully use the outputs of this script, we will either need to wait for that feature to be built, or generate an additional composite raster MBTiles from the output stylesheet, compiling both the raster (Bing satellite imagery) and vector (GeoJSON alert) MBTiles.