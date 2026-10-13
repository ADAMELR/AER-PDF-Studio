import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from annotations import add_rectangle_markup


class MarkupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.source = self.folder / "original.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with self.source.open("wb") as stream:
            writer.write(stream)
        self.output = self.folder / "marked.pdf"

    def test_rectangle_added_without_changing_source(self):
        original_bytes = self.source.read_bytes()
        add_rectangle_markup(self.source, self.output, 0, (30, 50, 180, 150))
        self.assertEqual(self.source.read_bytes(), original_bytes)
        self.assertEqual(len(PdfReader(self.output).pages), 1)
        self.assertNotEqual(self.output.read_bytes(), original_bytes)

    def test_out_of_bounds_rejected(self):
        with self.assertRaises(ValueError):
            add_rectangle_markup(self.source, self.output, 0, (30, 50, 700, 150))

    def test_invalid_page_rejected(self):
        with self.assertRaises(IndexError):
            add_rectangle_markup(self.source, self.output, 3, (30, 50, 180, 150))

    def test_empty_rectangle_rejected(self):
        with self.assertRaises(ValueError):
            add_rectangle_markup(self.source, self.output, 0, (30, 50, 30, 150))

    def test_source_cannot_be_overwritten(self):
        with self.assertRaises(ValueError):
            add_rectangle_markup(self.source, self.source, 0, (30, 50, 180, 150))


if __name__ == "__main__":
    unittest.main()
