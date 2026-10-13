import tempfile
import unittest
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pdf_operations import merge_pdfs, split_pdf, rotate_pdf

class PdfOperationsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.a, self.b = self.folder / "a.pdf", self.folder / "b.pdf"
        for target, count in [(self.a, 2), (self.b, 3)]:
            writer = PdfWriter()
            for _ in range(count):
                writer.add_blank_page(width=612, height=792)
            with target.open("wb") as stream:
                writer.write(stream)

    def test_merge(self):
        output = self.folder / "merged.pdf"
        self.assertEqual(merge_pdfs([self.a, self.b], output), 5)
        self.assertEqual(len(PdfReader(output).pages), 5)

    def test_merge_requires_input(self):
        with self.assertRaises(ValueError):
            merge_pdfs([], self.folder / "invalid.pdf")

    def test_split(self):
        outputs = split_pdf(self.b, self.folder / "pages")
        self.assertEqual(len(outputs), 3)
        self.assertTrue(all(len(PdfReader(p).pages) == 1 for p in outputs))

    def test_rotate(self):
        output = self.folder / "rotated.pdf"
        self.assertEqual(rotate_pdf(self.a, output), 2)
        self.assertTrue(all(page.get("/Rotate") == 90 for page in PdfReader(output).pages))

    def test_invalid_rotation(self):
        with self.assertRaises(ValueError):
            rotate_pdf(self.a, self.folder / "bad.pdf", 45)

if __name__ == "__main__":
    unittest.main()
