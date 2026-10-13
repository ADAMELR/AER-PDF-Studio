"""Versioned, local JSON project register with per-page scale calibration."""
import json
import math
import os
from pathlib import Path

SCHEMA_VERSION = 1

def _valid_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)

def save_project(path, source, records, calibrations):
    rows=[]
    for m in records:
        if not isinstance(m.page,int) or m.page < 1 or not _valid_number(m.value) or m.value < 0:
            raise ValueError("Invalid measurement record")
        if m.kind not in ("Distance","Rectangle","Polygon") or m.unit not in ("m","m2"):
            raise ValueError("Unsupported measurement type or units")
        rows.append({"page":m.page,"kind":m.kind,"value":m.value,"unit":m.unit,"description":str(m.description)})
    scales={}
    for page, calibration in calibrations.items():
        if not isinstance(page,int) or page < 0 or not _valid_number(calibration.metres_per_point) or calibration.metres_per_point <= 0:
            raise ValueError("Invalid page calibration")
        scales[str(page)]=calibration.metres_per_point
    payload={"schema_version":SCHEMA_VERSION,"source":str(Path(source).resolve()),"measurements":rows,"calibrations":scales}
    destination=Path(path)
    tmp=destination.with_name(destination.name+".tmp")
    try:
        with tmp.open("w",encoding="utf-8") as stream:
            json.dump(payload,stream,indent=2,ensure_ascii=False,allow_nan=False)
        os.replace(tmp,destination)
    finally:
        if tmp.exists():
            tmp.unlink()
    return destination

def load_project(path, source):
    from measurements import Calibration
    from takeoff import Measurement
    payload=json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported project format")
    if Path(payload["source"]).resolve() != Path(source).resolve():
        raise ValueError("Project was saved for a different PDF; open the correct source")
    rows=[]
    for record in payload["measurements"]:
        m=Measurement(**record)
        if not isinstance(m.page,int) or m.page<1 or not _valid_number(m.value) or m.value<0 or m.kind not in ("Distance","Rectangle","Polygon") or m.unit not in ("m","m2"):
            raise ValueError("Invalid measurement record")
        rows.append(m)
    scales={}
    for key,value in payload["calibrations"].items():
        page=int(key)
        if page<0 or not _valid_number(value):
            raise ValueError("Invalid calibration")
        scales[page]=Calibration(value)
    return rows,scales
