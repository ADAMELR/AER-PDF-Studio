# AER PDF Studio — Community Preview 0.3

Open-source Windows-oriented PDF workspace, implemented with Tkinter, **pypdf**, **pypdfium2**, Pillow and ReportLab.

## Features

- Local PDF page rendering, zoom, previous/next navigation using PDFium
- Per-page calibration using a known drawing dimension in metres
- Approximate distance and axis-aligned rectangular area measurements (m and m²)
- Drag a rectangle on a page and save visible red markup into a **new PDF**
- Reorder, merge, split and rotate PDFs
- Automated tests on Windows and Ubuntu for Python 3.11 and 3.13
- Windows EXE artifact built after successful test jobs

**Important:** Rectangle markups are flattened PDF content, not editable PDF annotations. Currently supported on ordinary non-rotated pages; polygon takeoffs, saved measurement registers, text editing, signatures, OCR, native annotations and GPT functions are not yet implemented.

## Windows installation

```powershell
git clone https://github.com/ADAMELR/AER-PDF-Studio.git
cd AER-PDF-Studio
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Select **Add PDFs**, choose a document, select its row and click **Open Viewer**. Use **Calibrate** mode: drag over a known length and enter its real-world metres. Then select **Distance** or **Area** and drag to measure. Area is an axis-aligned rectangle only. The calibration is maintained per currently calibrated page; repeat on other pages. In **rectangle** mode, drag and click **Save Rectangle Markup** to save a new PDF. Your source PDF remains unchanged. Measurements are approximate and must be checked against the design dimensions; drawings with different X/Y scaling cannot be accurately measured using the uniform calibration.

Tests: `py -m unittest discover -s tests -v`.

## Licensing and security

Original project code is MIT licensed. Third-party libraries and their dependencies retain their own licensing and required notices. Review `AUDIT.md`; audit bundled PDFium binary notices before public executable distribution. PDF files can contain malicious content: only use trusted inputs during this prototype stage. This is not a security-hardened PDF editor or an engineering-certified measuring tool.

Roadmap: saved measurement register, polygon takeoffs, drawing alignment/overlay, editable annotation layers, OCR, visual revisions and overlay, and opt-in GPT assistance.
