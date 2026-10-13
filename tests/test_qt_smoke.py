"""Optional Qt smoke tests; skipped when Qt is not installed in classic CI."""
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from qt_app import MainWindow, DocumentView
    HAS_QT = True
except ImportError:
    HAS_QT = False

from pypdf import PdfWriter

@unittest.skipUnless(HAS_QT, "PySide6 optional for classic build")
class QtSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application=QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source=Path(self.temp.name)/"اختبار الرسم.pdf"
        writer=PdfWriter()
        writer.add_blank_page(width=300,height=400)
        writer.add_blank_page(width=300,height=400)
        with self.source.open("wb") as output:
            writer.write(output)
        self.window=MainWindow()
        self.addCleanup(self.window.close)

    def test_tabs_and_document_navigation(self):
        self.window.open_path(str(self.source))
        view=self.window.current()
        self.assertIsInstance(view,DocumentView)
        self.assertEqual(len(view.document),2)
        self.window.step(1)
        self.assertEqual(view.state.page,1)
        self.window.step(1)
        self.assertEqual(view.state.page,1)
        self.window.zoom(1.25)
        self.assertGreater(view.state.zoom,1)
        self.window.open_path(str(self.source))
        self.assertEqual(len(self.window.views),1)
        self.assertEqual(self.window.tabs.count(),2)

    def test_arabic_layout_and_docks(self):
        self.window.set_language("ar")
        self.assertEqual(self.window.layoutDirection(),Qt.LayoutDirection.RightToLeft)
        self.assertIsNotNone(self.window.pages_dock)
        self.assertIsNotNone(self.window.properties_dock)

    def test_close_document(self):
        self.window.open_path(str(self.source))
        self.window.close_tab(self.window.tabs.currentIndex())
        self.assertEqual(len(self.window.views),0)

    def test_polygon_takeoff_and_project_roundtrip(self):
        from measurements import Calibration
        from project_store import load_project, save_project
        self.window.open_path(str(self.source))
        view=self.window.current()
        view.state.calibrations[0]=Calibration(0.1)
        view.measure_mode="polygon"
        # PDF points are captured in page coordinate space; use screen clicks
        # with a calibrated scale, then exercise the same finish action as UI.
        view.on_click((20,20))
        view.on_click((120,20))
        view.on_click((120,120))
        self.assertEqual(len(view.polygon),3)
        view.finish_polygon()
        self.assertEqual(len(view.state.measurements),1)
        record=view.state.measurements[0]
        self.assertEqual(record.kind,"Polygon")
        self.assertEqual(record.unit,"m2")
        self.assertGreater(record.value,0)
        destination=Path(self.temp.name)/"saved.aer.json"
        save_project(destination,view.state.path,view.state.measurements,view.state.calibrations)
        rows,scales=load_project(destination,view.state.path)
        self.assertEqual(rows[0].kind,"Polygon")
        self.assertEqual(scales[0].metres_per_point,0.1)

    def test_rectangle_save_schema(self):
        from measurements import Calibration
        from project_store import save_project
        self.window.open_path(str(self.source))
        view=self.window.current()
        view.state.calibrations[0]=Calibration(0.1)
        view.measure_mode="area"
        view.on_drag((20,20),(120,120))
        self.assertEqual(view.state.measurements[-1].kind,"Rectangle")
        self.assertEqual(view.state.measurements[-1].unit,"m2")
        target=Path(self.temp.name)/"area.aer.json"
        save_project(target,view.state.path,view.state.measurements,view.state.calibrations)
        self.assertTrue(target.exists())
