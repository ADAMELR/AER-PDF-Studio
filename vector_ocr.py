"""Preserve source PDF pages while adding Tesseract OCR text as a hidden overlay.

Unlike searchable_ocr.py, this retains the source PDF as the base. The OCR
image draw calls are stripped from Tesseract's generated PDF content stream.
Digital signatures are INVALIDATED by rewriting. Geometry/rotations should
be inspected on complex PDFs before using as engineering records.
"""
import os
from pathlib import Path
import subprocess
import tempfile

import pypdfium2 as pdfium
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import ContentStream, NameObject

from arabic_ocr import LANGUAGES, OCRSetupError, tesseract_executable, available_languages


def remove_ocr_page_images(page):
    """Retain OCR text instructions, remove all external-object draw calls.

    Tesseract's PDF uses /Do to draw the raster page under invisible text.
    Removing /Do ensures the image is not painted over original vector content.
    """
    original = page.get_contents()
    if original is None:
        raise ValueError("OCR PDF has no content stream")
    stream = ContentStream(original, page.pdf)
    stream.operations = [(args, op) for args,op in stream.operations if op != b"Do"]
    page.replace_contents(stream)
    resources = page.get("/Resources")
    if resources is not None:
        resources = resources.get_object()
        if "/XObject" in resources:
            del resources[NameObject("/XObject")]
    return page


def make_vector_searchable_pdf(source, destination, language="ara+eng",
                               executable=None, scale=2.0):
    if language not in LANGUAGES.values():
        raise ValueError("Unsupported OCR language selection")
    if not 1 <= scale <= 3:
        raise ValueError("OCR scale must be between 1 and 3")
    source=Path(source)
    destination=Path(destination)
    if source.resolve()==destination.resolve():
        raise ValueError("Cannot overwrite original PDF")
    binary=tesseract_executable(executable)
    missing=set(language.split("+"))-available_languages(binary)
    if missing:
        raise OCRSetupError("Tesseract language data missing: "+", ".join(sorted(missing)))
    source_reader=PdfReader(str(source))
    renderer=pdfium.PdfDocument(str(source))
    try:
        if not len(renderer) or len(source_reader.pages)!=len(renderer):
            raise ValueError("Invalid or inconsistent PDF page count")
        writer=PdfWriter()
        writer.append(source_reader)
        with tempfile.TemporaryDirectory(prefix="aer_vector_ocr_") as folder:
            directory=Path(folder)
            for index in range(len(renderer)):
                page=renderer[index]
                try:
                    bitmap=page.render(scale=scale)
                    image=bitmap.to_pil().convert("RGB")
                    if image.width*image.height>25_000_000:
                        raise ValueError("Page too large for OCR; use a lower scale")
                    img=directory/"page.png"
                    image.save(img,format="PNG")
                    base=directory/"recognized"
                    try:
                        subprocess.run([binary,str(img),str(base),"-l",language,"pdf"],
                                       capture_output=True,text=True,check=True,timeout=120,
                                       encoding="utf-8",errors="replace")
                    except (OSError, subprocess.SubprocessError) as exc:
                        raise RuntimeError(f"OCR failed on page {index+1}: {exc}") from exc
                    output=base.with_suffix(".pdf")
                    if not output.exists():
                        raise RuntimeError(f"No Tesseract OCR PDF generated for page {index+1}")
                    extracted=PdfReader(str(output))
                    if len(extracted.pages)!=1:
                        raise ValueError("Tesseract returned an unexpected page count")
                    overlay=remove_ocr_page_images(extracted.pages[0])
                    base_page=writer.pages[index]
                    ocr_w=float(overlay.mediabox.width)
                    ocr_h=float(overlay.mediabox.height)
                    original_w=float(base_page.mediabox.width)
                    original_h=float(base_page.mediabox.height)
                    if min(ocr_w,ocr_h,original_w,original_h)<=0:
                        raise ValueError("Invalid page dimensions")
                    # PDFium renders with rotations already applied; this simple overlay
                    # currently supports only zero-degree source rotation/crop geometry.
                    rotation=int(base_page.get("/Rotate",0))%360
                    if rotation:
                        raise ValueError("Rotated PDF pages need rotation-aware OCR alignment")
                    if (float(base_page.cropbox.left)!=float(base_page.mediabox.left) or
                        float(base_page.cropbox.bottom)!=float(base_page.mediabox.bottom) or
                        float(base_page.cropbox.right)!=float(base_page.mediabox.right) or
                        float(base_page.cropbox.top)!=float(base_page.mediabox.top)):
                        raise ValueError("Pages with nonstandard crop boxes are not supported")
                    transform=Transformation().scale(original_w/ocr_w,original_h/ocr_h).translate(
                        float(base_page.mediabox.left),float(base_page.mediabox.bottom))
                    base_page.merge_transformed_page(overlay,transform,expand=False)
                finally:
                    page.close()
            destination.parent.mkdir(parents=True,exist_ok=True)
            fd,temporary=tempfile.mkstemp(prefix=".aer_vector_",suffix=".pdf",dir=destination.parent)
            try:
                with os.fdopen(fd,"wb") as stream:
                    writer.write(stream)
                os.replace(temporary,destination)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        return {"pages":len(renderer),"output":str(destination),
                "warning":"Original page content retained; PDF signatures invalidated; inspect OCR alignment."}
    finally:
        renderer.close()
