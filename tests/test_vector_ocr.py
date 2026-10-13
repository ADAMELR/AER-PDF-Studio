import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from vector_ocr import make_vector_searchable_pdf, remove_ocr_page_images

class VectorOCRTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.source=self.root/"original.pdf"
        drawing=canvas.Canvas(str(self.source),pagesize=(200,200))
        drawing.setFont("Helvetica",12)
        drawing.drawString(20,120,"ORIGINAL-VECTOR")
        drawing.showPage()
        drawing.save()
        self.exe=self.root/"tesseract.exe"
        self.exe.write_bytes(b"fake")

    def mock_call(self,cmd,**kwargs):
        if "--list-langs" in cmd:
            return CompletedProcess(cmd,0,"List of available languages\nara\neng\n","")
        dest=str(Path(cmd[2]).with_suffix(".pdf"))
        document=canvas.Canvas(dest,pagesize=(200,200))
        # OCR text is invisible, similar to Tesseract's searchable PDFs.
        text=document.beginText(20,70)
        text.setTextRenderMode(3)
        text.textLine("SEARCHABLE-HIDDEN")
        document.drawText(text)
        document.showPage()
        document.save()
        return CompletedProcess(cmd,0,"","")

    def test_preserves_original_and_adds_hidden_text(self):
        output=self.root/"result.pdf"
        with patch("arabic_ocr.subprocess.run",side_effect=self.mock_call),\
             patch("vector_ocr.subprocess.run",side_effect=self.mock_call):
            result=make_vector_searchable_pdf(self.source,output,executable=self.exe)
        self.assertEqual(result["pages"],1)
        text=PdfReader(output).pages[0].extract_text()
        self.assertIn("ORIGINAL-VECTOR",text)
        self.assertIn("SEARCHABLE-HIDDEN",text)
        self.assertIn("ORIGINAL-VECTOR",PdfReader(self.source).pages[0].extract_text())

    def test_same_source_destination_rejected(self):
        with self.assertRaises(ValueError):
            make_vector_searchable_pdf(self.source,self.source,executable=self.exe)

    def test_failure_does_not_write_output(self):
        output=self.root/"result.pdf"
        def no_output(cmd,**kwargs):
            if "--list-langs" in cmd:
                return CompletedProcess(cmd,0,"List of available languages\nara\neng\n","")
            return CompletedProcess(cmd,0,"","")
        with patch("arabic_ocr.subprocess.run",side_effect=no_output),\
             patch("vector_ocr.subprocess.run",side_effect=no_output):
            with self.assertRaises(RuntimeError):
                make_vector_searchable_pdf(self.source,output,executable=self.exe)
        self.assertFalse(output.exists())
