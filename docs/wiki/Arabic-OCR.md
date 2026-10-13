# Arabic language and OCR

[← Wiki Home](Home.md)

**Arabic / العربية:** AER PDF Studio includes a bilingual English/Arabic toolbar and local OCR options. Arabic text editing and fully right-to-left PDF annotation are **not currently implemented**.

## Bilingual interface

Select `ar` or `en` in the main window. The primary toolbar translates, but the entire application is not yet fully translated or RTL-aware.

## Search existing text-based PDFs

In **Open Viewer**, choose **Search PDF / بحث في PDF**. Enter Arabic or English Unicode text. The viewer searches an existing extractable text layer and navigates to the first matching page.

A scanned PDF may look like readable Arabic but contain **no text layer**. Such a document requires OCR first.

## Install offline Tesseract

1. Install a trusted Windows build of Tesseract OCR.
2. Install `ara.traineddata` in the Tesseract `tessdata` directory for Arabic and `eng.traineddata` for English.
3. Make `tesseract.exe` available via your Windows PATH or select its location if prompted.
4. Open an OCR sample with no sensitive information for initial verification.

Tesseract runs locally; no built-in cloud OCR service is used.

## Three export options

| Viewer option | Output | Original vector content |
| --- | --- | --- |
| **OCR to Text / استخراج النص OCR** | UTF-8 `.txt` | Original PDF remains unchanged |
| **Create Searchable PDF / إنشاء PDF قابل للبحث** | New rasterised PDF with hidden OCR text | Does not preserve source vector objects |
| **Preserve Vector + OCR / حفظ الرسم المتجهي وإضافة OCR** | New PDF with original page content plus OCR overlay | Attempts to preserve vector page content; experimental |

Choose language `1` Arabic, `2` English or `3` both. Both-language mode requires both language datasets.

## Important limitations

- OCR can fail on handwritten Arabic, diacritics, poor scans and mixed Arabic/English layout.
- The vector-preserving path rejects rotated pages and nonstandard crop boxes.
- OCR overlays may be offset on complex PDFs; text extraction and copy/paste order can be imperfect.
- Rewriting a PDF invalidates existing digital signatures.
- Use a **new output file**, keep the original, and verify the rendered output and searchable Arabic text.
- Tesseract is not bundled in the Windows application.

For error messages, see [Troubleshooting](Troubleshooting.md).
