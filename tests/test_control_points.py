import unittest
from PIL import Image, ImageDraw
from control_points import align_control_points

class ControlPointTests(unittest.TestCase):
    def test_translation_recovery(self):
        ref=Image.new("RGB",(160,160),"white")
        draw=ImageDraw.Draw(ref)
        draw.rectangle((30,30,70,70),fill="black")
        moving=Image.new("RGB",ref.size,"white")
        moving.paste(ref,(10,5))
        corrected,report=align_control_points(ref,moving,[(30,30),(70,30)],[(40,35),(80,35)])
        self.assertEqual(corrected.getpixel((50,50)),(0,0,0))
        self.assertAlmostEqual(report["scale"],1)
    def test_rotate_corrects_points(self):
        im=Image.new("RGB",(100,100),"white")
        corrected,report=align_control_points(im,im,[(20,20),(20,60)],[(20,20),(60,20)])
        self.assertAlmostEqual(report["rotation_degrees"],90)
    def test_duplicate_points_rejected(self):
        im=Image.new("RGB",(100,100),"white")
        with self.assertRaises(ValueError):
            align_control_points(im,im,[(0,0),(0,0)],[(0,0),(5,5)])
    def test_large_scale_rejected(self):
        im=Image.new("RGB",(100,100),"white")
        with self.assertRaises(ValueError):
            align_control_points(im,im,[(0,0),(90,0)],[(0,0),(10,0)])
if __name__=="__main__":
    unittest.main()
