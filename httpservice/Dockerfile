FROM python:3.10-slim-bullseye

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Take bleeding-edge auditor-core package (from tox build in build.sh).
# We do not wait for a new auditor-core release (i.e. Git tag).
COPY gccd.tar.gz .
RUN pip install --no-cache-dir gccd.tar.gz

WORKDIR /code
COPY ./app /code/app

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "80"]
