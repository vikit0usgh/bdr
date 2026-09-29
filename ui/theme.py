import tkinter as tk
from tkinter import ttk


# ============================================================
# PALETA
# ============================================================

BG = "#0B1120"
SURFACE = "#111827"
SURFACE_2 = "#1F2937"
SURFACE_3 = "#273449"
BORDER = "#334155"
TEXT = "#E5E7EB"
MUTED = "#94A3B8"
EDITOR_BG = "#070D18"

ACCENT = "#60A5FA"
ACCENT_HOVER = "#3B82F6"

GET = "#60A5FA"
POST = "#34D399"
PUT = "#FBBF24"
PATCH = "#FB923C"
DELETE = "#F87171"

SUCCESS = "#34D399"
INFO = "#60A5FA"
WARNING = "#FBBF24"
ERROR = "#F87171"


METHOD_COLORS = {
    "GET": GET,
    "POST": POST,
    "PUT": PUT,
    "PATCH": PATCH,
    "DELETE": DELETE,
}


def setup(root: tk.Tk):
    style = ttk.Style(root)

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=BG)

    # ========================================================
    # BASE
    # ========================================================

    style.configure(
        "TFrame",
        background=BG,
    )

    style.configure(
        "Card.TFrame",
        background=SURFACE,
    )

    style.configure(
        "TLabel",
        background=BG,
        foreground=TEXT,
        font=("TkDefaultFont", 10),
    )

    style.configure(
        "Muted.TLabel",
        background=BG,
        foreground=MUTED,
    )

    style.configure(
        "Card.TLabel",
        background=SURFACE,
        foreground=TEXT,
    )

    style.configure(
        "Title.TLabel",
        background=BG,
        foreground=TEXT,
        font=("TkDefaultFont", 17, "bold"),
    )

    style.configure(
        "Subtitle.TLabel",
        background=BG,
        foreground=MUTED,
        font=("TkDefaultFont", 9),
    )

    style.configure(
        "Section.TLabel",
        background=SURFACE,
        foreground=MUTED,
        font=("TkDefaultFont", 9, "bold"),
    )

    # ========================================================
    # BUTTONS
    # ========================================================

    style.configure(
        "TButton",
        background=SURFACE_2,
        foreground=TEXT,
        bordercolor=BORDER,
        lightcolor=SURFACE_2,
        darkcolor=SURFACE_2,
        padding=(10, 6),
        font=("TkDefaultFont", 9),
    )

    style.map(
        "TButton",
        background=[
            ("active", SURFACE_3),
            ("pressed", SURFACE_3),
        ],
        foreground=[
            ("disabled", MUTED),
        ],
    )

    style.configure(
        "Accent.TButton",
        background=ACCENT,
        foreground="#08111F",
        bordercolor=ACCENT,
        padding=(14, 7),
        font=("TkDefaultFont", 9, "bold"),
    )

    style.map(
        "Accent.TButton",
        background=[
            ("active", ACCENT_HOVER),
            ("pressed", ACCENT_HOVER),
        ],
    )

    style.configure(
        "Danger.TButton",
        background=SURFACE_2,
        foreground=ERROR,
        bordercolor=BORDER,
        padding=(6, 4),
    )

    style.map(
        "Danger.TButton",
        background=[("active", SURFACE_3)],
    )

    # ========================================================
    # HTTP METHOD BUTTONS / COMBOBOXES
    # ========================================================

    for method, color in METHOD_COLORS.items():
        style.configure(
            f"{method}.TCombobox",
            fieldbackground=EDITOR_BG,
            foreground=color,
            background=SURFACE_2,
            arrowcolor=color,
            bordercolor=color,
            lightcolor=color,
            darkcolor=color,
            padding=(7, 7),
            font=("TkDefaultFont", 9, "bold"),
        )

        style.map(
            f"{method}.TCombobox",
            fieldbackground=[
                ("readonly", EDITOR_BG),
            ],
            foreground=[
                ("readonly", color),
            ],
            selectbackground=[
                ("readonly", SURFACE_3),
            ],
            selectforeground=[
                ("readonly", color),
            ],
        )

    # ========================================================
    # INPUTS
    # ========================================================

    style.configure(
        "TEntry",
        fieldbackground=EDITOR_BG,
        foreground=TEXT,
        insertcolor=TEXT,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        padding=(8, 7),
    )

    style.configure(
        "TCombobox",
        fieldbackground=EDITOR_BG,
        foreground=TEXT,
        background=SURFACE_2,
        arrowcolor=MUTED,
        bordercolor=BORDER,
        padding=(6, 6),
    )

    # ========================================================
    # NOTEBOOKS
    # ========================================================

    style.configure(
        "TNotebook",
        background=BG,
        borderwidth=0,
        tabmargins=(0, 0, 0, 0),
    )

    style.configure(
        "TNotebook.Tab",
        background=SURFACE,
        foreground=MUTED,
        padding=(14, 8),
        borderwidth=0,
        font=("TkDefaultFont", 9),
    )

    style.map(
        "TNotebook.Tab",
        background=[
            ("selected", SURFACE_2),
            ("active", SURFACE_3),
        ],
        foreground=[
            ("selected", TEXT),
        ],
    )

    # ========================================================
    # LABelframe
    # ========================================================

    style.configure(
        "TLabelframe",
        background=SURFACE,
        foreground=TEXT,
        bordercolor=BORDER,
    )

    style.configure(
        "TLabelframe.Label",
        background=SURFACE,
        foreground=MUTED,
    )

    # ========================================================
    # TREEVIEW
    # ========================================================

    style.configure(
        "Treeview",
        background=EDITOR_BG,
        fieldbackground=EDITOR_BG,
        foreground=TEXT,
        bordercolor=BORDER,
        rowheight=28,
    )

    style.configure(
        "Treeview.Heading",
        background=SURFACE_2,
        foreground=TEXT,
        bordercolor=BORDER,
    )

    style.map(
        "Treeview",
        background=[("selected", "#1D4ED8")],
        foreground=[("selected", "#FFFFFF")],
    )

    # ========================================================
    # RESPONSE STATUS BADGES
    # ========================================================

    style.configure(
        "Status.Neutral.TLabel",
        background=SURFACE_2,
        foreground=MUTED,
        padding=(10, 5),
        font=("TkDefaultFont", 9, "bold"),
    )

    style.configure(
        "Status.Info.TLabel",
        background="#172554",
        foreground=INFO,
        padding=(10, 5),
        font=("TkDefaultFont", 9, "bold"),
    )

    style.configure(
        "Status.Success.TLabel",
        background="#064E3B",
        foreground=SUCCESS,
        padding=(10, 5),
        font=("TkDefaultFont", 9, "bold"),
    )

    style.configure(
        "Status.Warning.TLabel",
        background="#451A03",
        foreground=WARNING,
        padding=(10, 5),
        font=("TkDefaultFont", 9, "bold"),
    )

    style.configure(
        "Status.ClientError.TLabel",
        background="#431407",
        foreground="#FB923C",
        padding=(10, 5),
        font=("TkDefaultFont", 9, "bold"),
    )

    style.configure(
        "Status.ServerError.TLabel",
        background="#4C0519",
        foreground=ERROR,
        padding=(10, 5),
        font=("TkDefaultFont", 9, "bold"),
    )


def configure_text(widget: tk.Text):
    widget.configure(
        bg=EDITOR_BG,
        fg=TEXT,
        insertbackground=TEXT,
        selectbackground="#1D4ED8",
        selectforeground="#FFFFFF",
        relief="flat",
        borderwidth=0,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=ACCENT,
        padx=10,
        pady=10,
        font=("TkFixedFont", 10),
    )
