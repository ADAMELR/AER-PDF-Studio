"""Headless PDF operations shared by the GUI and automated tests."""
from pathlib import Path
from pypdf import PdfReader, PdfWriter

def merge_pdfs(inputs, output):
    if not inputs:
        raise ValueError("At least one input PDF is required")
    writer = PdfWriter()
    for source in inputs:
        writer.append(str(source))
    with Path(output).open("wb") as stream:
        writer.write(stream)
    return len(writer.pages)

def split_pdf(source, folder):
    source, folder = Path(source), Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(str(source))
    outputs = []
    for index, page in enumerate(reader.pages, 1):
        writer = PdfWriter()
        writer.add_page(page)
        target = folder / f"{source.stem}_page_{index:03}.pdf"
        with target.open("wb") as stream:
            writer.write(stream)
        outputs.append(target)
    return outputs

def rotate_pdf(source, output, degrees=90):
    if degrees % 90:
        raise ValueError("Rotation must be a multiple of 90 degrees")
    reader = PdfReader(str(source))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page.rotate(degrees))
    with Path(output).open("wb") as stream:
        writer.write(stream)
    return len(writer.pages)
