"""Desktop PDF preview and rectangle markup tool."""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pypdfium2 as pdfium
from PIL import ImageTk

from annotations import add_rectangle_markup


class PDFViewer(tk.Toplevel):
    def __init__(self, parent, source):
        super().__init__(parent)
        self.source = source
        self.doc = pdfium.PdfDocument(source)
        self.page_index = 0
        self.zoom = 1.25
        self.photo = None
        self.drag_start = None
        self.selection = None
        self.title("AER PDF Studio — " + source)
        self.geometry("1000x760")

        toolbar = ttk.Frame(self, padding=8)
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="Previous", command=lambda: self.step(-1)).pack(side="left")
        ttk.Button(toolbar, text="Next", command=lambda: self.step(1)).pack(side="left")
        ttk.Button(toolbar, text="Zoom −", command=lambda: self.set_zoom(self.zoom / 1.25)).pack(side="left")
        ttk.Button(toolbar, text="Zoom +", command=lambda: self.set_zoom(self.zoom * 1.25)).pack(side="left")
        ttk.Button(toolbar, text="Save Rectangle Markup", command=self.save_markup).pack(side="left", padx=12)
        self.status = ttk.Label(toolbar, text="")
        self.status.pack(side="right")
        ttk.Label(self, text="Drag on the page to draw a red rectangle. Save creates a NEW PDF.", padding=(8, 0)).pack(anchor="w")

        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(frame, background="#555555", highlightthickness=0)
        vs = ttk.Scrollbar(frame, orient="vertical", command=self.canvas.yview)
        hs = ttk.Scrollbar(frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=hs.set, yscrollcommand=vs.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.finish_drag)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.render()

    def set_zoom(self, zoom):
        self.zoom = max(0.4, min(4, zoom))
        self.render()

    def step(self, offset):
        self.page_index = max(0, min(len(self.doc) - 1, self.page_index + offset))
        self.render()

    def render(self):
        self.selection = None
        self.drag_start = None
        self.canvas.delete("all")
        page = self.doc[self.page_index]
        bitmap = page.render(scale=self.zoom)
        image = bitmap.to_pil().convert("RGB")
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo, tags="page")
        self.canvas.configure(scrollregion=(0, 0, image.width, image.height))
        self.status.configure(text=f"Page {self.page_index + 1}/{len(self.doc)}  •  {self.zoom:.0%}")

    def coords(self, event):
        return self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

    def start_drag(self, event):
        self.drag_start = self.coords(event)
        self.selection = None
        self.canvas.delete("mark")
    
    def drag(self, event):
        if self.drag_start is None:
            return
        x0, y0 = self.drag_start
        x1, y1 = self.coords(event)
        self.canvas.delete("mark")
        self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", width=3, tags="mark")

    def finish_drag(self, event):
        if self.drag_start is None:
            return
        x0, y0 = self.drag_start
        x1, y1 = self.coords(event)
        self.selection = (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
        self.drag_start = None

    def save_markup(self):
        if not self.selection:
            messagebox.showinfo("Select an area", "Draw a rectangle on the page first.", parent=self)
            return
        result = filedialog.asksaveasfilename(parent=self, defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not result:
            return
        try:
            page = self.doc[self.page_index]
            pdf_w, pdf_h = page.get_size()
            x0, y0, x1, y1 = self.selection
            page_rect = (x0/self.zoom, pdf_h-y1/self.zoom, x1/self.zoom, pdf_h-y0/self.zoom)
            add_rectangle_markup(self.source, result, self.page_index, page_rect)
            messagebox.showinfo("Saved", "Markup PDF saved as:\n" + result, parent=self)
        except Exception as exc:
            messagebox.showerror("Cannot save markup", str(exc), parent=self)

    def close(self):
        self.doc.close()
        self.destroy()
