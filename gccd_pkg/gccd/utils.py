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
        geojson_output_filename = os.path.basename(f'{output_filename}.geojson')
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
        
def kill_container_by_image(image_name):
    try:
        # Get a list of running containers
        output = subprocess.check_output(['docker', 'ps', '--format', '{{.Image}} {{.ID}}']).decode('utf-8').splitlines()

        for line in output:
            if image_name in line:
                # Extract the container ID
                container_id = line.split()[-1]
                # Stop the container
                subprocess.check_output(['docker', 'kill', container_id])
                print(f"Taking down tileserver-gl with Docker image {image_name} and ID {container_id}...")
                return
        print(f"Container with image {image_name} is not running.")

    except subprocess.CalledProcessError as e:
        print(f"\033[1m\033[31mAn error occurred trying to kill the Docker container:\033[0m {e}")
        return