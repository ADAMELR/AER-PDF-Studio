# Engineering measurements and takeoffs

[← Wiki Home](Home.md)

These features provide **approximate, calibrated PDF-screen measurements** and are not professional survey or quantity-certification tools.

## Calibrate a drawing page

1. Open a PDF in the viewer.
2. Set the mode to `calibrate`.
3. Drag along a clearly identified dimension that is known in **metres**.
4. Enter the correct real-world length in metres.
5. Repeat for other pages because calibration is stored **per page**.

Avoid dimensions shortened by perspective, distorted scans, plotting-scale errors or nonuniform X/Y stretching.

## Length

Choose `distance`, drag between the two points and read the estimated length in **m**.

## Rectangular area

Choose `area`, drag opposite rectangle corners and read the estimated area in **m²**. This is an axis-aligned rectangular measurement.

## Polygon area

1. Select `polygon` mode.
2. Click at least three polygon vertices in order around the perimeter.
3. Choose **Finish Polygon**.
4. The approximate polygon area appears in **m²**.

Self-intersecting polygons and malformed geometry may produce inaccurate results. Review the vertices before recording the quantity.

## Measurement register

Use **Export CSV** to write measurements to a file that can be opened in Excel. Use **Save Project** to retain recorded measurements/calibration for the same local PDF path.

## Validation checklist

- Confirm the drawing's revision, sheet number and dimensional units.
- Calibrate on an explicit dimension printed on the current page.
- Repeat a known check length after calibration.
- Compare key quantities with engineering schedules or independent calculations.
- Record your check and assumptions outside the app where required.

See [Drawing Comparison](Drawing-Comparison.md) for revision checking.
