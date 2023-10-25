import json
import os
import tarfile
import tempfile
from typing import Any

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
    feacoll: Any = fastapi.Body(), output_tar=fastapi.Depends(sendable_tempfile)
):
    with tempfile.NamedTemporaryFile(
        "w+", prefix="input-", suffix=".json"
    ) as input_fp, tempfile.TemporaryDirectory() as outdir:
        json.dump(feacoll, input_fp)
        input_fp.flush()
        input_fp.seek(0)

        gccd.flow(input_fp.name, outdir, "output")

        create_tarfile(outdir, output_tar)

    return fastapi.responses.FileResponse(
        output_tar,
        headers={"Content-Disposition": "attachment; filename=changemap.tar"},
    )
