"""Desktop PDF preview and rectangle markup tool."""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pypdfium2 as pdfium
from PIL import ImageTk
from thumbnails import make_thumbnail, visible_thumbnail_indices

from annotations import add_rectangle_markup
from measurements import calibrate, length_metres, rectangle_area_m2, screen_to_pdf
from takeoff import Measurement, polygon_area_m2, export_register_csv
from project_store import save_project, load_project
from localization import tr
from pdf_text_search import find_text_pages
from arabic_ocr import ocr_pdf_pages, OCRSetupError, LANGUAGES
from searchable_ocr import make_searchable_pdf
from vector_ocr import make_vector_searchable_pdf
from ui_theme import apply_theme, NAVY, LIGHT, WHITE, MUTED


class PDFViewer(tk.Toplevel):
    def __init__(self, parent, source, language="en"):
        super().__init__(parent)
        self.source = source
        self.language=language
        self.doc = pdfium.PdfDocument(source)
        self.page_index = 0
        self.zoom = 1.25
        self.photo = None
        self.thumbnail_photos = []
        self.show_thumbnails = True
        self.show_tools = True
        self.drag_start = None
        self.selection = None
        self.calibration = None
        self.calibration_page = None
        self.calibrations = {}
        self.register = []
        self.polygon_vertices = []
        self.mode = tk.StringVar(value="rectangle")
        self.measure_text = tk.StringVar(value="Calibrate using a known drawing dimension.")
        self.title("AER PDF Studio — " + source)
        self.geometry("1400x880")
        self.minsize(970, 620)
        apply_theme(self)

        header = tk.Frame(self, bg=NAVY, height=54)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="  AER  PDF STUDIO  /  DOCUMENT VIEWER",
                 bg=NAVY, fg=WHITE,
                 font=("Segoe UI Semibold", 13)).pack(side="left", padx=16)
        tk.Label(header, text=source.rsplit("/", 1)[-1].rsplit(chr(92), 1)[-1],
                 bg=NAVY, fg="#C0D0E0", font=("Segoe UI", 10)).pack(
                     side="right", padx=22)

        tabs = ttk.Notebook(self)
        tabs.pack(fill="x")
        home_tab = ttk.Frame(tabs, style="Ribbon.TFrame")
        measure_tab = ttk.Frame(tabs, style="Ribbon.TFrame")
        annotate_tab = ttk.Frame(tabs, style="Ribbon.TFrame")
        ocr_tab = ttk.Frame(tabs, style="Ribbon.TFrame")
        tabs.add(home_tab, text="View / عرض")
        tabs.add(measure_tab, text="Measure / قياس")
        tabs.add(annotate_tab, text="Markup / تعليم")
        tabs.add(ocr_tab, text="OCR / النصوص")

        for label, command in (
            (tr(language, "prev"), lambda: self.step(-1)),
            (tr(language, "next"), lambda: self.step(1)),
            ("Zoom −", lambda: self.set_zoom(self.zoom / 1.25)),
            ("Zoom +", lambda: self.set_zoom(self.zoom * 1.25)),
            ("Thumbnails", self.toggle_thumbnails),
            ("Tools panel", self.toggle_tools),
            (tr(language, "search"), self.search_pdf),
        ):
            ttk.Button(home_tab, text=label, command=command).pack(
                side="left", padx=5, pady=9)

        ttk.Label(measure_tab, text="Measurement tool:", style="Surface.TLabel").pack(
            side="left", padx=(14, 7))
        self.tool_selector = ttk.Combobox(measure_tab, textvariable=self.mode,
            values=["rectangle", "calibrate", "distance", "area", "polygon"],
            state="readonly", width=15)
        self.tool_selector.pack(side="left", padx=5, pady=9)
        for label, command in (
            ("Finish Polygon", self.finish_polygon),
            ("Export Measurements CSV", self.export_register),
            ("Save Project", self.save_project),
            ("Open Project", self.open_project),
        ):
            ttk.Button(measure_tab, text=label, command=command).pack(
                side="left", padx=5, pady=9)

        ttk.Button(annotate_tab, text="Save Rectangle Markup",
                   style="Accent.TButton", command=self.save_markup).pack(
                       side="left", padx=14, pady=9)
        ttk.Label(annotate_tab, text="Choose rectangle in the Measure tab, then drag over the page.",
                  style="Surface.TLabel").pack(side="left", padx=7)

        for label, command in (
            (tr(language, "ocr"), self.run_ocr),
            (tr(language, "searchable_pdf"), self.export_searchable_pdf),
            (tr(language, "vector_pdf"), self.export_vector_searchable_pdf),
        ):
            ttk.Button(ocr_tab, text=label, command=command).pack(
                side="left", padx=6, pady=9)

        ttk.Label(self, text="PAGE WORKSPACE", style="Section.TLabel",
                  padding=(18, 10)).pack(anchor="w")
        ttk.Label(self, text="Calibrate using a known length, then measure. Use the ribbon for search, markup and OCR.",
                  style="Muted.TLabel", padding=(18, 0)).pack(anchor="w")
        self.measurement_banner = ttk.Frame(self, padding=(18, 8))
        self.measurement_banner.pack(fill="x")
        ttk.Label(self.measurement_banner, textvariable=self.measure_text,
                  style="Section.TLabel").pack(side="left")
        self.status = ttk.Label(self.measurement_banner, text="", style="Muted.TLabel")
        self.status.pack(side="right")

        self.content_frame = ttk.Frame(self, padding=(8, 8, 8, 10))
        self.content_frame.pack(fill="both", expand=True)
        self.thumb_panel = ttk.Frame(self.content_frame, width=180)
        self.thumb_panel.pack(side="left", fill="y", padx=(0, 8))
        self.thumb_panel.pack_propagate(False)
        ttk.Label(self.thumb_panel, text="PAGE THUMBNAILS", style="Section.TLabel").pack(anchor="w", padx=8, pady=8)
        self.thumbnail_canvas = tk.Canvas(self.thumb_panel, background="#E9EEF4", highlightthickness=0, width=166)
        self.thumbnail_scroll = ttk.Scrollbar(self.thumb_panel, orient="vertical", command=self.thumbnail_canvas.yview)
        self.thumbnail_canvas.configure(yscrollcommand=self.thumbnail_scroll.set)
        self.thumbnail_canvas.pack(side="left", fill="both", expand=True)
        self.thumbnail_scroll.pack(side="right", fill="y")

        self.tools_panel = ttk.Frame(self.content_frame, width=185)
        self.tools_panel.pack(side="right", fill="y", padx=(8, 0))
        self.tools_panel.pack_propagate(False)
        ttk.Label(self.tools_panel, text="QUICK TOOLS", style="Section.TLabel").pack(anchor="w", padx=8, pady=(12, 14))
        for label, callback in (
            ("Select rectangle", lambda: self.mode.set("rectangle")),
            ("Calibrate", lambda: self.mode.set("calibrate")),
            ("Measure length", lambda: self.mode.set("distance")),
            ("Measure area", lambda: self.mode.set("area")),
            ("Polygon area", lambda: self.mode.set("polygon")),
            ("Finish polygon", self.finish_polygon),
            ("Export CSV", self.export_register),
            ("Search text", self.search_pdf),
        ):
            ttk.Button(self.tools_panel, text=label, command=callback).pack(fill="x", padx=8, pady=3)

        frame = ttk.Frame(self.content_frame)
        frame.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(frame, background="#C5CDD7", highlightthickness=0)
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
        self.bind("<Control-f>", lambda _event: self.search_pdf())
        self.bind("<Prior>", lambda _event: self.step(-1))
        self.bind("<Next>", lambda _event: self.step(1))
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.render()

    def toggle_thumbnails(self):
        self.show_thumbnails = not self.show_thumbnails
        if self.show_thumbnails:
            self.thumb_panel.pack(side="left", fill="y", padx=(0, 8), before=self.canvas.master)
            self.refresh_thumbnails()
        else:
            self.thumb_panel.pack_forget()

    def toggle_tools(self):
        self.show_tools = not self.show_tools
        if self.show_tools:
            self.tools_panel.pack(side="right", fill="y", padx=(8, 0))
        else:
            self.tools_panel.pack_forget()

    def show_page(self, index):
        if 0 <= index < len(self.doc):
            self.page_index = index
            self.render()

    def refresh_thumbnails(self):
        if not self.show_thumbnails:
            return
        canvas = self.thumbnail_canvas
        canvas.delete("all")
        self.thumbnail_photos = []
        y = 12
        for index in visible_thumbnail_indices(self.page_index, len(self.doc), radius=3):
            page = self.doc[index]
            try:
                image = make_thumbnail(page)
            finally:
                page.close()
            photo = ImageTk.PhotoImage(image)
            self.thumbnail_photos.append(photo)
            x = (164 - image.width) // 2
            canvas.create_rectangle(4, y-5, 160, y+image.height+25,
                fill="#D8EBFA" if index == self.page_index else "#E9EEF4",
                outline="#1769AA" if index == self.page_index else "#D4DCE7",
                width=2 if index == self.page_index else 1,
                tags=(f"thumb_{index}",))
            canvas.create_image(x, y, anchor="nw", image=photo,
                                tags=(f"thumb_{index}",))
            canvas.create_text(82, y+image.height+10,
                text=f"Page {index+1} / {len(self.doc)}",
                fill="#26364A", tags=(f"thumb_{index}",))
            canvas.tag_bind(f"thumb_{index}", "<Button-1>",
                            lambda _event, i=index: self.show_page(i))
            y += image.height + 41
        canvas.configure(scrollregion=(0, 0, 166, y+12))
        canvas.yview_moveto(0)

    def search_pdf(self):
        from tkinter import simpledialog
        phrase=simpledialog.askstring(tr(self.language,"search"),tr(self.language,"query"),parent=self)
        if phrase is None:
            return
        try:
            matching=find_text_pages(self.source,phrase)
            if not matching:
                messagebox.showinfo(tr(self.language,"result"),tr(self.language,"notfound"),parent=self)
                return
            self.page_index=matching[0]
            self.render()
            messagebox.showinfo(tr(self.language,"result"),tr(self.language,"found",page=self.page_index+1),parent=self)
        except Exception as exc:
            messagebox.showerror(tr(self.language,"error"),str(exc),parent=self)

    def run_ocr(self):
        from tkinter import simpledialog
        options = {"1": "ara", "2": "eng", "3": "ara+eng"}
        option = simpledialog.askstring(
            tr(self.language, "ocr"), tr(self.language, "ocr_choice"),
            initialvalue="3", parent=self)
        if option is None:
            return
        language = options.get(option.strip())
        if not language:
            messagebox.showerror(tr(self.language,"error"),tr(self.language,"ocr_bad_choice"),parent=self)
            return
        destination = filedialog.asksaveasfilename(parent=self, defaultextension=".txt",
            filetypes=[("UTF-8 text","*.txt")])
        if not destination:
            return
        try:
            result = ocr_pdf_pages(self.source, destination, language=language)
        except OCRSetupError:
            executable = filedialog.askopenfilename(
                parent=self,title=tr(self.language,"ocr_choose_exe"),
                filetypes=[("Programs","*.exe"),("All files","*.*")])
            if not executable:
                return
            try:
                result = ocr_pdf_pages(self.source,destination,language=language,executable=executable)
            except Exception as exc:
                messagebox.showerror(tr(self.language,"error"),str(exc),parent=self)
                return
        except Exception as exc:
            messagebox.showerror(tr(self.language,"error"),str(exc),parent=self)
            return
        messagebox.showinfo(tr(self.language,"ocr"),
            tr(self.language,"ocr_done",pages=result["pages"],file=result["output"]),parent=self)

    def export_searchable_pdf(self):
        from tkinter import simpledialog
        option=simpledialog.askstring(
            tr(self.language,"searchable_pdf"),
            tr(self.language,"ocr_choice"),initialvalue="3",parent=self)
        if option is None:
            return
        language={"1":"ara","2":"eng","3":"ara+eng"}.get(option.strip())
        if not language:
            messagebox.showerror(tr(self.language,"error"),tr(self.language,"ocr_bad_choice"),parent=self)
            return
        if not messagebox.askyesno(tr(self.language,"searchable_pdf"),
                tr(self.language,"ocr_raster_warning"),parent=self):
            return
        destination=filedialog.asksaveasfilename(
            parent=self,defaultextension=".pdf",filetypes=[("PDF","*.pdf")])
        if not destination:
            return
        try:
            result=make_searchable_pdf(self.source,destination,language=language)
        except OCRSetupError:
            executable=filedialog.askopenfilename(
                parent=self,title=tr(self.language,"ocr_choose_exe"),
                filetypes=[("Programs","*.exe"),("All files","*.*")])
            if not executable:
                return
            try:
                result=make_searchable_pdf(self.source,destination,language=language,executable=executable)
            except Exception as exc:
                messagebox.showerror(tr(self.language,"error"),str(exc),parent=self)
                return
        except Exception as exc:
            messagebox.showerror(tr(self.language,"error"),str(exc),parent=self)
            return
        messagebox.showinfo(tr(self.language,"searchable_pdf"),
            tr(self.language,"ocr_done",pages=result["pages"],file=result["output"]),parent=self)

    def export_vector_searchable_pdf(self):
        from tkinter import simpledialog
        selection=simpledialog.askstring(tr(self.language,"vector_pdf"),
            tr(self.language,"ocr_choice"),initialvalue="3",parent=self)
        if selection is None:
            return
        language={"1":"ara","2":"eng","3":"ara+eng"}.get(selection.strip())
        if language is None:
            messagebox.showerror(tr(self.language,"error"),tr(self.language,"ocr_bad_choice"),parent=self)
            return
        if not messagebox.askyesno(tr(self.language,"vector_pdf"),
                tr(self.language,"vector_warning"),parent=self):
            return
        destination=filedialog.asksaveasfilename(parent=self,defaultextension=".pdf",
            filetypes=[("PDF","*.pdf")])
        if not destination:
            return
        try:
            result=make_vector_searchable_pdf(self.source,destination,language=language)
        except OCRSetupError:
            executable=filedialog.askopenfilename(parent=self,
                title=tr(self.language,"ocr_choose_exe"),
                filetypes=[("Programs","*.exe"),("All files","*.*")])
            if not executable:
                return
            try:
                result=make_vector_searchable_pdf(self.source,destination,
                    language=language,executable=executable)
            except Exception as exc:
                messagebox.showerror(tr(self.language,"error"),str(exc),parent=self)
                return
        except Exception as exc:
            messagebox.showerror(tr(self.language,"error"),str(exc),parent=self)
            return
        messagebox.showinfo(tr(self.language,"vector_pdf"),
            tr(self.language,"ocr_done",pages=result["pages"],file=result["output"]),parent=self)

    def set_zoom(self, zoom):
        self.zoom = max(0.4, min(4, zoom))
        self.render()

    def step(self, offset):
        self.page_index = max(0, min(len(self.doc) - 1, self.page_index + offset))
        self.render()

    def render(self):
        self.selection = None
        self.drag_start = None
        self.polygon_vertices = []
        self.canvas.delete("all")
        self.calibration = self.calibrations.get(self.page_index)
        self.calibration_page = self.page_index if self.calibration else None
        page = self.doc[self.page_index]
        bitmap = page.render(scale=self.zoom)
        image = bitmap.to_pil().convert("RGB")
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo, tags="page")
        self.canvas.configure(scrollregion=(0, 0, image.width, image.height))
        self.status.configure(text=f"Page {self.page_index + 1}/{len(self.doc)}  •  {self.zoom:.0%}")
        self.refresh_thumbnails()

    def coords(self, event):
        return self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

    def start_drag(self, event):
        if self.mode.get() == "polygon":
            if self.calibration is None or self.calibration_page != self.page_index:
                messagebox.showerror("Calibration required", "Calibrate the current page first.", parent=self)
                return
            point = self.coords(event)
            self.polygon_vertices.append(point)
            if len(self.polygon_vertices) > 1:
                x0,y0 = self.polygon_vertices[-2]
                x1,y1 = point
                self.canvas.create_line(x0,y0,x1,y1,fill="blue",width=3,tags="polygon")
            return
        self.drag_start = self.coords(event)
        self.selection = None
        self.canvas.delete("mark")
    
    def drag(self, event):
        if self.drag_start is None:
            return
        x0, y0 = self.drag_start
        x1, y1 = self.coords(event)
        self.canvas.delete("mark")
        if self.mode.get() in ("calibrate", "distance"):
            self.canvas.create_line(x0, y0, x1, y1, fill="red", width=3, tags="mark")
        else:
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", width=3, tags="mark")

    def finish_drag(self, event):
        if self.drag_start is None:
            return
        x0, y0 = self.drag_start
        x1, y1 = self.coords(event)
        self.selection = (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
        self.drag_start = None
        if self.mode.get() != "rectangle":
            self.process_measurement((x0,y0),(x1,y1))

    def process_measurement(self, start, end):
        from tkinter import simpledialog
        page = self.doc[self.page_index]
        _, height = page.get_size()
        a = screen_to_pdf(start, self.zoom, height)
        b = screen_to_pdf(end, self.zoom, height)
        mode = self.mode.get()
        try:
            if mode == "calibrate":
                known = simpledialog.askfloat("Calibrate drawing", "Known dimension in metres:", parent=self, minvalue=0.000001)
                if known is None:
                    return
                self.calibration = calibrate(a, b, known)
                self.calibrations[self.page_index] = self.calibration
                self.calibration_page = self.page_index
                self.measure_text.set(f"Page {self.page_index+1} calibration: {self.calibration.metres_per_point:.8f} metres / PDF point")
            else:
                if self.calibration is None or self.calibration_page != self.page_index:
                    raise ValueError("Calibrate this page using a known dimension first.")
                if mode == "distance":
                    value = length_metres(a,b,self.calibration)
                    self.register.append(Measurement(self.page_index+1,"Distance",value,"m"))
                    self.measure_text.set(f"Approximate measured distance: {value:.3f} m")
                elif mode == "area":
                    rect = (min(a[0],b[0]), min(a[1],b[1]), max(a[0],b[0]), max(a[1],b[1]))
                    value = rectangle_area_m2(rect,self.calibration)
                    self.register.append(Measurement(self.page_index+1,"Rectangle",value,"m2"))
                    self.measure_text.set(f"Approximate rectangular area: {value:.3f} m²")
        except (ValueError, TypeError) as exc:
            messagebox.showerror("Measurement error", str(exc), parent=self)

    def finish_polygon(self):
        if len(self.polygon_vertices) < 3:
            messagebox.showinfo("Polygon", "Click at least three points in polygon mode.", parent=self)
            return
        try:
            _, height = self.doc[self.page_index].get_size()
            points = [screen_to_pdf(v,self.zoom,height) for v in self.polygon_vertices]
            value = polygon_area_m2(points,self.calibration)
            self.register.append(Measurement(self.page_index+1,"Polygon",value,"m2"))
            self.measure_text.set(f"Approximate polygon area: {value:.3f} m²; register entries: {len(self.register)}")
            self.polygon_vertices=[]
        except (ValueError,TypeError) as exc:
            messagebox.showerror("Polygon error",str(exc),parent=self)

    def export_register(self):
        if not self.register:
            messagebox.showinfo("No measurements", "Measure an area or length first.", parent=self)
            return
        target = filedialog.asksaveasfilename(parent=self,defaultextension=".csv",filetypes=[("CSV spreadsheet","*.csv")])
        if target:
            try:
                export_register_csv(self.register,target)
                messagebox.showinfo("Export complete",target,parent=self)
            except Exception as exc:
                messagebox.showerror("Export error",str(exc),parent=self)

    def save_project(self):
        path = filedialog.asksaveasfilename(parent=self,defaultextension=".aer.json",filetypes=[("AER project","*.aer.json")])
        if path:
            try:
                save_project(path,self.source,self.register,self.calibrations)
                messagebox.showinfo("Saved",f"Project saved to {path}",parent=self)
            except Exception as exc:
                messagebox.showerror("Project save error",str(exc),parent=self)

    def open_project(self):
        path = filedialog.askopenfilename(parent=self,filetypes=[("AER project","*.aer.json"),("JSON","*.json")])
        if path:
            try:
                records,scales = load_project(path,self.source)
                self.register,self.calibrations = records,scales
                self.calibration=self.calibrations.get(self.page_index)
                self.calibration_page=self.page_index if self.calibration else None
                self.measure_text.set(f"Loaded {len(records)} measurements and {len(scales)} page calibrations")
            except Exception as exc:
                messagebox.showerror("Project load error",str(exc),parent=self)

    def save_markup(self):
        if self.mode.get() != "rectangle":
            messagebox.showinfo("Choose rectangle", "Choose rectangle mode to save visible markups.", parent=self)
            return
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
