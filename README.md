# AER PDF Studio — Community Preview 0.1

A Windows-oriented open-source PDF organiser prototype. Built with Python, Tkinter and pypdf. Current capabilities: merge, split, rotate and reorder PDF files; this is not yet an Acrobat-style editor.

## Run locally

Install Python 3.11+ and run:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

## Tests

```powershell
py -m unittest discover -s tests -v
```

The GitHub Actions workflow tests on Linux and Windows and then packages a Windows executable as a downloadable workflow artifact if all test jobs pass. A successful CI build is not a signed or professionally certified release.

## Open-source licence

The project-original source is MIT licensed. Third-party dependency pypdf is BSD-3-Clause. No code from Stirling PDF, PDF Arranger, PDF.js or other PDF applications has yet been copied.

## Roadmap

PDF.js viewer; pdf-lib editing; annotated engineering measurements and overlays; OCR; optional GPT assistance. Licence review and regression tests must precede release.

## Limitations

No page previews, OCR, direct text editing, or digital-signature preservation guarantees. Test output PDFs before professional use.
