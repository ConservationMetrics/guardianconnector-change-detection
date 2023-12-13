FROM python:3.11-slim as map-utilities-build-image

RUN apt-get update && apt-get install -y --no-install-recommends build-essential libsqlite3-dev zlib1g-dev git
RUN git clone https://github.com/felt/tippecanoe.git && cd tippecanoe && make -j && make install && cd .. && rm -r tippecanoe
RUN apt-get install -y wget && \
    wget -qO- https://github.com/protomaps/go-pmtiles/releases/download/v1.11.1/go-pmtiles_1.11.1_Linux_x86_64.tar.gz | tar -xz && \
    mv pmtiles /usr/local/bin

#-#-#-#-#-#-#
FROM python:3.11-slim
COPY --from=map-utilities-build-image /usr/local/bin/tile-join /usr/local/bin/tippecanoe* /usr/local/bin/pmtiles /usr/local/bin/
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN apt-get update && \
    apt-get install -y binutils libproj-dev gdal-bin

# Take bleeding-edge auditor-core package (from tox build in build.sh).
# We do not wait for a new auditor-core release (i.e. Git tag).
COPY gccd.tar.gz .
RUN pip install --no-cache-dir gccd.tar.gz

WORKDIR /code
COPY ./app /code/app

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "80"]
