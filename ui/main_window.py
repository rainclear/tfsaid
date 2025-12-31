# ui/main_window.py
import tkinter as tk
from tkinter import ttk
from .styles import SIDEBAR_COLOR, SIDEBAR_WIDTH

class MainWindowLayout:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.sidebar_buttons = [] # Store buttons here to access them later
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

        # This tells content_area to let the frame at (0,0) fill the whole space
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

    def _setup_sidebar(self):
        ttk.Label(self.sidebar_frame, text="Navigation", background=SIDEBAR_COLOR).pack(pady=20)
        
        nav_items = [
            ("Accounts", "AccountsListFrame"),
            ("Transactions", "TransactionsListFrame"),
            ("Room by Year", "RoomYearsListFrame"),
            ("New Account", "NewAccountFrame"),
            ("New Transaction", "NewTransactionFrame"),
            ("New Room/Year", "NewRoomYearFrame"),
            ("Report (CRA Format)", "CRAReportFrame")
        ]

        for text, frame_name in nav_items:
            # We use a lambda to tell the controller which frame to show
            btn = ttk.Button(
                self.sidebar_frame,
                text=text,
                command=lambda f=frame_name: self.controller.show_frame(f)
            )
            btn.pack(fill='x', padx=10, pady=5)
            self.sidebar_buttons.append(btn) # Add to our list for toggling

    def set_navigation_state(self, enabled=True):
        """Enable or disable all navigation buttons."""
        state = "normal" if enabled else "disabled"
        for btn in self.sidebar_buttons:
            btn.config(state=state)