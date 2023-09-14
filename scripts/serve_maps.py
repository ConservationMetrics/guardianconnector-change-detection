import os
import sys
import subprocess
import json
import socket

def generate_tileserver_config(output_directory, output_filename):
    map_directory = os.path.join(output_directory, 'mapbox-map')
    
    # Check if config already exists
    config_path = os.path.join(map_directory, "config.json")
    
    if os.path.exists(config_path):
        os.remove(config_path)

    style_path = os.path.join(map_directory, "style.json")
    if not os.path.exists(style_path):
        print("style.json not found in the map directory.")
        sys.exit(1)

    # Load the style.json
    with open(style_path, 'r') as style_file:
        style_data = json.load(style_file)

    mbtiles_sources = []
    for source_name, source_data in style_data["sources"].items():
        source_type = source_data["type"]
        source_data["url"] = f"{source_data['url']}"
        mbtiles_sources.append({
            "name": source_name,
            "type": source_type,
            "url": source_data["url"]
        })

    config = {
        "options": {
            "paths": {
                "fonts": "fonts",
                "sprites": "sprites",
                "mbtiles": "tiles",
                "styles": "./"
            },
            "serveAllFonts": "true"
        },
        "styles": {
            output_filename: {
                "style": "style.json",
                "tilejson": {
                    "format": "png"
                },
                "serve_rendered": "true",
                "serve_data": "true"
            }
        },
        "data": {
            f"{output_filename}-raster":{
                "mbtiles":f"{output_filename}-raster.mbtiles"
            },
            f"{output_filename}-vector":{
                "mbtiles":f"{output_filename}-vector.mbtiles"
            }
        }
    }

    try:
        with open(config_path, 'w') as config_file:
            json.dump(config, config_file, indent=4)
        print(f"\033[1m\033[32mConfig.json file generated:\033[0m {config_path}")
    except Exception as e:
        print(f"[31mError generating config.json: {e}")
        sys.exit(1)

def serve_tileserver_gl(output_directory, output_filename):
    map_directory = os.path.join(output_directory, 'mapbox-map')

    # Generate Tileserver-GL config if not found
    config_path = os.path.join(map_directory, "config.json")
    if os.path.exists(config_path):
        os.remove(config_path)
    generate_tileserver_config(map_directory, output_filename)

    current_directory = os.getcwd()
    volume_mapping = f"{current_directory}/{map_directory}:/data"

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()

    command = [
        "docker", "run", "--rm", "-it",
        "-v", volume_mapping,
        "-p", "8080:8080",
        "maptiler/tileserver-gl"
    ]

    try:
        print("Starting up TileServer-GL...")
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        while True:
            line = proc.stdout.readline()
            if "Startup complete" in line:
                subprocess.run('stty sane', shell=True)
                print(f"\033[0m\033[1m\033[32mTileServer-GL is serving the map at http://{local_ip}:8080!\033[0m")
                break
    except subprocess.CalledProcessError:
        subprocess.run('stty sane', shell=True)
        print("\033[1m\033[31mError in serving tiles using TileServer-GL.\033[0m")
        sys.exit(1)
    except FileNotFoundError:
        subprocess.run('stty sane', shell=True)
        print("\033[1m\033[31mTileServer-GL command not found. Ensure it's installed and in your PATH.\033[0m")
        sys.exit(1)