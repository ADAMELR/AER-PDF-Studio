"""Interactive paired control point picker for first-page PDF alignment."""
import tkinter as tk
from tkinter import ttk, messagebox
import pypdfium2 as pdfium
from PIL import ImageTk

class PointPicker(tk.Toplevel):
    """Pick two corresponding points on each image, in raster pixel coordinates."""
    def __init__(self, parent, original, revised, scale=1.5):
        super().__init__(parent)
        self.title("Register drawings — two matching points")
        self.geometry("1180x750")
        self.transient(parent)
        self.scale=scale
        self.result=None
        self.points=[[],[]]
        self.photos=[]
        ttk.Label(self,text="Choose two DISTINCT reference points on ORIGINAL, then the corresponding two points on REVISED. Use identifiable corners or grid intersections.",wraplength=1000).pack(padx=8,pady=8)
        bar=ttk.Frame(self)
        bar.pack(fill="x")
        self.status=ttk.Label(bar,text="Original: 0/2    Revised: 0/2")
        self.status.pack(side="left",padx=8)
        ttk.Button(bar,text="Reset points",command=self.reset).pack(side="right",padx=5)
        ttk.Button(bar,text="Use these points",command=self.accept).pack(side="right",padx=5)
        frame=ttk.Frame(self)
        frame.pack(fill="both",expand=True)
        self.canvases=[]
        for index,(label,path) in enumerate((("ORIGINAL",original),("REVISED",revised))):
            section=ttk.Frame(frame)
            section.pack(side="left",fill="both",expand=True,padx=3)
            ttk.Label(section,text=label).pack()
            canvas=tk.Canvas(section,background="#777777",height=600,width=550)
            sx=ttk.Scrollbar(section,orient="horizontal",command=canvas.xview)
            sy=ttk.Scrollbar(section,orient="vertical",command=canvas.yview)
            canvas.configure(xscrollcommand=sx.set,yscrollcommand=sy.set)
            canvas.pack(side="left",fill="both",expand=True)
            sy.pack(side="right",fill="y")
            sx.pack(side="bottom",fill="x")
            doc=pdfium.PdfDocument(path)
            try:
                if not len(doc):
                    raise ValueError("PDF has no pages")
                photo=ImageTk.PhotoImage(doc[0].render(scale=scale).to_pil().convert("RGB"))
            finally:
                doc.close()
            self.photos.append(photo)
            canvas.create_image(0,0,anchor="nw",image=photo)
            canvas.configure(scrollregion=(0,0,photo.width(),photo.height()))
            canvas.bind("<Button-1>",lambda event,i=index: self.pick(i,event))
            self.canvases.append(canvas)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW",self.cancel)

    def pick(self,index,event):
        if len(self.points[index])>=2:
            return
        canvas=self.canvases[index]
        x,y=canvas.canvasx(event.x),canvas.canvasy(event.y)
        photo=self.photos[index]
        if not (0<=x<photo.width() and 0<=y<photo.height()):
            return
        self.points[index].append((x,y))
        n=len(self.points[index])
        canvas.create_oval(x-5,y-5,x+5,y+5,outline="red",width=2,tags="picked")
        canvas.create_text(x+12,y-12,text=str(n),fill="red",tags="picked")
        self.status.config(text=f"Original: {len(self.points[0])}/2    Revised: {len(self.points[1])}/2")

    def reset(self):
        self.points=[[],[]]
        for canvas in self.canvases:
            canvas.delete("picked")
        self.status.config(text="Original: 0/2    Revised: 0/2")

    def accept(self):
        if any(len(points)!=2 for points in self.points):
            messagebox.showwarning("Incomplete", "Select two points on EACH drawing.",parent=self)
            return
        self.result=(self.points[0],self.points[1])
        self.destroy()

    def cancel(self):
        self.result=None
        self.destroy()

def pick_control_points(parent,original,revised,scale=1.5):
    dialog=PointPicker(parent,original,revised,scale)
    parent.wait_window(dialog)
    return dialog.result
