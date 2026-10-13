"""Conservative translation-only alignment for same-size rasterised PDF pages.

Coordinates are shifts applied to the revised image to align it to original.
Uses downsampled edge maps and minimum mean absolute difference.
No automatic rotation, scale, skew or page matching.
"""
from PIL import Image, ImageChops, ImageFilter, ImageStat

def estimate_translation(original, revised, max_shift=12, sample_width=180):
    if original.size != revised.size:
        raise ValueError("Images must have matching dimensions")
    if max_shift < 0 or max_shift > 30:
        raise ValueError("Invalid maximum shift")
    width,height = original.size
    ratio = min(1.0, sample_width / max(width,height))
    shape = (max(1, round(width*ratio)), max(1,round(height*ratio)))
    a=original.convert("L").resize(shape,Image.Resampling.BILINEAR).filter(ImageFilter.FIND_EDGES)
    b=revised.convert("L").resize(shape,Image.Resampling.BILINEAR).filter(ImageFilter.FIND_EDGES)
    # An almost blank drawing does not contain enough registration evidence.
    if max(ImageStat.Stat(a).stddev[0], ImageStat.Stat(b).stddev[0]) < 2:
        return 0,0,False
    search = min(max_shift,shape[0]//5,shape[1]//5)
    best=(float("inf"),0,0)
    for dy in range(-search,search+1):
        for dx in range(-search,search+1):
            left=max(0,dx); top=max(0,dy)
            right=min(shape[0],shape[0]+dx)
            bottom=min(shape[1],shape[1]+dy)
            if right-left < 5 or bottom-top < 5:
                continue
            first=a.crop((left,top,right,bottom))
            second=b.crop((left-dx,top-dy,right-dx,bottom-dy))
            score=ImageStat.Stat(ImageChops.difference(first,second)).mean[0]
            if score < best[0]:
                best=(score,dx,dy)
    dx=round(best[1]/ratio)
    dy=round(best[2]/ratio)
    return dx,dy,True

def translate_to_match(image, dx, dy):
    result=Image.new("RGB",image.size,"white")
    result.paste(image,(dx,dy))
    return result
