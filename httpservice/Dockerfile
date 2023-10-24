FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends build-essential libsqlite3-dev zlib1g-dev git
RUN git clone https://github.com/mapbox/tippecanoe.git && cd tippecanoe && make -j && make install && cd .. && rm -r tippecanoe

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Take bleeding-edge auditor-core package (from tox build in build.sh).
# We do not wait for a new auditor-core release (i.e. Git tag).
COPY gccd.tar.gz .
RUN pip install --no-cache-dir gccd.tar.gz

WORKDIR /code
COPY ./app /code/app

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "80"]
