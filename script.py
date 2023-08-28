import argparse
import os
import sys
from dotenv import load_dotenv
import json
from shutil import copyfile

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
    print(f"GeoJSON file copied to: {geojson_output_path}")
except Exception as e:
    print(f"Error copying GeoJSON file: {e}")
    sys.exit(1)

# STEP 2: Generate HTML Mapbox map for previewing change detection alert
# If --output flag is not provided, set the output filename to match the GeoJSON filename
if args.output is None:
    output_filename = os.path.splitext(os.path.basename(args.input))[0] + '.html'
else:
    output_filename = args.output

# Determine the full path to the output HTML file
output_path = os.path.join(output_directory, output_filename + '.html')

# Ensure the specified GeoJSON file exists
if not os.path.exists(args.input):
    print(f"Error: GeoJSON file '{args.input}' does not exist.")
    sys.exit(1)

# Read the GeoJSON data from the input file
try:
    with open(args.input, 'r') as geojson_file:
        geojson_data = geojson_file.read()
except Exception as e:
    print(f"Error reading GeoJSON file: {e}")
    sys.exit(1)

# Load the HTML template
template_path = os.path.join('templates', 'map.html')
try:
    with open(template_path, 'r') as template_file:
        html_template = template_file.read()
except Exception as e:
    print(f"Error reading HTML template: {e}")
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
    print(f"Error writing HTML output file: {e}")
    sys.exit(1)

print(f"Map HTML file generated: {output_path}")

# STEP 3: Generate vector MBTiles from GeoJSON
# Determine the output MBTiles filename
if args.output is None:
    mbtiles_output_filename = os.path.splitext(os.path.basename(args.input))[0] + '.mbtiles'
else:
    mbtiles_output_filename = os.path.splitext(os.path.basename(args.output))[0] + '.mbtiles'

# Determine the full path to the output MBTiles file
mbtiles_output_path = os.path.join(output_directory, mbtiles_output_filename)

# Generate MBTiles using tippecanoe
command = f"tippecanoe -o {mbtiles_output_path} --force --no-tile-compression {args.input} --layer=geojson-layer"

try:
    os.system(command)
    print(f"MBTiles file generated: {mbtiles_output_path}")
except Exception as e:
    print(f"Error generating MBTiles: {e}")
    sys.exit(1)
    
    
# STEP 4: Generate stylesheet with MBTiles included
# Load the style.json template
style_template_path = os.path.join('templates', 'style.json')
try:
    with open(style_template_path, 'r') as style_template_file:
        style_template = json.load(style_template_file)
except Exception as e:
    print(f"Error reading style.json template: {e}")
    sys.exit(1)

# Add raster source and layer to style.json template
raster_source = {
    "type": "raster",
    "tiles": [mbtiles_output_path],  # Use the generated MBTiles file as the tile source
    "tileSize": 256
}

raster_layer = {
    "id": "raster-layer",
    "type": "raster",
    "source": "raster-source",
    "paint": {}
}

label_layer = {
    "id": "label-layer",
    "type": "symbol",
    "source": "raster-source",
    "layout": {
        'text-field': ['get', 'type_of_alert'],
        "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
        "text-offset": [0, 1.25],
        "text-anchor": "top"
    },
    "paint": {
        "text-color": "white", 
        "text-halo-color": "black", 
        "text-halo-width": 1,
        "text-halo-blur": 1
    }
}

style_template['sources']['raster-source'] = raster_source
style_template['layers'].append(raster_layer)
style_template['layers'].append(label_layer)

# Write the final style.json content to the output file
style_output_path = os.path.join(output_directory, 'style.json')
try:
    with open(style_output_path, 'w') as style_output_file:
        json.dump(style_template, style_output_file, indent=4)
except Exception as e:
    print(f"Error writing style.json output file: {e}")
    sys.exit(1)

print(f"Style JSON file generated: {style_output_path}")