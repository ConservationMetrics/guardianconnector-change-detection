import os
import sys
from shutil import copyfile

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
        geometry_type = feature['geometry']['type']
        coordinates = feature['geometry']['coordinates']

        # If it's a Point
        if geometry_type == 'Point':
            x, y = coordinates
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

        # If it's a LineString
        elif geometry_type == 'LineString':
            for coord in coordinates:
                x, y = coord
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

        # If it's a Polygon
        elif geometry_type == 'Polygon':
            for ring in coordinates:
                for coord in ring:
                    x, y = coord
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)

    return min_x, min_y, max_x, max_y

def load_html_template(template_path):
    try:
        with open(template_path, 'r') as template_file:
            return template_file.read()
    except Exception as e:
        print(f"\033[1m\033[31mError reading HTML template:\033[0m {e}")
        sys.exit(1)
