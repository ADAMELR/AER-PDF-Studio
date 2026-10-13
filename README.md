# AER PDF Studio — Community Preview 0.2

Open-source Windows-oriented PDF workspace, implemented with Tkinter, **pypdf**, **pypdfium2**, Pillow and ReportLab.

## Features

- Local PDF page rendering, zoom, previous/next navigation using PDFium
- Drag a rectangle on a page and save visible red markup into a **new PDF**
- Reorder, merge, split and rotate PDFs
- Automated tests on Windows and Ubuntu for Python 3.11 and 3.13
- Windows EXE artifact built after successful test jobs

**Important:** Rectangle markups are flattened PDF content, not editable PDF annotations. Currently supported on ordinary non-rotated pages; engineering measurement scale calibration, text editing, signatures, OCR, native annotations and GPT functions are not yet implemented.

## Windows installation

```powershell
git clone https://github.com/ADAMELR/AER-PDF-Studio.git
cd AER-PDF-Studio
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Select **Add PDFs**, choose a document, select its row and click **Open Viewer**. Drag to draw a rectangle and click **Save Rectangle Markup**. Your source PDF remains unchanged.

Tests: `py -m unittest discover -s tests -v`.

## Licensing and security

Original project code is MIT licensed. Third-party libraries and their dependencies retain their own licensing and required notices. Review `AUDIT.md`; audit bundled PDFium binary notices before public executable distribution. PDF files can contain malicious content: only use trusted inputs during this prototype stage. This is not a security-hardened PDF editor or an engineering-certified measuring tool.

Roadmap: editable annotation layers, engineering drawing calibration, OCR, visual revisions and overlay, and opt-in GPT assistance.
