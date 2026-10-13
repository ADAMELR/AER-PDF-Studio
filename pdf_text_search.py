"""Unicode-aware search in existing PDF text layers. OCR is not provided."""
import unicodedata
import pypdfium2 as pdfium

def normalize_text(text):
    if not isinstance(text,str):
        raise TypeError("Search text must be Unicode text")
    return unicodedata.normalize("NFC",text).casefold()

def find_text_pages(filename,phrase):
    query=normalize_text(phrase).strip()
    if not query:
        raise ValueError("Search phrase cannot be empty")
    document=pdfium.PdfDocument(str(filename))
    pages=[]
    try:
        for index in range(len(document)):
            page=document[index]
            try:
                text_page=page.get_textpage()
                try:
                    text=text_page.get_text_range()
                    if query in normalize_text(text):
                        pages.append(index)
                finally:
                    text_page.close()
            finally:
                page.close()
    finally:
        document.close()
    return pages
