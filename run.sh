#!/bin/bash

echo -e "\033[95mStarting Docker workflow...\033[0m"

# Get the input file from the first argument.
INPUT_FILE=$1
export INPUT_FILE
INPUT_NAME=$(basename ${INPUT_FILE} .geojson)

# Replace the placeholder in docker-compose.yml with the actual input file
sed -i.bak -e "s|example.geojson|${INPUT_FILE}|g" -e "s|example|${INPUT_NAME}|g" docker-compose.yml

# Run docker compose up
docker compose up &

# Check to see if the tileserver-gl container is running and the generate-assets and compile-composite-raster containers are not (in other words, they have successfully exited)
while true; do
  if [[ $(docker compose ps --services | grep 'tileserver-gl' | wc -l) -eq 1 ]] && [[ $(docker compose ps --services | grep 'generate-assets\|compile-composite-raster' | wc -l) -eq 0 ]]; then
    docker compose stop
    break
  fi
  sleep 5
done

docker compose down

echo -e "\033[95mChange detection map assets generated successfully in /outputs/$INPUT_NAME/ directory!\033[0m"

# Restore the original docker-compose.yml
mv docker-compose.yml.bak docker-compose.yml