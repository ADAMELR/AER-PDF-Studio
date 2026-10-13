"""Qt document tab state and scale math without any GUI dependencies."""
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class DocumentState:
    path: str
    page: int = 0
    zoom: float = 1.25
    calibrations: dict = field(default_factory=dict)
    measurements: list = field(default_factory=list)

    @property
    def title(self):
        return Path(self.path).name

    def set_page(self, index, count):
        if count < 1:
            raise ValueError("Document has no pages")
        self.page = max(0, min(int(index), count - 1))
        return self.page

    def set_zoom(self, value):
        self.zoom = max(0.25, min(4.0, float(value)))
        return self.zoom

    def calibration(self):
        return self.calibrations.get(self.page)

def page_size_fit(page_width, page_height, viewport_width, viewport_height, padding=28):
    """Compute document render scale from page coordinates and available pixels."""
    if min(page_width,page_height,viewport_width,viewport_height) <= 0:
        raise ValueError("Page and viewport dimensions must be positive")
    width=max(1,viewport_width-padding)
    height=max(1,viewport_height-padding)
    return min(width/page_width,height/page_height,4.0)
