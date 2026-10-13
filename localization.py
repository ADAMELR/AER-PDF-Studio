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
 "result":"Search result","error":"Error"},
 "ar":{"add":"إضافة ملفات PDF","open":"فتح العارض","compare":"مقارنة الرسومات",
 "remove":"إزالة","up":"تحريك للأعلى","down":"تحريك للأسفل",
 "merge":"دمج / حفظ","split":"تقسيم الملف المحدد","rotate":"تدوير الملف المحدد",
 "pages":"الصفحات","file":"ملف PDF","footer":"تُعالَج الملفات محلياً دون رفعها",
 "language":"اللغة","search":"بحث في PDF","prev":"السابق","next":"التالي",
 "notfound":"لم يُعثر على النص في طبقة النص القابلة للبحث.",
 "found":"عُثر عليه في الصفحة {page}",
 "query":"أدخل النص للبحث (عربي أو إنجليزي):",
 "viewer":"عارض PDF","help":"البحث في ملفات PDF النصية؛ الملفات الممسوحة تحتاج OCR.",
 "result":"نتيجة البحث","error":"خطأ"}
}
def tr(language,key,**kwargs):
    data=STRINGS.get(language,STRINGS["en"])
    return data.get(key,STRINGS["en"].get(key,key)).format(**kwargs)
