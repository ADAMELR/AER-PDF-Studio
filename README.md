# AER PDF Studio — Community Preview 0.9

Open-source Windows-oriented PDF workspace, implemented with Tkinter, **pypdf**, **pypdfium2**, Pillow and ReportLab.

## Features

- Local PDF page rendering, zoom, previous/next navigation using PDFium
- Per-page calibration using a known drawing dimension in metres
- Approximate distance, rectangular area and polygon area takeoffs (m and m²)
- Measurement register with CSV export and local JSON project save/reopen, including per-page calibrations
- Multi-page visual difference images with translation-only auto-alignment (same page sizes and counts)
- Side-by-side drawing comparison images (original next to revised with red-highlighted differences)
- Interactive selection of two matching control points on selected pages on original and revised drawings
- Manual two-point rotation, uniform scaling and translation on selected pages; other pages use automatic translation-only matching
- Per-page alignment_report.json recording offsets, registration method, and percentage of changed pixels
- drawing_revision_register.csv with a manual-review-required status
- Drag a rectangle on a page and save visible red markup into a **new PDF**
- Reorder, merge, split and rotate PDFs
- Automated tests on Windows and Ubuntu for Python 3.11 and 3.13
- Windows EXE artifact built after successful test jobs

**Important:** Rectangle markups are flattened PDF content, not editable PDF annotations. Currently supported on ordinary non-rotated pages; native PDF annotations, text editing, signatures, OCR, native annotations and GPT functions are not yet implemented.

## Windows installation

```powershell
git clone https://github.com/ADAMELR/AER-PDF-Studio.git
cd AER-PDF-Studio
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Select **Add PDFs**, choose a document, select its row and click **Open Viewer**. Use **Calibrate** mode: drag over a known length and enter its real-world metres. Then select **Distance** or **Area** and drag to measure. Area mode measures an axis-aligned rectangle. For polygon takeoffs select Polygon, click at least three vertices, then Finish Polygon. Choose Export CSV to save recorded measurements. Use Save Project and Open Project to preserve measurements and page calibrations between sessions. Projects are tied to the same local PDF path. Compare Drawings creates PNG difference images for every page for same-size PDFs, with automatic translation-only registration, side-by-side output and a JSON offset report. Choose **Yes** at the registration prompt, enter page numbers such as 1,3-5 or all, and click corresponding control points on each selected page in matching order. Other pages use translation-only matching. The changed-pixel percentage is a comparison statistic, NOT a registration-confidence score. Alignment does not correct rotation, different page scales, cropping or distortion. Inspect comparison images manually; automatic matching is not guaranteed. The calibration is maintained per currently calibrated page; repeat on other pages. In **rectangle** mode, drag and click **Save Rectangle Markup** to save a new PDF. Your source PDF remains unchanged. Measurements are approximate and must be checked against the design dimensions; drawings with different X/Y scaling cannot be accurately measured using the uniform calibration.

Tests: `py -m unittest discover -s tests -v`.

## Licensing and security

Original project code is MIT licensed. Third-party libraries and their dependencies retain their own licensing and required notices. Review `AUDIT.md`; audit bundled PDFium binary notices before public executable distribution. PDF files can contain malicious content: only use trusted inputs during this prototype stage. This is not a security-hardened PDF editor or an engineering-certified measuring tool.

Roadmap: registration accuracy checks with independent control points, editable annotation layers, OCR, visual revisions and overlay, and opt-in GPT assistance.
