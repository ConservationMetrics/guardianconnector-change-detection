# Change Detection httpservice

This is a thin HTTP endpoint to expose the change-detection workflow as a microservice
that can be called by other services without requiring them to have all the scientific
dependencies.

## Build Docker image

The http service runs as a Docker container.

The Docker image needs to have the gccd python package installed.  To allow
developing the http service against a bleeding-edge version of the python package,
the Dockerfile installs that package from an artifact on local disk instead of
installing from GitHub or another hosted artifact server.  The `./build.sh` script
in the repo root will build that python package (which lives in another folder in
this repo) and copy it to where it needs to live for the Dockerfile to slurp it up.

    # to build image tagged `gccd`
    ./build.sh

or

    # to build image with a custom tag, pass the tag as an argument:
    DATE=`date "+%Y%m%d.%H%M%S"`
    GIT_HEAD=$(git rev-parse --short HEAD)
    IMAGE_TAG=$DATE-$GIT_HEAD
    ./build.sh guardiancr.azurecr.io/gccd:${IMAGE_TAG}

## Run HTTP server

In production:

    docker run -it -p 80:80 gccd

For local development with hot-reloading:

    docker run -it -v /home/cmi/dev/guardianconnector-change-detection/httpservice/app:/code/app -p 80:80 --env-file .env gccd uvicorn app.app:app --host 0.0.0.0 --port 80 --reload

## Payload structure

The `changemaps` endpoint expects a JSON payload consisting of three values, one required and two optional:

* `input_geojson` (array, required): this is a GeoJSON feature collection which will be saved as a temp file and used for the `input_geojson_path` by the GCCD flow.
* `input_t0` and `input_t1` (string, optional): base64-encoded data strings for the t0 and t1 GeoTIFFs, if provided. 

### Example API call

This is providing just `input_geojson`.

``` sh
curl -v -XPOST 'http://localhost:80/changemaps/' -H 'Content-Type: application/json' -H 'X-API-KEY: your-api-key' -d '{  
  "input_geojson": {
    "type": "FeatureCollection",
    "name": "08142023-001",
    "features": [
        {
        "type": "Feature",
            "properties": {
                "date_end_t0": "2023-09-30",
                "date_end_t1": "2023-10-31",         
                "alert_type": "gold mining",
                "id": "2023101800161660100"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-54.117676498677, 3.312402112301291]
            }
        },
        {
        "type": "Feature",
            "properties": {
                "date_end_t0": "2023-09-30",
                "date_end_t1": "2023-10-31",        
                "alert_type": "logging",
                "id": "2023101800161660101"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-54.024968, 3.414382]
            }
        },
            {
            "type": "Feature",
            "properties": {
                "date_end_t0": "2023-09-30",
                "date_end_t1": "2023-10-31",
                "alert_type": "land invasion",
                "id": "2023101800161660102"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-54.017286, 3.427148]
            }
        }
    ]
  }
}' > changemap.tar
```
