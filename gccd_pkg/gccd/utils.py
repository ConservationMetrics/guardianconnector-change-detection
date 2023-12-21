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

def copy_input_files(input_geojson_path, input_t0_path, input_t1_path, output_directory, output_filename):
    resources_dir = os.path.join(output_directory, "resources")
    os.makedirs(resources_dir, exist_ok=True)

    # Copy GeoJSON file
    try:
        # Determine the GeoJSON filename
        geojson_output_filename = os.path.basename(f'{output_filename}.geojson')
        # Determine the full path to the GeoJSON output file
        geojson_output_path = os.path.join(resources_dir, geojson_output_filename)
        # Copy the GeoJSON file to the outputs directory
        copyfile(input_geojson_path, geojson_output_path)
        print(f"\033[1m\033[32mGeoJSON file copied to:\033[0m {geojson_output_path}")
    except Exception as e:
        print(f"\033[1m\033[31mError copying GeoJSON file:\033[0m {e}")
        sys.exit(1)
    
    # Copy t0 / t1 GeoTIFF files
    if input_t0_path is not None and input_t1_path is not None:
        try:
            # Determine the GeoTIFF output filenames
            t0_output_filename = os.path.basename(f'{output_filename}_t0.tif')
            t1_output_filename = os.path.basename(f'{output_filename}_t1.tif')
            # Determine the full path to the GeoTIFF output files
            t0_output_path = os.path.join(resources_dir, t0_output_filename)
            t1_output_path = os.path.join(resources_dir, t1_output_filename)
            # Copy the GeoTIFF files to the outputs directory
            copyfile(input_t0_path, t0_output_path)
            copyfile(input_t1_path, t1_output_path)
            print(f"\033[1m\033[32mT0 and T2 GeoTIFF files copied to:\033[0m {resources_dir}")
        except Exception as e:
            print(f"\033[1m\033[31mError copying GeoTIFF files:\033[0m {e}")
            sys.exit(1)

def generate_jpgs_from_geotiffs(input_t0_path, input_t1_path, output_directory, output_filename):
    resources_dir = os.path.join(output_directory, "resources")
    os.makedirs(resources_dir, exist_ok=True)

    # Generate JPGs from GeoTIFFs
    try:
        # Determine the JPG output filenames
        t0_output_filename = os.path.basename(f'{output_filename}_t0.jpg')
        t1_output_filename = os.path.basename(f'{output_filename}_t1.jpg')
        # Determine the full path to the JPG output files
        t0_output_path = os.path.join(resources_dir, t0_output_filename)
        t1_output_path = os.path.join(resources_dir, t1_output_filename)
        # Generate the JPG files
        subprocess.check_output(['gdal_translate', '-of', 'JPEG', input_t0_path, t0_output_path])
        subprocess.check_output(['gdal_translate', '-of', 'JPEG', input_t1_path, t1_output_path])
        # Delete the xml artifacts that gdal_translate generates
        os.remove(f'{t0_output_path}.aux.xml')
        os.remove(f'{t1_output_path}.aux.xml')
        print(f"\033[1m\033[32mT0 and T1 JPG files generated and saved to:\033[0m {resources_dir}")
    except subprocess.CalledProcessError as e:
        print(f"\033[1m\033[31mAn error occurred trying to generate JPG files:\033[0m {e}")
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
