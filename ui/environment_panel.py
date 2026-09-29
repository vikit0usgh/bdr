from tkinter import ttk


class EnvironmentPanel(ttk.Frame):
    """
    Placeholder para ambientes futuros:
    Development, Homolog, Production etc.
    """

    def __init__(self, master):
        super().__init__(master)

        ttk.Label(
            self,
            text="Environment",
        ).pack(
            anchor="w",
            padx=8,
            pady=8,
        )
