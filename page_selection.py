"""Safe page selection for per-page drawing registration."""
def parse_page_selection(text, page_count):
    if not isinstance(page_count,int) or page_count < 1:
        raise ValueError("Page count must be positive")
    if not isinstance(text,str) or not text.strip():
        raise ValueError("Enter page numbers, such as 1,3-5 or all")
    if text.strip().lower()=="all":
        return list(range(page_count))
    chosen=set()
    for section in text.split(","):
        section=section.strip()
        if not section:
            raise ValueError("Empty page selection")
        if "-" in section:
            pieces=section.split("-")
            if len(pieces)!=2 or any(not s.strip().isdigit() for s in pieces):
                raise ValueError("Invalid page range")
            a,b=map(int,pieces)
            if a>b:
                raise ValueError("Page ranges must ascend")
            if b-a>page_count:
                raise ValueError("Page range is too large")
            values=range(a,b+1)
        else:
            if not section.isdigit():
                raise ValueError("Invalid page number")
            values=(int(section),)
        for page in values:
            if page<1 or page>page_count:
                raise ValueError(f"Page {page} is outside document (1-{page_count})")
            chosen.add(page-1)
    return sorted(chosen)
