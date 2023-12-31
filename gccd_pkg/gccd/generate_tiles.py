import os
import subprocess
import sys
import shutil
import json
import requests
import socket
import time
import math
import mercantile
import sqlite3

def generate_pmtiles_from_geotiff(raster_max_zoom, t_number, output_directory, output_filename):
    resources_dir = os.path.join(output_directory, "resources")
    os.makedirs(resources_dir, exist_ok=True)

    tif_filename = f"{output_filename}_{t_number}"
    tif_filepath = os.path.join(resources_dir, os.path.basename(tif_filename)) 
    xyz_dir = f"{resources_dir}/{tif_filename}/"
    mbtiles_file = f"{resources_dir}/{tif_filename}.mbtiles"
    pmtiles_file = f"{resources_dir}/{tif_filename}.pmtiles"

    try:
        # Convert GeoTIFF to XYZ
        geotiff_to_xyz(raster_max_zoom, tif_filepath, xyz_dir)

        # Convert XYZ to MBTiles
        xyz_to_mbtiles(xyz_dir, "png", mbtiles_file)

        # Convert MBTiles to PMTiles
        mbtiles_to_pmtiles(mbtiles_file, pmtiles_file)

        print(f"\033[1m\033[32mPMTiles file generated:\033[0m {pmtiles_file}")

    except Exception as e:
        print(f"\033[1m\033[31mError generating PMTiles:\033[0m {e}")
        sys.exit(1)

def generate_vector_mbtiles(output_directory, output_filename):
    # Create the mapgl-map dir if it doesn't already exist
    mapgl_dir = os.path.join(output_directory, "mapgl-map")
    os.makedirs(mapgl_dir, exist_ok=True)
    os.makedirs(f'{mapgl_dir}/tiles', exist_ok=True)

    vector_mbtiles_output_filename = str(output_filename) + '-vector'

    # Determine the full path to the output MBTiles file within the 'mapgl-map/' directory
    vector_mbtiles_output_path = os.path.join(mapgl_dir, 'tiles', f"{vector_mbtiles_output_filename}.mbtiles")

    # Generate MBTiles using tippecanoe
    command = f"tippecanoe -o {vector_mbtiles_output_path} --force {output_directory}/resources/{output_filename}.geojson"

    try:
        ret = os.system(command)
        if ret == 0:
            print(f"\033[1m\033[32mVector MBTiles file generated:\033[0m {vector_mbtiles_output_path}")
        else:
            print(f"\033[1m\033[31mError generating Vector MBTiles:\033[0m tippecanoe exit code {ret}")
            sys.exit(1)
    except Exception as e:
        print(f"\033[1m\033[31mError generating Vector MBTiles:\033[0m {e}")
        sys.exit(1)

def generate_raster_tiles(raster_imagery_url, raster_imagery_attribution, raster_max_zoom, bbox, output_directory, output_filename):
    xyz_output_dir = os.path.join(output_directory, "mapgl-map/tiles/xyz")
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
    
    # Much of the below code is adapted from Microsoft's Bing Maps Tile System documentation:
    # https://learn.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system
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

def convert_raster_tiles(output_directory, output_filename):
    mapgl_dir = os.path.join(output_directory, 'mapgl-map')
    xyz_output_dir = os.path.join(mapgl_dir, 'tiles', 'xyz')
    mbtiles_output_path = os.path.join(mapgl_dir, 'tiles', f"{output_filename}.mbtiles")
    xyz_to_mbtiles(xyz_output_dir, "jpg", mbtiles_output_path)

def geotiff_to_xyz(raster_max_zoom, tif_filepath, xyz_dir):
    command = f"gdal2tiles.py -p mercator -z 0-{raster_max_zoom} -w none -r bilinear --xyz {tif_filepath}.tif {xyz_dir}"
    ret = os.system(command)
    if ret != 0:
        raise Exception(f"gdal2tiles.py exit code {ret}")
        sys.exit(1)

def xyz_to_mbtiles(xyz_dir, image_format, mbtiles_file):
    if os.path.exists(mbtiles_file):
        os.remove(mbtiles_file)
        print(f"Deleted existing MBTiles file: {mbtiles_file}")

    # Convert XYZ to MBTiles using mb-util
    command = f"mb-util --image_format={image_format} --silent {xyz_dir} {mbtiles_file}"

    print("Creating MBTiles...")
    try:
        subprocess.call(command, shell=True)
        print()
        print("\033[1m\033[32mMBTiles file generated:\033[0m", f"{mbtiles_file}")

        shutil.rmtree(xyz_dir)
        print(f"Deleted XYZ directory: {xyz_dir}")
    except subprocess.CalledProcessError:
        raise RuntimeError(f"\033[1m\033[31mFailed to generate MBTiles using command:\033[0m {command}")
    
def mbtiles_to_pmtiles(mbtiles_file, pmtiles_file):
    if os.path.exists(pmtiles_file):
        os.remove(pmtiles_file)
        print(f"Deleted existing PMTiles file: {pmtiles_file}")

    # Convert MBTiles to PMTiles using go-pmtiles
    command = f"pmtiles convert {mbtiles_file} {pmtiles_file}"

    print("Creating PMTiles...")
    ret = os.system(command)
    os.remove(mbtiles_file)
    if ret != 0:
        raise Exception(f"pmtiles convert exit code {ret}")
        sys.exit(1)

def download_tile(zoom, x, y, url_template):
    tile_url = url_template.format(z=zoom, x=x, y=y)
    response = requests.get(tile_url)
    response.raise_for_status()
    return response.content

def latlon_to_tile(lat, lon, zoom):
    n = 2.0 ** zoom
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(math.radians(lat)) + (1 / math.cos(math.radians(lat)))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def wait_for_tileserver_gl(address, port):
    while True:
        try:
            response = requests.get(f'http://{address}:{port}/health')
            if response.status_code == 200:
                print('Health check: tileserver is ready')
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)

def generate_mbtiles_from_tileserver(bbox, maxzoom, raster_imagery_attribution, output_directory, output_filename, env_port):
    try:
        minzoom = 0
        maxzoom = int(maxzoom)

        environment = os.environ.get('ENVIRONMENT')

        if environment == 'docker':
            address = "tileserver-gl"
        else:
            address = "localhost"
            
        port = env_port if env_port is not None else "8080"

        url_template = f"http://{address}:{port}/styles/{output_filename}/{{z}}/{{x}}/{{y}}.jpg"

        longitudes = [coord[0] for coord in bbox]
        latitudes = [coord[1] for coord in bbox]

        bbox = [min(longitudes), min(latitudes), max(longitudes), max(latitudes)]
        west, south, east, north = bbox

        output_file = os.path.join(output_directory, f"{output_filename}.mbtiles")

        if os.path.exists(output_file):
            os.remove(output_file)

        # Wait until Tileserver-GL has fully started
        wait_for_tileserver_gl(address, port)
        
        print("Downloading composite raster tiles from Tileserver-GL...")
        conn = sqlite3.connect(output_file)
        cursor = conn.cursor()

        # Create the tiles table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tiles (
            zoom_level integer,
            tile_column integer,
            tile_row integer,
            tile_data blob
        )
        ''')

        # Create metadata table and insert basic values
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            name text,
            value text
        )
        ''')
        
        cursor.executemany('INSERT OR REPLACE INTO metadata (name, value) VALUES (?, ?)', [
            ('name', 'Composite change detection raster map'),
            ('type', 'baselayer'),
            ('version', '1.1'),
            ('description', raster_imagery_attribution),
            ('format', 'jpg'),
        ])

        for zoom in range(minzoom, maxzoom+1):
            start_x, start_y = latlon_to_tile(north, west, zoom)
            end_x, end_y = latlon_to_tile(south, east, zoom)

            for x in range(start_x, end_x + 1):
                for y in range(start_y, end_y + 1):
                    tile_data = download_tile(zoom, x, y, url_template)
                    # Note: The TMS y value needs to be flipped for the SQLite database.
                    flipped_y = (2**zoom - 1) - y
                    cursor.execute("INSERT INTO tiles (zoom_level, tile_column, tile_row, tile_data) VALUES (?, ?, ?, ?)", 
                                (zoom, x, flipped_y, tile_data))

        conn.commit()
        conn.close()

        print("\033[1m\033[32mComposite raster MBTiles file generated:\033[0m", f"{output_file}")
    except Exception as e:
        print()
        print("\033[1m\033[31mError occurred:\033[0m", str(e))
