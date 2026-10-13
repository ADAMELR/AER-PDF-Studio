import tempfile
import unittest
from pathlib import Path
from measurements import Calibration
from takeoff import Measurement
from project_store import save_project, load_project

class StorageTests(unittest.TestCase):
    def test_save_load_scales_and_records(self):
        with tempfile.TemporaryDirectory() as root:
            source=Path(root)/"drawing.pdf"
            source.write_bytes(b"dummy")
            file=Path(root)/"project.aer.json"
            save_project(file,source,[Measurement(2,"Polygon",35.75,"m2","Concrete")],{1:Calibration(.02)})
            records,scales=load_project(file,source)
            self.assertEqual(records[0].value,35.75)
            self.assertEqual(records[0].description,"Concrete")
            self.assertAlmostEqual(scales[1].metres_per_point,.02)
            with self.assertRaises(ValueError):
                load_project(file,Path(root)/"other.pdf")

    def test_bad_measurement_does_not_write(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                save_project(Path(root)/"bad.json",Path(root)/"a.pdf",[Measurement(1,"Polygon",float("nan"),"m2")],{})
            self.assertFalse((Path(root)/"bad.json").exists())
