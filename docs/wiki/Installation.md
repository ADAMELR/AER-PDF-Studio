# Installation and first run

[← Wiki Home](Home.md)

## Option 1 — Windows portable build

1. Open [Releases](https://github.com/ADAMELR/AER-PDF-Studio/releases).
2. Choose the newest tested community-preview release and download its Windows ZIP.
3. Extract the ZIP and run `AER-PDF-Studio.exe`. It is a **portable app**, not a traditional installer.
4. In the app choose **Add PDFs → Open Viewer** to open a document.

If the Releases page has no published package yet, find the most recent *successful* run at [GitHub Actions](https://github.com/ADAMELR/AER-PDF-Studio/actions/workflows/ci.yml), and download its `AER-PDF-Studio-Windows` artifact. GitHub may require sign-in to download Actions artifacts.

**Windows SmartScreen:** The preview EXE is not digitally signed. Only run it if you trust the source and build. Scan downloads using your security software.

## Option 2 — Run from source

Install Python 3.11 or 3.13 and Git. Open Windows PowerShell:

```powershell
git clone https://github.com/ADAMELR/AER-PDF-Studio.git
cd AER-PDF-Studio
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

## Updating

For a portable installation, close the program, back up your project JSON files, then replace the old EXE with the verified newer release. The program does not include an automatic updater. From source, run `git pull` and reinstall requirements if they have changed.

## Before working on important documents

- Use disposable copies of your PDFs during the preview stage.
- Keep source files separate from output PDFs and comparison images.
- Test page counts, measurement calibration and OCR search with known examples.
- See [Troubleshooting](Troubleshooting.md) if the program fails to start.

## Arabic OCR prerequisite

The Windows executable **does not include Tesseract**. To run OCR, separately install Tesseract and its `ara.traineddata` or `eng.traineddata` language files. See [Arabic OCR](Arabic-OCR.md).
