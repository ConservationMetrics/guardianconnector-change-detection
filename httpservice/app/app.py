import json
import os
import tarfile
import tempfile
import base64
from typing import Any, Optional


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


@app.post("/changemaps/", dependencies=[fastapi.Security(check_apikey_header)])
async def make_changemaps(
    data: dict = fastapi.Body(...),
    output_tar=fastapi.Depends(sendable_tempfile)
):
    input_geojson = data.get("input_geojson")
    images = data.get("images", {})

    with tempfile.NamedTemporaryFile(
        "w+", prefix="input-", suffix=".json"
    ) as input_fp, tempfile.TemporaryDirectory() as outdir:

        # Dump input geojson to temp file
        json.dump(input_geojson, input_fp)
        input_fp.flush()
        input_fp.seek(0)

        t0 = images.get("t0")
        t1 = images.get("t1")

        # Run GCCD.flow()
        # With GeoTIFF inputs:
        if t0 and t1:
            with WriteToTempFile(images["t0"], suffix=".tif") as t0_fp, \
            WriteToTempFile(images["t1"], suffix=".tif") as t1_fp: \
            gccd.flow(input_fp.name, t0_fp, t1_fp, outdir, "output")
        # Without GeoTIFF inputs:
        else:
            gccd.flow(input_fp.name, None, None, outdir, "output")

        create_tarfile(outdir, output_tar)

    return fastapi.responses.FileResponse(
        output_tar,
        headers={"Content-Disposition": "attachment; filename=changemap.tar"},
    )

class WriteToTempFile:
    def __init__(self, base64_str, suffix=""):
        self.base64_str = base64_str
        self.suffix = suffix

    def __enter__(self):
        # Create a temporary file with the specified suffix
        self.temp_file = tempfile.NamedTemporaryFile(suffix=self.suffix, delete=False)

        # Decode the base64 string and write to the temporary file
        decoded_data = base64.b64decode(self.base64_str)
        self.temp_file.write(decoded_data)
        self.temp_file.close()

        # Return the temporary file name
        return self.temp_file.name

    def __exit__(self, exc_type, exc_value, traceback):
        # Delete the temporary file when the context exits
        os.remove(self.temp_file.name)
