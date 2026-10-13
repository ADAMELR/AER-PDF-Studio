import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from pypdf import PdfWriter
from arabic_ocr import ocr_pdf_pages, OCRSetupError

class ArabicOCRTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.source=self.root/"مسح ضوئي.pdf"
        writer=PdfWriter()
        writer.add_blank_page(width=200,height=200)
        with self.source.open("wb") as stream:
            writer.write(stream)
        self.exe=self.root/"tesseract.exe"
        self.exe.write_bytes(b"test")

    def test_local_ocr_mocked(self):
        from subprocess import CompletedProcess
        def fake_run(command, **kwargs):
            if "--list-langs" in command:
                return CompletedProcess(command,0,"List of available languages\nara\neng\n","")
            return CompletedProcess(command,0,"مرحبا بالعالم","")
        target=self.root/"النص.txt"
        with patch("arabic_ocr.subprocess.run",side_effect=fake_run):
            result=ocr_pdf_pages(self.source,target,executable=self.exe)
        self.assertEqual(result["pages"],1)
        self.assertIn("مرحبا بالعالم",target.read_text(encoding="utf-8-sig"))

    def test_missing_language(self):
        from subprocess import CompletedProcess
        with patch("arabic_ocr.subprocess.run",
                   return_value=CompletedProcess([],0,"List of available languages\neng\n","")):
            with self.assertRaises(OCRSetupError):
                ocr_pdf_pages(self.source,self.root/"text.txt",executable=self.exe)

    def test_bad_language_rejected(self):
        with self.assertRaises(ValueError):
            ocr_pdf_pages(self.source,self.root/"text.txt",language="foo",executable=self.exe)

    def test_bad_page_rejected(self):
        from subprocess import CompletedProcess
        with patch("arabic_ocr.subprocess.run",
                   return_value=CompletedProcess([],0,"List of available languages\nara\neng\n","")):
            with self.assertRaises(ValueError):
                ocr_pdf_pages(self.source,self.root/"text.txt",pages=[2],executable=self.exe)
