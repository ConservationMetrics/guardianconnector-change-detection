# GuardianConnector Change Detection

This WIP repo contains a Python script which takes an input GeoJSON file and generates several outputs to show the data on a satellite imagery map, and prepare offline map assets for usage in data collection applications.

## Prerequisites

* Install [Tippecanoe](https://github.com/felt/tippecanoe) for conversion of GeoJSON to vector MBTiles.

## Configure

Create a `.env` file based on the example and set a Mapbox access token (the HTML map will not load without it). The other Mapbox map properties are optional.

## Run the script

The command to run the script is:

```
python ./script.py --input [FILENAME].geojson --output [OUTPUT].geojson
```

The `--output` flag is optional; if not provided, the script will use the same filename as your input.

## Outputs

Currently, the script generates the following outputs in the `/outputs` directory:

* **GeoJSON**: a copy of the GeoJSON file.
* **HTML map**: to preview the GeoJSON file on a Mapbox satellite imagery + streets map. The map shows the GeoJSON as a label and zooms to the maximum extent of the data. Currently, the template is only mapping Point GeoJSON data.
* **Vector MBTiles**: MBTiles of the GeoJSON to be used in map stylesheets for data collection applications.
* **Stylesheet**: A `style.json` file which overlays the MBTiles on top of Bing satellite imagery. The reason for using Bing imagery is because Bing does not require access tokens, so we don't run into any issues with API token limits.

## How to use the outputs

ODK/Kobo Collect can [render the vector MBTiles](https://docs.getodk.org/collect-offline-maps/) but displayed without styling; each feature is displayed in a different color picked by the applications. However, the process of transferring the MBTile file(s) to the device is still somewhat cumbersome, involving either the use of a USB cable or `adb` (see link).

 Mapeo can import MBTile files directly using the background map manager UI, but is not able to render vector MBTiles (yet). Hence, we will either need to wait for that feature to be built, or find a way to generate a raster MBTiles from the output stylesheet. (This will be a desirable thing to figure out anyway, in order to get offline raster tiles for the Bing satellite imagery.)