"""Engineering geometry in PDF point coordinates (1 point = 1/72 inch).
User-supplied calibration is always required; printed scale labels are not trusted.
"""
from dataclasses import dataclass
from math import hypot, isfinite

@dataclass(frozen=True)
class Calibration:
    metres_per_point: float

    def __post_init__(self):
        if not isfinite(self.metres_per_point) or self.metres_per_point <= 0:
            raise ValueError("Calibration must be finite and positive")

def distance_points(start, end):
    coordinates = (*start, *end)
    if len(coordinates) != 4 or not all(isfinite(float(v)) for v in coordinates):
        raise ValueError("Coordinates must be finite pairs")
    return hypot(float(end[0])-float(start[0]), float(end[1])-float(start[1]))

def calibrate(start, end, known_length_m):
    length = float(known_length_m)
    if not isfinite(length) or length <= 0:
        raise ValueError("Known length must be positive")
    length_in_points = distance_points(start, end)
    if length_in_points <= 0:
        raise ValueError("Select two different points to calibrate")
    return Calibration(length / length_in_points)

def length_metres(start, end, calibration):
    return distance_points(start, end) * calibration.metres_per_point

def rectangle_area_m2(rect, calibration):
    x0, y0, x1, y1 = map(float, rect)
    if not all(isfinite(v) for v in (x0,y0,x1,y1)) or x1 <= x0 or y1 <= y0:
        raise ValueError("Rectangle must have positive finite dimensions")
    return (x1-x0) * (y1-y0) * calibration.metres_per_point**2

def screen_to_pdf(point, zoom, page_height_points):
    if not isfinite(zoom) or zoom <= 0:
        raise ValueError("Zoom must be positive")
    return (point[0] / zoom, page_height_points - point[1] / zoom)
