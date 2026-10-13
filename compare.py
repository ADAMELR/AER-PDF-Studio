"""Visual drawing comparison with optional translation-only alignment."""
from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image, ImageChops
from control_points import align_control_points
from alignment import estimate_translation, translate_to_match

def compare_pages(original, revised, destination, page_index=0, scale=1.5, auto_align=True, return_alignment=False, control_points=None, side_by_side=False):
    if scale <= 0 or scale > 4:
        raise ValueError("Scale must be between 0 and 4")
    a = pdfium.PdfDocument(str(original))
    b = pdfium.PdfDocument(str(revised))
    try:
        if page_index < 0 or page_index >= len(a) or page_index >= len(b):
            raise IndexError("Page missing in one or both documents")
        size_a, size_b = a[page_index].get_size(), b[page_index].get_size()
        if any(abs(x-y) > .01 for x,y in zip(size_a,size_b)):
            raise ValueError("Page sizes differ; comparison requires same physical dimensions")
        image_a = a[page_index].render(scale=scale).to_pil().convert("RGB")
        image_b = b[page_index].render(scale=scale).to_pil().convert("RGB")
        if image_a.size != image_b.size:
            raise ValueError("Raster dimensions differ")
        dx,dy,valid=(0,0,False)
        manual_info=None
        if control_points is not None:
            manual_ref,manual_moving=control_points
            image_b,manual_info=align_control_points(image_a,image_b,manual_ref,manual_moving)
        elif auto_align:
            dx,dy,valid=estimate_translation(image_a,image_b)
            if valid:
                image_b=translate_to_match(image_b,dx,dy)
        delta = ImageChops.difference(image_a,image_b).convert("L")
        mask = delta.point(lambda p: 255 if p > 24 else 0)
        overlay = image_b.copy()
        overlay.paste((255,0,0), (0,0,*image_b.size), mask)
        result = ImageChops.blend(image_b,overlay,0.55)
        if side_by_side:
            combined=Image.new("RGB",(image_a.width*2,image_a.height),"white")
            combined.paste(image_a,(0,0))
            combined.paste(result,(image_a.width,0))
            result=combined
        target = Path(destination)
        result.save(target, format="PNG")
        if return_alignment:
            return target,{"shift_x_px":dx,"shift_y_px":dy,"estimated":valid,"manual_registration":manual_info,
                "warning":"Translation-only estimate; visually verify alignment before using highlighted changes."}
        return target
    finally:
        a.close()
        b.close()
