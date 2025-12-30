# ui/frames.py
import tkinter as tk
from tkinter import ttk, messagebox
from .styles import ROW_COLOR_LIGHT, ROW_COLOR_DARK # Import your colors

class AccountsListFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        """Creates the Treeview widget for displaying account data."""
        self.columns = ("ID", "Account Name", "Account Name in CRA", "Type", "Institution", "Account Number", "Opening Date", "Actions")
        self.tree = ttk.Treeview(self, columns=self.columns, show='headings')

        # Column configuration
        column_configs = {
            "ID": (0, 'center'), # We will hide this
            "Account Name": (150, 'w'),
            "Account Name in CRA": (150, 'w'),
            "Type": (100, 'center'),
            "Institution": (120, 'w'),
            "Account Number": (100, 'w'),
            "Opening Date": (100, 'center'),
            "Actions": (80, 'center') # Action column
        }

        for col, (width, anchor) in column_configs.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor)

        # Hide the ID column (it's for internal use only)
        self.tree.column("ID", width=0, stretch=tk.NO)

        # Bind the click event to detect "Delete" clicks
        self.tree.bind("<Button-1>", self._on_click)
        
        # Scrollbar
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Configure Tags for alternating colors
        self.tree.tag_configure('oddrow', background=ROW_COLOR_LIGHT)
        self.tree.tag_configure('evenrow', background=ROW_COLOR_DARK)

        # Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        vsb.grid(row=0, column=1, sticky='ns', pady=10)

    def _on_click(self, event):
        """Detects if the user clicked the 'Delete' text in the Actions column."""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item_id = self.tree.identify_row(event.y)

            # Check if the 'Actions' column (column #8) was clicked
            if column == f"#{len(self.columns)}":
                values = self.tree.item(item_id, 'values')
                if values:
                    account_id = values[0]
                    account_name = values[1]
                    # Call the controller to handle the confirmation and deletion
                    self.controller.confirm_delete_account(account_id, account_name)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.controller.db.conn:
            for i, row in enumerate(self.controller.db.get_accounts()):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                # Append "🗑 Delete" to the row data for the Actions column
                display_row = list(row) + ["🗑 Delete"]
                self.tree.insert('', tk.END, values=display_row, tags=(tag,))

class NewAccountFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        """Builds the form based on the original layout."""
        # Main container with some padding from the edges
        container = tk.Frame(self, bg='white', padx=40, pady=20)
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure(1, weight=1)

        ttk.Label(container, text="Create New Account",
                  font=('Arial', 18, 'bold')).grid(row=0, column=0, columnspan=2, pady=(10, 25), sticky="w")

        # Define fields to build them programmatically or manually
        # 1. Internal Name
        ttk.Label(container, text="Account Name (Internal):").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_account_name = ttk.Entry(container)
        self.entry_account_name.grid(row=1, column=1, sticky="ew", pady=5, padx=(10, 0))

        # 2. CRA Name
        ttk.Label(container, text="Account Name (CRA):").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_account_name_cra = ttk.Entry(container)
        self.entry_account_name_cra.grid(row=2, column=1, sticky="ew", pady=5, padx=(10, 0))

        # 3. Type
        ttk.Label(container, text="Account Type:").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_account_type = ttk.Entry(container)
        self.entry_account_type.grid(row=3, column=1, sticky="ew", pady=5, padx=(10, 0))

        ttk.Separator(container, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky='ew', pady=15)

        # 4. Institution
        ttk.Label(container, text="Institution:").grid(row=5, column=0, sticky="w", pady=5)
        self.entry_institution = ttk.Entry(container)
        self.entry_institution.grid(row=5, column=1, sticky="ew", pady=5, padx=(10, 0))

        # 5. Account Number
        ttk.Label(container, text="Account Number:").grid(row=6, column=0, sticky="w", pady=5)
        self.entry_account_number = ttk.Entry(container)
        self.entry_account_number.grid(row=6, column=1, sticky="ew", pady=5, padx=(10, 0))

        ttk.Separator(container, orient='horizontal').grid(row=7, column=0, columnspan=2, sticky='ew', pady=15)

        # 6. Dates
        ttk.Label(container, text="Opening Date (YYYY-MM-DD):").grid(row=8, column=0, sticky="w", pady=5)
        self.entry_opening_date = ttk.Entry(container)
        self.entry_opening_date.grid(row=8, column=1, sticky="ew", pady=5, padx=(10, 0))

        ttk.Label(container, text="Close Date (Optional):").grid(row=9, column=0, sticky="w", pady=5)
        self.entry_close_date = ttk.Entry(container)
        self.entry_close_date.grid(row=9, column=1, sticky="ew", pady=5, padx=(10, 0))

        # 7. Notes
        ttk.Label(container, text="Notes:").grid(row=10, column=0, sticky="nw", pady=5)
        self.text_notes = tk.Text(container, height=4)
        self.text_notes.grid(row=10, column=1, sticky="ew", pady=5, padx=(10, 0))

        # Action Button
        ttk.Button(container, text="Save Account", command=self.save).grid(
            row=11, column=1, sticky="e", pady=20)

    def clear_form(self):
        """Resets the form to empty state."""
        self.entry_account_name.delete(0, tk.END)
        self.entry_account_name_cra.delete(0, tk.END)
        self.entry_account_type.delete(0, tk.END)
        self.entry_institution.delete(0, tk.END)
        self.entry_account_number.delete(0, tk.END)
        self.entry_opening_date.delete(0, tk.END)
        self.entry_close_date.delete(0, tk.END)
        self.text_notes.delete("1.0", tk.END)

    def save(self):
        """Collects data and passes it to the Controller."""
        # 1. Collect data from View widgets
        data = (
            self.entry_account_name.get().strip(),
            self.entry_account_name_cra.get().strip(),
            self.entry_account_type.get().strip(),
            self.entry_institution.get().strip(),
            self.entry_account_number.get().strip(),
            self.entry_opening_date.get().strip(),
            self.entry_close_date.get().strip(),
            self.text_notes.get("1.0", tk.END).strip()
        )

        # 2. Basic Validation: Internal name is required
        if not data[0]:
            messagebox.showwarning("Validation Error", "Account Name (Internal) is required.")
            return

        # 3. Hand off to Controller
        self.controller.handle_save_account(data)

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
            "Deposit": (100, 'e'),
            "Withdrawal": (100, 'e'),
            "Notes": (200, 'w')
        }

        for col, (width, anchor) in column_configs.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor)

        # Scrollbar
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        # Configure Tags
        self.tree.tag_configure('oddrow', background=ROW_COLOR_LIGHT)
        self.tree.tag_configure('evenrow', background=ROW_COLOR_DARK)

        # Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        vsb.grid(row=0, column=1, sticky='ns', pady=10)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.controller.db.conn:
            raw_data = self.controller.db.get_transactions()

            for i, row in enumerate(raw_data):
                # Unpack raw data from Model
                name, date, t_type, amount, notes = row

                # Split amount based on type
                formatted_amount = f"{amount:.2f}"
                deposit = formatted_amount if t_type == 'Deposit' else ""
                withdrawal = formatted_amount if t_type == 'Withdrawal' else ""

                # Determine tag for zebra striping
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'

                self.tree.insert('', tk.END,
                                 values=(name, date, deposit, withdrawal, notes),
                                 tags=(tag,))

class NewTransactionFrame(tk.Frame):
    # ... (This class remains unchanged from your snippet) ...
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
        # Implementation of saving logic
        pass

class WelcomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        """Creates a friendly welcome screen with instructions."""
        # Main container for centering content
        container = tk.Frame(self, bg='white')
        container.place(relx=0.5, rely=0.4, anchor='center')

        # Welcome Title
        title_label = tk.Label(
            container,
            text="Welcome to TFSAid",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#333333'
        )
        title_label.pack(pady=(0, 10))

        # Instructions
        instr_text = (
            "To get started, please use the 'File' menu either to:\n\n"
            "1. Open an existing database file (.db) or\n"
            "2. Create a new database file.                 "
        )
        instr_label = tk.Label(
            container,
            text=instr_text,
            font=('Arial', 12),
            bg='white',
            fg='#666666',
            justify='center'
        )
        instr_label.pack(pady=10)

        # Decorative separator
        line = tk.Frame(container, height=2, width=300, bg='#D1EAF0')
        line.pack(pady=20)

# ... You would add NewAccountFrame, RoomYearsListFrame, etc., similarly ...