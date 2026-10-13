import csv
import tempfile
import unittest
from pathlib import Path
from measurements import Calibration
from takeoff import Measurement, polygon_area_m2, export_register_csv

class TakeoffTests(unittest.TestCase):
    def setUp(self):
        self.scale = Calibration(.1)

    def test_polygon_rectangle(self):
        self.assertAlmostEqual(polygon_area_m2([(0,0),(100,0),(100,50),(0,50)],self.scale),50)

    def test_triangle(self):
        self.assertAlmostEqual(polygon_area_m2([(0,0),(100,0),(0,100)],self.scale),50)

    def test_reverse_winding(self):
        a=[(0,0),(100,0),(0,100)]
        self.assertAlmostEqual(polygon_area_m2(a,self.scale),polygon_area_m2(list(reversed(a)),self.scale))

    def test_invalid_polygon(self):
        with self.assertRaises(ValueError):
            polygon_area_m2([(0,0),(1,1)],self.scale)

    def test_csv_and_injection_protection(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/"results.csv"
            export_register_csv([Measurement(1,"Polygon",50,"m2","=HYPERLINK(\"bad\")")],target)
            with target.open(encoding="utf-8-sig",newline="") as stream:
                rows=list(csv.reader(stream))
            self.assertEqual(len(rows),2)
            self.assertTrue(rows[1][4].startswith("'="))
            self.assertEqual(rows[1][2],"50.0000")

if __name__ == "__main__":
    unittest.main()
