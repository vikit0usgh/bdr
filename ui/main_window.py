import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from models.collection import Collection
from models.request import HttpRequest
from services.collection_service import CollectionService
from services.variable_service import VariableService
from ui.request_tab import RequestTab
from ui.theme import setup, BG, SURFACE


class MainWindow:

    def __init__(self):
        self.root = tk.Tk()
        setup(self.root)
        self.root.title(
            "API Client"
        )
        self.root.geometry(
            "1280x820"
        )
        self.root.minsize(
            900,
            650,
        )

        self.collection = Collection()
        self.variable_service = VariableService()
        self._tab_counter = 0

        self._build()

        self.add_request_tab()

    def _build(self):
        self.root.columnconfigure(
            0,
            weight=1,
        )
        self.root.rowconfigure(
            2,
            weight=1,
        )

        header = ttk.Frame(self.root)
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 4))

        ttk.Label(header, text="API Client", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="  •  HTTP workspace", style="Subtitle.TLabel").pack(side="left", pady=(5, 0))

        toolbar = ttk.Frame(
            self.root
        )
        toolbar.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=12,
            pady=(4, 8),
        )

        ttk.Button(
            toolbar,
            text="＋ Nova request",
            command=self.add_request_tab,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            toolbar,
            text="Salvar",
            command=self.save_collection,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            toolbar,
            text="Abrir",
            command=self.load_collection,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            toolbar,
            text="Variáveis",
            command=self.show_variables,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            toolbar,
            text="Renomear",
            command=self.rename_current_request,
        ).pack(
            side="left",
            padx=3,
        )

        self.notebook = ttk.Notebook(
            self.root
        )
        self.notebook.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 12),
        )

        # Fechar request: botão do meio, Ctrl+W / Cmd+W e clique no ✕.
        self.notebook.bind(
            "<Button-2>",
            self._close_tab_middle_click,
        )
        self.notebook.bind(
            "<Control-w>",
            self._close_current_tab,
        )
        self.notebook.bind(
            "<Command-w>",
            self._close_current_tab,
        )
        self.notebook.bind(
            "<Button-1>",
            self._handle_tab_click,
            add="+",
        )

    def add_request_tab(
        self,
        request: HttpRequest | None = None,
    ):
        self._tab_counter += 1

        if request is None:
            request = HttpRequest(
                name=f"Request {self._tab_counter}"
            )

        tab = RequestTab(
            self.notebook,
            request=request,
            variable_service=self.variable_service,
        )

        self.notebook.add(
            tab,
            text=f"{request.name}  ✕",
        )

        self.notebook.select(tab)

    def _handle_tab_click(self, event):
        try:
            tab_index = self.notebook.index(f"@{event.x},{event.y}")
        except tk.TclError:
            return

        tabs = self.notebook.tabs()
        if not tabs or tab_index < 0 or tab_index >= len(tabs):
            return

        tab_id = tabs[tab_index]
        try:
            bbox = self.notebook.bbox(tab_id)
        except tk.TclError:
            return

        if not bbox:
            return

        x, _y, width, _height = bbox
        if event.x >= x + width - 28:
            self._close_tab(tab_id)
            return "break"

    def _close_tab_middle_click(self, event):
        try:
            tab_index = self.notebook.index(f"@{event.x},{event.y}")
        except tk.TclError:
            return "break"

        tabs = self.notebook.tabs()
        if not tabs or tab_index < 0 or tab_index >= len(tabs):
            return "break"

        self._close_tab(tabs[tab_index])
        return "break"

    def _close_current_tab(self, _event=None):
        current = self.notebook.select()
        if current:
            self._close_tab(current)
        return "break"

    def _close_tab(self, tab_id):
        if tab_id not in self.notebook.tabs():
            return

        self.notebook.forget(tab_id)

        if not self.notebook.tabs():
            self.add_request_tab()

    def get_current_tab(self):
        current = self.notebook.select()

        if not current:
            return None

        return self.root.nametowidget(
            current
        )

    def rename_current_request(self):
        tab = self.get_current_tab()

        if tab is None:
            return

        new_name = simpledialog.askstring(
            "Renomear Request",
            "Nome da request:",
            initialvalue=tab.request.name,
            parent=self.root,
        )

        if new_name:
            tab.request.name = new_name.strip()

            self.notebook.tab(
                tab,
                text=f"{tab.request.name}  ✕",
            )

    def collect_requests(self):
        requests = []

        for tab_id in self.notebook.tabs():
            tab = self.root.nametowidget(
                tab_id
            )
            requests.append(
                tab.get_request()
            )

        return requests

    def save_collection(self):
        requests = self.collect_requests()

        name = simpledialog.askstring(
            "Collection",
            "Nome da Collection:",
            initialvalue=self.collection.name,
            parent=self.root,
        )

        if not name:
            return

        self.collection = Collection(
            name=name.strip(),
            variables=dict(
                self.variable_service.variables
            ),
            requests=requests,
        )

        path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Salvar Collection",
            defaultextension=".json",
            filetypes=[
                ("JSON", "*.json"),
                ("Todos os arquivos", "*.*"),
            ],
        )

        if not path:
            return

        try:
            CollectionService.save(
                self.collection,
                path,
            )

            messagebox.showinfo(
                "Collection",
                "Collection salva com sucesso.",
                parent=self.root,
            )

        except Exception as exc:
            messagebox.showerror(
                "Erro",
                f"Não foi possível salvar:\n{exc}",
                parent=self.root,
            )

    def load_collection(self):
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Abrir Collection",
            filetypes=[
                ("JSON", "*.json"),
                ("Todos os arquivos", "*.*"),
            ],
        )

        if not path:
            return

        try:
            collection = CollectionService.load(
                path
            )

        except Exception as exc:
            messagebox.showerror(
                "Erro",
                f"Não foi possível abrir:\n{exc}",
                parent=self.root,
            )
            return

        for tab_id in self.notebook.tabs():
            self.notebook.forget(tab_id)

        self.collection = collection

        self.variable_service = VariableService(
            dict(collection.variables)
        )

        for request in collection.requests:
            self.add_request_tab(
                request
            )

        if not collection.requests:
            self.add_request_tab()

    def show_variables(self):
        window = tk.Toplevel(
            self.root
        )
        window.title(
            "Collection Variables"
        )
        window.geometry(
            "650x450"
        )

        window.columnconfigure(
            0,
            weight=1,
        )
        window.rowconfigure(
            1,
            weight=1,
        )

        ttk.Label(
            window,
            text=(
                "Variáveis compartilhadas entre as requests. "
                "Use {{nome}} na URL, Headers ou Body."
            ),
            wraplength=600,
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=10,
            pady=10,
        )

        tree = ttk.Treeview(
            window,
            columns=("name", "value"),
            show="headings",
        )

        tree.heading(
            "name",
            text="Nome",
        )
        tree.heading(
            "value",
            text="Valor",
        )

        tree.column(
            "name",
            width=200,
        )
        tree.column(
            "value",
            width=400,
        )

        tree.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=5,
        )

        for name, value in (
            self.variable_service.variables.items()
        ):
            tree.insert(
                "",
                "end",
                values=(name, value),
            )

        ttk.Button(
            window,
            text="Fechar",
            command=window.destroy,
        ).grid(
            row=2,
            column=0,
            sticky="e",
            padx=10,
            pady=10,
        )

    def run(self):
        self.root.mainloop()
