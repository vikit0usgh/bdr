from tkinter import ttk


class CollectionPanel(ttk.Frame):
    """
    Painel reservado para a futura árvore de Collections.
    """

    def __init__(self, master):
        super().__init__(master)

        ttk.Label(
            self,
            text="Collections",
        ).pack(
            anchor="w",
            padx=8,
            pady=8,
        )

        self.tree = ttk.Treeview(
            self
        )

        self.tree.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=(0, 8),
        )
