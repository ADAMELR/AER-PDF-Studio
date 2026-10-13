import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from pypdf import PdfReader
from pathlib import Path
from pdf_operations import merge_pdfs, split_pdf, rotate_pdf
from viewer import PDFViewer
from compare_batch import compare_document_pages
from point_picker import pick_control_points
from page_selection import parse_page_selection
from localization import tr
from ui_theme import apply_theme, NAVY, BLUE, WHITE, MUTED

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AER PDF Studio — Community Preview 1.6")
        self.geometry("1320x830")
        self.minsize(980, 620)
        apply_theme(self)
        self.files = []
        self.language = tk.StringVar(value="en")
        self.language.trace_add("write", self.update_language)
        self._labels = []
        self._build_shell()
        self.bind("<Control-o>", lambda _event: self.add())
        self.bind("<Control-m>", lambda _event: self.merge())
        self.bind("<Return>", lambda _event: self.open_viewer() if self.focus_get() == self.tree else None)

    def _ribbon_button(self, parent, key, callback, accent=False):
        button = ttk.Button(parent, text=tr(self.language.get(), key),
                            style="Accent.TButton" if accent else "TButton",
                            command=callback)
        button.pack(side="left", padx=(0, 8), pady=8)
        self._labels.append((button, key))
        return button

    def _build_shell(self):
        top = tk.Frame(self, bg=NAVY, height=57)
        top.pack(side="top", fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="  AER  PDF STUDIO", bg=NAVY, fg=WHITE,
                 font=("Segoe UI Semibold", 17)).pack(side="left", padx=18)
        tk.Label(top, text="ENGINEERING  •  DOCUMENT WORKSPACE",
                 bg=NAVY, fg="#B9CADD", font=("Segoe UI", 9)).pack(side="left", padx=14)
        ttk.Combobox(top, textvariable=self.language, values=("en", "ar"),
                     state="readonly", width=5).pack(side="right", padx=18, pady=12)
        tk.Label(top, text="Language / اللغة", bg=NAVY, fg=WHITE,
                 font=("Segoe UI", 9)).pack(side="right")

        tabs = ttk.Notebook(self)
        tabs.pack(fill="x")
        file_tab = ttk.Frame(tabs, style="Ribbon.TFrame")
        drawing_tab = ttk.Frame(tabs, style="Ribbon.TFrame")
        docs_tab = ttk.Frame(tabs, style="Ribbon.TFrame")
        tabs.add(file_tab, text="Home / الرئيسية")
        tabs.add(drawing_tab, text="Drawings / الرسومات")
        tabs.add(docs_tab, text="Organise / تنظيم")

        self._ribbon_button(file_tab, "add", self.add, accent=True)
        self._ribbon_button(file_tab, "open", self.open_viewer)
        self._ribbon_button(file_tab, "remove", self.remove)
        self._ribbon_button(drawing_tab, "compare", self.compare_drawings, accent=True)
        self._ribbon_button(drawing_tab, "open", self.open_viewer)
        self._ribbon_button(docs_tab, "merge", self.merge, accent=True)
        self._ribbon_button(docs_tab, "split", self.split)
        self._ribbon_button(docs_tab, "rotate", self.rotate)
        self._ribbon_button(docs_tab, "up", lambda: self.move(-1))
        self._ribbon_button(docs_tab, "down", lambda: self.move(1))

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)
        sidebar = ttk.Frame(body, style="Sidebar.TFrame", width=215)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ttk.Label(sidebar, text="WORKSPACE", style="SidebarTitle.TLabel").pack(
            fill="x", padx=18, pady=(24, 22))
        ttk.Button(sidebar, text="  ▣  Documents", style="Nav.TButton",
                   command=lambda: self.tree.focus_set()).pack(fill="x")
        ttk.Button(sidebar, text="  ⊞  Compare drawings", style="Nav.TButton",
                   command=self.compare_drawings).pack(fill="x")
        ttk.Button(sidebar, text="  ＋  Add PDFs", style="Nav.TButton",
                   command=self.add).pack(fill="x")
        ttk.Separator(sidebar).pack(fill="x", padx=16, pady=22)
        ttk.Label(sidebar, text="PDF tools • Local files", style="Sidebar.TLabel").pack(
            anchor="w", padx=19)
        main = ttk.Frame(body, padding=(22, 20, 22, 12))
        main.pack(side="left", fill="both", expand=True)

        ttk.Label(main, text="Document workspace", style="Title.TLabel").pack(anchor="w")
        ttk.Label(main, text="Select a PDF to preview or use the ribbon to manage your documents.",
                  style="Muted.TLabel").pack(anchor="w", pady=(3, 17))
        summary = ttk.Frame(main)
        summary.pack(fill="x", pady=(0, 12))
        self.file_count = ttk.Label(summary, text="0 documents", style="Section.TLabel")
        self.file_count.pack(side="left")
        ttk.Button(summary, text="Open selected PDF  →",
                   style="Accent.TButton", command=self.open_viewer).pack(side="right")

        surface = ttk.Frame(main, style="Surface.TFrame", padding=4)
        surface.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(surface, columns=("name", "pages", "path"),
                                 show="headings", selectmode="browse")
        self.tree.heading("name", text="DOCUMENT")
        self.tree.heading("pages", text=tr(self.language.get(), "pages"))
        self.tree.heading("path", text=tr(self.language.get(), "file"))
        self.tree.column("name", width=240, minwidth=130)
        self.tree.column("pages", width=80, minwidth=70, anchor="center", stretch=False)
        self.tree.column("path", width=490, minwidth=220)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(surface, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<Double-1>", lambda _event: self.open_viewer())

        status = ttk.Frame(self, padding=(16, 8))
        status.pack(side="bottom", fill="x")
        self.footer = ttk.Label(status, text=tr(self.language.get(), "footer"),
                                style="Muted.TLabel")
        self.footer.pack(side="left")
        ttk.Label(status, text="Community Preview 1.5", style="Muted.TLabel").pack(side="right")
        self.update_file_count()

    def update_file_count(self):
        self.file_count.configure(text=f"{len(self.files)} document(s)")

    def update_language(self, *_):
        language = self.language.get()
        for widget, key in self._labels:
            widget.configure(text=tr(language, key))
        self.tree.heading("pages", text=tr(language, "pages"))
        self.tree.heading("path", text=tr(language, "file"))
        self.footer.configure(text=tr(language, "footer"))

    def add(self):
        for path in filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")]):
            try:
                count = len(PdfReader(path).pages)
                self.files.append(path)
                self.tree.insert("", "end", values=(Path(path).name, count, path))
                self.update_file_count()
            except Exception as exc:
                messagebox.showerror("Cannot open PDF", f"{path}\n{exc}")

    def selected(self):
        selection = self.tree.selection()
        return self.tree.index(selection[0]) if selection else None

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for path in self.files:
            self.tree.insert("", "end", values=(Path(path).name, len(PdfReader(path).pages), path))
        self.update_file_count()

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
                messagebox.showinfo("Comparison saved", f"Saved {len(outputs)} page comparison images and alignment_report.json and drawing_revision_register.csv to:\n" + target)
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
