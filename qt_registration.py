"""Manual drawing registration dialog using three independent point pairs.

The first two corresponding pairs define a similarity transform; the third
is held out for an independent check. Dialog uses the same raster scale as
the multipage comparison engine (default 1.5).
"""
from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget, QLabel,
    QPushButton, QMessageBox
)

def _pixmap(image):
    rgba=image.convert("RGBA")
    data=rgba.tobytes("raw","RGBA")
    qt=QImage(data,rgba.width,rgba.height,rgba.width*4,QImage.Format.Format_RGBA8888)
    return QPixmap.fromImage(qt.copy())

def render_registration_page(source,page_index,scale):
    doc=pdfium.PdfDocument(str(source))
    try:
        if page_index < 0 or page_index >= len(doc):
            raise ValueError("Invalid comparison page")
        page=doc[page_index]
        try:
            image=page.render(scale=scale).to_pil().convert("RGB")
            if image.width*image.height>30_000_000:
                raise ValueError("Drawing raster is too large for point registration")
            return _pixmap(image)
        finally:
            page.close()
    finally:
        doc.close()

class PointCanvas(QLabel):
    changed=Signal()
    def __init__(self,pixmap):
        super().__init__()
        self.picture=pixmap
        self.points=[]
        self.setFixedSize(pixmap.size())
        self.setCursor(Qt.CursorShape.CrossCursor)
    def mousePressEvent(self,event):
        if event.button()!=Qt.MouseButton.LeftButton or len(self.points)>=3:
            return
        x,y=event.position().x(),event.position().y()
        if 0<=x<self.width() and 0<=y<self.height():
            self.points.append((x,y))
            self.changed.emit()
            self.update()
    def paintEvent(self,event):
        painter=QPainter(self)
        painter.drawPixmap(0,0,self.picture)
        painter.setPen(QPen(QColor("#D82626"),3))
        for n,(x,y) in enumerate(self.points,1):
            painter.drawEllipse(int(x)-5,int(y)-5,10,10)
            painter.drawText(int(x)+12,int(y)-10,str(n))
        painter.end()
    def reset(self):
        self.points.clear()
        self.changed.emit()
        self.update()

class RegistrationDialog(QDialog):
    """Returns paired point arrays matching compare_pages(control_points=...)."""
    def __init__(self,parent,original,revised,page_index,scale=1.5):
        super().__init__(parent)
        self.setWindowTitle(f"Register drawing revision — page {page_index+1}")
        self.resize(1300,800)
        self.setModal(True)
        self.result_points=None
        layout=QVBoxLayout(self)
        label=QLabel(
            "Pick THREE distinct reference points in the original drawing and "
            "the corresponding points in the revised drawing, in the SAME order. "
            "Points 1–2 align the sheets; point 3 checks alignment independently."
        )
        label.setWordWrap(True)
        layout.addWidget(label)
        row=QHBoxLayout()
        self.canvases=[]
        for name,path in (("ORIGINAL",original),("REVISED",revised)):
            part=QVBoxLayout()
            part.addWidget(QLabel(name))
            canvas=PointCanvas(render_registration_page(path,page_index,scale))
            canvas.changed.connect(self._update_status)
            self.canvases.append(canvas)
            scroll=QScrollArea()
            scroll.setWidget(canvas)
            scroll.setWidgetResizable(False)
            part.addWidget(scroll)
            row.addLayout(part)
        layout.addLayout(row,1)
        controls=QHBoxLayout()
        self.status=QLabel()
        controls.addWidget(self.status,1)
        reset=QPushButton("Reset points")
        reset.clicked.connect(self._reset)
        controls.addWidget(reset)
        cancel=QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        controls.addWidget(cancel)
        confirm=QPushButton("Use these points")
        confirm.clicked.connect(self._accept)
        controls.addWidget(confirm)
        layout.addLayout(controls)
        self._update_status()

    def _update_status(self):
        self.status.setText(
            f"Original: {len(self.canvases[0].points)}/3    "
            f"Revised: {len(self.canvases[1].points)}/3"
        )

    def _reset(self):
        for canvas in self.canvases:
            canvas.reset()

    def _accept(self):
        if any(len(canvas.points)!=3 for canvas in self.canvases):
            QMessageBox.warning(self,"Incomplete","Choose three points on EACH drawing.")
            return
        # Reject duplicate locations because 2-point similarity registration
        # cannot be computed from identical control coordinates.
        for canvas in self.canvases:
            if len(set(canvas.points)) != 3:
                QMessageBox.warning(self,"Invalid points","Use distinct points on each drawing.")
                return
        self.result_points=(list(self.canvases[0].points),list(self.canvases[1].points))
        self.accept()
