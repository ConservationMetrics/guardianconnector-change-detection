import json
import tempfile
from typing import Any, List, Union

import fastapi

import gccd


app = fastapi.FastAPI()


@app.get("/")
def redirect_to_docs():
    return fastapi.responses.RedirectResponse("/docs")


@app.post("/changemaps/")
def make_changemaps(feacoll: Any = fastapi.Body(), q: Union[str, None] = None):
    with tempfile.NamedTemporaryFile(
        "w+", prefix="input-", suffix=".json"
    ) as input_fp, tempfile.TemporaryDirectory() as outdir:
        print(input_fp.name)
        json.dump(feacoll, input_fp)
        input_fp.flush()
        input_fp.seek(0)

        bbox = gccd.flow(input_fp.name, outdir, "output")
    return {"bbox": bbox}
