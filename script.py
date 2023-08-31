import argparse
import os
import sys
import traceback
import json
import geojson
import requests
import subprocess
import shutil
import math
import tarfile
from itertools import product
from dotenv import load_dotenv
from shutil import copyfile, copytree
import mercantile

# Load environment variables from .env file
load_dotenv()

# Get environment variables
mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')
mapbox_style = os.getenv('MAPBOX_STYLE')
mapbox_zoom = float(os.getenv('MAPBOX_ZOOM'))
mapbox_center_longitude = float(os.getenv('MAPBOX_CENTER_LONGITUDE'))
mapbox_center_latitude = float(os.getenv('MAPBOX_CENTER_LATITUDE'))
raster_max_zoom = os.getenv('RASTER_MBTILES_MAX_ZOOM')
xyz_url_template = os.getenv('XYZ_URL_TEMPLATE')

# Modular functions for script
def copy_geojson_file(input_path, output_directory, output_filename):
    try:
        # Determine the output GeoJSON filename
        geojson_output_filename = os.path.basename(input_path)
        # Determine the full path to the output GeoJSON file
        geojson_output_path = os.path.join(output_directory, geojson_output_filename)
        # Copy the GeoJSON file to the outputs directory
        copyfile(input_path, geojson_output_path)
        print(f"\033[1m\033[32mGeoJSON file copied to:\033[0m {geojson_output_path}")
    except Exception as e:
        print(f"\033[1m\033[31mError copying GeoJSON file:\033[0m {e}")
        sys.exit(1)

def read_geojson_file(input_path):
    try:
        with open(input_path, 'r') as geojson_file:
            geojson_data = geojson_file.read()
            return geojson_data
    except Exception as e:
        print(f"\033[1m\033[31mError reading GeoJSON file:\033[0m {e}")
        sys.exit(1)

def calculate_bounding_box(features):
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
    
    for feature in features: 
        coordinates = feature['geometry']['coordinates']
        min_x = min(min_x, coordinates[0])
        min_y = min(min_y, coordinates[1])
        max_x = max(max_x, coordinates[0])
        max_y = max(max_y, coordinates[1])
    
    return min_x, min_y, max_x, max_y

def load_html_template(template_path):
    try:
        with open(template_path, 'r') as template_file:
            return template_file.read()
    except Exception as e:
        print(f"\033[1m\033[31mError reading HTML template:\033[0m {e}")
        sys.exit(1)

def generate_map_html(mapbox_access_token, mapbox_style, mapbox_center_longitude, mapbox_center_latitude, mapbox_zoom, geojson_input_path, output_path, output_filename):

    # Determine the full path to the output HTML file
    output_html_path = os.path.join(output_path, output_filename + '.html')

    # Load the HTML template
    template_path = os.path.join('templates', 'map.html')
    html_template = load_html_template(template_path)

    # Insert environment variables into the HTML template
    html_template = html_template.replace('pk.ey', mapbox_access_token)
    html_template = html_template.replace('mapbox://styles/mapbox/satellite-streets-v11', mapbox_style)
    html_template = html_template.replace('center: [0, 0]', f'center: [{mapbox_center_longitude}, {mapbox_center_latitude}]')
    html_template = html_template.replace('zoom: 1', f'zoom: {mapbox_zoom}')

    # Replace the placeholder script in the template with the GeoJSON script
    final_html = html_template.replace('fetch(\'geojson-filename.geojson\')', f'fetch(\'{geojson_input_path}\')')

    # Write the final HTML content to the output file
    try:
        with open(output_html_path, 'w') as output_html_file:
            output_html_file.write(final_html)
        print(f"\033[1m\033[32mMap HTML file generated:\033[0m {output_html_path}")
    except Exception as e:
        print(f"\033[1m\033[31mError writing HTML output file:\033[0m {e}")
        sys.exit(1)

def generate_vector_mbtiles(geojson_input_path, output_directory, output_filename):
    # Create the Mapbox-map dir if it doesn't already exist
    mapbox_map_dir = os.path.join(output_directory, "mapbox-map")
    os.makedirs(mapbox_map_dir, exist_ok=True)
    os.makedirs(f'{mapbox_map_dir}/tiles', exist_ok=True)

    vector_mbtiles_output_filename = str(output_filename) + '-vector'

    # Determine the full path to the output MBTiles file within the 'mapbox-map/' directory
    vector_mbtiles_output_path = os.path.join(mapbox_map_dir, 'tiles', f"{vector_mbtiles_output_filename}.mbtiles")

    # Generate MBTiles using tippecanoe
    command = f"tippecanoe -o {vector_mbtiles_output_path} --force --no-tile-compression {geojson_input_path} --layer=geojson-layer"

    try:
        os.system(command)
        print(f"\033[1m\033[32mVector MBTiles file generated:\033[0m {vector_mbtiles_output_path}")
    except Exception as e:
        print(f"\033[1m\033[31mError generating Vector MBTiles:\033[0m {e}")
        sys.exit(1)

def generate_raster_tiles(xyz_url_template, raster_max_zoom, bbox, output_directory, output_filename):
    xyz_output_dir = os.path.join(output_directory, 'xyz-tiles')
    os.makedirs(xyz_output_dir, exist_ok=True)

    bbox_top_left = bbox[0]
    bbox_bottom_right = bbox[2]

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
            # Remove hash if you want to see each file download printed
            # print(f"Downloaded at zoom level {zoom_level}: {xyz_url} -> {filename}")
        else:
            print(f"Failed to download: {xyz_url} (Status code: {response.status_code})")
            print(response.text)

    print("Downloading satellite imagery raster XYZ tiles...")
    for zoom_level in range(1, int(raster_max_zoom) + 1):
        col_start, row_end = latlon_to_tilexy(bbox_top_left[1], bbox_top_left[0], zoom_level)
        col_end, row_start = latlon_to_tilexy(bbox_bottom_right[1], bbox_bottom_right[0], zoom_level)

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

                xyz_url = xyz_url_template.format(q=quadkey)

                filename = f"{xyz_output_dir}/{zoom_level}/{col}/{row}.jpg"
                os.makedirs(os.path.dirname(filename), exist_ok=True)

                download_xyz_tile(xyz_url, filename)
        print(f"Zoom level {zoom_level} downloaded")

    metadata = {
        "name": output_filename,
        "description": "Satellite imagery from Bing Virtual Earth intersecting with the bounding box of the change detection alert GeoJSON",
        "version": "1.0.0",
        "attribution": "Conservation Metrics",
        "format": "jpg",
        "type": "overlay"
    }

    metadata_file_path = os.path.join(xyz_output_dir, "metadata.json")

    with open(metadata_file_path, "w") as metadata_file:
        json.dump(metadata, metadata_file, indent=4)

    print(f"XYZ tiles metadata.json saved to {metadata_file_path}")

def convert_xyz_to_mbtiles(output_directory, output_filename):
    xyz_output_dir = os.path.join(output_directory, 'xyz-tiles')
    mapbox_map_dir = os.path.join(output_directory, "mapbox-map")
    raster_mbtiles_output_path = os.path.join(mapbox_map_dir, 'tiles', f"{output_filename}-raster.mbtiles")

    if os.path.exists(raster_mbtiles_output_path):
        os.remove(raster_mbtiles_output_path)
        print(f"Deleted existing MBTiles file: {raster_mbtiles_output_path}")

    command = f"mb-util --image_format=jpg --silent {xyz_output_dir} {raster_mbtiles_output_path}"

    print("Creating raster mbtiles...")
    try:
        subprocess.call(command, shell=True)
        print()
        print("\033[1m\033[32mRaster MBTiles file generated:\033[0m", f"{raster_mbtiles_output_path}")
    except subprocess.CalledProcessError:
        raise RuntimeError(f"\033[1m\033[31mFailed to generate MBTiles using command:\033[0m {command}")

def generate_style_with_mbtiles(output_directory, output_filename):
    mapbox_map_dir = os.path.join(output_directory, "mapbox-map")
    style_template_path = os.path.join('templates', 'style.json')
    try:
        with open(style_template_path, 'r') as style_template_file:
            style_template = json.load(style_template_file)
    except Exception as e:
        print(f"\033[1m\033[31mError reading style.json template:\033[0m {e}")
        sys.exit(1)

    # ...

    # Add mbtiles sources and layers to style.json template
    vector_source = {
        "type": "vector",
        "url": f"{output_filename}-vector/{{z}}/{{x}}/{{y}}.pbf"
    }

    raster_source = { 
        "type": "raster",
        "url": f"{output_filename}-raster/{{z}}/{{x}}/{{y}}.jpg",
         "tileSize": 256,
        "maxzoom": raster_max_zoom   
    }

    raster_layer = {
        "id": "satellite-layer",
        "type": "raster",
        "source": "raster-source",
        "paint": {}
    }

    vector_layer = {
        "id": "vector-layer",
        "type": "circle",
        "source": "vector-source",
        "source-layer": "points",
        "paint": {
            "circle-radius": 6,
            "circle-color": "#ff0000"
        }
    }

    label_layer = {
        "id": "label-layer",
        "type": "symbol",
        "source": "vector-source",
        "source-layer": "points",
        "layout": {
            'text-field': ['get', 'type_of_alert'],
            'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],
            'text-offset': [0, -0.5],
            'text-anchor': 'bottom',
            'icon-image': 'border-dot-13'
        },
        "paint": {
            'text-color': '#FFA500',
            'text-halo-color': 'black',
            'text-halo-width': 1,
            'text-halo-blur': 1
        }
    }

    style_template['sources']['vector_source'] = vector_source
    style_template['sources']['raster_source'] = raster_source
    style_template['layers'].append(raster_layer)
    style_template['layers'].append(vector_layer)
    style_template['layers'].append(label_layer)

    # Write the final style.json content to the output file
    style_output_path = os.path.join(mapbox_map_dir, 'style.json')
    try:
        with open(style_output_path, 'w') as style_output_file:
            json.dump(style_template, style_output_file, indent=4)
    except Exception as e:
        print(f"\033[1m\033[31mError writing style.json output file:\033[0m {e}")
        sys.exit(1)

    print(f"\033[1m\033[32mStyle JSON file generated:\033[0m {style_output_path}")

def copy_fonts_and_sprites(output_directory):
    mapbox_map_dir = os.path.join(output_directory, "mapbox-map")
    fonts_archive_path = 'templates/fonts.tar.gz'
    sprites_dir_path = os.path.join('templates', 'sprites')
    output_fonts_dir = os.path.join(mapbox_map_dir, 'fonts')
    output_sprites_dir = os.path.join(mapbox_map_dir, 'sprites')

    try:
        if not os.path.exists(output_fonts_dir):
            # Untar fonts
            with tarfile.open(fonts_archive_path, 'r:gz') as archive:
                archive.extractall(output_fonts_dir)
            print(f"\033[1m\033[32mFonts copied to:\033[0m {output_fonts_dir}")

        if not os.path.exists(output_sprites_dir):
            shutil.copytree(sprites_dir_path, output_sprites_dir)
            print(f"\033[1m\033[32mSprites copied to:\033[0m {output_sprites_dir}")
    except Exception as e:
        print(f"\033[1m\033[31mAn error occurred while copying fonts and sprites:\033[0m {e}")

def main():
    # Get arguments from command line
    parser = argparse.ArgumentParser(description='Generate HTML and MBTiles files with GeoJSON data.')
    parser.add_argument('--input', required=True, help='Path to the input GeoJSON file')
    parser.add_argument('--output', help='Path to the output files')
    args = parser.parse_args()

    input_geojson_path = args.input

    # If output flag is not provided, set the output name to match the GeoJSON filename
    if args.output is None:
        # Prepare output directory
        output_filename = os.path.splitext(os.path.basename(input_geojson_path))[0]
        subdir_name = os.path.splitext(os.path.basename(input_geojson_path))[0]
        output_directory = os.path.join('outputs', subdir_name)
    else:
        output_filename = args.output
        output_directory = args.output
    
    os.makedirs(output_directory, exist_ok=True)

    try:
        # Call the modularized functions to perform different steps
        # STEP 1: Copy GeoJSON file to outputs
        copy_geojson_file(input_geojson_path, output_directory, output_filename)

        # STEP 2: Get bounding box for GeoJSON
        geojson_data = read_geojson_file(input_geojson_path)
        geojson_object = geojson.loads(geojson.dumps(geojson_data))
        geojson_dict = json.loads(geojson_data)
        features = geojson_dict["features"]
        min_lon, min_lat, max_lon, max_lat = calculate_bounding_box(features)
        bounding_box = {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [[min_lon, min_lat], [max_lon, min_lat], [max_lon, max_lat], [min_lon, max_lat], [min_lon, min_lat]]
                ]
            }
        }
        print(f"\033[1m\033[32mGeoJSON Bounding Box:\033[0m", bounding_box)

        # STEP 3: Generate HTML Mapbox map for previewing change detection alert
        generate_map_html(mapbox_access_token, mapbox_style, mapbox_center_longitude, mapbox_center_latitude, mapbox_zoom, input_geojson_path, output_directory, output_filename)

        # STEP 4: Generate vector MBTiles from GeoJSON
        generate_vector_mbtiles(input_geojson_path, output_directory, output_filename)

        # STEP 5: Generate raster XYZ tiles from satellite imagery and bbox
        generate_raster_tiles(xyz_url_template, raster_max_zoom, bounding_box['geometry']['coordinates'][0], output_directory, output_filename)
        
        # STEP 6: Convert raster XYZ directory to MBTiles
        convert_xyz_to_mbtiles(output_directory, output_filename)

        # STEP 7: Generate stylesheet with MBTiles included
        generate_style_with_mbtiles(output_directory, output_filename)

        # STEP 8: Copy over fonts and glyphs
        copy_fonts_and_sprites(output_directory)

    except Exception as e:
        exc_type, exc_obj, tb = sys.exc_info()
        lineno = tb.tb_lineno
        error_message = f"An error occurred on line {lineno}: {e}"
        traceback_message = traceback.format_exc()
        print(f"\033[1m\033[31m{error_message}\n{traceback_message}\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()
