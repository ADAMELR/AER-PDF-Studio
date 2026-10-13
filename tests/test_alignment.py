import unittest
from PIL import Image, ImageDraw
from alignment import estimate_translation, translate_to_match

class TranslationAlignmentTests(unittest.TestCase):
    def test_known_shift(self):
        original=Image.new("RGB",(240,200),"white")
        pen=ImageDraw.Draw(original)
        pen.rectangle((40,30,170,155),outline="black",width=3)
        pen.line((50,50,180,145),fill="black",width=3)
        moved=translate_to_match(original,7,-5)
        dx,dy,valid=estimate_translation(original,moved,max_shift=12,sample_width=240)
        self.assertTrue(valid)
        self.assertEqual((dx,dy),(-7,5))

    def test_blank_page_not_registered(self):
        a=Image.new("RGB",(200,200),"white")
        self.assertEqual(estimate_translation(a,a),(0,0,False))

    def test_mismatched_images_rejected(self):
        with self.assertRaises(ValueError):
            estimate_translation(Image.new("RGB",(200,200)), Image.new("RGB",(300,200)))
