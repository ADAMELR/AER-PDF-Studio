# GitHub public launch checklist

## Repository About section (maintainer action)

GitHub's **About** panel has no description or topics yet. Configure these on the repository home page using the gear icon.

**Suggested description (copy exactly or edit):**
Free open-source Windows PDF studio for engineering drawing comparison, takeoffs, and Arabic/English OCR.

**Suggested topics** (up to 20):
`pdf-editor`, `pdf-tools`, `python`, `tkinter`, `windows`, `open-source`, `pdf-viewer`, `pdf-annotation`, `pdf-comparison`, `engineering`, `construction`, `ocr`, `arabic-ocr`, `tesseract`, `pypdf`.

Suggested homepage: leave blank until an actual project website or documentation page exists. Optionally enable Issues and Discussions under **Settings → General → Features** if you intend to support community discussion.

## Before a public prerelease

- [ ] Test the latest EXE on a real Windows PC, including Add PDFs, Open Viewer, merge, split, measurements, compare, and close/reopen.
- [ ] Test Arabic OCR with Tesseract + `ara.traineddata` on a non-sensitive scanned document.
- [ ] Test the vector-preserving OCR output against a disposable engineering drawing; compare rendering and extractable text carefully.
- [ ] Review `AUDIT.md` and third-party binary licensing, especially bundled PDFium.
- [ ] Run Windows Defender/AV and avoid uploading client documents publicly.
- [ ] Collect genuine screenshots (main interface, comparison, takeoffs and Arabic OCR); only use files you are entitled to share.
- [ ] Review the README and limitations; confirm the app version matches the release tag.

## Publishing a formal downloadable prerelease

1. Open **Actions → Publish reviewed Windows prerelease → Run workflow**.
2. Choose the intended **main** branch.
3. Enter a new tag such as `v1.4.0-preview.1`.
4. Check the manual testing/licence review acknowledgement only when it is true.
5. Run workflow. It retests on Windows/Ubuntu, packages `AER-PDF-Studio.exe`, and creates a **prerelease** with ZIP and SHA256.
6. Verify the release at https://github.com/ADAMELR/AER-PDF-Studio/releases and check download/install before announcing.

**Important:** This workflow is intentionally manual, not automatic. Automated unit tests and PyInstaller success do not confirm runtime quality or absence of security vulnerabilities.

## Sharing

Publish an honest short demo to relevant communities only where permitted. Prefer real engineering examples with sensitive data removed. Avoid implying that OCR takeoffs, comparison confidence, or annotations are professionally certified.
