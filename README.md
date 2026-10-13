# AER PDF Studio

**Free, open-source desktop PDF tools for Windows — engineering drawing comparison, takeoffs, and Arabic/English OCR.**

[![CI: tests and Windows build](https://github.com/ADAMELR/AER-PDF-Studio/actions/workflows/ci.yml/badge.svg)](https://github.com/ADAMELR/AER-PDF-Studio/actions/workflows/ci.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-informational)](https://github.com/ADAMELR/AER-PDF-Studio/releases)

**[User Wiki](docs/wiki/Home.md)** · **[Download releases](https://github.com/ADAMELR/AER-PDF-Studio/releases)** · **[Features](#features)** · **[Getting started](#getting-started)** · **[Report a bug](https://github.com/ADAMELR/AER-PDF-Studio/issues/new/choose)**

> **Community Preview v1.5 — not a certified engineering, document-control or PDF-signing product.**
> Release downloads will appear under **Releases** once a reviewed release is published.
> Until then, successful builds can be downloaded from [GitHub Actions](https://github.com/ADAMELR/AER-PDF-Studio/actions) (sign-in may be required).

AER PDF Studio is a locally running Python/Tkinter desktop application. It is designed for engineers, designers, construction teams, and anyone managing PDF drawings and bilingual documents. PDFs are processed locally; the project does not contain cloud upload functionality.

## Redesigned desktop interface (v1.5)

The Windows UI now uses a contemporary, Office-inspired ribbon and an Acrobat-style document workspace (original visual styling; no Microsoft or Adobe logos/assets). The main window has a dark header, left navigation rail, Home / Drawings / Organise tabs, a searchable-looking but **not yet filterable** document list, double-click to open a PDF, and a simplified footer. The viewer has separate View, Measure, Markup and OCR tabs, avoiding the previous overcrowded toolbar. All original PDF processing features remain available. The redesign has automated Python tests but still requires practical review on Windows at different DPI and screen sizes.

## Features

| Category | Current capability | Limitations |
| --- | --- | --- |
| PDF workspace | View pages, navigate, zoom, merge, split, rotate | Still an early desktop preview |
| Engineering takeoffs | Calibrate page scale; distance, rectangular and polygon area measurements; CSV register | Approximate measurements only; independently verify against design dimensions |
| Drawing revisions | Side-by-side difference images, automatic translation matching, manual three-point selection, alignment report and CSV review register | Matched page counts/sizes required; control points 1–2 align, point 3 checks; human review required |
| Markup | Add flattened red rectangle markups in a **new** PDF | Not editable native PDF annotations |
| Local projects | Save and reopen measurements and page calibrations in JSON | Tied to the source PDF path |
| Arabic and English | Partial bilingual toolbar, search text-based PDFs | Not yet full RTL interface or text editing |
| OCR text | Extract Arabic, English or mixed OCR to UTF-8 text using separately installed Tesseract | OCR quality depends on document and language data |
| Searchable scanned PDF | Export a new rasterized PDF with OCR text layer | Source vector content not preserved in this mode |
| **Vector-preserving OCR** | Add hidden OCR text to a copy of original PDF pages | Experimental; rotated/custom-cropped pages unsupported; signature invalidation |

### Screenshots and demos

Real screenshots and a short demonstration of the Windows interface are planned. **Screenshots have intentionally not been fabricated.** Contributions of verified screenshots or a screen recording are welcome; see [Contributing](CONTRIBUTING.md).

## Documentation and Wiki

Read the [AER PDF Studio Wiki knowledge base](docs/wiki/Home.md) for installation, PDF tools, engineering measurements, revision comparison, Arabic OCR and troubleshooting. These pages are maintained in the main repository under [`docs/wiki`](docs/wiki); a separate GitHub Wiki tab may need an initial manual publication because the GitHub Wiki is a different Git repository.

## Getting started

### Option A — Windows download

1. Check [Releases](https://github.com/ADAMELR/AER-PDF-Studio/releases) for a published, tested Windows release.
2. Download its ZIP, extract, and launch `AER-PDF-Studio.exe`.
3. If no formal release exists yet, use the latest *successful* [CI workflow](https://github.com/ADAMELR/AER-PDF-Studio/actions/workflows/ci.yml), find the `AER-PDF-Studio-Windows` artifact, and extract it. GitHub may ask you to sign in.

AER PDF Studio is presently a **portable executable**, not a signed Windows installer. Unsigned builds may trigger Windows SmartScreen. Only run software you trust, and work on copies of important files.

### Option B — Run from source

Requires Python 3.11 or 3.13 on Windows:

```powershell
git clone https://github.com/ADAMELR/AER-PDF-Studio.git
cd AER-PDF-Studio
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

## Quick workflow

**Open and measure:** Choose **Add PDFs**, select the document and click **Open Viewer**. Set **calibrate** mode and drag between two points of a known dimension, entering its length in metres. Then use **distance**, **area**, or **polygon**; export the takeoff register as CSV. For polygon measurements, click at least three points and select **Finish Polygon**. Project data can be saved and reopened.

**Compare revisions:** Choose **Compare Drawings** and select the original/revised PDFs and an output directory. Select automatic translation alignment or manually register pages such as `1,3-5` using three matching points. The first two points define a similarity transform, and the independent third point gives an approximate residual in rendered pixels. The outputs include side-by-side PNG files, `alignment_report.json`, and `drawing_revision_register.csv`. Every revision is flagged for manual review.

**Arabic text search:** Select `ar` in the main window to switch the primary toolbar labels. In the viewer, choose **Search PDF / بحث في PDF** to search existing selectable text. Scanned PDFs require OCR first.

**Arabic OCR:** Install Tesseract separately, together with `ara.traineddata` and/or `eng.traineddata` in its `tessdata` directory. The viewer offers:
- **OCR to Text:** Output plain text to a new `.txt` file.
- **Create Searchable PDF:** Create a rasterized PDF with hidden OCR text.
- **Preserve Vector + OCR:** Experimental text-layer overlay on the original page content in a *new* PDF, with restrictions on rotation/crop boxes and potential alignment errors.

**Keep the original PDF.** OCR does not guarantee correct Arabic ligatures, diacritics, mixed-direction paragraphs, drawings or tables. New OCR PDFs may invalidate digital signatures. Validate outputs before distributing or using them for engineering records.

## Development and testing

```powershell
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
```

GitHub Actions runs tests on Windows and Ubuntu with Python 3.11 and 3.13, and builds a Windows EXE after successful tests. A separate manual release workflow is provided for maintainers; a green CI badge **does not** mean that UI interactions, Arabic OCR accuracy or engineering measurements have been field-validated.

## Roadmap

- [ ] Verified screenshots, short demo, and user-tested portable Windows distribution
- [ ] High-DPI and keyboard accessibility checks for the new ribbon interface
- [ ] Better RTL handling and full Arabic translations throughout the viewer
- [ ] OCR placement/quality validation on real-world Arabic documents and architectural/civil drawings
- [ ] Editable annotation objects and more robust page geometry support
- [ ] More complete drawing revision-management and sheet matching
- [ ] Signed Windows installer once distribution and security review are ready

See [Contributing](CONTRIBUTING.md) for ways to help, or [open a feature request](https://github.com/ADAMELR/AER-PDF-Studio/issues/new/choose).

## Security, limitations and licence

Only open PDFs you trust during this preview stage. The application has not been security-hardened, audited for all PDF attacks, or certified for quantity surveying or engineering. See [SECURITY.md](SECURITY.md) and [AUDIT.md](AUDIT.md). Third-party packages and binaries have separate licenses; verify notices before public redistribution.

AER PDF Studio original source code is released under the [MIT License](LICENSE).
