import os
import sys
import argparse
import traceback
from dotenv import load_dotenv
from scripts.calculate_bbox import get_bounding_box
from scripts.generate_tiles import generate_mbtiles_from_tileserver

# Load environment variables from .env file
load_dotenv()

# Get environment variables
raster_max_zoom = os.getenv('RASTER_MBTILES_MAX_ZOOM')
raster_imagery_attribution = os.getenv('RASTER_IMAGERY_ATTRIBUTION')
raster_buffer_size = os.getenv('RASTER_BUFFER_SIZE')

def main():
    # Get arguments from command line
    parser = argparse.ArgumentParser(description='Finalize the map by serving it using tileserver-gl and generating composite MBTiles.')
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
        print("\033[95mStarting final script to generate composite MBTiles from Tileserver...\033[0m")
                        
        # STEP 11: Generate composite MBTiles from tileserver-gl map
        bounding_box = get_bounding_box(input_geojson_path, raster_buffer_size)
        
        generate_mbtiles_from_tileserver(bounding_box['geometry']['coordinates'][0], raster_max_zoom, raster_imagery_attribution, output_directory, output_filename)

        print("\033[95mFinal steps of script complete! Composite MBTiles from tileserver-gl map successfully generated.")
    except Exception as e:
        exc_type, exc_obj, tb = sys.exc_info()
        lineno = tb.tb_lineno
        error_message = f"An error occurred on line {lineno}: {e}"
        traceback_message = traceback.format_exc()
        print(f"\033[1m\033[31m{error_message}\n{traceback_message}\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()
