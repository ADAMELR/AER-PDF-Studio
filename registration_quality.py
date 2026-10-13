"""Independent check-point validation for two-point similarity registration.
The third pair must NOT be used to determine the transformation.
Residual is expressed in rendered image pixels, not real-world metres.
"""
from math import cos, sin, radians, hypot, isfinite

def check_point_residual(reference_check, moving_check, transform):
    vals=(*reference_check,*moving_check)
    if len(vals)!=4 or not all(isfinite(float(v)) for v in vals):
        raise ValueError("Check points must contain finite coordinates")
    angle=radians(transform["rotation_degrees"])
    factor=transform["scale"]
    if not isfinite(factor) or factor<=0:
        raise ValueError("Invalid registration scale")
    x,y=map(float,moving_check)
    tx=transform["translation_x"]
    ty=transform["translation_y"]
    mapped_x=factor*(cos(angle)*x-sin(angle)*y)+tx
    mapped_y=factor*(sin(angle)*x+cos(angle)*y)+ty
    residual=hypot(mapped_x-float(reference_check[0]),mapped_y-float(reference_check[1]))
    return {"check_residual_px":round(residual,3),
            "quality_status":"CHECK" if residual<=3 else "REVIEW",
            "quality_note":"Independent third-point residual in render pixels; check drawing accuracy manually."}
