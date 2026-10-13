"""Bounded thumbnail preparation and navigation helpers for the PDF viewer."""
from PIL import Image

THUMB_WIDTH = 132
THUMB_HEIGHT = 170

def thumbnail_size(width, height, max_width=THUMB_WIDTH, max_height=THUMB_HEIGHT):
    if width <= 0 or height <= 0 or max_width <= 0 or max_height <= 0:
        raise ValueError("Page and thumbnail dimensions must be positive")
    ratio=min(max_width / width, max_height / height, 1.0)
    return max(1,round(width*ratio)), max(1,round(height*ratio))

def make_thumbnail(page, max_width=THUMB_WIDTH, max_height=THUMB_HEIGHT):
    """Render at low resolution, constraining both dimensions."""
    width,height=page.get_size()
    size=thumbnail_size(width,height,max_width,max_height)
    scale=min(size[0]/width,size[1]/height)
    if scale<=0:
        raise ValueError("Invalid page dimensions")
    image=page.render(scale=scale).to_pil().convert("RGB")
    image.thumbnail((max_width,max_height),Image.Resampling.LANCZOS)
    return image

def visible_thumbnail_indices(current,total,radius=2):
    if total<0 or radius<0:
        raise ValueError("Invalid page count or radius")
    if total == 0:
        return []
    if not 0<=current<total:
        raise ValueError("Page index out of range")
    return list(range(max(0,current-radius), min(total,current+radius+1)))
