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

    docker run -it -v /home/cmi/dev/guardianconnector-change-detection/httpservice/app:/code/app -p 80:80 gccd uvicorn app.app:app --host 0.0.0.0 --port 80 --reload
