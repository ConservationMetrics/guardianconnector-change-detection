import argparse
import os
import sys
from dotenv import load_dotenv
import json
import geojson
from shutil import copyfile
import requests
from itertools import product
import subprocess

# Load environment variables from .env file
load_dotenv()

# Get environment variables
mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')
mapbox_style = os.getenv('MAPBOX_STYLE')
mapbox_zoom = float(os.getenv('MAPBOX_ZOOM'))
mapbox_center_longitude = float(os.getenv('MAPBOX_CENTER_LONGITUDE'))
mapbox_center_latitude = float(os.getenv('MAPBOX_CENTER_LATITUDE'))

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Generate HTML and MBTiles files with GeoJSON data.')
parser.add_argument('--input', required=True, help='Path to the input GeoJSON file')
parser.add_argument('--output', help='Path to the output files')
args = parser.parse_args()

# Determine the output directory based on --output or input filename
if args.output is None:
    subdir_name = os.path.splitext(os.path.basename(args.input))[0]
    output_directory = os.path.join('outputs', subdir_name)
else:
    output_directory = os.path.join('outputs', args.output)
    
# Create the output subdirectory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# STEP 1: Copy GeoJSON file to outputs
# Determine the output GeoJSON filename
if args.output is None:
    geojson_output_filename = os.path.basename(args.input)
else:
    geojson_output_filename = os.path.basename(args.output) + '.geojson'

# Determine the full path to the output GeoJSON file
geojson_output_path = os.path.join(output_directory, geojson_output_filename)

# Copy the GeoJSON file to the outputs directory
try:
    copyfile(args.input, geojson_output_path)
    print(f"\033[1m\033[32mGeoJSON file copied to:\033[0m {geojson_output_path}")
except Exception as e:
    print(f"\033[1m\033[31mError copying GeoJSON file:\033[0m {e}")
    sys.exit(1)

# STEP 2: Get bounding box for GeoJSON
# Ensure the specified GeoJSON file exists
if not os.path.exists(args.input):
    print(f"\033[1m\033[31mError:\033[0m GeoJSON file '{args.input}' does not exist.")
    sys.exit(1)

# Read the GeoJSON data from the input file
try:
    with open(args.input, 'r') as geojson_file:
        geojson_data = geojson_file.read()
except Exception as e:
    print(f"\033[1m\033[31mError reading GeoJSON file:\033[0m {e}")
    sys.exit(1)

# Convert the string representation of GeoJSON to a GeoJSON object and dictionary
geojson_object = geojson.loads(geojson.dumps(geojson_data))
geojson_dict = json.loads(geojson_data)

features = geojson_dict["features"]

# Calculate bounding box
def calculate_bounding_box(geojson_dict):
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
    
    for feature in features: 
        coordinates = feature['geometry']['coordinates']
        min_x = min(min_x, coordinates[0])
        min_y = min(min_y, coordinates[1])
        max_x = max(max_x, coordinates[0])
        max_y = max(max_y, coordinates[1])
    
    return min_x, min_y, max_x, max_y

min_lon, min_lat, max_lon, max_lat = calculate_bounding_box(geojson_object)
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
# If --output flag is not provided, set the output filename to match the GeoJSON filename
if args.output is None:
    output_filename = os.path.splitext(os.path.basename(args.input))[0]
else:
    output_filename = args.output

# Determine the full path to the output HTML file
output_path = os.path.join(output_directory, output_filename + '.html')

# Load the HTML template
template_path = os.path.join('templates', 'map.html')
try:
    with open(template_path, 'r') as template_file:
        html_template = template_file.read()
except Exception as e:
    print(f"\033[1m\033[31mError reading HTML template:\033[0m {e}")
    sys.exit(1)

# Insert environment variables into the HTML template
html_template = html_template.replace('pk.ey', mapbox_access_token)
html_template = html_template.replace('mapbox://styles/mapbox/satellite-streets-v11', mapbox_style)
html_template = html_template.replace('center: [0, 0]', f'center: [{mapbox_center_longitude}, {mapbox_center_latitude}]')
html_template = html_template.replace('zoom: 1', f'zoom: {mapbox_zoom}')

# Replace the placeholder script in the template with the GeoJSON script
final_html = html_template.replace('fetch(\'geojson-filename.geojson\')', f'fetch(\'{args.input}\')')

# Write the final HTML content to the output file
try:
    with open(output_path, 'w') as output_html_file:
        output_html_file.write(final_html)
except Exception as e:
    print(f"\033[1m\033[31mError writing HTML output file:\033[0m {e}")
    sys.exit(1)

print(f"\033[1m\033[32mMap HTML file generated:\033[0m {output_path}")

# STEP 4: Generate vector MBTiles from GeoJSON
# Determine the output MBTiles filename
if args.output is None:
    v_mbtiles_output_filename = os.path.splitext(os.path.basename(args.input))[0] + '-vector.mbtiles'
else:
    v_mbtiles_output_filename = os.path.splitext(os.path.basename(args.output))[0] + '-vector.mbtiles'

# Determine the full path to the output MBTiles file
v_mbtiles_output_path = os.path.join(output_directory, v_mbtiles_output_filename)

# Generate MBTiles using tippecanoe
command = f"tippecanoe -o {v_mbtiles_output_path} --force --no-tile-compression {args.input} --layer=geojson-layer"

try:
    os.system(command)
    print(f"\033[1m\033[32mMBTiles file generated:\033[0m {v_mbtiles_output_path}")
except Exception as e:
    print(f"\033[1m\033[31mError generating MBTiles:\033[0m {e}")
    sys.exit(1)
    
# STEP 5: Generate raster MBTiles from satellite imagery and bbox
# Define the XYZ tile URL template; this is currently set to Bing Virtual Earth
xyz_url_template = "http://ecn.t3.tiles.virtualearth.net/tiles/a{q}.jpeg?g=1"

# Define the max zoom level and bounding box
r_max_zoom = 14
bbox = bounding_box['geometry']['coordinates'][0]

# Define the output directory
xyz_output_dir = f"{output_directory}/xyz_tiles"

# Create the output directory if it doesn't exist
os.makedirs(xyz_output_dir, exist_ok=True)

# Iterate through the zoom levels and rows and columns of tiles within the bounding box
# TODO: calibrate this using Bing maps tile system: https://learn.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system
for zoom_level in range(1, r_max_zoom + 1):
    num_tiles = 2 ** zoom_level

    col_range = row_range = range(num_tiles)

    for col, row in product(col_range, row_range):
        # Calculate the geographical coordinates of the current tile's corners
        lon_left = -180 + 360 * col / num_tiles
        lon_right = -180 + 360 * (col + 1) / num_tiles
        lat_top = 90 - 180 * row / num_tiles
        lat_bottom = 90 - 180 * (row + 1) / num_tiles

        # Check if the current tile's bounding box intersects with the area of interest
        if (lon_right >= bbox[0][0] and lon_left <= bbox[1][0] and
            lat_bottom <= bbox[1][1] and lat_top >= bbox[0][1]):

            # Generate the quadkey based on the current row and column
            quadkey = ""
            for i in range(zoom_level, 1, -1):
                digit = 0
                mask = 1 << (i - 1)
                if (col & mask) != 0:
                    digit += 1
                if (row & mask) != 0:
                    digit += 2
                quadkey += str(digit)

            # Construct the XYZ tile URL
            xyz_url = xyz_url_template.format(q=quadkey)

            # Define the filename for the downloaded tile
            filename = f"{xyz_output_dir}/{zoom_level}/{row}/{col}.jpg"

            # Create the directory structure if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            # Download the tile and save it to the specified location
            response = requests.get(xyz_url)
            if response.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(response.content)
                print(f"Downloaded: {xyz_url} -> {filename}")
            else:
                print(f"Failed to download: {xyz_url}")

# STEP 6: Convert XYZ directory to MBTiles
# Determine the output MBTiles filename
if args.output is None:
    r_mbtiles_output_filename = os.path.splitext(os.path.basename(args.input))[0] + '-raster.mbtiles'
else:
    r_mbtiles_output_filename = os.path.splitext(os.path.basename(args.output))[0] + '-raster.mbtiles'

command = f"mb-util {xyz_output_dir} {output_directory}/{r_mbtiles_output_filename}"

try:
    subprocess.call(command, shell=True)
    print("\033[1m\033[32mRaster MBTiles file generated:\033[0m", r_mbtiles_output_filename)
except subprocess.CalledProcessError:
    raise RuntimeError(f"\033[1m\033[31mFailed to generate MBTiles using command:\033[0m {command}")

# STEP 6: Generate stylesheet with MBTiles included
# Load the style.json template
style_template_path = os.path.join('templates', 'style.json')
try:
    with open(style_template_path, 'r') as style_template_file:
        style_template = json.load(style_template_file)
except Exception as e:
    print(f"\033[1m\033[31mError reading style.json template:\033[0m {e}")
    sys.exit(1)

# Add mbtiles sources and layers to style.json template
vector_source = {
    "type": "vector",
    "url": f"mbtiles://{v_mbtiles_output_filename}",
    "maxzoom": 14  # Adjust maxzoom as needed
}

raster_source = { 
    "type": "raster",
    "url": f"mbtiles://{r_mbtiles_output_filename}",
    "maxzoom": r_max_zoom  # Adjust maxzoom as needed    
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
style_output_path = os.path.join(output_directory, 'style.json')
try:
    with open(style_output_path, 'w') as style_output_file:
        json.dump(style_template, style_output_file, indent=4)
except Exception as e:
    print(f"\033[1m\033[31mError writing style.json output file:\033[0m {e}")
    sys.exit(1)

print(f"\033[1m\033[32mStyle JSON file generated:\033[0m {style_output_path}")