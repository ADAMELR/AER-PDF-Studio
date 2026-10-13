"""Multi-page comparisons with conservative translation-only alignment and audit manifest."""
import json
from pathlib import Path
import pypdfium2 as pdfium
from compare import compare_pages

def compare_document_pages(original, revised, output_folder, scale=1.5, auto_align=True):
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
              "scale":scale,"auto_align":auto_align,"pages":[]}
    for page in range(count_a):
        destination=output/f"comparison_page_{page+1:03d}.png"
        result,info=compare_pages(original,revised,destination,page_index=page,scale=scale,
                                  auto_align=auto_align,return_alignment=True)
        results.append(result)
        manifest["pages"].append({"page":page+1,"output":result.name,**info})
    (output/"alignment_report.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    return results
