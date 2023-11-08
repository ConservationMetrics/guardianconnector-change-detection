#!/bin/bash

echo -e "\033[95mStarting Docker workflow...\033[0m"

usage() {
  echo "Usage: $0 --geojson INPUT_FILE [--t0 INPUT_T0_FILE] [--t1 INPUT_T1_FILE] [--output OUTPUT]"
  exit 1
}

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --geojson) export INPUT_GEOJSON_FILE="$2"; shift ;;
        --t0) export INPUT_T0_FILE="$2"; shift ;;
        --t1) export INPUT_T1_FILE="$2"; shift ;;
        --output) export OUTPUT="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; usage ;;
    esac
    shift
done

export INPUT_GEOJSON_NAME=$(basename ${INPUT_GEOJSON_FILE} .geojson)
export INPUT_T0_FILE=${INPUT_T0_FILE}
export INPUT_T1_FILE=${INPUT_T1_FILE}

# If OUTPUT is not specified, set it to INPUT_FILE
if [ -z "${OUTPUT}" ]; then
    export OUTPUT="${INPUT_GEOJSON_FILE}"
fi

# Remove .geojson extension from OUTPUT
export OUTPUT="${OUTPUT%.geojson}"

# If either INPUT_T0_FILE or INPUT_T1_FILE is not specified, set it to None
if [ -z "${INPUT_T0_FILE}" ] || [ -z "${INPUT_T1_FILE}" ]; then
  export COMMAND="python docker-generate.py --geojson ${INPUT_GEOJSON_FILE} --output ${OUTPUT}"
else
  export COMMAND="python docker-generate.py --geojson ${INPUT_GEOJSON_FILE} --t0 ${INPUT_T0_FILE} --t1 ${INPUT_T1_FILE} --output ${OUTPUT}"
fi

# Run docker compose up
docker compose up &

# Check to see if the tileserver-gl container is running and the generate-assets and compile-composite-raster containers are not (in other words, they have successfully exited)
while true; do
  if [[ $(docker compose ps --services | grep 'tileserver-gl' | wc -l) -eq 1 ]] && [[ $(docker compose ps --services | grep 'generate-assets\|compile-composite-raster' | wc -l) -eq 0 ]]; then
    docker compose stop
    break
  fi
  sleep 1
done

docker compose down

echo -e "\033[95mChange detection map assets generated successfully in /outputs/$INPUT_GEOJSON_NAME/ directory!\033[0m"
