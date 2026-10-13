# PDF tools and viewing

[← Wiki Home](Home.md)

## Adding and opening PDFs

Use **Add PDFs** to select one or more files. Select a row and click **Open Viewer**. The viewer supports page navigation and zoom.

## Merge, split and rotate

- **Merge / Save:** Reorder the selected file list with **Move Up/Move Down**, then merge the list into a new PDF.
- **Split Selected:** Split the selected PDF into individual pages in an output folder.
- **Rotate Selected:** Save a separately rotated PDF.

Always inspect the resulting page order and orientation. Operations are intended to save new outputs rather than alter the originals.

## Rectangle markup

In the viewer, choose `rectangle` mode and drag a rectangle over a region. Click **Save Rectangle Markup** to save a new PDF with the rectangle drawn on it. This is **flattened page content**, not a native editable PDF annotation.

## Project saving

Measurements and per-page calibration values can be exported to a local `.aer.json` project through **Save Project** and restored using **Open Project**. These projects are tied to the source PDF path and should not be treated as complete drawing archives.

## Limitations

There is no general-purpose text editing, native signature support, editable annotation layers or guaranteed preservation of all advanced PDF structures. Test with copies of important source documents.

See [Engineering Measurements](Engineering-Measurements.md) and [Drawing Comparison](Drawing-Comparison.md).
