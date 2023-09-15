import os
import sys
import argparse
import traceback
from dotenv import load_dotenv
from scripts.utils import (copy_geojson_file)
from scripts.calculate_bbox import get_bounding_box
from scripts.generate_maps import (generate_map_html, generate_overlay_map)
from scripts.generate_tiles import (generate_vector_mbtiles, generate_raster_tiles, convert_xyz_to_mbtiles)
from scripts.generate_style import generate_style_with_mbtiles
from scripts.generate_fonts_sprites import copy_fonts_and_sprites
from scripts.serve_maps import generate_tileserver_config

# Load environment variables from .env file
load_dotenv()

# Get environment variables
mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')
mapbox_style = os.getenv('MAPBOX_STYLE')
mapbox_zoom = float(os.getenv('MAPBOX_ZOOM'))
mapbox_center_longitude = float(os.getenv('MAPBOX_CENTER_LONGITUDE'))
mapbox_center_latitude = float(os.getenv('MAPBOX_CENTER_LATITUDE'))
raster_imagery_url = os.getenv('RASTER_IMAGERY_URL')
raster_imagery_attribution = os.getenv('RASTER_IMAGERY_ATTRIBUTION')
raster_max_zoom = os.getenv('RASTER_MBTILES_MAX_ZOOM')
raster_buffer_size = os.getenv('RASTER_BUFFER_SIZE')

def main():
    # Get arguments from command line
    parser = argparse.ArgumentParser(description='Generate HTML and MBTiles files with GeoJSON data.')
    parser.add_argument('--input', required=True, help='Path to the input GeoJSON file')
    parser.add_argument('--output', help='Path to the output files')
    args = parser.parse_args()

    input_geojson_path = args.input
    # Prepare output directory
    # If output flag is not provided, set the output name to match the GeoJSON filename
    if args.output is None:
        output_filename = os.path.splitext(os.path.basename(input_geojson_path))[0]
        subdir_name = os.path.splitext(os.path.basename(input_geojson_path))[0]
        output_directory = os.path.join('outputs', subdir_name)
    else:
        output_filename = args.output
        output_directory = args.output
    
    os.makedirs(output_directory, exist_ok=True)

    # Call the modularized functions to perform different steps
    try:    
        print("\033[95mStarting script to generate map assets...\033[0m")
        
        if os.path.exists(f"{output_directory}\wait-for-config-done"):
            os.remove(f"{output_directory}\wait-for-config-done")
        if os.path.exists(f"{output_directory}\mapbox-map\config.json"):
            os.remove(f"{output_directory}\wait-for-config-done")    

        # STEP 1: Copy GeoJSON file to outputs
        copy_geojson_file(input_geojson_path, output_directory, output_filename)

        # STEP 2: Get bounding box for GeoJSON
        bounding_box = get_bounding_box(input_geojson_path, raster_buffer_size)

        # STEP 3: Generate HTML Mapbox map for previewing change detection alert
        generate_map_html(mapbox_access_token, mapbox_style, mapbox_center_longitude, mapbox_center_latitude, mapbox_zoom, input_geojson_path, output_directory, output_filename)

        # STEP 4: Generate vector MBTiles from GeoJSON
        generate_vector_mbtiles(input_geojson_path, output_directory, output_filename)

        # STEP 5: Generate raster XYZ tiles from satellite imagery and bbox
        generate_raster_tiles(raster_imagery_url, raster_imagery_attribution, raster_max_zoom, bounding_box['geometry']['coordinates'][0], output_directory, output_filename)
        
        # STEP 6: Convert raster XYZ directory to MBTiles
        convert_xyz_to_mbtiles(output_directory, output_filename)

        # STEP 7: Generate stylesheet with MBTiles included
        generate_style_with_mbtiles(raster_max_zoom, output_directory, output_filename)

        # STEP 8: Download and copy over fonts and glyphs
        copy_fonts_and_sprites(output_directory)

        # STEP 9: Generate overlay HTML map
        generate_overlay_map(mapbox_access_token, output_directory, output_filename)

        # STEP 10: Generate Tileserver-GL config and other necessary files
        generate_tileserver_config(output_directory, output_filename)
        
        print("\033[95mAll map assets generated! You may now proceed to serve the map (using tileserver-gl) if needed.\033[0m")
    except Exception as e:
        exc_type, exc_obj, tb = sys.exc_info()
        lineno = tb.tb_lineno
        error_message = f"An error occurred on line {lineno}: {e}"
        traceback_message = traceback.format_exc()
        print(f"\033[1m\033[31m{error_message}\n{traceback_message}\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()
