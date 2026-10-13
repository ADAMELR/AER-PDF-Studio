# AER PDF Studio — Community Preview 1.4

Open-source Windows-oriented PDF workspace, implemented with Tkinter, **pypdf**, **pypdfium2**, Pillow and ReportLab.

## Arabic / English support (preview)

- Main toolbar language switch (en / ar); English and Arabic labels on principal commands
- Search existing PDF text layers for Arabic or English Unicode text from the viewer; jumps to the first matching page
- Arabic filenames and pre-rendered text can work through the underlying Unicode and PDFium handling, but are not yet independently tested with representative documents
- Local OCR to UTF-8 text using a separately installed Tesseract executable with Arabic (ara), English (eng), or both language datasets
- The OCR to Text button exports UTF-8 .txt without altering source
- **Create Searchable PDF / إنشاء PDF قابل للبحث** rasterizes source pages, adding searchable text; original unchanged
- **Preserve Vector + OCR / حفظ الرسم المتجهي وإضافة OCR** retains original PDF pages and adds extracted hidden text from Tesseract's PDF text layer, without overlaying OCR page images
- Direct Arabic PDF text editing, embedded Arabic font authoring, search-result highlighting and complete RTL layout are not implemented yet

## Features

- Local PDF page rendering, zoom, previous/next navigation using PDFium
- Per-page calibration using a known drawing dimension in metres
- Approximate distance, rectangular area and polygon area takeoffs (m and m²)
- Measurement register with CSV export and local JSON project save/reopen, including per-page calibrations
- Multi-page visual difference images with translation-only auto-alignment (same page sizes and counts)
- Side-by-side drawing comparison images (original next to revised with red-highlighted differences)
- Interactive selection of three matching control points on selected pages on original and revised drawings
- Manual two-point rotation, uniform scaling and translation on selected pages; other pages use automatic translation-only matching
- Per-page alignment_report.json recording offsets, registration method, and percentage of changed pixels
- drawing_revision_register.csv with a manual-review-required status
- An independent third corresponding point used to calculate a check residual (rendered pixels) after alignment
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

## Alignment check

Pick three corresponding locations on each selected page. The first two define the rotation/scale/translation; the third is held out for validation. A residual at or below 3 raster pixels receives a CHECK label, otherwise REVIEW. This threshold is a preliminary heuristic, not a certified accuracy criterion; all drawing comparisons remain subject to manual review.

## Offline Arabic OCR setup (Windows)

1. Install Tesseract OCR for Windows from a trusted source. Its installation location can be selected through the app if it is not on PATH.
2. Ensure Arabic language data `ara.traineddata` is installed alongside English `eng.traineddata` in the Tesseract `tessdata` directory.
3. Open your PDF in AER PDF Studio. Choose **OCR to Text / استخراج النص OCR**.
4. Select **1 Arabic**, **2 English** or **3 Both**. Choose a destination .txt file.
5. The tool renders pages locally and uses Tesseract without uploading files. Long documents may take time.

**Limitations:** Tesseract is an external prerequisite, not bundled with the Windows EXE. Mixed-direction layout, Arabic diacritics, tables, and handwriting may not be recovered accurately; validate extracted text against the original. The Searchable PDF action creates a rasterized PDF with hidden OCR text; it is not suitable for preserving vector drawings, measurements, links or annotations. OCR reads the entire PDF and has a maximum raster page size of 25 megapixels.

## Searchable Arabic PDF export (v1.3)

Open the scanned PDF and choose **Create Searchable PDF / إنشاء PDF قابل للبحث**. Pick Arabic, English or both and save to a **different** PDF file. The program renders all pages as images and invokes locally installed Tesseract to produce a PDF with a hidden OCR text layer, then combines pages. OCR accuracy varies with scan quality, Arabic ligatures and diacritics; confirm text using a PDF reader. Source vector graphics, editable text, bookmarks, links, and annotations are not preserved. For engineering drawings, retain the original vector PDF and use this new copy only as a searchable reference. Tesseract and language models are separate prerequisites.

## Vector-preserving OCR export (v1.4 preview)

In the PDF viewer choose **Preserve Vector + OCR / حفظ الرسم المتجهي وإضافة OCR**. This method overlays extracted OCR text onto original PDF page content. Existing linework, image content, page annotations, and most page resources remain in the PDF. Tesseract must be installed locally with the requested language models. Unsupported: rotated or custom-cropped pages, signed PDFs (signatures are invalidated), and guaranteed exact text alignment on unusual sheet formats. Text recognition is imperfect, including Arabic diacritics and complex mixed-direction passages. Before using the output, inspect original geometry, page count, annotations, fonts and OCR text positioning. Save to a new PDF path, never the source file.
