from typing import Any, List, Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


class GeoJson(BaseModel):
    properties: Any
    geometry: List


@app.post("/changemaps/")
def post_geojson(geojson: GeoJson, q: Union[str, None] = None):
    return geojson
