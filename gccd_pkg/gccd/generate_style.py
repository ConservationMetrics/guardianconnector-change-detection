import os
import sys
import json

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


def generate_style_with_mbtiles(raster_max_zoom, output_directory, output_filename):
    mapbox_map_dir = os.path.join(output_directory, "mapbox-map")
    style_template_path = os.path.join(TEMPLATES_DIR, 'style.json')
    try:
        with open(style_template_path, 'r') as style_template_file:
            style_template = json.load(style_template_file)
    except Exception as e:
        print(f"\033[1m\033[31mError reading style.json template:\033[0m {e}")
        sys.exit(1)

    # Add mbtiles sources and layers to style.json template
    vector_source = {
        "type": "vector",
        "url": f"mbtiles://{output_filename}-vector.mbtiles"
    }

    raster_source = { 
        "type": "raster",
        "url": f"mbtiles://{output_filename}-raster.mbtiles",
        "tileSize": 256,
        "maxzoom": int(raster_max_zoom)
   }

    raster_layer = {
        "id": "satellite-layer",
        "type": "raster",
        "source": "raster_source",
        "paint": {}
    }

    point_layer = {
        "id": "point-layer",
        "type": "circle",
        "source": "vector_source",
        "source-layer": output_filename,
        "filter": ["==", "$type", "Point"],
        "paint": {
            "circle-radius": 6,
            "circle-color": "#FF0000"
        }
    }

    polygon_layer = {
        "id": "polygon-layer",
        "type": "fill",
        "source": "vector_source",
        "source-layer": output_filename,
        "filter": ["==", "$type", "Polygon"],
        "paint": {
            "fill-color": "#FF0000",
            "fill-opacity": 0.5
        }
    }

    line_layer = {
        "id": "line-layer",
        "type": "line",
        "source": "vector_source",
        "source-layer": output_filename,
        "filter": ["==", "$type", "LineString"],
        "paint": {
            "line-color": "#FF0000",
            "line-width": 2
        }
    }

    point_label_layer = {
        "id": "label-layer",
        "type": "symbol",
        "source": "vector_source",
        "source-layer": output_filename,
        "filter": ["==", "$type", "Point"],
        "layout": {
            'text-field': ['get', 'type_of_alert'],
            'text-font': ['Open Sans Regular'],
            'text-offset': [0, -0.5],
            'text-anchor': 'bottom',
            'icon-image': 'border-dot-13'
        },
        "paint": {
            'text-color': '#FFFFFF',
            'text-halo-color': 'black',
            'text-halo-width': 1,
            'text-halo-blur': 1
        }
    }

    geojson_label_layer = {
        "id": "polygon-label-layer",
        "type": "symbol",
        "source": "vector_source",
        "source-layer": output_filename,
        "filter": ['in', '$type', 'Polygon', 'LineString'],
        "layout": {
            'text-field': ['get', 'type_of_alert'],
            'text-font': ['Open Sans Regular'],
            'text-offset': [0, 0.5],
            'text-anchor': 'top'
        },
        "paint": {
            'text-color': '#FFFFFF',
            'text-halo-color': 'black',
            'text-halo-width': 1,
            'text-halo-blur': 1
        }
    }

    style_template['sources']['vector_source'] = vector_source
    style_template['sources']['raster_source'] = raster_source
    style_template['layers'].append(raster_layer)
    style_template['layers'].append(point_layer)
    style_template['layers'].append(polygon_layer)
    style_template['layers'].append(line_layer)
    style_template['layers'].append(point_label_layer)
    style_template['layers'].append(geojson_label_layer)
    style_template['id'] = output_filename

    # Write the final style.json content to the output file
    style_output_path = os.path.join(mapbox_map_dir, 'style.json')
    try:
        with open(style_output_path, 'w') as style_output_file:
            json.dump(style_template, style_output_file, indent=4)
    except Exception as e:
        print(f"\033[1m\033[31mError writing style.json output file:\033[0m {e}")
        sys.exit(1)

    print(f"\033[1m\033[32mStyle JSON file generated:\033[0m {style_output_path}")
