# Contributing to AER PDF Studio

Thank you for helping improve this free Windows PDF workspace.

## How to contribute

1. Search [existing issues](https://github.com/ADAMELR/AER-PDF-Studio/issues) before opening a duplicate.
2. For new features, describe the user problem, intended workflow, and known edge cases in a feature request.
3. For code changes, create a fork or branch and open a focused pull request. Explain how you tested the change.
4. Add a regression test for bug fixes and keep compatibility with Python 3.11 and 3.13.
5. Run `python -m unittest discover -s tests -v` locally. GitHub Actions will also run the Windows/Ubuntu test matrix.

## Engineering and Arabic contributions

Especially helpful: anonymized test PDFs you have permission to share; Windows interface feedback; Arabic right-to-left / mixed-script defects; Tesseract placement edge cases; page rotation/crop issues; measurements and comparison registration accuracy. **Remove names, addresses, client information, personal data, and confidential design content** from shared test cases.

## Scope and safety

AER PDF Studio is a preview, not a signed, certified, or security-hardened PDF editor. Measurements, OCR placement, and visual comparisons require independent checking. Do not share private documents or security vulnerabilities in public issues: follow [SECURITY.md](SECURITY.md).

## Code and licensing

By submitting a contribution, you agree your original contribution can be distributed under the repository's [MIT license](LICENSE). Do not paste proprietary software or copyrighted document content without permission. Preserve notices and third-party licence obligations. Maintain the current local-only default rather than introducing network uploads unexpectedly.

## Pull request checklist

- [ ] The change has a clear purpose and relevant tests
- [ ] Windows and Ubuntu CI checks pass
- [ ] Documentation accurately identifies implementation and limitations
- [ ] Sample PDFs contain no sensitive/confidential information
- [ ] No new binary third-party dependencies are added without licence/security review
