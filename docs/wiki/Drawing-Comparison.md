# Drawing comparison and revision review

[← Wiki Home](Home.md)

AER PDF Studio generates visual revision comparisons for original/revised PDF packages with the same page count and corresponding page sizes.

## Create comparisons

1. From the main application, click **Compare Drawings**.
2. Select the original drawing PDF and then the revised PDF.
3. Choose either automatic translation matching or interactive manual control-point registration.
4. For manual matching, specify page numbers such as `1,3-5` or `all`.
5. On each selected page, click **three corresponding points** on the original drawing, then in the same order on the revised drawing.
6. Select an output folder.

## How registration works

- **Automatic mode:** estimates horizontal and vertical translation. It cannot handle substantial rotation, skew or changes of scale.
- **Manual mode:** first two corresponding point pairs determine a rotation, uniform scale and translation.
- **Independent check:** the third point is held back from the transform and gives a residual in **rendered pixels**. A heuristic threshold classifies it as `CHECK` or `REVIEW`. This is **not** an engineering tolerance or certification.

Use corresponding identifiable intersections or corners widely separated on the sheet. Check additional known features manually.

## Outputs

- `comparison_page_001.png` and subsequent PNGs: original and difference-highlighted revised drawing side by side
- `alignment_report.json`: page registration information and changed-pixel fraction
- `drawing_revision_register.csv`: comparison image, registration method, changed-pixel percentage, offsets, review flag and available checkpoint residual

The changed-pixel fraction is **not** registration confidence. It may reflect line thickness, font changes, rendering noise and true design revisions.

## Best-practice review

Use original drawing numbers and revision metadata to confirm matching sheets. Check the registration and manually inspect every highlighted change. The register flags comparisons for manual review; it does not determine approval or formal document control status.

For vector drawings that need OCR, see [Arabic OCR](Arabic-OCR.md). Do not use rasterised OCR exports as dimension-controlled originals.
