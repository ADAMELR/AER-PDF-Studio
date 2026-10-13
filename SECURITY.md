# Security Policy

## Project status

AER PDF Studio is a **community preview** and has not been security-audited for untrusted PDFs. PDF parsing, raster rendering, image processing, and OCR can be attacked via specially crafted documents. Do not open untrusted files on critical computers.

## Reporting vulnerabilities

**Do not post exploit details, malicious sample files or private information in public GitHub issues.**

If the repository has private vulnerability reporting enabled, use GitHub's **Security → Report a vulnerability** feature. Otherwise, contact the repository maintainer privately through an existing trusted channel and request a secure way to provide the report. This project does not currently promise a fixed security-response deadline.

## Supported versions

Security work generally targets the current community preview; older Actions artifacts may not be maintained. Download only from this repository's verified Actions runs or official Releases, and verify what you run. Windows executables are currently unsigned.

## Practical precautions

- Work on copies of important documents; avoid running unknown PDFs on sensitive workstations.
- Tesseract is installed separately: obtain executable and language models from trusted sources.
- PDF files are processed locally by this application; do not add unexpected network upload flows.
- The OCR/searchable PDF workflows may invalidate existing signatures and may not preserve all PDF features.
