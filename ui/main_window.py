# ui/main_window.py
import tkinter as tk
from tkinter import ttk
from .styles import SIDEBAR_COLOR, SIDEBAR_WIDTH

class MainWindowLayout:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self._setup_layout()
        self._setup_sidebar()

    def _setup_layout(self):
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = tk.Frame(self.root, width=SIDEBAR_WIDTH, bg=SIDEBAR_COLOR)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        self.content_area = tk.Frame(self.root, bg="white")
        self.content_area.grid(row=0, column=1, sticky="nsew")

    def _setup_sidebar(self):
        ttk.Label(self.sidebar_frame, text="Navigation", background=SIDEBAR_COLOR).pack(pady=20)
        
        self.buttons = []
        nav_items = [
            ("Accounts", lambda: self.controller.show_frame("AccountsListFrame")),
            ("Transactions", lambda: self.controller.show_frame("TransactionsListFrame")),
            ("New Account", lambda: self.controller.show_frame("NewAccountFrame")),
            ("New Transaction", lambda: self.controller.show_frame("NewTransactionFrame")),
        ]

        for text, cmd in nav_items:
            btn = ttk.Button(self.sidebar_frame, text=text, command=cmd)
            btn.pack(fill='x', padx=10, pady=5)
            self.buttons.append(btn)