import unittest
from thumbnails import thumbnail_size, visible_thumbnail_indices

class ThumbnailsTests(unittest.TestCase):
    def test_landscape_page(self):
        self.assertEqual(thumbnail_size(400,200,120,160),(120,60))
    def test_portrait_page(self):
        self.assertEqual(thumbnail_size(200,400,120,160),(80,160))
    def test_no_enlargement(self):
        self.assertEqual(thumbnail_size(40,60),(40,60))
    def test_neighbors(self):
        self.assertEqual(visible_thumbnail_indices(0,30,2),[0,1,2])
        self.assertEqual(visible_thumbnail_indices(29,30,2),[27,28,29])
    def test_invalid_bounds(self):
        with self.assertRaises(ValueError):
            visible_thumbnail_indices(4,2)
