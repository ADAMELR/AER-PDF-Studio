"""Visual pixel-difference comparison for equal-sized, aligned PDF pages."""
from pathlib import Path
import pypdfium2 as pdfium
from PIL import ImageChops, ImageEnhance

def compare_pages(original, revised, destination, page_index=0, scale=1.5):
    if scale <= 0 or scale > 4:
        raise ValueError("Scale must be between 0 and 4")
    a = pdfium.PdfDocument(str(original))
    b = pdfium.PdfDocument(str(revised))
    try:
        if page_index < 0 or page_index >= len(a) or page_index >= len(b):
            raise IndexError("Page missing in one or both documents")
        size_a, size_b = a[page_index].get_size(), b[page_index].get_size()
        if any(abs(x-y) > .01 for x,y in zip(size_a,size_b)):
            raise ValueError("Page sizes differ; comparison requires aligned pages of the same dimensions")
        image_a = a[page_index].render(scale=scale).to_pil().convert("RGB")
        image_b = b[page_index].render(scale=scale).to_pil().convert("RGB")
        if image_a.size != image_b.size:
            raise ValueError("Raster dimensions differ")
        delta = ImageChops.difference(image_a,image_b).convert("L")
        mask = delta.point(lambda p: 255 if p > 24 else 0)
        result = image_b.copy()
        overlay = result.copy()
        overlay.paste((255,0,0), (0,0,*result.size), mask)
        result = ImageChops.blend(result,overlay,0.55)
        target = Path(destination)
        result.save(target, format="PNG")
        return target
    finally:
        a.close()
        b.close()
