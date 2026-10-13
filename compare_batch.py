"""Multi-page comparisons with conservative translation-only alignment and audit manifest."""
import json
import csv
from pathlib import Path
import pypdfium2 as pdfium
from compare import compare_pages

def compare_document_pages(original, revised, output_folder, scale=1.5, auto_align=True, control_points=None, side_by_side=False):
    a=pdfium.PdfDocument(str(original))
    b=pdfium.PdfDocument(str(revised))
    try:
        count_a,count_b=len(a),len(b)
    finally:
        a.close()
        b.close()
    if count_a!=count_b:
        raise ValueError(f"Document page count mismatch ({count_a} versus {count_b}); manually match revisions first")
    if not count_a:
        raise ValueError("Documents contain no pages")
    output=Path(output_folder)
    output.mkdir(parents=True,exist_ok=True)
    results=[]
    manifest={"original":str(Path(original).resolve()),"revised":str(Path(revised).resolve()),
              "scale":scale,"auto_align":auto_align,"side_by_side":side_by_side,"pages":[]}
    for page in range(count_a):
        destination=output/f"comparison_page_{page+1:03d}.png"
        page_points = control_points.get(page) if isinstance(control_points,dict) else control_points
        result,info=compare_pages(original,revised,destination,page_index=page,scale=scale,
                                  auto_align=auto_align,return_alignment=True,
                                  control_points=page_points,side_by_side=side_by_side)
        results.append(result)
        manifest["pages"].append({"page":page+1,"output":result.name,**info})
    (output/"alignment_report.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    with (output/"drawing_revision_register.csv").open("w",newline="",encoding="utf-8-sig") as stream:
        writer=csv.writer(stream)
        writer.writerow(("Page","Comparison Image","Registration Method","Changed Pixel %","X Offset (px)","Y Offset (px)","Review Status","Check Point Residual (px)","Registration Check"))
        for page in manifest["pages"]:
            writer.writerow((page["page"],page["output"],page["registration_method"],
                             format(page["changed_pixel_fraction"]*100,".2f"),
                             page["shift_x_px"],page["shift_y_px"],"REQUIRES MANUAL REVIEW",
                             (page.get("manual_registration") or {}).get("check_residual_px",""),
                             (page.get("manual_registration") or {}).get("quality_status","NOT CHECKED")))
    return results
