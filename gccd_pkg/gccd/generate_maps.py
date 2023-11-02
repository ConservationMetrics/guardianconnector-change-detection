import os
import sys

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


def generate_html_file(template_filename, output_path, **template_vars):
    try:
        # Load the template
        template_path = os.path.join(TEMPLATES_DIR, template_filename)
        with open(template_path, 'r') as template_file:
            template_content = template_file.read()

        # Replace placeholders with provided template variables
        for var_name, var_value in template_vars.items():
            template_content = template_content.replace(var_name, var_value)

        # Write the final HTML content to the output file
        with open(output_path, 'w') as output_file:
            output_file.write(template_content)
        print(f"\033[1m\033[32mHTML file generated:\033[0m {output_path}")
    except Exception as e:
        print(f"\033[1m\033[31mError writing HTML output file:\033[0m {e}")
        sys.exit(1)

def generate_html_map(map_center_longitude, map_center_latitude, map_zoom, input_geojson_path, input_t0_path, input_t1_path, output_path, output_filename):
    
    output_html_path = os.path.join(output_path, output_filename + '.html')
    if input_t0_path is None and input_t1_path is None:
        generate_html_file(
            'map.html', output_html_path,
            map_long=str(map_center_longitude),
            map_lat=str(map_center_latitude),
            map_zoom=str(map_zoom),
            geojson_filepath=f"./resources/{output_filename}.geojson"
        )
    else:
        generate_html_file(
            'swipe_map.html', output_html_path,
            map_long=str(map_center_longitude),
            map_lat=str(map_center_latitude),
            map_zoom=str(map_zoom),
            geojson_filepath=f"./resources/{output_filename}.geojson",
            t0_filepath=f"./resources/{output_filename}_t0.pmtiles",
            t1_filepath=f"./resources/{output_filename}_t1.pmtiles",
        )

def generate_overlay_map(output_directory, output_filename):
    mapgl_dir = os.path.join(output_directory, "mapgl-map")
    overlay_map_html_path = os.path.join(mapgl_dir, "index.html")
    generate_html_file(
        'overlay_map.html', overlay_map_html_path,
        geojson_filename=f"../resources/{output_filename}.geojson"
    )
