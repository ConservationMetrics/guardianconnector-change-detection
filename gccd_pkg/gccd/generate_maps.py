import os
import sys

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


def generate_html_file(template_filename, output_path, mapbox_access_token=None, **template_vars):
    try:
        # Load the template
        template_path = os.path.join(TEMPLATES_DIR, template_filename)
        with open(template_path, 'r') as template_file:
            template_content = template_file.read()

        # Replace placeholders with provided template variables
        if mapbox_access_token:
            template_vars['pk.ey'] = mapbox_access_token
        for var_name, var_value in template_vars.items():
            template_content = template_content.replace(var_name, var_value)

        # Write the final HTML content to the output file
        with open(output_path, 'w') as output_file:
            output_file.write(template_content)
        print(f"\033[1m\033[32mHTML file generated:\033[0m {output_path}")
    except Exception as e:
        print(f"\033[1m\033[31mError writing HTML output file:\033[0m {e}")
        sys.exit(1)

def generate_map_html(mapbox_access_token, mapbox_style, mapbox_center_longitude, mapbox_center_latitude, mapbox_zoom, geojson_input_path, output_path, output_filename):
    output_html_path = os.path.join(output_path, output_filename + '.html')
    generate_html_file(
        'map.html', output_html_path,
        mapbox_access_token=mapbox_access_token,
        mapbox_style=mapbox_style,
        mapbox_center_longitude=str(mapbox_center_longitude),
        mapbox_center_latitude=str(mapbox_center_latitude),
        mapbox_zoom=str(mapbox_zoom),
        geojson_input_path=geojson_input_path
    )

def generate_overlay_map(mapbox_access_token, output_directory, output_filename):
    mapbox_map_dir = os.path.join(output_directory, "mapbox-map")
    overlay_map_html_path = os.path.join(mapbox_map_dir, "index.html")
    generate_html_file(
        'overlay_map.html', overlay_map_html_path,
        mapbox_access_token=mapbox_access_token,
        geojson_filename=f"{output_filename}.geojson"
    )