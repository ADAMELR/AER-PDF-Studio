import unittest
from qt_model import DocumentState, page_size_fit

class QtDocumentStateTests(unittest.TestCase):
    def test_page_clamping(self):
        state=DocumentState("drawing.pdf")
        self.assertEqual(state.set_page(50,3),2)
        self.assertEqual(state.set_page(-1,3),0)
    def test_zoom_bounds(self):
        state=DocumentState("drawing.pdf")
        self.assertEqual(state.set_zoom(0.01),0.25)
        self.assertEqual(state.set_zoom(99),4.0)
    def test_filename_unicode(self):
        self.assertEqual(DocumentState("/tmp/الرسومات.pdf").title,"الرسومات.pdf")
    def test_fit_scale(self):
        self.assertAlmostEqual(page_size_fit(100,200,500,500),2.36)
        with self.assertRaises(ValueError):
            page_size_fit(0,200,500,500)
