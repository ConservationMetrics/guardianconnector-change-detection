import os

from gccd.calculate_bbox import get_bounding_box
from gccd.generate_maps import generate_map_html, generate_overlay_map
from gccd.generate_tiles import (
    generate_vector_mbtiles,
    generate_raster_tiles,
    convert_xyz_to_mbtiles,
)
from gccd.generate_style import generate_style_with_mbtiles
from gccd.generate_fonts_sprites import copy_fonts_and_sprites
from gccd.utils import copy_geojson_file


# Get environment variables
mapbox_access_token = os.getenv("MAPBOX_ACCESS_TOKEN")
mapbox_style = os.getenv("MAPBOX_STYLE")
mapbox_zoom = float(os.getenv("MAPBOX_ZOOM"))
mapbox_center_longitude = float(os.getenv("MAPBOX_CENTER_LONGITUDE"))
mapbox_center_latitude = float(os.getenv("MAPBOX_CENTER_LATITUDE"))
raster_imagery_url = os.getenv("RASTER_IMAGERY_URL")
raster_imagery_attribution = os.getenv("RASTER_IMAGERY_ATTRIBUTION")
raster_max_zoom = os.getenv("RASTER_MBTILES_MAX_ZOOM")
raster_buffer_size = os.getenv("RASTER_BUFFER_SIZE")


def flow(input_geojson_path, output_directory, output_filename):

    # STEP 1: Copy GeoJSON file to outputs
    copy_geojson_file(input_geojson_path, output_directory, output_filename)

    # STEP 2: Get bounding box for GeoJSON
    bounding_box = get_bounding_box(input_geojson_path, raster_buffer_size)

    # STEP 3: Generate HTML Mapbox map for previewing change detection alert
    generate_map_html(
        mapbox_access_token,
        mapbox_style,
        mapbox_center_longitude,
        mapbox_center_latitude,
        mapbox_zoom,
        input_geojson_path,
        output_directory,
        output_filename,
    )

    # STEP 4: Generate vector MBTiles from GeoJSON
    generate_vector_mbtiles(output_directory, output_filename)

    # STEP 5: Generate raster XYZ tiles from satellite imagery and bbox
    generate_raster_tiles(
        raster_imagery_url,
        raster_imagery_attribution,
        raster_max_zoom,
        bounding_box["geometry"]["coordinates"][0],
        output_directory,
        output_filename,
    )

    # STEP 6: Convert raster XYZ directory to MBTiles
    convert_xyz_to_mbtiles(output_directory, output_filename)

    # STEP 7: Generate stylesheet with MBTiles included
    generate_style_with_mbtiles(raster_max_zoom, output_directory, output_filename)

    # STEP 8: Download and copy over fonts and glyphs
    copy_fonts_and_sprites(output_directory)

    # STEP 9: Generate overlay HTML map
    generate_overlay_map(mapbox_access_token, output_directory, output_filename)

    return bounding_box
