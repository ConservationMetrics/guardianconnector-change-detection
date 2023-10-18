from gccd.calculate_bbox import calculate_bounding_box


def test_calculate_bounding_box__point():
    fcoll = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-122.680, 45.58]},
            }
        ],
    }
    assert calculate_bounding_box(fcoll["features"]) == (
        -122.680,
        45.58,
        -122.680,
        45.58,
    )


def test_calculate_bounding_box__line():
    fcoll = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Line",
                    "coordinates": [
                        [-122.680, 45.58],
                        [-123.230, 45.62],
                        [-122.80, 45.22],
                    ],
                },
            }
        ],
    }
    assert calculate_bounding_box(fcoll["features"]) == (-123.23, 45.22, -122.68, 45.62)
