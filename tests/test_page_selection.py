import unittest
from page_selection import parse_page_selection

class PageSelectionTests(unittest.TestCase):
    def test_all(self):
        self.assertEqual(parse_page_selection("all",3),[0,1,2])
    def test_mixed_pages(self):
        self.assertEqual(parse_page_selection("3,1-2,2",5),[0,1,2])
    def test_outside_document(self):
        with self.assertRaises(ValueError):
            parse_page_selection("2-4",3)
    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            parse_page_selection("1,,3",4)
