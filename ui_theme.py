"""Compact Fluent-inspired ttk theme. No Microsoft/Adobe assets or branding."""
import tkinter as tk
from tkinter import ttk

NAVY = "#14243B"
BLUE = "#1769AA"
BLUE_HOVER = "#0C548E"
LIGHT = "#F2F5F9"
WHITE = "#FFFFFF"
TEXT = "#203047"
MUTED = "#64748B"
LINE = "#D8E0EA"

def apply_theme(root):
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    root.configure(background=LIGHT)
    style.configure(".", font=("Segoe UI", 10), background=LIGHT, foreground=TEXT)
    style.configure("TFrame", background=LIGHT)
    style.configure("Surface.TFrame", background=WHITE)
    style.configure("Ribbon.TFrame", background=WHITE)
    style.configure("Sidebar.TFrame", background=NAVY)
    style.configure("TLabel", background=LIGHT, foreground=TEXT)
    style.configure("Surface.TLabel", background=WHITE, foreground=TEXT)
    style.configure("Muted.TLabel", background=LIGHT, foreground=MUTED)
    style.configure("Title.TLabel", background=LIGHT, foreground=NAVY, font=("Segoe UI Semibold", 19))
    style.configure("Section.TLabel", background=LIGHT, foreground=NAVY, font=("Segoe UI Semibold", 12))
    style.configure("RibbonTitle.TLabel", background=WHITE, foreground=MUTED, font=("Segoe UI", 9))
    style.configure("Sidebar.TLabel", background=NAVY, foreground=WHITE, font=("Segoe UI", 11))
    style.configure("SidebarTitle.TLabel", background=NAVY, foreground=WHITE, font=("Segoe UI Semibold", 17))
    style.configure("TButton", font=("Segoe UI", 10), padding=(11, 9),
                    background=WHITE, foreground=TEXT, borderwidth=1, relief="flat")
    style.map("TButton", background=[("active", "#E8F1FA"), ("pressed", "#DBEAF8")])
    style.configure("Accent.TButton", background=BLUE, foreground=WHITE,
                    font=("Segoe UI Semibold", 10), padding=(15, 10))
    style.map("Accent.TButton", background=[("active", BLUE_HOVER), ("pressed", NAVY)],
              foreground=[("disabled", "#ABB6C4")])
    style.configure("Nav.TButton", background=NAVY, foreground=WHITE,
                    anchor="w", padding=(18, 13), borderwidth=0)
    style.map("Nav.TButton", background=[("active", "#264365"), ("pressed", "#315277")])
    style.configure("TNotebook", background=WHITE, borderwidth=0)
    style.configure("TNotebook.Tab", font=("Segoe UI Semibold", 10), padding=(18, 10),
                    background="#E8EEF5", foreground=MUTED)
    style.map("TNotebook.Tab", background=[("selected", WHITE)],
              foreground=[("selected", BLUE)])
    style.configure("Treeview", background=WHITE, fieldbackground=WHITE,
                    foreground=TEXT, rowheight=34, borderwidth=0,
                    font=("Segoe UI", 10))
    style.configure("Treeview.Heading", font=("Segoe UI Semibold", 10),
                    background="#E6ECF4", foreground=NAVY, padding=10)
    style.map("Treeview", background=[("selected", "#DCECF9")],
              foreground=[("selected", NAVY)])
    style.configure("TCombobox", padding=(7, 6))
    return style
