"""Non-destructive rectangular drawing markups.

Markup coordinates use PDF points with an origin at the bottom-left.
All edits are written to a new PDF; source documents are unchanged.
"""
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def add_rectangle_markup(source, output, page_index, rect, colour=(1, 0, 0), width=2):
    """Draw a visible rectangular markup. Not a native, editable PDF annotation."""
    from reportlab.pdfgen.canvas import Canvas

    if len(rect) != 4:
        raise ValueError("Rectangle must contain four coordinates")
    x0, y0, x1, y1 = map(float, rect)
    if x1 <= x0 or y1 <= y0:
        raise ValueError("Rectangle must have positive dimensions")
    if width <= 0:
        raise ValueError("Stroke width must be positive")

    reader = PdfReader(str(source))
    if not (0 <= page_index < len(reader.pages)):
        raise IndexError("Page index is outside the document")
    page = reader.pages[page_index]
    bounds = page.mediabox
    llx, lly = float(bounds.left), float(bounds.bottom)
    page_width, page_height = float(bounds.width), float(bounds.height)
    # This preview implementation supports standard, non-rotated PDF pages.
    if int(page.get("/Rotate", 0)) % 360:
        raise ValueError("Save rotated PDFs as unrotated pages before marking up")
    if x0 < llx or y0 < lly or x1 > llx + page_width or y1 > lly + page_height:
        raise ValueError("Markup must fit inside the page")

    overlay_buffer = BytesIO()
    overlay = Canvas(overlay_buffer, pagesize=(page_width, page_height))
    overlay.setStrokeColorRGB(*colour)
    overlay.setLineWidth(width)
    overlay.rect(x0 - llx, y0 - lly, x1 - x0, y1 - y0, stroke=1, fill=0)
    overlay.save()
    overlay_buffer.seek(0)
    overlay_page = PdfReader(overlay_buffer).pages[0]

    writer = PdfWriter()
    for i, original in enumerate(reader.pages):
        writer.add_page(original)
        if i == page_index:
            writer.pages[-1].merge_page(overlay_page)
    destination = Path(output)
    if Path(source).resolve() == destination.resolve():
        raise ValueError("Select a different output filename to preserve the original")
    with destination.open("wb") as stream:
        writer.write(stream)
    return destination
