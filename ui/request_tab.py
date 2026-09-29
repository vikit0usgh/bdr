
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

from models.request import HttpRequest, ResponseVariable
from services.curl_parser import CurlParser, CurlParseError
from services.http_client import HttpClient
from services.variable_service import VariableService
from utils.json_utils import format_json
from ui.theme import (
    BG,
    SURFACE,
    SURFACE_2,
    BORDER,
    TEXT,
    MUTED,
    ACCENT,
    SUCCESS,
    ERROR,
    configure_text,
)


class RequestTab(ttk.Frame):

    def __init__(
        self,
        master,
        request: HttpRequest | None = None,
        variable_service: VariableService | None = None,
    ):
        super().__init__(master)

        self.request = request or HttpRequest()
        self.variable_service = variable_service or VariableService()
        self.http_client = HttpClient()

        self._request_running = False
        self._request_started_at = None
        self._timer_after_id = None
        self._last_status = None
        self._last_response_headers = {}
        self._last_response_body = ""
        self._last_elapsed_ms = None

        self.method_var = tk.StringVar(
            value=self.request.method
        )

        self.url_var = tk.StringVar(
            value=self.request.url
        )

        self.status_var = tk.StringVar(
            value="—"
        )

        self.time_var = tk.StringVar(
            value="—"
        )

        self._build()
        self._apply_method_style()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)

        # ========================================================
        # REQUEST BAR
        # ========================================================

        request_card = ttk.Frame(
            self,
            style="Card.TFrame",
        )

        request_card.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=12,
            pady=(8, 5),
        )

        request_card.columnconfigure(
            1,
            weight=1,
        )

        ttk.Label(
            request_card,
            text="REQUEST",
            style="Section.TLabel",
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            padx=12,
            pady=(10, 6),
        )

        self.method_combo = ttk.Combobox(
            request_card,
            textvariable=self.method_var,
            values=self.http_client.SUPPORTED_METHODS,
            state="readonly",
            width=10,
        )

        self.method_combo.grid(
            row=1,
            column=0,
            padx=(12, 5),
            pady=(0, 12),
        )

        self.method_combo.bind(
            "<<ComboboxSelected>>",
            self._on_method_changed,
        )

        self.url_entry = ttk.Entry(
            request_card,
            textvariable=self.url_var,
        )

        self.url_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=5,
            pady=(0, 12),
        )

        self.send_button = ttk.Button(
            request_card,
            text="▶  Enviar",
            command=self.send_request,
            style="Accent.TButton",
        )

        self.send_button.grid(
            row=1,
            column=2,
            padx=(4, 12),
            pady=(0, 12),
        )

        self.url_entry.bind(
            "<Return>",
            self._url_enter,
        )

        self._bind_select_all(self)
        self._bind_select_all(self.url_entry)

        self.url_entry.bind(
            "<Control-v>",
            self._paste_into_url,
        )

        self.url_entry.bind(
            "<Command-v>",
            self._paste_into_url,
        )

        # ========================================================
        # REQUEST OPTIONS
        # ========================================================

        self.options = ttk.Notebook(self)

        self.options.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=5,
        )

        headers_frame = ttk.Frame(
            self.options,
            style="Card.TFrame",
        )

        body_frame = ttk.Frame(
            self.options,
            style="Card.TFrame",
        )

        extract_frame = ttk.Frame(
            self.options,
            style="Card.TFrame",
        )

        self.options.add(
            headers_frame,
            text="  Headers  ",
        )

        self.options.add(
            body_frame,
            text="  Body  ",
        )

        self.options.add(
            extract_frame,
            text="  Extract  ",
        )

        self._build_headers(
            headers_frame
        )

        self._build_body(
            body_frame
        )

        self._build_extract(
            extract_frame
        )

        # ========================================================
        # RESPONSE SUMMARY
        # ========================================================

        response_info = ttk.Frame(self)

        response_info.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=12,
            pady=(8, 4),
        )

        ttk.Label(
            response_info,
            text="RESPONSE",
            style="Section.TLabel",
        ).pack(
            side="left",
            padx=(2, 10),
        )

        self.status_badge = ttk.Label(
            response_info,
            textvariable=self.status_var,
            style="Status.Neutral.TLabel",
        )

        self.status_badge.pack(
            side="left"
        )

        self.time_badge = ttk.Label(
            response_info,
            textvariable=self.time_var,
            style="Status.Neutral.TLabel",
        )

        self.time_badge.pack(
            side="left",
            padx=7,
        )

        # ========================================================
        # RESPONSE TABS
        # ========================================================

        response_frame = ttk.Frame(
            self,
            style="Card.TFrame",
        )

        response_frame.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(4, 12),
        )

        response_frame.columnconfigure(
            0,
            weight=1,
        )

        response_frame.rowconfigure(
            0,
            weight=1,
        )

        self.response_notebook = ttk.Notebook(
            response_frame
        )

        self.response_notebook.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=6,
            pady=6,
        )

        body_response_frame = ttk.Frame(
            self.response_notebook,
            style="Card.TFrame",
        )

        headers_response_frame = ttk.Frame(
            self.response_notebook,
            style="Card.TFrame",
        )

        timing_response_frame = ttk.Frame(
            self.response_notebook,
            style="Card.TFrame",
        )

        self.response_notebook.add(
            body_response_frame,
            text="  Body  ",
        )

        self.response_notebook.add(
            headers_response_frame,
            text="  Headers  ",
        )

        self.response_notebook.add(
            timing_response_frame,
            text="  Timing  ",
        )

        self._build_response_body(
            body_response_frame
        )

        self._build_response_headers(
            headers_response_frame
        )

        self._build_response_timing(
            timing_response_frame
        )

    # ============================================================
    # REQUEST METHOD
    # ============================================================

    def _on_method_changed(
        self,
        _event=None,
    ):
        self._apply_method_style()

    def _apply_method_style(self):
        method = self.method_var.get().upper()

        if method in self.http_client.SUPPORTED_METHODS:
            self.method_combo.configure(
                style=f"{method}.TCombobox"
            )

    # ============================================================
    # RESPONSE UI
    # ============================================================

    def _build_response_body(
        self,
        parent,
    ):
        parent.columnconfigure(
            0,
            weight=1,
        )

        parent.rowconfigure(
            0,
            weight=1,
        )

        self.response_text = tk.Text(
            parent,
            wrap="none",
        )

        configure_text(
            self.response_text
        )

        self.response_text.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        scroll_y = ttk.Scrollbar(
            parent,
            orient="vertical",
            command=self.response_text.yview,
        )

        scroll_y.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        scroll_x = ttk.Scrollbar(
            parent,
            orient="horizontal",
            command=self.response_text.xview,
        )

        scroll_x.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        self.response_text.configure(
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
        )

        self._bind_select_all(
            self.response_text
        )

    def _build_response_headers(
        self,
        parent,
    ):
        parent.columnconfigure(
            0,
            weight=1,
        )

        parent.rowconfigure(
            0,
            weight=1,
        )

        self.response_headers_text = tk.Text(
            parent,
            wrap="none",
        )

        configure_text(
            self.response_headers_text
        )

        self.response_headers_text.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        self._bind_select_all(
            self.response_headers_text
        )

    def _build_response_timing(
        self,
        parent,
    ):
        parent.columnconfigure(
            0,
            weight=1,
        )

        self.timing_status_label = ttk.Label(
            parent,
            text="Aguardando requisição",
            style="Card.TLabel",
            font=(
                "TkDefaultFont",
                11,
                "bold",
            ),
        )

        self.timing_status_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=16,
            pady=(18, 8),
        )

        self.timing_detail_label = ttk.Label(
            parent,
            text="—",
            style="Card.TLabel",
        )

        self.timing_detail_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=16,
            pady=4,
        )

    def _set_response_headers(
        self,
        headers,
    ):
        self.response_headers_text.delete(
            "1.0",
            "end",
        )

        if not headers:
            self.response_headers_text.insert(
                "1.0",
                "Nenhum header de resposta disponível.",
            )
            return

        lines = [
            f"{key}: {value}"
            for key, value in headers.items()
        ]

        self.response_headers_text.insert(
            "1.0",
            "\n".join(lines),
        )

    def _set_response_timing(
        self,
        status=None,
        elapsed_ms=None,
    ):
        if elapsed_ms is None:
            self.timing_status_label.configure(
                text="Aguardando requisição"
            )

            self.timing_detail_label.configure(
                text="—"
            )

            return

        self.timing_status_label.configure(
            text=f"{elapsed_ms / 1000:.2f} s"
        )

        if status is None:
            self.timing_detail_label.configure(
                text="Requisição finalizada com erro."
            )

        else:
            self.timing_detail_label.configure(
                text=(
                    f"HTTP {status}  •  "
                    f"{elapsed_ms:.0f} ms"
                )
            )

    # ============================================================
    # BASIC UI HELPERS
    # ============================================================

    def _bind_select_all(
        self,
        widget,
    ):
        widget.bind(
            "<Control-a>",
            self._select_all,
            add="+",
        )

        widget.bind(
            "<Command-a>",
            self._select_all,
            add="+",
        )

    @staticmethod
    def _select_all(
        event,
    ):
        widget = event.widget

        try:
            widget.selection_range(
                0,
                "end",
            )

        except (
            AttributeError,
            tk.TclError,
        ):
            try:
                widget.tag_add(
                    "sel",
                    "1.0",
                    "end",
                )

            except (
                AttributeError,
                tk.TclError,
            ):
                pass

        return "break"

    def _paste_into_url(
        self,
        _event=None,
    ):
        try:
            clipboard = self.clipboard_get()

        except tk.TclError:
            return "break"

        self.url_entry.delete(
            0,
            "end",
        )

        self.url_entry.insert(
            0,
            clipboard,
        )

        if CurlParser.is_curl(
            clipboard
        ):
            self.import_curl(
                clipboard
            )

        return "break"

    def _url_enter(
        self,
        _event,
    ):
        if CurlParser.is_curl(
            self.url_var.get()
        ):
            self.import_curl()

    # ============================================================
    # CURL
    # ============================================================

    def import_curl(
        self,
        command=None,
    ):
        command = (
            self.url_var.get().strip()
            if command is None
            else command.strip()
        )

        if not CurlParser.is_curl(
            command
        ):
            messagebox.showwarning(
                "cURL",
                "Cole um comando cURL no campo de URL.",
                parent=self.winfo_toplevel(),
            )

            return

        try:
            method, url, headers, body = CurlParser.parse(
                command
            )

            if method not in self.http_client.SUPPORTED_METHODS:
                raise CurlParseError(
                    f"O método '{method}' não é suportado pela "
                    "interface atual."
                )

            self.method_var.set(
                method
            )

            self.url_var.set(
                url
            )

            self._apply_method_style()

            self._replace_headers(
                headers
            )

            self._replace_body(
                body
            )

            self.options.select(
                0
            )

        except CurlParseError as exc:
            messagebox.showerror(
                "Erro ao interpretar cURL",
                str(exc),
                parent=self.winfo_toplevel(),
            )

    # ============================================================
    # HEADERS
    # ============================================================

    def _replace_headers(
        self,
        headers,
    ):
        parent = self._headers_frame

        for child in parent.winfo_children():
            child.destroy()

        self.header_rows = []

        self._setup_headers(
            parent
        )

        for key, value in headers.items():
            self._add_header_row(
                parent,
                key,
                value,
            )

        self._add_header_row(
            parent
        )

    def _setup_headers(
        self,
        parent,
    ):
        parent.columnconfigure(
            0,
            weight=1,
        )

        parent.columnconfigure(
            1,
            weight=2,
        )

        parent.columnconfigure(
            2,
            weight=0,
        )

        ttk.Label(
            parent,
            text="KEY",
            style="Muted.TLabel",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=10,
            pady=(10, 5),
        )

        ttk.Label(
            parent,
            text="VALUE",
            style="Muted.TLabel",
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=10,
            pady=(10, 5),
        )

        ttk.Button(
            parent,
            text="＋ Header",
            command=lambda: self._add_header_row(
                parent
            ),
        ).grid(
            row=50,
            column=0,
            columnspan=3,
            sticky="w",
            padx=10,
            pady=10,
        )

    def _build_headers(
        self,
        parent,
    ):
        self._headers_frame = parent

        self.header_rows = []

        self._setup_headers(
            parent
        )

        for key, value in self.request.headers.items():
            self._add_header_row(
                parent,
                key,
                value,
            )

        self._add_header_row(
            parent
        )

    def _add_header_row(
        self,
        parent,
        key="",
        value="",
    ):
        row = len(
            self.header_rows
        ) + 1

        key_var = tk.StringVar(
            value=key
        )

        value_var = tk.StringVar(
            value=value
        )

        key_entry = ttk.Entry(
            parent,
            textvariable=key_var,
        )

        key_entry.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=(10, 5),
            pady=3,
        )

        value_entry = ttk.Entry(
            parent,
            textvariable=value_var,
        )

        value_entry.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=5,
            pady=3,
        )

        row_data = {
            "key": key_var,
            "value": value_var,
            "key_entry": key_entry,
            "value_entry": value_entry,
        }

        ttk.Button(
            parent,
            text="✕",
            width=3,
            style="Danger.TButton",
            command=lambda data=row_data: self._remove_header_row(
                data
            ),
        ).grid(
            row=row,
            column=2,
            padx=(3, 10),
            pady=3,
        )

        self.header_rows.append(
            row_data
        )

    def _remove_header_row(
        self,
        row_data,
    ):
        if row_data not in self.header_rows:
            return

        self.header_rows.remove(
            row_data
        )

        self._refresh_header_rows()

    def _refresh_header_rows(self):
        parent = self._headers_frame

        values = [
            (
                item["key"].get(),
                item["value"].get(),
            )
            for item in self.header_rows
        ]

        for child in parent.winfo_children():
            child.destroy()

        self.header_rows = []

        self._setup_headers(
            parent
        )

        for key, value in values:
            self._add_header_row(
                parent,
                key,
                value,
            )

        self._add_header_row(
            parent
        )

    # ============================================================
    # BODY
    # ============================================================

    def _build_body(
        self,
        parent,
    ):
        parent.columnconfigure(
            0,
            weight=1,
        )

        parent.rowconfigure(
            1,
            weight=1,
        )

        body_toolbar = ttk.Frame(
            parent,
            style="Card.TFrame",
        )

        body_toolbar.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=(10, 2),
        )

        ttk.Label(
            body_toolbar,
            text="Request body",
            style="Card.TLabel",
        ).pack(
            side="left"
        )

        ttk.Button(
            body_toolbar,
            text="Format JSON",
            command=self._format_body,
        ).pack(
            side="right"
        )

        self.body_text = tk.Text(
            parent,
            wrap="none",
        )

        configure_text(
            self.body_text
        )

        self.body_text.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(5, 10),
        )

        self._bind_select_all(
            self.body_text
        )

        # Ativa comportamento de editor:
        # {}, [], "", (), auto-close e backspace de pares.
        self._bind_json_auto_pairing()

        if self.request.body:
            self.body_text.insert(
                "1.0",
                self.request.body,
            )

    def _bind_json_auto_pairing(self):
        """
        Ativa pequenos recursos de editor para o Body.

        Exemplos:

            {  ->  {}

            [  ->  []

            "  ->  ""

            (  ->  ()

        O cursor permanece no meio do par.
        """

        self.body_text.bind(
            "<KeyPress>",
            self._json_keypress,
            add="+",
        )

        self.body_text.bind(
            "<BackSpace>",
            self._json_backspace,
            add="+",
        )

    def _json_keypress(
        self,
        event,
    ):
        pairs = {
            '"': '"',
            "{": "}",
            "[": "]",
            "(": ")",
        }

        closing = {
            '"': '"',
            "}": "}",
            "]": "]",
            ")": ")",
        }

        # ========================================================
        # FECHAMENTO EXISTENTE
        # ========================================================
        #
        # Exemplo:
        #
        # {
        #     "nome": |}
        #
        # Ao digitar "}", não queremos:
        #
        # {
        #     "nome": |}}
        #
        # Apenas pulamos o caractere existente.
        #

        if event.char in closing:
            next_char = self.body_text.get(
                "insert",
                "insert + 1 chars",
            )

            if next_char == event.char:
                self.body_text.mark_set(
                    "insert",
                    "insert + 1 chars",
                )

                return "break"

            return None

        # ========================================================
        # ABERTURA AUTOMÁTICA
        # ========================================================

        if event.char in pairs:
            close_char = pairs[
                event.char
            ]

            self.body_text.insert(
                "insert",
                event.char + close_char,
            )

            self.body_text.mark_set(
                "insert",
                "insert - 1 chars",
            )

            return "break"

        return None

    def _json_backspace(
        self,
        _event,
    ):
        try:
            previous_char = self.body_text.get(
                "insert - 1 chars",
                "insert",
            )

            next_char = self.body_text.get(
                "insert",
                "insert + 1 chars",
            )

        except tk.TclError:
            return None

        pairs = {
            '"': '"',
            "{": "}",
            "[": "]",
            "(": ")",
        }

        # Se o cursor estiver entre um par vazio:
        #
        # {}
        #  ^
        #
        # Backspace remove os dois.
        if pairs.get(
            previous_char
        ) == next_char:

            self.body_text.delete(
                "insert - 1 chars",
                "insert + 1 chars",
            )

            return "break"

        return None

    def _replace_body(
        self,
        body,
    ):
        self.body_text.delete(
            "1.0",
            "end",
        )

        if body:
            self.body_text.insert(
                "1.0",
                format_json(body),
            )

    def _format_body(self):
        raw = self.body_text.get(
            "1.0",
            "end-1c",
        )

        try:
            formatted = format_json(
                raw
            )

            self.body_text.delete(
                "1.0",
                "end",
            )

            self.body_text.insert(
                "1.0",
                formatted,
            )

        except Exception:
            pass

    # ============================================================
    # EXTRACT
    # ============================================================

    def _build_extract(
        self,
        parent,
    ):
        parent.columnconfigure(
            0,
            weight=1,
        )

        parent.rowconfigure(
            1,
            weight=1,
        )

        ttk.Label(
            parent,
            text=(
                "Extraia variáveis da última Response usando "
                "JSON Path. Ex.: $.token ou $.user.id"
            ),
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=8,
            pady=8,
        )

        container = ttk.Frame(
            parent
        )

        container.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=8,
        )

        container.columnconfigure(
            0,
            weight=1,
        )

        container.columnconfigure(
            1,
            weight=1,
        )

        ttk.Label(
            container,
            text="Nome da variável",
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        ttk.Label(
            container,
            text="JSON Path",
        ).grid(
            row=0,
            column=1,
            sticky="w",
        )

        self.extract_rows = []

        for variable in self.request.response_variables:
            self._add_extract_row(
                container,
                variable.name,
                variable.json_path,
            )

        self._add_extract_row(
            container
        )

        ttk.Button(
            container,
            text="＋ Variável",
            command=lambda: self._add_extract_row(
                container
            ),
        ).grid(
            row=50,
            column=0,
            columnspan=2,
            sticky="w",
            pady=8,
        )

    def _add_extract_row(
        self,
        parent,
        name="",
        json_path="",
    ):
        row = len(
            self.extract_rows
        ) + 1

        name_var = tk.StringVar(
            value=name
        )

        path_var = tk.StringVar(
            value=json_path
        )

        ttk.Entry(
            parent,
            textvariable=name_var,
        ).grid(
            row=row,
            column=0,
            sticky="ew",
            padx=(0, 5),
            pady=2,
        )

        ttk.Entry(
            parent,
            textvariable=path_var,
        ).grid(
            row=row,
            column=1,
            sticky="ew",
            padx=(5, 0),
            pady=2,
        )

        self.extract_rows.append(
            (
                name_var,
                path_var,
            )
        )

    # ============================================================
    # REQUEST MODEL
    # ============================================================

    def get_request(
        self,
    ) -> HttpRequest:

        headers = {}

        for header in self.header_rows:
            key = header[
                "key"
            ].get().strip()

            value = header[
                "value"
            ].get().strip()

            if key:
                headers[key] = value

        response_variables = []

        for name_var, path_var in self.extract_rows:
            name = name_var.get().strip()

            json_path = path_var.get().strip()

            if name and json_path:
                response_variables.append(
                    ResponseVariable(
                        name=name,
                        json_path=json_path,
                    )
                )

        self.request.method = (
            self.method_var.get()
        )

        self.request.url = (
            self.url_var.get().strip()
        )

        self.request.headers = headers

        self.request.body = self.body_text.get(
            "1.0",
            "end-1c",
        )

        self.request.response_variables = (
            response_variables
        )

        return self.request

    # ============================================================
    # HTTP REQUEST
    # ============================================================

    def send_request(
        self,
    ):
        if CurlParser.is_curl(
            self.url_var.get()
        ):
            self.import_curl()

            if CurlParser.is_curl(
                self.url_var.get()
            ):
                return

        if self._request_running:
            return

        request = self.get_request()

        resolved_url = (
            self.variable_service.resolve(
                request.url
            )
        )

        resolved_headers = (
            self.variable_service.resolve_dict(
                request.headers
            )
        )

        resolved_body = (
            self.variable_service.resolve(
                request.body
            )
        )

        self._request_running = True

        self._request_started_at = (
            time.perf_counter()
        )

        self._last_status = None
        self._last_response_headers = {}
        self._last_response_body = ""
        self._last_elapsed_ms = None

        self.status_var.set(
            "Enviando…"
        )

        self._set_status_visual(
            "running"
        )

        self.time_var.set(
            "0.00 s"
        )

        self._set_response_headers(
            {}
        )

        self._set_response_timing()

        self.response_text.delete(
            "1.0",
            "end",
        )

        self.response_text.insert(
            "1.0",
            "Enviando requisição…"
        )

        self._set_send_button_state(
            False
        )

        self._update_live_timer()

        thread = threading.Thread(
            target=self._execute_request,
            args=(
                request.method,
                resolved_url,
                resolved_headers,
                resolved_body,
            ),
            daemon=True,
        )

        thread.start()

    def _execute_request(
        self,
        method,
        url,
        headers,
        body,
    ):
        try:
            result = self.http_client.send(
                method=method,
                url=url,
                headers=headers,
                body=body,
            )

            self.after(
                0,
                lambda: self._request_finished(
                    result=result
                ),
            )

        except Exception as exc:
            self.after(
                0,
                lambda: self._request_failed(
                    exc
                ),
            )

    # ============================================================
    # TIMER
    # ============================================================

    def _update_live_timer(
        self,
    ):
        if not self._request_running:
            return

        elapsed = (
            time.perf_counter()
            - self._request_started_at
        )

        self.time_var.set(
            f"{elapsed:.2f} s"
        )

        self._timer_after_id = self.after(
            50,
            self._update_live_timer,
        )

    def _stop_live_timer(
        self,
    ):
        if self._timer_after_id is not None:
            try:
                self.after_cancel(
                    self._timer_after_id
                )

            except tk.TclError:
                pass

            self._timer_after_id = None

    # ============================================================
    # REQUEST RESULT
    # ============================================================

    def _request_finished(
        self,
        result,
    ):
        if not self._request_running:
            return

        (
            status,
            elapsed_ms,
            response_body,
            response_headers,
        ) = result

        self._request_running = False

        self._stop_live_timer()

        self._set_send_button_state(
            True
        )

        self._last_status = status
        self._last_response_headers = (
            response_headers or {}
        )
        self._last_response_body = (
            response_body
        )
        self._last_elapsed_ms = (
            elapsed_ms
        )

        self.status_var.set(
            f"{status}  "
            f"{self._status_text(status)}"
        )

        self._set_status_visual(
            self._status_state(status)
        )

        self.time_var.set(
            f"{elapsed_ms / 1000:.2f} s"
        )

        self._set_response_headers(
            self._last_response_headers
        )

        self._set_response_timing(
            status,
            elapsed_ms,
        )

        self.response_text.delete(
            "1.0",
            "end",
        )

        self.response_text.insert(
            "1.0",
            format_json(
                response_body
            ),
        )

        self.response_notebook.select(
            0
        )

        self._extract_variables(
            response_body
        )

    def _request_failed(
        self,
        exc,
    ):
        if not self._request_running:
            return

        self._request_running = False

        self._stop_live_timer()

        self._set_send_button_state(
            True
        )

        elapsed = (
            time.perf_counter()
            - self._request_started_at
        )

        elapsed_ms = elapsed * 1000

        self.status_var.set(
            "ERROR  Request failed"
        )

        self._set_status_visual(
            "error"
        )

        self.time_var.set(
            f"{elapsed:.2f} s"
        )

        self._set_response_headers(
            {}
        )

        self._set_response_timing(
            None,
            elapsed_ms,
        )

        self.response_text.delete(
            "1.0",
            "end",
        )

        self.response_text.insert(
            "1.0",
            f"{type(exc).__name__}: {exc}",
        )

        self.response_notebook.select(
            0
        )

    # ============================================================
    # STATUS COLORS
    # ============================================================

    @staticmethod
    def _status_state(
        status,
    ):
        if 200 <= status < 300:
            return "success"

        if 300 <= status < 400:
            return "warning"

        if 400 <= status < 500:
            return "client_error"

        if 500 <= status < 600:
            return "server_error"

        return "info"

    @staticmethod
    def _status_text(
        status,
    ):
        if 200 <= status < 300:
            return "OK"

        if 300 <= status < 400:
            return "Redirect"

        if 400 <= status < 500:
            return "Client Error"

        if 500 <= status < 600:
            return "Server Error"

        return "HTTP"

    def _set_status_visual(
        self,
        state,
    ):
        styles = {
            "running": "Status.Info.TLabel",
            "success": "Status.Success.TLabel",
            "warning": "Status.Warning.TLabel",
            "client_error": "Status.ClientError.TLabel",
            "server_error": "Status.ServerError.TLabel",
            "error": "Status.ServerError.TLabel",
            "info": "Status.Info.TLabel",
        }

        self.status_badge.configure(
            style=styles.get(
                state,
                "Status.Neutral.TLabel",
            )
        )

    def _set_send_button_state(
        self,
        enabled,
    ):
        if hasattr(
            self,
            "send_button",
        ):
            self.send_button.configure(
                state=(
                    "normal"
                    if enabled
                    else "disabled"
                )
            )

    # ============================================================
    # RESPONSE VARIABLES
    # ============================================================

    def _extract_variables(
        self,
        response_body: str,
    ):
        if not self.request.response_variables:
            return

        extracted = []

        for variable in self.request.response_variables:
            try:
                value = (
                    self.variable_service.extract_from_response(
                        response_body,
                        variable.json_path,
                    )
                )

                self.variable_service.set(
                    variable.name,
                    value,
                )

                extracted.append(
                    f"{variable.name} = {value}"
                )

            except Exception as exc:
                extracted.append(
                    f"{variable.name} -> ERRO: {exc}"
                )

        if extracted:
            self.response_text.insert(
                "end",
                "\n\n--- Variables extracted ---\n"
                + "\n".join(extracted),
            )
