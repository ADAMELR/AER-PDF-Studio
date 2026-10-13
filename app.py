import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from pypdf import PdfReader
from pdf_operations import merge_pdfs, split_pdf, rotate_pdf
from viewer import PDFViewer
from compare_batch import compare_document_pages
from point_picker import pick_control_points
from page_selection import parse_page_selection
from localization import tr

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AER PDF Studio — Community Preview 1.3")
        self.geometry("900x600")
        self.files = []
        self.language = tk.StringVar(value="en")
        self._labels=[]
        bar = ttk.Frame(self, padding=10)
        bar.pack(fill="x")
        for label, fn in [
            ("Add PDFs", self.add), ("Open Viewer", self.open_viewer), ("Compare Drawings", self.compare_drawings), ("Remove", self.remove),
            ("Move Up", lambda: self.move(-1)), ("Move Down", lambda: self.move(1)),
            ("Merge / Save", self.merge), ("Split Selected", self.split),
            ("Rotate Selected", self.rotate)
        ]:
            key={"Add PDFs":"add","Open Viewer":"open","Compare Drawings":"compare","Remove":"remove","Move Up":"up","Move Down":"down","Merge / Save":"merge","Split Selected":"split","Rotate Selected":"rotate"}[label]
            btn=ttk.Button(bar, text=tr(self.language.get(),key), command=fn)
            btn.pack(side="left", padx=3)
            self._labels.append((btn,key))
        ttk.Combobox(bar, textvariable=self.language, values=("en","ar"), state="readonly", width=4).pack(side="right", padx=6)
        self.language.trace_add("write",self.update_language)
        self.tree = ttk.Treeview(self, columns=("pages", "path"), show="headings", selectmode="browse")
        self.tree.heading("pages", text="Pages")
        self.tree.heading("path", text="PDF File")
        self.tree.column("pages", width=70, anchor="center")
        self.tree.column("path", width=750)
        self.tree.pack(fill="both", expand=True, padx=12, pady=12)
        self.footer=ttk.Label(self, text=tr("en","footer"), padding=10)
        self.footer.pack(fill="x")

    def update_language(self,*_):
        language=self.language.get()
        for widget,key in self._labels:
            widget.configure(text=tr(language,key))
        self.tree.heading("pages",text=tr(language,"pages"))
        self.tree.heading("path",text=tr(language,"file"))
        self.footer.configure(text=tr(language,"footer"))

    def add(self):
        for path in filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")]):
            try:
                count = len(PdfReader(path).pages)
                self.files.append(path)
                self.tree.insert("", "end", values=(count, path))
            except Exception as exc:
                messagebox.showerror("Cannot open PDF", f"{path}\n{exc}")

    def selected(self):
        selection = self.tree.selection()
        return self.tree.index(selection[0]) if selection else None

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for path in self.files:
            self.tree.insert("", "end", values=(len(PdfReader(path).pages), path))

    def open_viewer(self):
        index = self.selected()
        if index is not None:
            try:
                PDFViewer(self, self.files[index], language=self.language.get())
            except Exception as exc:
                messagebox.showerror("Preview failed", str(exc))

    def compare_drawings(self):
        original = filedialog.askopenfilename(title="Select original drawing PDF", filetypes=[("PDF", "*.pdf")])
        if not original:
            return
        revised = filedialog.askopenfilename(title="Select revised drawing PDF", filetypes=[("PDF", "*.pdf")])
        if not revised:
            return
        manual = messagebox.askyesno("Drawing registration", "Select matching control points on chosen pages?\\nYes = manual page selection.\\nNo = automatic translation alignment.")
        points = {}
        if manual:
            try:
                count_original = len(PdfReader(original).pages)
                count_revised = len(PdfReader(revised).pages)
                if count_original != count_revised:
                    raise ValueError("PDF page counts differ; match revisions manually first")
                selection = simpledialog.askstring("Choose drawing pages", f"Enter pages (1-{count_original}), e.g. 1,3-5 or all:", initialvalue="1", parent=self)
                if selection is None:
                    return
                pages = parse_page_selection(selection, count_original)
                for page in pages:
                    selected = pick_control_points(self, original, revised, scale=1.5, page_index=page)
                    if selected is None:
                        return
                    points[page] = selected
            except Exception as exc:
                messagebox.showerror("Point selection failed",str(exc))
                return
        target = filedialog.askdirectory(title="Select folder for multi-page comparison images")
        if target:
            try:
                outputs = compare_document_pages(original, revised, target, side_by_side=True, control_points=points if points else None)
                messagebox.showinfo("Comparison saved", f"Saved {len(outputs)} page comparison images and alignment_report.json and drawing_revision_register.csv to:\\n" + target)
            except Exception as exc:
                messagebox.showerror("Comparison failed", str(exc))

    def remove(self):
        index = self.selected()
        if index is not None:
            self.files.pop(index)
            self.refresh()

    def move(self, direction):
        index = self.selected()
        if index is None or not 0 <= index + direction < len(self.files):
            return
        self.files[index], self.files[index + direction] = self.files[index + direction], self.files[index]
        self.refresh()
        self.tree.selection_set(self.tree.get_children()[index + direction])

    def merge(self):
        if not self.files:
            return
        output = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if output:
            try:
                merge_pdfs(self.files, output)
                messagebox.showinfo("Saved", output)
            except Exception as exc:
                messagebox.showerror("Merge failed", str(exc))

    def split(self):
        index = self.selected()
        if index is None:
            return
        folder = filedialog.askdirectory()
        if folder:
            try:
                outputs = split_pdf(self.files[index], folder)
                messagebox.showinfo("Done", f"Created {len(outputs)} PDFs")
            except Exception as exc:
                messagebox.showerror("Split failed", str(exc))

    def rotate(self):
        index = self.selected()
        if index is None:
            return
        output = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if output:
            try:
                rotate_pdf(self.files[index], output)
                messagebox.showinfo("Saved", output)
            except Exception as exc:
                messagebox.showerror("Rotation failed", str(exc))

if __name__ == "__main__":
    App().mainloop()
