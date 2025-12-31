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
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item_id = self.tree.identify_row(event.y)

            # Actions column check
            if column == f"#{len(self.columns)}":
                values = self.tree.item(item_id, 'values')
                acc_id, acc_name = values[0], values[1]

                # Simple text-based detection: 
                # If the user clicks on the left side of the cell, it's Edit.
                # Treeview doesn't give us the word, so we use the X coordinate within the cell.
                column_box = self.tree.bbox(item_id, column)
                click_x_in_cell = event.x - column_box[0]

                if click_x_in_cell < column_box[2] / 2:
                    # Clicked left half (Edit)
                    self.controller.prepare_edit_account(acc_id)
                else:
                    # Clicked right half (Delete)
                    self.controller.confirm_delete_account(acc_id, acc_name)

    def refresh(self):
        """Clears the current list and re-populates it from the database."""
        # 1. FIX: Clear ALL existing items in the Treeview first
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 2. FIX: Only use ONE loop and ensure there is an active connection
        if self.controller.db.conn:
            accounts = self.controller.db.get_accounts()

            for i, row in enumerate(accounts):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'

                # 3. FIX: Create a unified 'Edit | Delete' action for every row
                # row[0] is the ID, row[1] is the Account Name, etc.
                display_row = list(row) + ["Edit | Delete"]

                self.tree.insert('', tk.END, values=display_row, tags=(tag,))

class NewAccountFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller
        self.edit_id = None # Track if we are editing or adding
        self._is_loading_edit = False # Flag to prevent refresh from wiping edit data
        self._setup_ui()

    def refresh(self):
        """Standard refresh called by show_frame. Clears the form for 'New' mode."""
        # If we just called load_account_data, skip clearing this one time
        if self._is_loading_edit:
            self._is_loading_edit = False
            return

        self.clear_form()

    def load_account_data(self, account_id, data):
        """Pre-fills the form with existing account data."""
        self.clear_form() # This sets _is_loading_edit to False initially
        self.edit_id = account_id

        # IMPORTANT: Set this flag to True so the upcoming refresh() doesn't wipe this data
        self._is_loading_edit = True

        # data index matches your SELECT * query order from database_manager.py
        # [0:id, 1:Name, 2:CRA, 3:Type, 4:Inst, 5:Num, 6:Open, 7:Close, 8:Notes]
        self.entry_account_name.insert(0, data[1])
        self.entry_account_name_cra.insert(0, data[2])
        self.entry_account_type.insert(0, data[3])
        self.entry_institution.insert(0, data[4])
        self.entry_account_number.insert(0, data[5])
        self.entry_opening_date.insert(0, data[6])

        # Load Close Date (index 7) if it exists
        if data[7]:
            self.entry_close_date.insert(0, data[7])

        self.text_notes.insert("1.0", data[8] if data[8] else "")

        # Change button text to reflect Edit Mode
        self.save_btn.config(text="Update Account")

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
        self.save_btn = ttk.Button(container, text="Save Account", command=self.save)
        self.save_btn.grid(row=11, column=1, sticky="e", pady=20)

    def clear_form(self):
        """Resets the form to empty state and 'New' mode."""
        self.edit_id = None
        self._is_loading_edit = False
        self.save_btn.config(text="Save Account")

        # Clear all input widgets
        for widget in [self.entry_account_name, self.entry_account_name_cra,
                       self.entry_account_type, self.entry_institution,
                       self.entry_account_number, self.entry_opening_date,
                       self.entry_close_date]:
            widget.delete(0, tk.END)
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
        if self.edit_id:
            # Tell controller to update
            self.controller.handle_update_account(self.edit_id, data)
        else:
            # Tell controller to save new
            self.controller.handle_save_account(data)

class TransactionsListFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        # Added 'ID' at start and 'Actions' at the end
        self.columns = ("ID", "Account", "Date", "Deposit", "Withdrawal", "Notes", "Actions")
        self.tree = ttk.Treeview(self, columns=self.columns, show='headings')

        column_configs = {
            "ID": (0, 'center'),         # Will be hidden
            "Account": (150, 'w'),
            "Date": (100, 'center'),
            "Deposit": (100, 'e'),
            "Withdrawal": (100, 'e'),
            "Notes": (200, 'w'),
            "Actions": (80, 'center')    # New Actions column
        }

        for col, (width, anchor) in column_configs.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor)

        # Hide ID column
        self.tree.column("ID", width=0, stretch=tk.NO)
        # Bind click event for the Delete action
        self.tree.bind("<Button-1>", self._on_click)

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.tag_configure('oddrow', background=ROW_COLOR_LIGHT)
        self.tree.tag_configure('evenrow', background=ROW_COLOR_DARK)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        vsb.grid(row=0, column=1, sticky='ns', pady=10)

    def _on_click(self, event):
        """Identifies if Edit or Delete was clicked based on cell horizontal position."""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item_id = self.tree.identify_row(event.y)
            values = self.tree.item(item_id, 'values')

            if not values:
                return

            # Verify we are clicking in the 'Actions' column
            if self.tree.heading(column, "text") == "Actions":
                # Get the cell's bounding box: (x, y, width, height)
                bbox = self.tree.bbox(item_id, column)
                if not bbox:
                    return

                # Calculate where inside the cell the click happened
                click_x_in_cell = event.x - bbox[0]
                cell_width = bbox[2]

                trans_id = values[0]
                date = values[2]
                # Determine amount for the prompt: check Deposit (index 3) then Withdrawal (index 4)
                amount = values[3] if values[3] != "" else values[4]

                # Use the midpoint (width/2) to separate Edit and Delete
                if click_x_in_cell < (cell_width / 2):
                    self.controller.prepare_edit_transaction(trans_id)
                else:
                    self.controller.confirm_delete_transaction(trans_id, date, amount)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.controller.db.conn:
            transactions = self.controller.db.get_transactions()
            for i, row in enumerate(transactions):
                t_id, name, date, t_type, amount, notes = row

                dep = f"{amount:.2f}" if t_type == 'Deposit' else ""
                wd = f"{amount:.2f}" if t_type == 'Withdrawal' else ""
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'

                # Ensure "Edit | Delete" is the 7th value (index 6)
                self.tree.insert('', tk.END,
                                 values=(t_id, name, date, dep, wd, notes, "Edit | Delete"),
                                 tags=(tag,))

class NewTransactionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller
        self.edit_id = None
        self._is_loading_edit = False
        self.account_map = {} # To map Name -> ID for the combobox
        self._setup_ui()

    def _setup_ui(self):
        container = tk.Frame(self, bg='white', padx=20, pady=20)
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure(1, weight=1)

        self.lbl_title = tk.Label(container, text="Add New Transaction", font=('Arial', 16, 'bold'), bg='white')
        self.lbl_title.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 1. Account Dropdown
        tk.Label(container, text="Select Account:", bg='white').grid(row=1, column=0, sticky="w", pady=5)
        self.combo_account = ttk.Combobox(container, state="readonly")
        self.combo_account.grid(row=1, column=1, sticky="ew", padx=10)

        # 2. Date
        tk.Label(container, text="Date (YYYY-MM-DD):", bg='white').grid(row=2, column=0, sticky="w", pady=5)
        self.entry_trans_date = ttk.Entry(container)
        self.entry_trans_date.grid(row=2, column=1, sticky="ew", padx=10)

        # 3. Transaction Type (Radio Buttons)
        tk.Label(container, text="Transaction Type:", bg='white').grid(row=3, column=0, sticky="w", pady=5)
        self.trans_type_var = tk.StringVar(value="Deposit")

        radio_frame = tk.Frame(container, bg='white')
        radio_frame.grid(row=3, column=1, sticky="w", padx=10)

        tk.Radiobutton(radio_frame, text="Deposit", variable=self.trans_type_var,
                       value="Deposit", bg='white').pack(side="left")
        tk.Radiobutton(radio_frame, text="Withdrawal", variable=self.trans_type_var,
                       value="Withdrawal", bg='white').pack(side="left", padx=15)

        # 4. Amount
        tk.Label(container, text="Amount:", bg='white').grid(row=4, column=0, sticky="w", pady=5)
        self.entry_amount = ttk.Entry(container)
        self.entry_amount.grid(row=4, column=1, sticky="ew", padx=10)

        # 5. Notes
        tk.Label(container, text="Notes:", bg='white').grid(row=5, column=0, sticky="nw", pady=5)
        self.text_trans_notes = tk.Text(container, width=40, height=4)
        self.text_trans_notes.grid(row=5, column=1, sticky="ew", padx=10)

        self.save_btn = ttk.Button(container, text="Save Transaction", command=self.save)
        self.save_btn.grid(row=6, column=1, sticky="e", pady=20, padx=10)

    def refresh(self):
        if self._is_loading_edit:
            self._is_loading_edit = False
            return
        self.clear_form()
        # Populate account dropdown
        accounts = self.controller.db.get_accounts()
        self.account_map = {acc[1]: acc[0] for acc in accounts}
        self.combo_account['values'] = list(self.account_map.keys())

    def load_transaction_data(self, trans_id, data, accounts):
        """Pre-fills form for editing and sets the edit flag."""
        self.clear_form()
        self.edit_id = trans_id
        self._is_loading_edit = True # Prevents refresh() from clearing the form immediately

        # data: (id, Account_id, TransDate, TransType, Amount, Notes)
        self.account_map = {acc[1]: acc[0] for acc in accounts}
        self.combo_account['values'] = list(self.account_map.keys())

        # Select Account
        for name, acc_id in self.account_map.items():
            if acc_id == data[1]:
                self.combo_account.set(name)
                break

        self.entry_trans_date.insert(0, data[2])
        self.trans_type_var.set(data[3]) # Updates Radio Buttons
        self.entry_amount.insert(0, str(data[4]))
        self.text_trans_notes.insert("1.0", data[5] if data[5] else "")

        self.lbl_title.config(text="Edit Transaction")
        self.save_btn.config(text="Update Transaction")

    def clear_form(self):
        self.edit_id = None
        self.lbl_title.config(text="Add New Transaction")
        self.save_btn.config(text="Save Transaction")
        self.combo_account.set('')
        self.entry_trans_date.delete(0, tk.END)
        self.trans_type_var.set("Deposit")
        self.entry_amount.delete(0, tk.END)
        self.text_trans_notes.delete("1.0", tk.END)

    def save(self):
        acc_name = self.combo_account.get()
        if not acc_name:
            messagebox.showwarning("Input Error", "Please select an account.")
            return

        self.controller.handle_save_transaction(
            self.edit_id,
            self.account_map[acc_name],
            self.entry_trans_date.get(),
            self.trans_type_var.get(),
            float(self.entry_amount.get() or 0),
            self.text_trans_notes.get("1.0", tk.END).strip()
        )

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

class CRAReportFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        container = tk.Frame(self, bg='white', padx=20, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="TFSA Report (CRA Format)",
                 font=('Arial', 18, 'bold'), bg='white').pack(pady=(0, 10))

        # UPDATED: Removed Notes, Added Net Change to header/columns
        # We use 'Net Change' as the 5th column header
        self.columns = ("Account Name in CRA", "Date", "Deposit", "Withdrawal", "Net Change")
        self.tree = ttk.Treeview(container, columns=self.columns, show='headings', height=25)

        column_configs = {
            "Account Name in CRA": 250,
            "Date": 120,
            "Deposit": 150,
            "Withdrawal": 150,
            "Net Change": 150
        }

        for col, width in column_configs.items():
            self.tree.heading(col, text=col)
            # Center the financial numbers
            anchor = 'center' if col in ["Deposit", "Withdrawal", "Net Change"] else 'w'
            self.tree.column(col, width=width, anchor=anchor)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Visual style for summary rows
        self.tree.tag_configure('summary', background='#e8f4f8', font=('Arial', 10, 'bold'))
        self.tree.tag_configure('grand_total', background='#d1e7dd', font=('Arial', 11, 'bold'))

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.controller.db.conn:
            return

        data = self.controller.db.get_cra_report_data()
        if not data:
            return

        current_account = None
        acc_dep_total = 0.0
        acc_wd_total = 0.0

        grand_dep = 0.0
        grand_wd = 0.0

        for row in data:
            cra_name, date, t_type, amount, notes = row

            # Grouping logic: Detect when account name changes
            if current_account is not None and cra_name != current_account:
                self._insert_summary(current_account, acc_dep_total, acc_wd_total)
                acc_dep_total = 0.0
                acc_wd_total = 0.0

            current_account = cra_name

            dep_str = ""
            wd_str = ""

            if t_type == "Deposit":
                dep_str = f"{amount:.2f}"
                acc_dep_total += amount
                grand_dep += amount
            else:
                wd_str = f"{amount:.2f}"
                acc_wd_total += amount
                grand_wd += amount

            self.tree.insert('', tk.END, values=(cra_name, date, dep_str, wd_str, ""))

        # Final account summary
        if current_account:
            self._insert_summary(current_account, acc_dep_total, acc_wd_total)

        # Grand Total for the entire report
        net_grand = grand_dep - grand_wd
        self.tree.insert('', tk.END, values=("", "", "", "", ""), tags=()) # Spacer
        self.tree.insert('', tk.END, values=(
            "REPORT TOTALS",
            "All Accounts",
            f"{grand_dep:.2f}",
            f"{grand_wd:.2f}",
            f"{net_grand:.2f}"
        ), tags=('grand_total',))

    def _insert_summary(self, name, dep_total, wd_total):
        net_change = dep_total - wd_total

        # Insert Summary Row
        self.tree.insert('', tk.END, values=(
            f"TOTALS: {name}",
            "",
            f"{dep_total:.2f}",
            f"{wd_total:.2f}",
            f"{net_change:.2f}"
        ), tags=('summary',))

        # Empty row for visual spacing between account groups
        self.tree.insert('', tk.END, values=("", "", "", "", ""))

# ... You would add RoomYearsListFrame, etc., similarly ...
