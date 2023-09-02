import os
import sys
import json
from shapely.geometry import Polygon
from shapely.ops import transform
import pyproj
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

def get_bounding_box(input_geojson_path, raster_buffer_size=None):
    try:
        raster_buffer_size = float(raster_buffer_size)
    except ValueError:
        raster_buffer_size = None

    geojson_data = read_geojson_file(input_geojson_path)
    geojson_dict = json.loads(geojson_data)
    features = geojson_dict["features"]

    if raster_buffer_size is None:
        min_lon, min_lat, max_lon, max_lat = calculate_bounding_box(features)
    else:
        min_lon, min_lat, max_lon, max_lat = calculate_buffered_bbox(features, raster_buffer_size)

    bounding_box = format_bbox_as_geojson(min_lon, min_lat, max_lon, max_lat)
    print(f"\033[1m\033[32mGeoJSON Bounding Box:\033[0m", bounding_box)
    return bounding_box

def format_bbox_as_geojson(min_lon, min_lat, max_lon, max_lat):
    return {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [[min_lon, min_lat], [max_lon, min_lat], [max_lon, max_lat], [min_lon, max_lat], [min_lon, min_lat]]
            ]
        }
    }

def calculate_bounding_box(features):
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
    for feature in features:
        geometry_type = feature['geometry']['type']
        coordinates = feature['geometry']['coordinates']

        def traverse_coords(coords):
            nonlocal min_x, min_y, max_x, max_y
            if type(coords[0]) == list:
                for coord in coords:
                    traverse_coords(coord)
            else:
                x, y = coords
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

        traverse_coords(coordinates)

    return min_x, min_y, max_x, max_y

def calculate_buffered_bbox(features, raster_buffer_size):
    min_lon, min_lat, max_lon, max_lat = calculate_bounding_box(features)
    bbox_polygon = Polygon([(min_lon, min_lat), (max_lon, min_lat), (max_lon, max_lat), (min_lon, max_lat)])
    
    average_lat = (min_lat + max_lat) / 2

    wgs84 = pyproj.CRS('EPSG:4326')
    zone_number = int((min_lon + 180) / 6) + 1
    if average_lat < 0:  # Southern hemisphere
        zone_code = f"327{zone_number:02}"  # UTM zone with '32' for southern hemisphere and padded zone number
    else:  # Northern hemisphere
        zone_code = f"326{zone_number:02}"  # UTM zone with '32' for northern hemisphere and padded zone number
    utm_zone = pyproj.CRS(f"EPSG:{zone_code}")
    project = pyproj.Transformer.from_crs(wgs84, utm_zone, always_xy=True).transform
    inverse = pyproj.Transformer.from_crs(utm_zone, wgs84, always_xy=True).transform

    buffered_polygon = transform(project, bbox_polygon).buffer(float(raster_buffer_size) * 1000)  # Convert km to meters
    buffered_polygon_wgs84 = transform(inverse, buffered_polygon)

    min_lon, min_lat, max_lon, max_lat = buffered_polygon_wgs84.bounds
    return min_lon, min_lat, max_lon, max_lat