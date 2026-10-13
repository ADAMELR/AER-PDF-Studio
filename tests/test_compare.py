import tempfile
import unittest
from pathlib import Path
from pypdf import PdfWriter
from compare import compare_pages
from PIL import Image

class ComparisonTests(unittest.TestCase):
    def create_pdf(self,path,w,h):
        writer=PdfWriter()
        writer.add_blank_page(width=w,height=h)
        with path.open("wb") as stream:
            writer.write(stream)

    def test_identical_pages(self):
        with tempfile.TemporaryDirectory() as folder:
            a=Path(folder)/"a.pdf"
            b=Path(folder)/"b.pdf"
            target=Path(folder)/"compare.png"
            self.create_pdf(a,200,200)
            self.create_pdf(b,200,200)
            compare_pages(a,b,target,scale=1)
            self.assertEqual(Image.open(target).size,(200,200))

    def test_mismatched_sizes(self):
        with tempfile.TemporaryDirectory() as folder:
            a=Path(folder)/"a.pdf"
            b=Path(folder)/"b.pdf"
            self.create_pdf(a,200,200)
            self.create_pdf(b,300,200)
            with self.assertRaises(ValueError):
                compare_pages(a,b,Path(folder)/"x.png")

if __name__ == "__main__":
    unittest.main()
