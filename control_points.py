"""Two-control-point similarity registration for equal-size raster images.

Control points are pixel (x,y) coordinates. Corresponding pairs define
a rotation, uniform scale and translation; this does NOT fix perspective
or nonuniform stretch. Points must be distinct.
"""
from math import atan2, cos, sin, hypot, isfinite
from PIL import Image

def align_control_points(reference, moving, reference_points, moving_points):
    if reference.size != moving.size:
        raise ValueError("Images must have equal canvas sizes")
    if len(reference_points)!=2 or len(moving_points)!=2:
        raise ValueError("Exactly two matching control points are required")
    (ax,ay),(bx,by)=reference_points
    (cx,cy),(dx,dy)=moving_points
    values=[ax,ay,bx,by,cx,cy,dx,dy]
    if not all(isfinite(float(v)) for v in values):
        raise ValueError("Control points must be finite")
    ux,uy=bx-ax,by-ay
    vx,vy=dx-cx,dy-cy
    n_ref=hypot(ux,uy)
    n_mov=hypot(vx,vy)
    if min(n_ref,n_mov)<1:
        raise ValueError("Control points must be distinct")
    factor=n_ref/n_mov
    if not .5<=factor<=2:
        raise ValueError("Scale correction exceeds allowed 0.5–2.0 range")
    angle=atan2(uy,ux)-atan2(vy,vx)
    c=cos(angle)
    s=sin(angle)
    tx=ax-factor*(c*cx-s*cy)
    ty=ay-factor*(s*cx+c*cy)
    # PIL output-coordinate -> source-coordinate inverse affine map
    a=c/factor
    b=s/factor
    d=-s/factor
    e=c/factor
    x0=-(a*tx+b*ty)
    y0=-(d*tx+e*ty)
    aligned=moving.transform(reference.size,Image.Transform.AFFINE,
        (a,b,x0,d,e,y0),resample=Image.Resampling.BICUBIC,fillcolor="white")
    return aligned,{"rotation_degrees":angle*180/3.141592653589793,"scale":factor,
                    "translation_x":tx,"translation_y":ty,
                    "warning":"Two-point registration; manually validate other drawing features."}
