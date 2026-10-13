"""UI translation strings. Arabic support is currently a bilingual UI subset."""
STRINGS = {
 "en":{"add":"Add PDFs","open":"Open Viewer","compare":"Compare Drawings","remove":"Remove",
 "up":"Move Up","down":"Move Down","merge":"Merge / Save","split":"Split Selected",
 "rotate":"Rotate Selected","pages":"Pages","file":"PDF File",
 "footer":"Local PDF operations • Source files are not uploaded",
 "language":"Language","search":"Search PDF","prev":"Previous","next":"Next",
 "notfound":"No matching selectable text found.","found":"Found on page {page}",
 "query":"Enter text to find (Arabic or English):","viewer":"PDF viewer",
 "help":"Search supports text-layer PDFs; scanned documents require OCR.",
 "result":"Search result","error":"Error","ocr":"OCR to Text","ocr_choice":"Select OCR language: 1 Arabic, 2 English, 3 Both","ocr_bad_choice":"Enter 1, 2 or 3.","ocr_choose_exe":"Select tesseract.exe (install it first if needed)","ocr_done":"OCR of {pages} pages saved to {file}","searchable_pdf":"Create Searchable PDF","ocr_raster_warning":"This creates a NEW PDF by rasterizing every page and adding a hidden OCR text layer. Vector drawings, links, existing text, and annotations are NOT retained. Continue?"},
 "ar":{"add":"إضافة ملفات PDF","open":"فتح العارض","compare":"مقارنة الرسومات",
 "remove":"إزالة","up":"تحريك للأعلى","down":"تحريك للأسفل",
 "merge":"دمج / حفظ","split":"تقسيم الملف المحدد","rotate":"تدوير الملف المحدد",
 "pages":"الصفحات","file":"ملف PDF","footer":"تُعالَج الملفات محلياً دون رفعها",
 "language":"اللغة","search":"بحث في PDF","prev":"السابق","next":"التالي",
 "notfound":"لم يُعثر على النص في طبقة النص القابلة للبحث.",
 "found":"عُثر عليه في الصفحة {page}",
 "query":"أدخل النص للبحث (عربي أو إنجليزي):",
 "viewer":"عارض PDF","help":"البحث في ملفات PDF النصية؛ الملفات الممسوحة تحتاج OCR.",
 "result":"نتيجة البحث","error":"خطأ","ocr":"استخراج النص OCR","ocr_choice":"اختر اللغة: 1 عربي، 2 إنجليزي، 3 اللغتان","ocr_bad_choice":"أدخل 1 أو 2 أو 3","ocr_choose_exe":"اختر ملف tesseract.exe بعد تثبيت البرنامج","ocr_done":"اكتمل استخراج نص {pages} صفحات وحُفظ في {file}","searchable_pdf":"إنشاء PDF قابل للبحث","ocr_raster_warning":"سيتم إنشاء ملف PDF جديد من صور الصفحات مع إضافة طبقة نص مخفية للبحث. لن تُحفظ الرسومات المتجهة والتعليقات والروابط الأصلية. هل تريد المتابعة؟"}
}
def tr(language,key,**kwargs):
    data=STRINGS.get(language,STRINGS["en"])
    return data.get(key,STRINGS["en"].get(key,key)).format(**kwargs)
