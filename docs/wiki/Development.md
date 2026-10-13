# Contributing and development

[← Wiki Home](Home.md)

AER PDF Studio is written in Python with Tkinter and uses pypdf, pypdfium2, Pillow and ReportLab. The current main development environment supports Python 3.11 and 3.13.

## Repository structure

| File | Role |
| --- | --- |
| `app.py`, `viewer.py` | Main window and PDF viewing interface |
| `pdf_operations.py` | Merge, split and rotate |
| `measurements.py`, `takeoff.py` | Calibrated measurements and CSV export |
| `alignment.py`, `control_points.py`, `registration_quality.py` | Drawing registration and residual checks |
| `compare.py`, `compare_batch.py` | Difference rendering and revision register |
| `localization.py`, `pdf_text_search.py` | Bilingual UI strings and Unicode text search |
| `arabic_ocr.py`, `searchable_ocr.py`, `vector_ocr.py` | OCR export implementations |
| `tests/` | Automated regression tests |
| `.github/workflows/ci.yml` | Continuous integration and Windows artifact build |
| `.github/workflows/release.yml` | Manually reviewed Windows prerelease publication |

## Run tests

```powershell
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
```

GitHub Actions tests Windows and Ubuntu with Python 3.11 and 3.13.

## Helpful contributions

- Reproducible drawing-registration failures with non-sensitive synthetic samples
- Arabic ligature, diacritic and mixed-script OCR evaluation
- RTL improvements throughout the application
- UI accessibility and usability improvements
- More careful PDF crop/rotation geometry support
- Independent checks for calibration and measured quantities

Before submitting a pull request, read [CONTRIBUTING.md](https://github.com/ADAMELR/AER-PDF-Studio/blob/main/CONTRIBUTING.md), [SECURITY.md](https://github.com/ADAMELR/AER-PDF-Studio/blob/main/SECURITY.md), and the [MIT license](https://github.com/ADAMELR/AER-PDF-Studio/blob/main/LICENSE).
