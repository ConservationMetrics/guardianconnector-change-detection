import os
import tarfile
import requests

def copy_fonts_and_sprites(output_directory):
    mapgl_dir = os.path.join(output_directory, "mapgl-map")
    output_fonts_dir = os.path.join(mapgl_dir, 'fonts')
    output_sprites_dir = os.path.join(mapgl_dir, 'sprites')
    fonts_archive_url = 'https://cmi4earth.blob.core.windows.net/public-map-tiles/change_detection/fonts.tar.gz'
    sprite_dir_url = 'https://cmi4earth.blob.core.windows.net/public-map-tiles/change_detection/sprites/'
    sprite_files = [
                "sprite.json",
                "sprite.png",
                "sprite@2x.json",
                "sprite@2x.png"
            ]

    try:
        # Create the output fonts directory if it doesn't exist
        os.makedirs(output_fonts_dir, exist_ok=True)

        if not os.listdir(output_fonts_dir):
            archive_path = os.path.join(output_fonts_dir, 'archive.tar.gz')
            if not os.path.exists(archive_path):
                # Download the fonts archive
                print("Downloading fonts...")
                response = requests.get(fonts_archive_url)
                if response.status_code == 200:
                    with open(archive_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded archive file from {fonts_archive_url} to {archive_path}")
                else:
                    print(f"Failed to download the archive from {fonts_archive_url}. Status code: {response.status_code}")
                    return False

            # Extract fonts directly into the output_fonts_dir (without creating a subdirectory)
            print("Extracting fonts...")
            with tarfile.open(archive_path, 'r:gz') as archive:
                members = [m for m in archive.getmembers() if m.name.startswith('fonts/')]
                for member in members:
                    member.name = member.name.replace('fonts/', '', 1)
                archive.extractall(output_fonts_dir, members=members)

            # Remove the downloaded archive
            os.remove(archive_path)
            
        print(f"\033[1m\033[32mFonts copied to:\033[0m {output_fonts_dir}")
    except Exception as e:
        print(f"\033[1m\033[31mAn error occurred while copying fonts:\033[0m {e}")
    
    try:
        if not os.path.exists(output_sprites_dir):
            os.makedirs(output_sprites_dir, exist_ok=True)

            for sprite_file in sprite_files:
                sprite_url = sprite_dir_url + sprite_file
                output_path = os.path.join(output_sprites_dir, sprite_file)

                response = requests.get(sprite_url)
                if response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                else:
                    print(f"Failed to download sprite file from {sprite_url}. Status code: {response.status_code}")
                    return False

        print(f"\033[1m\033[32mSprites copied to:\033[0m {output_sprites_dir}")
    except Exception as e:
        print(f"\033[1m\033[31mAn error occurred while copying sprites:\033[0m {e}")
