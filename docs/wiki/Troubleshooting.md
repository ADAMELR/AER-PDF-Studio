# Troubleshooting

[← Wiki Home](Home.md)

## The Windows application will not open

Make sure you extracted the ZIP first and are running `AER-PDF-Studio.exe` from the extracted folder. If Windows SmartScreen blocks the unsigned preview build, verify the repository and file provenance before deciding whether to run it. Antivirus blocks should be reviewed rather than bypassed blindly.

## Tesseract was not found

Install Tesseract separately. Ensure `tesseract.exe` is on PATH or browse to the installed executable when the viewer prompts you.

## Missing Arabic or English language data

Check for `ara.traineddata` and `eng.traineddata` in Tesseract's `tessdata` directory. The exact file depends on selected Arabic, English or mixed mode. Confirm installation with:

```powershell
tesseract --list-langs
```

## Search fails for Arabic words

The PDF may only contain scanned images, or the document may have a defective text layer. OCR the page into a **new PDF**, reopen that output, and test a clear word. Arabic diacritics and letter order may still cause recognition/search issues.

## Revision comparison refuses two drawings

The current comparison requires the same page count and page dimensions across corresponding sheets. Match pages manually and confirm the same drawing size. The alignment feature does not resolve different sheet sets automatically.

## Distorted or incorrect measurements

Recalibrate the current page using a clear printed dimension and check a second known dimension. Nonuniform scan stretch, sheet rotation and PDF display scaling can invalidate results.

## Vector-preserving OCR rejects a page

Page rotations and nonstandard crop boxes are not supported by the current overlay implementation. Use a separate rasterised OCR **reference copy** if acceptable, retaining the original PDF for engineering geometry.

## Reporting a bug

Use [GitHub Issues](https://github.com/ADAMELR/AER-PDF-Studio/issues/new/choose), describe the error and steps, and provide anonymised examples only. Do not publish sensitive client files or exploit samples; see [Security Policy](https://github.com/ADAMELR/AER-PDF-Studio/blob/main/SECURITY.md).
