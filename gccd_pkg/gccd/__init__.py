import os

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
from gccd.utils import copy_input_files, generate_jpgs_from_geotiffs


# Get environment variables
map_zoom = float(os.getenv("MAP_ZOOM"))
map_center_longitude = float(os.getenv("MAP_CENTER_LONGITUDE"))
map_center_latitude = float(os.getenv("MAP_CENTER_LATITUDE"))
raster_imagery_url = os.getenv("RASTER_IMAGERY_URL")
raster_imagery_attribution = os.getenv("RASTER_IMAGERY_ATTRIBUTION")
raster_max_zoom = os.getenv("RASTER_MBTILES_MAX_ZOOM")
raster_buffer_size = os.getenv("RASTER_BUFFER_SIZE")


def flow(input_geojson_path, input_t0_path, input_t1_path, output_directory, output_filename):

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
        output_filename,
    )

    # STEP 5: Generate vector MBTiles from GeoJSON
    generate_vector_mbtiles(output_directory, output_filename)

    # STEP 6: Generate raster XYZ tiles from satellite imagery and bbox
    generate_raster_tiles(
        raster_imagery_url,
        raster_imagery_attribution,
        raster_max_zoom,
        bounding_box["geometry"]["coordinates"][0],
        output_directory,
        output_filename,
    )

    # STEP 7: Convert raster XYZ directory to MBTiles
    convert_raster_tiles(output_directory, output_filename + "-raster")

    # STEP 8: Generate stylesheet with MBTiles included
    generate_style_with_mbtiles(raster_max_zoom, output_directory, output_filename)

    # STEP 9: Download and copy over fonts and glyphs
    copy_fonts_and_sprites(output_directory)

    # STEP 10: Generate overlay HTML map
    generate_overlay_map(output_directory, output_filename)

    return bounding_box
