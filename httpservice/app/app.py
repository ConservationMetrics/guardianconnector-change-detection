from typing import Any, List, Union

import fastapi

from gccd.calculate_bbox import calculate_bounding_box

app = fastapi.FastAPI()


@app.get("/")
def redirect_to_docs():
    return fastapi.responses.RedirectResponse("/docs")


@app.post("/boundingbox/")
def calc_bbox(feacoll: Any = fastapi.Body(), q: Union[str, None] = None):
    bbox = calculate_bounding_box(feacoll["features"])
    return {"bbox": bbox}
