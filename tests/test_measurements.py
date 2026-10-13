import unittest
from measurements import calibrate, length_metres, rectangle_area_m2, screen_to_pdf

class EngineeringMeasurements(unittest.TestCase):
    def setUp(self):
        self.cal = calibrate((0,0), (100,0), 10)

    def test_calibrated_length(self):
        self.assertAlmostEqual(length_metres((0,0), (30,40), self.cal), 5)

    def test_area_in_square_metres(self):
        self.assertAlmostEqual(rectangle_area_m2((0,0,100,50), self.cal), 50)

    def test_zoom_independent_coordinates(self):
        self.assertEqual(screen_to_pdf((200, 100), 2, 792), (100,742))

    def test_invalid_calibration_zero_line(self):
        with self.assertRaises(ValueError):
            calibrate((20,20),(20,20),5)

    def test_invalid_calibration_negative_length(self):
        with self.assertRaises(ValueError):
            calibrate((0,0),(20,0),-1)

    def test_invalid_area(self):
        with self.assertRaises(ValueError):
            rectangle_area_m2((100,0,0,20), self.cal)

    def test_nonfinite_data(self):
        with self.assertRaises(ValueError):
            calibrate((0,0),(float("nan"),0),10)

if __name__ == "__main__":
    unittest.main()
