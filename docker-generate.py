import os
import sys
import argparse
import traceback
from gccd.utils import copy_input_files, generate_jpgs_from_geotiffs
from gccd.calculate_bbox import get_bounding_box
from gccd.generate_maps import generate_html_map, generate_overlay_map
from gccd.generate_tiles import (
    generate_pmtiles_from_geotiff,
    generate_vector_mbtiles,
    generate_raster_tiles,
    convert_raster_tiles,
)
from gccd.generate_style import generate_style_with_mbtiles
from gccd.generate_fonts_sprites import copy_fonts_and_sprites
from gccd.serve_maps import generate_tileserver_config


# Get environment variables
map_zoom = float(os.getenv('MAP_ZOOM'))
map_center_longitude = float(os.getenv('MAP_CENTER_LONGITUDE'))
map_center_latitude = float(os.getenv('MAP_CENTER_LATITUDE'))
raster_imagery_url = os.getenv('RASTER_IMAGERY_URL')
raster_imagery_attribution = os.getenv('RASTER_IMAGERY_ATTRIBUTION')
raster_max_zoom = os.getenv('RASTER_MBTILES_MAX_ZOOM')
raster_buffer_size = os.getenv('RASTER_BUFFER_SIZE')

def main():
    # Get arguments from command line
    parser = argparse.ArgumentParser(description='Generate HTML and MBTiles files with GeoJSON and GeoTIFF data.')
    parser.add_argument('--geojson', required=True, help='Path to the input GeoJSON file')
    parser.add_argument('--t0', help='Path to the input T0 (before) GeoTIFF file')
    parser.add_argument('--t1', help='Path to the input T1 (after) GeoTIFF file')
    parser.add_argument('--output', help='Path to the output files')
    args = parser.parse_args()

    input_geojson_path = args.geojson
    input_t0_path = args.t0
    input_t1_path = args.t1

    # Exit the script if GeoJSON input is None
    if input_geojson_path is None:
        sys.exit("\033[1m\033[31mError: input GeoJSON file is required\033[0m")

    # Check if both t0 and t1 are provided or not provided
    if bool(input_t0_path) != bool(input_t1_path):
        sys.exit("\033[1m\033[31mError: both T0 and T1 files must be provided, or neither should be provided\033[0m")
        
    # Prepare output directory
    # If output flag is not provided, set the output name to match the GeoJSON filename
    if args.output is None:
        output_filename = os.path.splitext(os.path.basename(input_geojson_path))[0]
        subdir_name = os.path.splitext(os.path.basename(input_geojson_path))[0]
        output_directory = os.path.join('outputs', subdir_name)
    else:
        output_filename = args.output
        output_directory = os.path.join('outputs', output_filename)
    
    os.makedirs(output_directory, exist_ok=True)

    # Call the modularized functions to perform different steps
    try:    
        print("\033[95mStarting script to generate map assets...\033[0m")
        
        if os.path.exists(f"{output_directory}\mapgl-map\config.json"):
            os.remove(f"{output_directory}\config.json")    

        # STEP 1: Copy input files to resources, and generate a JPG version of the GeoTIFFs (if provided)
        copy_input_files(input_geojson_path, input_t0_path, input_t1_path, output_directory, output_filename)
        if input_t0_path is not None and input_t1_path is not None:
            generate_jpgs_from_geotiffs(input_t0_path, input_t1_path, output_directory, output_filename)

        # STEP 2: Get bounding box for GeoJSON
        bounding_box = get_bounding_box(input_geojson_path, raster_buffer_size)

        # STEP 3: Generate PMTiles for GeoTIFFS (if provided)
        if input_t0_path is not None and input_t1_path is not None:
            generate_pmtiles_from_geotiff(raster_max_zoom, "t0", output_directory, output_filename)
            generate_pmtiles_from_geotiff(raster_max_zoom, "t1", output_directory, output_filename)

        # STEP 4: Generate HTML map for previewing change detection alert
        generate_html_map(
            map_center_longitude, 
            map_center_latitude, 
            map_zoom, 
            input_geojson_path, 
            input_t0_path,
            input_t1_path,
            output_directory, 
            output_filename
        )

        # STEP 5: Generate vector MBTiles from GeoJSON
        generate_vector_mbtiles(output_directory, output_filename)

        # STEP 6: Generate raster XYZ tiles from satellite imagery and bbox
        generate_raster_tiles(
            raster_imagery_url, 
            raster_imagery_attribution, 
            raster_max_zoom, 
            bounding_box['geometry']['coordinates'][0], 
            output_directory, 
            output_filename
        )
        
        # STEP 7: Convert raster XYZ directory to MBTiles
        convert_raster_tiles(output_directory, output_filename + "-raster")

        # STEP 8: Generate stylesheet with MBTiles included
        generate_style_with_mbtiles(raster_max_zoom, output_directory, output_filename)

        # STEP 9: Download and copy over fonts and glyphs
        copy_fonts_and_sprites(output_directory)

        # STEP 10: Generate overlay HTML map
        generate_overlay_map(output_directory, output_filename)

        # STEP 11: Generate Tileserver-GL config and other necessary files
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
