import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from pypdf import PdfReader, PdfWriter
from searchable_ocr import make_searchable_pdf
from arabic_ocr import OCRSetupError

class SearchableOCRTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.source=self.root/"الأصل.pdf"
        writer=PdfWriter()
        writer.add_blank_page(width=120,height=160)
        writer.add_blank_page(width=120,height=160)
        with self.source.open("wb") as output:
            writer.write(output)
        self.exe=self.root/"tesseract.exe"
        self.exe.write_bytes(b"mock binary")

    def fake_tesseract(self,command,**kwargs):
        if "--list-langs" in command:
            return CompletedProcess(command,0,"List of available languages\nara\neng\n","")
        self.assertEqual(command[-1],"pdf")
        destination=Path(command[2]).with_suffix(".pdf")
        pdf=PdfWriter()
        pdf.add_blank_page(width=120,height=160)
        with destination.open("wb") as handle:
            pdf.write(handle)
        return CompletedProcess(command,0,"","")

    def test_searchable_pdf_two_pages(self):
        target=self.root/"searchable.pdf"
        with patch("searchable_ocr.subprocess.run",side_effect=self.fake_tesseract),\
             patch("arabic_ocr.subprocess.run",side_effect=self.fake_tesseract):
            result=make_searchable_pdf(self.source,target,executable=self.exe)
        self.assertEqual(result["pages"],2)
        self.assertEqual(len(PdfReader(target).pages),2)
        self.assertEqual(len(PdfReader(self.source).pages),2)

    def test_no_source_overwrite(self):
        with self.assertRaises(ValueError):
            make_searchable_pdf(self.source,self.source,executable=self.exe)

    def test_missing_arabic_model(self):
        def installed(command,**kwargs):
            return CompletedProcess(command,0,"List of available languages\neng\n","")
        with patch("arabic_ocr.subprocess.run",side_effect=installed):
            with self.assertRaises(OCRSetupError):
                make_searchable_pdf(self.source,self.root/"new.pdf",executable=self.exe)

    def test_missing_page_output_does_not_write_final(self):
        target=self.root/"new.pdf"
        def no_pdf(command,**kwargs):
            if "--list-langs" in command:
                return CompletedProcess(command,0,"List of available languages\neng\nara\n","")
            return CompletedProcess(command,0,"","")
        with patch("arabic_ocr.subprocess.run",side_effect=no_pdf),\
             patch("searchable_ocr.subprocess.run",side_effect=no_pdf):
            with self.assertRaises(RuntimeError):
                make_searchable_pdf(self.source,target,executable=self.exe)
        self.assertFalse(target.exists())
