import os
import sys
import argparse
import traceback
from gccd.calculate_bbox import get_bounding_box
from gccd.generate_tiles import generate_mbtiles_from_tileserver


# Get environment variables
raster_max_zoom = os.getenv('RASTER_MBTILES_MAX_ZOOM')
raster_imagery_attribution = os.getenv('RASTER_IMAGERY_ATTRIBUTION')
raster_buffer_size = os.getenv('RASTER_BUFFER_SIZE')
port = '8080'

def main():
    # Get arguments from command line
    parser = argparse.ArgumentParser(description='Generate composite (raster and vector) MBTiles from tileserver-gl.')
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
        output_directory = os.path.join('outputs', output_filename)
    
    os.makedirs(output_directory, exist_ok=True)

    # Call the modularized functions to perform different steps
    try:    
        print("\033[95mStarting script to generate composite MBTiles (raster and vector baked into raster) from tileserver-gl...\033[0m")
                        
        # STEP 11: Generate composite MBTiles from tileserver-gl map
        bounding_box = get_bounding_box(input_geojson_path, raster_buffer_size)
        
        generate_mbtiles_from_tileserver(bounding_box['geometry']['coordinates'][0], raster_max_zoom, raster_imagery_attribution, output_directory, output_filename, port)

        print("\033[95mComposite raster MBTiles from tileserver-gl map successfully generated!\033[0m")
    except Exception as e:
        exc_type, exc_obj, tb = sys.exc_info()
        lineno = tb.tb_lineno
        error_message = f"An error occurred on line {lineno}: {e}"
        traceback_message = traceback.format_exc()
        print(f"\033[1m\033[31m{error_message}\n{traceback_message}\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()
