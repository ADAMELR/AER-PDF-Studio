# Preliminary licence audit

This is not a full legal compliance review.

| Project | Licence | Decision |
| --- | --- | --- |
| pypdf | BSD-3-Clause | Initial PDF processing dependency |
| PDF.js | Apache-2.0 | Future viewer |
| pdf-lib | MIT | Future JavaScript editing engine |
| PDF Arranger | GPL-3.0 | Reference only; do not copy into MIT core |
| Xournal++ | GPL-family; verify specific upstream revision | Reference only |
| Stirling PDF | Edition/version-specific terms require verification | External service candidate only |
| PyMuPDF | AGPL-3.0 or commercial | Excluded from MIT core |

Before public packaged distribution: pin and audit dependency versions, retain upstream notices and licences, scan dependency vulnerabilities, test malicious inputs and verify artefact provenance.
