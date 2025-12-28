# ui/menu_bar.py
import tkinter as tk
from tkinter import messagebox

class AppMenuBar(tk.Menu):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        
        # --- File Menu ---
        file_menu = tk.Menu(self, tearoff=0)
        file_menu.add_command(label="New Database", command=self.controller.new_database)
        file_menu.add_command(label="Open Database", command=self.controller.open_database)
        file_menu.add_separator()
        file_menu.add_command(label="Close DB", command=self.controller.close_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.controller.quit)
        self.add_cascade(label="File", menu=file_menu)

        # --- Edit Menu ---
        edit_menu = tk.Menu(self, tearoff=0)
        edit_menu.add_command(label="Undo", command=self._placeholder)
        edit_menu.add_command(label="Redo", command=self._placeholder)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self._placeholder)
        edit_menu.add_command(label="Copy", command=self._placeholder)
        edit_menu.add_command(label="Paste", command=self._placeholder)
        self.add_cascade(label="Edit", menu=edit_menu)

        # --- Help Menu ---
        help_menu = tk.Menu(self, tearoff=0)
        help_menu.add_command(label="Help Index", command=self._placeholder)
        help_menu.add_command(label="About", command=self._show_about)
        self.add_cascade(label="Help", menu=help_menu)

    def _placeholder(self):
        pass

    def _show_about(self):
        messagebox.showinfo("About TFSAid", "TFSAid v1.0\nA tool for tracking TFSA contributions and room.")