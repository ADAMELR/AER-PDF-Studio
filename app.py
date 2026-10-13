import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pypdf import PdfReader
from pdf_operations import merge_pdfs, split_pdf, rotate_pdf
from viewer import PDFViewer
from compare_batch import compare_document_pages

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AER PDF Studio — Community Preview 0.7")
        self.geometry("900x600")
        self.files = []
        bar = ttk.Frame(self, padding=10)
        bar.pack(fill="x")
        for label, fn in [
            ("Add PDFs", self.add), ("Open Viewer", self.open_viewer), ("Compare Drawings", self.compare_drawings), ("Remove", self.remove),
            ("Move Up", lambda: self.move(-1)), ("Move Down", lambda: self.move(1)),
            ("Merge / Save", self.merge), ("Split Selected", self.split),
            ("Rotate Selected", self.rotate)
        ]:
            ttk.Button(bar, text=label, command=fn).pack(side="left", padx=3)
        self.tree = ttk.Treeview(self, columns=("pages", "path"), show="headings", selectmode="browse")
        self.tree.heading("pages", text="Pages")
        self.tree.heading("path", text="PDF File")
        self.tree.column("pages", width=70, anchor="center")
        self.tree.column("path", width=750)
        self.tree.pack(fill="both", expand=True, padx=12, pady=12)
        ttk.Label(self, text="Local-only PDF operations • Files are not uploaded • Save produces new PDFs", padding=10).pack(fill="x")

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
                PDFViewer(self, self.files[index])
            except Exception as exc:
                messagebox.showerror("Preview failed", str(exc))

    def compare_drawings(self):
        original = filedialog.askopenfilename(title="Select original drawing PDF", filetypes=[("PDF", "*.pdf")])
        if not original:
            return
        revised = filedialog.askopenfilename(title="Select revised drawing PDF", filetypes=[("PDF", "*.pdf")])
        if not revised:
            return
        target = filedialog.askdirectory(title="Select folder for multi-page comparison images")
        if target:
            try:
                outputs = compare_document_pages(original, revised, target, side_by_side=True)
                messagebox.showinfo("Comparison saved", f"Saved {len(outputs)} page comparison images and alignment_report.json to:\\n" + target)
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
