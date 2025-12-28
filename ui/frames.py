# ui/frames.py
import tkinter as tk
from tkinter import ttk, messagebox

class AccountsListFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        """Creates the Treeview widget for displaying account data."""
        columns = ("Account Name", "Account Name in CRA", "Type", "Institution", "Account Number", "Opening Date")
        self.tree = ttk.Treeview(self, columns=columns, show='headings')

        # Column configuration
        column_configs = {
            "Account Name": (150, 'w'),
            "Account Name in CRA": (150, 'w'),
            "Type": (120, 'center'),
            "Institution": (150, 'w'),
            "Account Number": (100, 'w'),
            "Opening Date": (100, 'center')
        }

        for col, (width, anchor) in column_configs.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor)
        
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        vsb.grid(row=0, column=1, sticky='ns', pady=10)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if self.controller.db.conn:
            for row in self.controller.db.get_accounts():
                self.tree.insert('', tk.END, values=row)

class TransactionsListFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        """Creates the Treeview for Transactions with separate Deposit/Withdrawal columns."""

        columns = ("Account", "Date", "Deposit", "Withdrawal", "Notes")
        self.tree = ttk.Treeview(self, columns=columns, show='headings')

        # Column configuration
        column_configs = {
            "Account": (150, 'w'),
            "Date": (100, 'center'),
            "Deposit": (100, 'e'),    # Align numbers to the right (East)
            "Withdrawal": (100, 'e'), # Align numbers to the right (East)
            "Notes": (200, 'w')
        }

        for col, (width, anchor) in column_configs.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor)

        # Scrollbar
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        # Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        vsb.grid(row=0, column=1, sticky='ns', pady=10)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if self.controller.db.conn:
            for row in self.controller.db.get_transactions():
                self.tree.insert('', tk.END, values=row)

class NewTransactionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white', padx=20, pady=20, bd=1, relief="solid")
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        ttk.Label(self, text="Add New Transaction", font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)
        
        ttk.Label(self, text="Select Account:").grid(row=1, column=0, sticky="w")
        self.combo_account = ttk.Combobox(self, state="readonly")
        self.combo_account.grid(row=1, column=1, sticky="ew", padx=10)

        ttk.Label(self, text="Amount:").grid(row=2, column=0, sticky="w")
        self.entry_amount = ttk.Entry(self)
        self.entry_amount.grid(row=2, column=1, sticky="ew", padx=10)

        ttk.Button(self, text="Save", command=self.save).grid(row=3, column=1, sticky="e", pady=10)

    def refresh(self):
        if self.controller.db.conn:
            self.account_map = self.controller.db.get_account_map()
            self.combo_account['values'] = list(self.account_map.keys())

    def save(self):
        # Logic to call self.controller.db.save_transaction
        pass

# ... You would add NewAccountFrame, RoomYearsListFrame, etc., similarly ...