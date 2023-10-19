#!/usr/bin/env python3

import os
import sys
import argparse
import traceback

import gccd
from gccd.utils import kill_container_by_image
from gccd.generate_tiles import generate_mbtiles_from_tileserver
from gccd.serve_maps import serve_tileserver_gl


port = os.getenv("PORT")


def main():
    # Get arguments from command line
    parser = argparse.ArgumentParser(description='Generate HTML and MBTiles files with GeoJSON data.')
    parser.add_argument('--input', required=True, help='Path to the input GeoJSON file')
    parser.add_argument('--output', help='Path to the output files')
    args = parser.parse_args()

    input_geojson_path = args.input

    # Exit the script if input is None
    if input_geojson_path is None:
        sys.exit("\033[1m\033[31mError: input GeoJSON file is required\033[0m")

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
        print("\033[95mStarting script...\033[0m")
        # PRELIMINARY: Make sure the tileserver-gl Docker container is taken down if running
        kill_container_by_image('maptiler/tileserver-gl')

        bounding_box = gccd.flow(input_geojson_path, output_directory, output_filename)

        # STEP 10: Serve map using tileserver-gl
        serve_tileserver_gl(output_directory, output_filename, port)
                        
        # STEP 11: Generate composite MBTiles from tileserver-gl map
        generate_mbtiles_from_tileserver(bounding_box['geometry']['coordinates'][0], raster_max_zoom, raster_imagery_attribution, output_directory, output_filename, port)

        # POSTSCRIPT: Kill docker container now that we are done
        kill_container_by_image('maptiler/tileserver-gl')

        print("\033[95mScript complete! Raster MBTiles overlaying your GeoJSON input on satellite imagery successfully generated.")
    except Exception as e:
        exc_type, exc_obj, tb = sys.exc_info()
        lineno = tb.tb_lineno
        error_message = f"An error occurred on line {lineno}: {e}"
        traceback_message = traceback.format_exc()
        print(f"\033[1m\033[31m{error_message}\n{traceback_message}\033[0m")
        sys.exit(1)


if __name__ == "__main__":
    main()
