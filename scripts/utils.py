import os
import sys
import subprocess
from shutil import copyfile

def load_html_template(template_path):
    try:
        with open(template_path, 'r') as template_file:
            return template_file.read()
    except Exception as e:
        print(f"\033[1m\033[31mError reading HTML template:\033[0m {e}")
        sys.exit(1)

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