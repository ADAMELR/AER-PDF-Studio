"""Create a NEW searchable PDF from rasterized source pages and Tesseract's hidden text layer.

Intended for scanned documents. Vector content, PDF annotations, and links in
the source are NOT preserved. No network access or external cloud OCR.
"""
from pathlib import Path
import os
import subprocess
import tempfile

import pypdfium2 as pdfium
from pypdf import PdfReader, PdfWriter

from arabic_ocr import LANGUAGES, OCRSetupError, available_languages, tesseract_executable


def make_searchable_pdf(source, destination, language="ara+eng", executable=None, scale=2.0):
    if language not in LANGUAGES.values():
        raise ValueError("Unsupported OCR language selection")
    if not 1 <= scale <= 3:
        raise ValueError("OCR scale must be between 1 and 3")
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError("Never overwrite the source PDF")
    binary = tesseract_executable(executable)
    missing = set(language.split("+")) - available_languages(binary)
    if missing:
        raise OCRSetupError("Tesseract language data missing: " + ", ".join(sorted(missing)))
    doc = pdfium.PdfDocument(str(source))
    try:
        if not len(doc):
            raise ValueError("PDF contains no pages")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="aer_searchable_") as directory:
            temp = Path(directory)
            writer = PdfWriter()
            for index in range(len(doc)):
                page = doc[index]
                try:
                    image = page.render(scale=scale).to_pil().convert("RGB")
                    if image.width * image.height > 25_000_000:
                        raise ValueError("Page too large for OCR at this resolution; reduce scale")
                    image_path = temp / "source.png"
                    image.save(image_path, format="PNG")
                    output_base = temp / "ocr_page"
                    try:
                        subprocess.run(
                            [binary, str(image_path), str(output_base), "-l", language, "pdf"],
                            capture_output=True, text=True, timeout=120, check=True,
                            encoding="utf-8", errors="replace")
                    except (OSError, subprocess.SubprocessError) as exc:
                        raise RuntimeError(f"Searchable OCR failed on page {index+1}: {exc}") from exc
                    generated_pdf = output_base.with_suffix(".pdf")
                    if not generated_pdf.is_file():
                        raise RuntimeError(f"Tesseract did not generate a PDF for page {index+1}")
                    reader = PdfReader(str(generated_pdf))
                    if len(reader.pages) != 1:
                        raise RuntimeError(f"Tesseract returned an unexpected page count on page {index+1}")
                    writer.add_page(reader.pages[0])
                finally:
                    page.close()
            staging = temp / "complete.pdf"
            with staging.open("wb") as handle:
                writer.write(handle)
            # Copy to a sibling temp file before the final atomic rename.
            import shutil
            fd, temp_name = tempfile.mkstemp(prefix=".aer_ocr_", suffix=".pdf", dir=destination.parent)
            try:
                with os.fdopen(fd, "wb") as output, staging.open("rb") as data:
                    shutil.copyfileobj(data, output)
                os.replace(temp_name, destination)
            finally:
                if os.path.exists(temp_name):
                    os.unlink(temp_name)
        return {"pages": len(doc), "output": str(destination)}
    finally:
        doc.close()
