"""Optional offline OCR of PDF pages using an installed Tesseract executable.

No network requests. The PDF is not modified; OCR output is plain UTF-8 text.
Tesseract executable plus Arabic language data must be installed separately.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile

import pypdfium2 as pdfium

LANGUAGES = {"Arabic": "ara", "English": "eng", "Arabic + English": "ara+eng"}

class OCRSetupError(RuntimeError):
    pass

def tesseract_executable(override=None):
    path = override or shutil.which("tesseract")
    if not path or not Path(path).is_file():
        raise OCRSetupError("Tesseract was not found. Install Tesseract and add it to PATH (or configure its executable).")
    return str(path)

def available_languages(executable=None):
    executable = tesseract_executable(executable)
    try:
        response = subprocess.run(
            [executable, "--list-langs"], capture_output=True, text=True,
            timeout=15, check=True, encoding="utf-8", errors="replace",
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise OCRSetupError(f"Unable to check Tesseract languages: {exc}") from exc
    return set(response.stdout.splitlines()[1:])

def ocr_pdf_pages(source, destination, language="ara+eng", pages=None, executable=None, scale=2.0):
    if language not in LANGUAGES.values():
        raise ValueError("Unsupported OCR language selection")
    if not 1 <= scale <= 3:
        raise ValueError("OCR scale must be between 1 and 3")
    binary = tesseract_executable(executable)
    installed = available_languages(binary)
    missing = set(language.split("+")) - installed
    if missing:
        raise OCRSetupError("Tesseract language data missing: " + ", ".join(sorted(missing)) +
                            ". Install ara.traineddata for Arabic and eng.traineddata for English.")
    source = Path(source)
    target = Path(destination)
    if source.resolve() == target.resolve():
        raise ValueError("Output must differ from input")
    document = pdfium.PdfDocument(str(source))
    try:
        selected = list(range(len(document))) if pages is None else list(pages)
        if not selected or any(type(i) is not int or i < 0 or i >= len(document) for i in selected):
            raise ValueError("Invalid PDF page selection")
        sections = []
        with tempfile.TemporaryDirectory(prefix="aer_ocr_") as temporary:
            for index in selected:
                page = document[index]
                try:
                    bitmap = page.render(scale=scale)
                    image = bitmap.to_pil().convert("RGB")
                    if image.width * image.height > 25_000_000:
                        raise ValueError("Page too large for OCR at this resolution; reduce scale")
                    image_path = Path(temporary) / "page.png"
                    image.save(image_path, format="PNG")
                    try:
                        result = subprocess.run(
                            [binary, str(image_path), "stdout", "-l", language],
                            capture_output=True, text=True, timeout=90, check=True,
                            encoding="utf-8", errors="replace",
                        )
                    except (OSError, subprocess.SubprocessError) as exc:
                        raise RuntimeError(f"OCR failed on page {index+1}: {exc}") from exc
                    sections.append(f"----- Page {index+1} -----\n{result.stdout.strip()}\n")
                finally:
                    page.close()
        text = "\n".join(sections)
        target.write_text(text, encoding="utf-8-sig")
        return {"pages": len(selected), "characters": len(text), "output": str(target)}
    finally:
        document.close()
