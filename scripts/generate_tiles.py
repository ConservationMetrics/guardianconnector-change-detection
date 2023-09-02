import sys
import os
import json
import requests
import subprocess
from shutil import copyfile
import mercantile

def generate_vector_mbtiles(geojson_input_path, output_directory, output_filename):
    # Create the mapbox-map dir if it doesn't already exist
    mapbox_map_dir = os.path.join(output_directory, "mapbox-map")
    os.makedirs(mapbox_map_dir, exist_ok=True)
    os.makedirs(f'{mapbox_map_dir}/tiles', exist_ok=True)

    vector_mbtiles_output_filename = str(output_filename) + '-vector'

    # Determine the full path to the output MBTiles file within the 'mapbox-map/' directory
    vector_mbtiles_output_path = os.path.join(mapbox_map_dir, 'tiles', f"{vector_mbtiles_output_filename}.mbtiles")

    # Generate MBTiles using tippecanoe
    command = f"tippecanoe -o {vector_mbtiles_output_path} --force --no-tile-compression {geojson_input_path}"

    try:
        os.system(command)
        print(f"\033[1m\033[32mVector MBTiles file generated:\033[0m {vector_mbtiles_output_path}")
    except Exception as e:
        print(f"\033[1m\033[31mError generating Vector MBTiles:\033[0m {e}")
        sys.exit(1)

def generate_raster_tiles(raster_imagery_url, raster_imagery_attribution, raster_max_zoom, bbox, output_directory, output_filename):
    xyz_output_dir = os.path.join(output_directory, "mapbox-map/tiles/xyz")
    os.makedirs(xyz_output_dir, exist_ok=True)

    bbox_top_left = bbox[0]
    bbox_bottom_right = bbox[2]

    # Convert lat/long to Bing XYZ style spherical mercator tiles using Mercanetile
    def latlon_to_tilexy(lat, lon, zoom):
        tile = mercantile.tile(lon, lat, zoom)
        return tile.x, tile.y

    def download_xyz_tile(xyz_url, filename):
        if os.path.exists(filename):
            return

        # Download the tile and save it to the specified location
        response = requests.get(xyz_url)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            # Uncomment the following line if you want to see each file download printed
            # print(f"Downloaded at zoom level {zoom_level}: {xyz_url} -> {filename}")
        else:
            print(f"Failed to download: {xyz_url} (Status code: {response.status_code})")
            print(response.text)

    print("Downloading satellite imagery raster XYZ tiles...")
    for zoom_level in range(1, int(raster_max_zoom) + 1):
        col_start, row_end = latlon_to_tilexy(bbox_top_left[1], bbox_top_left[0], zoom_level)
        col_end, row_start = latlon_to_tilexy(bbox_bottom_right[1], bbox_bottom_right[0], zoom_level)

        # Calciulate quadkey for Bing maps API download
        for col in range(col_start, col_end + 1):
            for row in range(row_start, row_end + 1):
                quadkey = ""
                for i in range(zoom_level, 0, -1):
                    digit = 0
                    mask = 1 << (i - 1)
                    if (col & mask) != 0:
                        digit += 1
                    if (row & mask) != 0:
                        digit += 2
                    quadkey += str(digit)

                xyz_url = raster_imagery_url.format(q=quadkey)

                filename = f"{xyz_output_dir}/{zoom_level}/{col}/{row}.jpg"
                os.makedirs(os.path.dirname(filename), exist_ok=True)

                download_xyz_tile(xyz_url, filename)
        print(f"Zoom level {zoom_level} downloaded")

    metadata = {
        "name": output_filename,
        "description": "Satellite imagery intersecting with the bounding box of the change detection alert GeoJSON",
        "version": "1.0.0",
        "attribution": raster_imagery_attribution,
        "format": "jpg",
        "type": "overlay"
    }

    metadata_file_path = os.path.join(xyz_output_dir, "metadata.json")

    with open(metadata_file_path, "w") as metadata_file:
        json.dump(metadata, metadata_file, indent=4)

    print(f"XYZ tiles metadata.json saved to {metadata_file_path}")

def convert_xyz_to_mbtiles(output_directory, output_filename):
    mapbox_map_dir = os.path.join(output_directory, 'mapbox-map')
    xyz_output_dir = os.path.join(mapbox_map_dir, 'tiles', 'xyz')
    raster_mbtiles_output_path = os.path.join(mapbox_map_dir, 'tiles', f"{output_filename}-raster.mbtiles")

    if os.path.exists(raster_mbtiles_output_path):
        os.remove(raster_mbtiles_output_path)
        print(f"Deleted existing MBTiles file: {raster_mbtiles_output_path}")

    # Convert XYZ to MBtiles using mbutil
    command = f"mb-util --image_format=jpg --silent {xyz_output_dir} {raster_mbtiles_output_path}"

    print("Creating raster mbtiles...")
    try:
        subprocess.call(command, shell=True)
        print()
        print("\033[1m\033[32mRaster MBTiles file generated:\033[0m", f"{raster_mbtiles_output_path}")
    except subprocess.CalledProcessError:
        raise RuntimeError(f"\033[1m\033[31mFailed to generate MBTiles using command:\033[0m {command}")