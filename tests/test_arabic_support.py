import unittest
from localization import tr
from pdf_text_search import normalize_text

class ArabicSupportTests(unittest.TestCase):
    def test_translation_arabic(self):
        self.assertEqual(tr("ar","add"),"إضافة ملفات PDF")
    def test_translation_english(self):
        self.assertEqual(tr("en","open"),"Open Viewer")
    def test_unknown_language_fallback(self):
        self.assertEqual(tr("fr","open"),"Open Viewer")
    def test_unicode_normalization(self):
        self.assertEqual(normalize_text("أ"),normalize_text("أ"))
    def test_mixed_language_search(self):
        self.assertIn(normalize_text("مشروع 24"),normalize_text("ملف مشروع 24 - DWG"))
