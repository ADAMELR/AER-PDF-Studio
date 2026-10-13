import unittest
from registration_quality import check_point_residual

class QualityTests(unittest.TestCase):
    def test_perfect_translation(self):
        transform={"rotation_degrees":0,"scale":1,"translation_x":-10,"translation_y":5}
        result=check_point_residual((20,35),(30,30),transform)
        self.assertEqual(result["check_residual_px"],0)
        self.assertEqual(result["quality_status"],"CHECK")

    def test_bad_holdout(self):
        transform={"rotation_degrees":0,"scale":1,"translation_x":0,"translation_y":0}
        self.assertEqual(check_point_residual((100,100),(112,100),transform)["quality_status"],"REVIEW")

    def test_bad_coordinates(self):
        with self.assertRaises(ValueError):
            check_point_residual((float("nan"),0),(0,0),{})
