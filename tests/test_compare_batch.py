import tempfile
import unittest
from pathlib import Path
from pypdf import PdfWriter
from compare_batch import compare_document_pages

def make_pdf(path,pages):
    writer=PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=200,height=200)
    with path.open("wb") as file:
        writer.write(file)

class BatchComparisonTests(unittest.TestCase):
    def test_all_pages_exported(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            make_pdf(p/"a.pdf",2)
            make_pdf(p/"b.pdf",2)
            results=compare_document_pages(p/"a.pdf",p/"b.pdf",p/"output",scale=1)
            self.assertEqual(len(results),2)
            self.assertTrue(all(path.exists() for path in results))

    def test_count_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            make_pdf(p/"a.pdf",1)
            make_pdf(p/"b.pdf",2)
            with self.assertRaises(ValueError):
                compare_document_pages(p/"a.pdf",p/"b.pdf",p/"output",scale=1)
