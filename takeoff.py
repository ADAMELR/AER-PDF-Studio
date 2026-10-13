"""Calibrated polygon takeoffs and spreadsheet-safe CSV measurement register."""
import csv
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from measurements import Calibration

@dataclass(frozen=True)
class Measurement:
    page: int
    kind: str
    value: float
    unit: str
    description: str = ""

def polygon_area_m2(vertices, calibration: Calibration):
    points = [tuple(map(float, p)) for p in vertices]
    if len(points) < 3 or any(len(p) != 2 or not all(map(isfinite, p)) for p in points):
        raise ValueError("A polygon requires at least three finite 2D points")
    twice = sum(x0*y1 - x1*y0 for (x0,y0),(x1,y1) in zip(points, points[1:]+points[:1]))
    area = abs(twice) / 2 * calibration.metres_per_point**2
    if area <= 0 or not isfinite(area):
        raise ValueError("Polygon has no valid area")
    return area

def _excel_safe(value):
    """Prevent formula execution when CSVs are opened by spreadsheet software."""
    value = str(value)
    if value.lstrip().startswith(("=", "+", "-", "@")) or value.startswith(("\t","\r","\n")):
        return "'" + value
    return value

def export_register_csv(measurements, destination):
    target = Path(destination)
    with target.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(("Page", "Type", "Value", "Unit", "Description"))
        for item in measurements:
            if item.page < 1 or not isfinite(item.value) or item.value < 0:
                raise ValueError("Invalid measurement record")
            writer.writerow((item.page, item.kind, f"{item.value:.4f}", item.unit, _excel_safe(item.description)))
    return target
