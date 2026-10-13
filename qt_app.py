"""AER PDF Studio 2.0 Qt workspace (developer preview).

Run: python qt_app.py
PySide6 is optional and installed using requirements-qt.txt.
This is a replacement desktop shell, not a certified Acrobat equivalent.
"""
from pathlib import Path
import sys

import pypdfium2 as pdfium
from PySide6.QtCore import Qt, Signal, QPoint, QTimer, QSettings
from PySide6.QtGui import QAction, QImage, QPixmap, QIcon, QKeySequence, QPainter, QPen, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QScrollArea, QTabWidget, QDockWidget, QListWidget, QListWidgetItem,
    QToolBar, QFileDialog, QMessageBox, QInputDialog, QComboBox, QStatusBar,
    QPushButton, QFrame, QLineEdit, QMenu, QToolButton, QSizePolicy, QStyle
)
from PIL import Image

from qt_model import DocumentState, page_size_fit
from compare_batch import compare_document_pages
from pdf_operations import merge_pdfs, split_pdf, rotate_pdf
from measurements import calibrate, length_metres, rectangle_area_m2, screen_to_pdf
from takeoff import Measurement, export_register_csv
from pdf_text_search import find_text_pages
from arabic_ocr import ocr_pdf_pages, OCRSetupError
from searchable_ocr import make_searchable_pdf
from vector_ocr import make_vector_searchable_pdf
from thumbnails import visible_thumbnail_indices

STYLE = """
QMainWindow, QWidget {background:#f2f4f8;color:#24334b;font-family:'Segoe UI';font-size:10pt}
QMenuBar {background:#17293f;color:white;padding:5px}
QMenuBar::item:selected {background:#32516f}
QMenu {background:white;border:1px solid #d8e0e9}
QToolBar {background:#ffffff;border:0;border-bottom:1px solid #dce3eb;spacing:7px;padding:8px}
QToolButton, QPushButton {background:#fff;border:1px solid #d7e0eb;border-radius:5px;padding:8px 11px}
QToolButton:hover, QPushButton:hover {background:#e7f0fa;border-color:#7fa9d0}
QTabWidget::pane {border:0;background:#dce2e9}
QTabBar::tab {background:#e5eaf1;border:1px solid #cdd7e2;padding:10px 20px;min-width:140px}
QTabBar::tab:selected {background:white;border-bottom:3px solid #1769aa}
QDockWidget {background:#f8fafc;font-weight:600}
QDockWidget::title {padding:11px;background:#ebf0f6}
QListWidget {background:#f8fafc;border:0;padding:8px;outline:none}
QListWidget::item {padding:7px;border-radius:4px}
QListWidget::item:selected {background:#d8e9f9;color:#133b60}
QScrollArea {background:#bfc8d3;border:0}
QStatusBar {background:#182a40;color:white}
QStatusBar QLabel {background:#182a40;color:white}
QLineEdit,QComboBox {background:#fff;border:1px solid #cbd5e1;padding:7px;border-radius:4px}
"""

def pixmap_from_pil(image):
    data=image.convert("RGBA")
    raw=data.tobytes("raw","RGBA")
    qt=QImage(raw,data.width,data.height,data.width*4,QImage.Format.Format_RGBA8888)
    return QPixmap.fromImage(qt.copy())

class DrawingCanvas(QLabel):
    dragged=Signal(tuple,tuple)
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self._start=None
        self._end=None
        self._picture=None

    def set_image(self,pixmap):
        self._picture=pixmap
        self._start=None
        self._end=None
        self.setFixedSize(pixmap.size())
        self.setPixmap(pixmap)

    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton:
            self._start=(event.position().x(),event.position().y())
            self._end=None

    def mouseMoveEvent(self,event):
        if self._start and event.buttons() & Qt.MouseButton.LeftButton:
            self._end=(event.position().x(),event.position().y())
            self.update()

    def mouseReleaseEvent(self,event):
        if self._start and event.button()==Qt.MouseButton.LeftButton:
            end=(event.position().x(),event.position().y())
            start=self._start
            self._start=None
            self._end=None
            self.update()
            self.dragged.emit(start,end)

    def paintEvent(self,event):
        super().paintEvent(event)
        if self._start and self._end:
            painter=QPainter(self)
            painter.setPen(QPen(QColor("#d83b3b"),2))
            from PySide6.QtCore import QRectF
            painter.drawRect(QRectF(QPoint(int(self._start[0]),int(self._start[1])),
                                    QPoint(int(self._end[0]),int(self._end[1]))).normalized())
            painter.end()

class DocumentView(QWidget):
    page_changed=Signal(int)
    info_changed=Signal(str)

    def __init__(self,path):
        super().__init__()
        self.state=DocumentState(str(path))
        self.document=pdfium.PdfDocument(str(path))
        self.canvas=DrawingCanvas()
        self.canvas.dragged.connect(self.on_drag)
        self.measure_mode="pan"
        self._render_scale=1.25
        self._page_height=1
        self.polygon=[]
        self.scroll=QScrollArea()
        self.scroll.setWidget(self.canvas)
        self.scroll.setWidgetResizable(False)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)
        layout=QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.scroll)
        self.render()

    def close(self):
        self.document.close()

    def render(self):
        page=self.document[self.state.page]
        try:
            self._page_height=page.get_size()[1]
            self._render_scale=self.state.zoom
            image=page.render(scale=self._render_scale).to_pil().convert("RGB")
            self.canvas.set_image(pixmap_from_pil(image))
        finally:
            page.close()
        self.page_changed.emit(self.state.page)
        self.info_changed.emit(
            f"Page {self.state.page+1} / {len(self.document)}   ·   {self.state.zoom:.0%}")

    def change_page(self,index):
        self.state.set_page(index,len(self.document))
        self.render()

    def zoom(self,factor):
        self.state.set_zoom(self.state.zoom*factor)
        self.render()

    def fit(self,by_width=False):
        page=self.document[self.state.page]
        try:
            width,height=page.get_size()
        finally:
            page.close()
        size=self.scroll.viewport().size()
        value=(size.width()-24)/width if by_width else page_size_fit(width,height,size.width(),size.height())
        self.state.set_zoom(value)
        self.render()

    def on_drag(self,start,end):
        if self.measure_mode=="pan":
            return
        a=screen_to_pdf(start,self._render_scale,self._page_height)
        b=screen_to_pdf(end,self._render_scale,self._page_height)
        try:
            if self.measure_mode=="calibrate":
                value,ok=QInputDialog.getDouble(self,"Drawing calibration",
                    "Known distance in metres:",1.0,0.000001,1000000.0,4)
                if not ok:
                    return
                self.state.calibrations[self.state.page]=calibrate(a,b,value)
                self.info_changed.emit("Page calibrated — measured lengths remain approximate")
                return
            reference=self.state.calibration()
            if reference is None:
                QMessageBox.warning(self,"Calibration required",
                                    "Calibrate the current drawing page first.")
                return
            if self.measure_mode=="distance":
                value=length_metres(a,b,reference)
                kind,unit="Distance","m"
            elif self.measure_mode=="area":
                rect=(min(a[0],b[0]),min(a[1],b[1]),max(a[0],b[0]),max(a[1],b[1]))
                value=rectangle_area_m2(rect,reference)
                kind,unit="Rectangle area","m²"
            else:
                return
            self.state.measurements.append(Measurement(self.state.page+1,kind,value,unit))
            self.info_changed.emit(f"Approximate {kind}: {value:.3f} {unit}")
        except (ValueError,TypeError) as exc:
            QMessageBox.warning(self,"Measurement error",str(exc))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AER PDF Studio 2.0 — Qt Developer Preview")
        self.resize(1480,920)
        self.setMinimumSize(960,650)
        self.views={}
        self.locale="en"
        self.settings=QSettings("AER Engineering", "AER PDF Studio Qt")
        self.tabs=QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.currentChanged.connect(self.on_current_tab)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        self._build_menus()
        self._build_toolbar()
        self._build_docks()
        self._set_icons()
        self._welcome()
        self.status=QLabel("Ready — local PDF workspace")
        self.statusBar().addPermanentWidget(self.status)
        self.statusBar().showMessage("AER PDF Studio 2.0 preview • Source files remain unchanged")
        self._thumb_timer=QTimer(self)
        self._thumb_timer.setSingleShot(True)
        self._thumb_timer.timeout.connect(self.refresh_thumbnails)
        self._retranslate()
        geometry=self.settings.value("window_geometry")
        docks=self.settings.value("window_state")
        if geometry is not None:
            self.restoreGeometry(geometry)
        if docks is not None:
            self.restoreState(docks)

    def _set_icons(self):
        style=self.style()
        standard=QStyle.StandardPixmap
        icons=(
            (self.open_action,standard.SP_DialogOpenButton),
            (self.merge_action,standard.SP_DriveFDIcon),
            (self.split_action,standard.SP_FileIcon),
            (self.rotate_action,standard.SP_BrowserReload),
            (self.search_action,standard.SP_FileDialogContentsView),
            (self.compare_action,standard.SP_FileDialogDetailedView),
        )
        for action,icon in icons:
            action.setIcon(style.standardIcon(icon))
        self.ribbon.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

    def _action(self,label,slot,shortcut=None):
        act=QAction(label,self)
        act.triggered.connect(slot)
        if shortcut:
            act.setShortcut(QKeySequence(shortcut))
        self.addAction(act)
        return act

    def _build_menus(self):
        self.file_menu=self.menuBar().addMenu("File")
        self.open_action=self._action("Open PDF…",self.open_files,"Ctrl+O")
        self.file_menu.addAction(self.open_action)
        self.file_menu.addSeparator()
        self.merge_action=self._action("Merge PDFs…",self.merge)
        self.split_action=self._action("Split current PDF…",self.split)
        self.rotate_action=self._action("Rotate current PDF…",self.rotate)
        for action in (self.merge_action,self.split_action,self.rotate_action):
            self.file_menu.addAction(action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self._action("Exit",self.close,"Ctrl+Q"))
        self.view_menu=self.menuBar().addMenu("View")
        self.search_action=self._action("Find text…",self.search,"Ctrl+F")
        self.view_menu.addAction(self.search_action)
        self.view_menu.addAction(self._action("Fit page",lambda:self.fit(False),"Ctrl+0"))
        self.view_menu.addAction(self._action("Fit width",lambda:self.fit(True),"Ctrl+1"))
        self.tools_menu=self.menuBar().addMenu("Tools")
        self.compare_action=self._action("Compare drawings…",self.compare)
        self.tools_menu.addAction(self.compare_action)
        self.ocr_menu=self.menuBar().addMenu("OCR")
        self.ocr_menu.addAction(self._action("OCR to text…",lambda:self.ocr("text")))
        self.ocr_menu.addAction(self._action("Searchable scanned PDF…",lambda:self.ocr("raster")))
        self.ocr_menu.addAction(self._action("Preserve vector + OCR…",lambda:self.ocr("vector")))
        language=self.menuBar().addMenu("Language / اللغة")
        language.addAction(self._action("English",lambda:self.set_language("en")))
        language.addAction(self._action("العربية",lambda:self.set_language("ar")))

    def _build_toolbar(self):
        self.ribbon=QToolBar("Document commands",self)
        self.ribbon.setMovable(False)
        self.addToolBar(self.ribbon)
        for action in (self.open_action,self.merge_action,self.split_action,
                       self.rotate_action,self.compare_action,self.search_action):
            self.ribbon.addAction(action)
        self.ribbon.addSeparator()
        self.ribbon.addAction(self._action("◀",lambda:self.step(-1)))
        self.ribbon.addAction(self._action("▶",lambda:self.step(1)))
        self.ribbon.addAction(self._action("−",lambda:self.zoom(0.8)))
        self.ribbon.addAction(self._action("+",lambda:self.zoom(1.25)))
        self.ribbon.addAction(self._action("Fit page",lambda:self.fit(False)))
        self.ribbon.addSeparator()
        self.mode_box=QComboBox()
        self.mode_box.addItems(["pan","calibrate","distance","area"])
        self.mode_box.currentTextChanged.connect(self.change_mode)
        self.ribbon.addWidget(self.mode_box)

    def _build_docks(self):
        self.pages_dock=QDockWidget("Pages / الصفحات",self)
        self.pages_dock.setObjectName("PagesDock")
        self.pages=QListWidget()
        self.pages.setIconSize(__import__("PySide6.QtCore",fromlist=["QSize"]).QSize(90,120))
        self.pages.currentRowChanged.connect(self.select_page)
        self.pages_dock.setWidget(self.pages)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,self.pages_dock)
        self.pages_dock.setMinimumWidth(150)
        self.properties_dock=QDockWidget("Tools / الأدوات",self)
        self.properties_dock.setObjectName("PropertiesDock")
        box=QWidget()
        column=QVBoxLayout(box)
        for label,action in (
            ("Open PDF",self.open_files),
            ("Find text",self.search),
            ("Calibrate page",lambda:self.mode_box.setCurrentText("calibrate")),
            ("Measure distance",lambda:self.mode_box.setCurrentText("distance")),
            ("Measure area",lambda:self.mode_box.setCurrentText("area")),
            ("Export measurements CSV",self.export_measurements),
            ("Save measurements project",self.save_measurements),
        ):
            button=QPushButton(label)
            button.clicked.connect(action)
            column.addWidget(button)
        column.addStretch(1)
        self.properties_dock.setWidget(box)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,self.properties_dock)
        self.properties_dock.setMinimumWidth(205)
        self.view_menu.addAction(self.pages_dock.toggleViewAction())
        self.view_menu.addAction(self.properties_dock.toggleViewAction())

    def _welcome(self):
        page=QWidget()
        layout=QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title=QLabel("AER PDF Studio")
        title.setStyleSheet("font-size:28pt;font-weight:650;color:#173956")
        subtitle=QLabel("Engineering PDF workspace  ·  Arabic / English")
        subtitle.setStyleSheet("font-size:13pt;color:#64748b")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        button=QPushButton("Open a PDF")
        button.clicked.connect(self.open_files)
        layout.addWidget(button,alignment=Qt.AlignmentFlag.AlignCenter)
        self.tabs.addTab(page,"Home")

    def current(self):
        widget=self.tabs.currentWidget()
        return widget if isinstance(widget,DocumentView) else None

    def open_files(self):
        paths,_=QFileDialog.getOpenFileNames(self,"Open PDF documents","","PDF files (*.pdf)")
        for path in paths:
            self.open_path(path)

    def open_path(self,path):
        canonical=str(Path(path).resolve())
        if canonical in self.views:
            self.tabs.setCurrentWidget(self.views[canonical])
            return
        try:
            view=DocumentView(canonical)
            view.page_changed.connect(lambda _page,v=view:self.schedule_thumbnails(v))
            view.info_changed.connect(lambda text,v=view:self.set_view_status(v,text))
            self.views[canonical]=view
            index=self.tabs.addTab(view,Path(canonical).name)
            self.tabs.setTabToolTip(index,canonical)
            self.tabs.setCurrentIndex(index)
        except Exception as exc:
            QMessageBox.critical(self,"Cannot open PDF",str(exc))

    def close_tab(self,index):
        widget=self.tabs.widget(index)
        if isinstance(widget,DocumentView):
            self.views.pop(widget.state.path,None)
            widget.close()
        self.tabs.removeTab(index)
        if not self.tabs.count():
            self._welcome()

    def on_current_tab(self,_index):
        self.schedule_thumbnails(self.current())
        self._retranslate()

    def schedule_thumbnails(self,view):
        if view is self.current():
            self._thumb_timer.start(50) if hasattr(self,"_thumb_timer") else None

    def refresh_thumbnails(self):
        view=self.current()
        self.pages.blockSignals(True)
        self.pages.clear()
        if view:
            for index in range(len(view.document)):
                item=QListWidgetItem(f"  {index+1}")
                item.setData(Qt.ItemDataRole.UserRole,index)
                self.pages.addItem(item)
            self.pages.setCurrentRow(view.state.page)
        self.pages.blockSignals(False)
        # Render only a few nearby thumbnails, never all pages at once.
        if not view:
            return
        for index in visible_thumbnail_indices(view.state.page,len(view.document),2):
            page=view.document[index]
            try:
                width,height=page.get_size()
                scale=min(90/width,115/height)
                image=page.render(scale=scale).to_pil().convert("RGB")
                image.thumbnail((90,115),Image.Resampling.LANCZOS)
                pixmap=pixmap_from_pil(image)
                self.pages.item(index).setIcon(QIcon(pixmap))
            finally:
                page.close()

    def select_page(self,row):
        view=self.current()
        if view and row>=0 and row!=view.state.page:
            view.change_page(row)

    def step(self,offset):
        view=self.current()
        if view:
            view.change_page(view.state.page+offset)

    def zoom(self,factor):
        view=self.current()
        if view:
            view.zoom(factor)

    def fit(self,width=False):
        view=self.current()
        if view:
            view.fit(width)

    def change_mode(self,mode):
        view=self.current()
        if view:
            view.measure_mode=mode
            self.statusBar().showMessage(f"Tool: {mode}")

    def set_view_status(self,view,text):
        if view is self.current():
            self.status.setText(text)

    def set_language(self,language):
        self.locale=language
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if language=="ar" else Qt.LayoutDirection.LeftToRight)
        self._retranslate()

    def _retranslate(self):
        arabic=self.locale=="ar"
        self.file_menu.setTitle("ملف" if arabic else "File")
        self.view_menu.setTitle("عرض" if arabic else "View")
        self.tools_menu.setTitle("أدوات" if arabic else "Tools")
        self.ocr_menu.setTitle("استخراج النص" if arabic else "OCR")
        self.open_action.setText("فتح PDF" if arabic else "Open PDF")
        self.merge_action.setText("دمج" if arabic else "Merge PDFs")
        self.split_action.setText("تقسيم" if arabic else "Split PDF")
        self.rotate_action.setText("تدوير" if arabic else "Rotate PDF")
        self.compare_action.setText("مقارنة الرسومات" if arabic else "Compare drawings")
        self.search_action.setText("بحث" if arabic else "Find text")

    def need_document(self):
        view=self.current()
        if not view:
            QMessageBox.information(self,"Open a PDF","Open or select a PDF first.")
        return view

    def search(self):
        view=self.need_document()
        if not view:
            return
        query,ok=QInputDialog.getText(self,"Find text","Search Arabic or English:")
        if not ok or not query.strip():
            return
        try:
            pages=find_text_pages(view.state.path,query.strip())
            if pages:
                view.change_page(pages[0])
                self.statusBar().showMessage(f"Found on page {pages[0]+1}")
            else:
                QMessageBox.information(self,"Search","No matching selectable PDF text found.")
        except Exception as exc:
            QMessageBox.warning(self,"Search error",str(exc))

    def merge(self):
        paths,_=QFileDialog.getOpenFileNames(self,"Select PDFs to merge","","PDF files (*.pdf)")
        if not paths:
            return
        dest,_=QFileDialog.getSaveFileName(self,"Save merged PDF","","PDF files (*.pdf)")
        if dest:
            try:
                merge_pdfs(paths,dest)
                self.open_path(dest)
            except Exception as exc:
                QMessageBox.critical(self,"Merge error",str(exc))

    def split(self):
        view=self.need_document()
        if not view:
            return
        folder=QFileDialog.getExistingDirectory(self,"Save split pages")
        if folder:
            try:
                outputs=split_pdf(view.state.path,folder)
                QMessageBox.information(self,"Split",f"Created {len(outputs)} page PDFs.")
            except Exception as exc:
                QMessageBox.critical(self,"Split error",str(exc))

    def rotate(self):
        view=self.need_document()
        if not view:
            return
        dest,_=QFileDialog.getSaveFileName(self,"Save rotated PDF","","PDF files (*.pdf)")
        if dest:
            try:
                rotate_pdf(view.state.path,dest)
                self.open_path(dest)
            except Exception as exc:
                QMessageBox.critical(self,"Rotate error",str(exc))

    def compare(self):
        original,_=QFileDialog.getOpenFileName(self,"Original drawing PDF","","PDF files (*.pdf)")
        if not original:
            return
        revised,_=QFileDialog.getOpenFileName(self,"Revised drawing PDF","","PDF files (*.pdf)")
        if not revised:
            return
        folder=QFileDialog.getExistingDirectory(self,"Choose comparison output directory")
        if not folder:
            return
        try:
            outputs=compare_document_pages(original,revised,folder,side_by_side=True)
            QMessageBox.information(self,"Comparison complete",
                f"Saved {len(outputs)} comparison images, an alignment report and a revision CSV. "
                "Inspect all results manually. Manual three-point registration remains in the classic app.")
        except Exception as exc:
            QMessageBox.critical(self,"Comparison error",str(exc))

    def export_measurements(self):
        view=self.need_document()
        if not view or not view.state.measurements:
            return
        path,_=QFileDialog.getSaveFileName(self,"Export measurements","","CSV (*.csv)")
        if path:
            try:
                export_register_csv(view.state.measurements,path)
            except Exception as exc:
                QMessageBox.warning(self,"Export error",str(exc))

    def save_measurements(self):
        from project_store import save_project
        view=self.need_document()
        if not view:
            return
        path,_=QFileDialog.getSaveFileName(self,"Save project","","AER JSON (*.aer.json)")
        if path:
            save_project(path,view.state.path,view.state.measurements,view.state.calibrations)

    def ocr(self,kind):
        view=self.need_document()
        if not view:
            return
        languages=["Arabic + English","Arabic","English"]
        selected,ok=QInputDialog.getItem(self,"Offline OCR","Language:",languages,0,False)
        if not ok:
            return
        language={"Arabic + English":"ara+eng","Arabic":"ara","English":"eng"}[selected]
        extension="Text (*.txt)" if kind=="text" else "PDF (*.pdf)"
        target,_=QFileDialog.getSaveFileName(self,"Save OCR output","",extension)
        if not target:
            return
        if kind=="vector" and QMessageBox.question(self,"Vector OCR preview",
            "Vector-preserving OCR is experimental and invalidates PDF signatures. "
            "Rotated or nonstandard-cropped pages are unsupported. Continue?"
            )!=QMessageBox.StandardButton.Yes:
            return
        if kind=="raster" and QMessageBox.question(self,"Rasterized searchable PDF",
            "This export rasterizes every page and does not preserve editable vector "
            "linework or annotations. Continue?"
            )!=QMessageBox.StandardButton.Yes:
            return
        tasks={"text":ocr_pdf_pages,"raster":make_searchable_pdf,
               "vector":make_vector_searchable_pdf}
        try:
            result=tasks[kind](view.state.path,target,language=language)
            QMessageBox.information(self,"OCR complete",
                f"Saved {result['pages']} page(s) to:\\n{result['output']}")
        except OCRSetupError as exc:
            QMessageBox.warning(self,"Tesseract required",
                str(exc)+"\\nInstall Tesseract and its Arabic/English language data.")
        except Exception as exc:
            QMessageBox.critical(self,"OCR error",str(exc))

    def closeEvent(self,event):
        self.settings.setValue("window_geometry",self.saveGeometry())
        self.settings.setValue("window_state",self.saveState())
        for view in list(self.views.values()):
            view.close()
        event.accept()

def main():
    app=QApplication(sys.argv)
    app.setApplicationName("AER PDF Studio")
    app.setStyleSheet(STYLE)
    window=MainWindow()
    window.show()
    return app.exec()

if __name__=="__main__":
    raise SystemExit(main())
