import json
import os
import tarfile
import tempfile
import base64
from typing import Any, Optional
<<<<<<< HEAD
from pydantic import BaseModel, Field
=======

>>>>>>> 6455d80 (Receive base64 t0 and t1 inputs in JSON payload)

import fastapi
import gccd

from .security import check_apikey_header


app = fastapi.FastAPI()


@app.get("/")
def redirect_to_docs():
    return fastapi.responses.RedirectResponse("/docs")


async def sendable_tempfile():
    """Dependency injection to FastAPI to inject a temporary output file
    that won't be deleted until the FastAPI request is completely returned.

    Inspired by: https://stackoverflow.com/a/72535413
    """
    dir = tempfile.NamedTemporaryFile()
    try:
        yield dir.name
    finally:
        del dir


def create_tarfile(directory, tar_filename):
    with tarfile.open(tar_filename, "w") as tar:
        for root, _, files in os.walk(directory):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, directory)
                tar.add(full_path, arcname=relative_path)

class ChangemapRequestData(BaseModel):
    input_geojson: dict
    images: dict = Field(default_factory=dict)

@app.post("/changemaps/", dependencies=[fastapi.Security(check_apikey_header)])
async def make_changemaps(
<<<<<<< HEAD
    data: ChangemapRequestData,
    output_tar=fastapi.Depends(sendable_tempfile)
):
    input_geojson = data.input_geojson
    images = data.images
=======
    data: dict = fastapi.Body(...),
    output_tar=fastapi.Depends(sendable_tempfile)
):
    input_geojson = data.get("input_geojson")
    input_t0 = data.get("input_t0")
    input_t1 = data.get("input_t1")
>>>>>>> 6455d80 (Receive base64 t0 and t1 inputs in JSON payload)

    with tempfile.NamedTemporaryFile(
        "w+", prefix="input-", suffix=".json"
    ) as input_fp, tempfile.TemporaryDirectory() as outdir:

<<<<<<< HEAD
        # Dump input geojson to temp file
=======
        # Dump feacoll to temp file
>>>>>>> 6455d80 (Receive base64 t0 and t1 inputs in JSON payload)
        json.dump(input_geojson, input_fp)
        input_fp.flush()
        input_fp.seek(0)

        # Decode and save input_t0 and input_t1 (if provided)
        if input_t0:
            input_t0 = save_base64_to_tempfile(input_t0_base64, suffix=".tiff")

        if input_t1:
            input_t1 = save_base64_to_tempfile(input_t1_base64, suffix=".tiff")

        # Run the GCCD flow()
        gccd.flow(input_fp.name, input_t0, input_t1, outdir, "output")

        create_tarfile(outdir, output_tar)

    return fastapi.responses.FileResponse(
        output_tar,
        headers={"Content-Disposition": "attachment; filename=changemap.tar"},
    )

def save_base64_to_tempfile(base64_str, suffix=""):
    """
    Decode base64 string and write to a temporary file.
    Return the path of the temporary file.
    """
    binary_data = base64.b64decode(base64_str)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    with open(temp_file.name, 'wb') as file:
        file.write(binary_data)
    return temp_file.name
