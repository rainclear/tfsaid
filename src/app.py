import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import os

# --- Configuration Constants ---
# Define a custom color for the sidebar (Hex code for light blue)
SIDEBAR_COLOR = "#D1EAF0"
# Define a custom color for the content area (Hex code for white/light gray)
CONTENT_COLOR = "#F5F5F5"

SIDEBAR_WIDTH = 180

def donothing():
    pass

class TFSAid(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("TFSAid - Help Tracking TFSA Room")
        self.geometry("1500x750")
        self.minsize(1500, 750)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Dictionary to hold the content frames (for easy swapping)
        self.frames = {}

        # Lists to hold the buttons/widgets that need to be disabled/enabled
        self.sidebar_buttons = []

        # Dictionary to map Account Name -> Account ID
        self.account_map = {}

        # empty database
        self.conn = None

        self.__create_menubar()
        self.__create_main_window()

        # Initial State: No file is open
        self.set_ui_state(False)

    def __create_menubar(self):
        self.menubar = tk.Menu(self)
        self._setup_filemenu()
        self._setup_helpmenu()
        self.config(menu=self.menubar)

    def _setup_filemenu(self):
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_database)
        self.file_menu.add_command(label="Open", command=self.open_database)
        self.file_menu.add_command(label="Save as...", command=donothing)
        self.file_menu.add_command(label="Export to csv file...", command=donothing)
        self.file_menu.add_command(label="Close", command=self.close_database, state=tk.DISABLED)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=lambda: (self.close_database(), self.quit()))

    def _setup_helpmenu(self):
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="Help", command=donothing)
        self.help_menu.add_separator()
        self.help_menu.add_command(label="About", command=donothing)

    def __create_main_window(self):
        self._setup_layout()
        self._setup_sidebar()
        self._setup_content_frames()
        
    def _setup_layout(self):
        # Configure the grid to make the right content area expandable
        # Column 0 (Sidebar) has weight 0 (fixed size)
        # Column 1 (Content) has weight 1 (takes up all extra space)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        ## --- Left Sidebar Frame ---
        # Frame for the sidebar (Column 0)
        self.sidebar_frame = tk.Frame(self, 
                             width=180,  # Fixed width for the sidebar
                             bg=SIDEBAR_COLOR)
        # sticky="nsew" ensures it expands to fill its grid cell (top to bottom)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew") 
        # Prevent the grid from shrinking the sidebar frame width
        self.sidebar_frame.grid_propagate(False)

        ## --- Right Content Area Frame ---
        # Frame for the content area (Column 1)
        self.content_area = tk.Frame(self, bg=CONTENT_COLOR)
        # sticky="nsew" ensures it fills the entire right column and expands/shrinks with the window
        self.content_area.grid(row=0, column=1, sticky="nsew")

    def _setup_sidebar(self):
        """Creates and places the buttons in the sidebar, storing them."""
        ttk.Label(self.sidebar_frame, text="Navigation", font=('Arial', 12, 'bold'), 
                  background=SIDEBAR_COLOR).pack(pady=(20, 10))

        # --- Sidebar Buttons and Commands ---
        # Create buttons and save them to the list self.sidebar_buttons
        btn_accounts = ttk.Button(self.sidebar_frame, text="Accounts", 
                                  command=self.show_accounts_view)
        btn_accounts.pack(fill='x', padx=10, pady=5)
        self.sidebar_buttons.append(btn_accounts)

        btn_transactions = ttk.Button(self.sidebar_frame, text="Transactions", 
                                      command=self.show_transactions_view)
        btn_transactions.pack(fill='x', padx=10, pady=5)
        self.sidebar_buttons.append(btn_transactions)

        btn_room_year = ttk.Button(self.sidebar_frame, text="Room by Year",
                                      command=self.show_room_years_view)
        btn_room_year.pack(fill='x', padx=10, pady=5)
        self.sidebar_buttons.append(btn_room_year)

        btn_room_checking = ttk.Button(self.sidebar_frame, text="Room Checking")
        btn_room_checking.pack(fill='x', padx=10, pady=5)
        self.sidebar_buttons.append(btn_room_checking)

        btn_cra_reports = ttk.Button(self.sidebar_frame, text="CRA Reports")
        btn_cra_reports.pack(fill='x', padx=10, pady=5)
        self.sidebar_buttons.append(btn_cra_reports)

        btn_new_account = ttk.Button(self.sidebar_frame, text="New Account", 
                                     command=lambda: self.show_frame("NewAccountForm"))
        btn_new_account.pack(fill='x', padx=10, pady=5)
        self.sidebar_buttons.append(btn_new_account)

        btn_new_transaction = ttk.Button(self.sidebar_frame, text="New Transaction", 
                                         command=self.show_new_transaction_view)
        btn_new_transaction.pack(fill='x', padx=10, pady=5)
        self.sidebar_buttons.append(btn_new_transaction)

        btn_new_room_year = ttk.Button(self.sidebar_frame, text="New Room/Year",
                                       command=lambda: self.show_frame("NewRoomYearForm"))
        btn_new_room_year.pack(fill='x', padx=10, pady=5)
        self.sidebar_buttons.append(btn_new_room_year)

    def show_accounts_view(self):
        """Loads data into the Treeview and then raises the AccountsList frame."""
        if self.conn:
            self.load_accounts_list()
        self.show_frame("AccountsList")

    def show_transactions_view(self):
        """Loads data into the Transactions Treeview and raises the frame."""
        if self.conn:
            self.load_transactions_list()
        self.show_frame("TransactionsList")

    def show_room_years_view(self):
        """Loads data into the Room by Years Treeview and raises the frame."""
        if self.conn:
            self.load_room_year_list()
        self.show_frame("RoomYearsList")

    def _setup_content_frames(self):
        """Creates all dynamic content frames and places them on top of each other."""

        # --- 1. New Account Form Frame ---
        new_account_frame = tk.Frame(self.content_area, bg='white', padx=20, pady=20, bd=1, relief="solid")
        self.frames["NewAccountForm"] = new_account_frame
        self._create_new_account_form(new_account_frame)

        # --- 2. Accounts List Frame ---
        accounts_frame = tk.Frame(self.content_area, bg='white')
        self.frames["AccountsList"] = accounts_frame
        self._create_accounts_list_view(accounts_frame) # Renamed method

        # --- 3. New Transaction Form Frame ---
        new_trans_frame = tk.Frame(self.content_area, bg='white', padx=20, pady=20, bd=1, relief="solid")
        self.frames["NewTransactionForm"] = new_trans_frame
        self._create_new_transaction_form(new_trans_frame)

        # --- 4. Transactions List Frame ---
        transactions_frame = tk.Frame(self.content_area, bg='white')
        self.frames["TransactionsList"] = transactions_frame
        self._create_transactions_list_view(transactions_frame)

        # --- 4. Room Year List Frame ---
        room_years_frame = tk.Frame(self.content_area, bg='white')
        self.frames["RoomYearsList"] = room_years_frame
        self._create_room_years_list_view(room_years_frame)

        # --- 4. New Room Year Frame ---
        room_form_frame = tk.Frame(self.content_area, bg='white', padx=20, pady=20, bd=1, relief="solid")
        self.frames["NewRoomYearForm"] = room_form_frame
        self._create_new_room_year_form(room_form_frame)

        # --- 5. Default No File Open Frame ---
        default_frame = tk.Frame(self.content_area, bg=CONTENT_COLOR)
        self.frames["DefaultView"] = default_frame
        self._create_default_view(default_frame)

        # --- Stacking the Frames ---
        # Place ALL content frames in the exact same spot (row 0, column 0)
        # They will stack on top of each other, and tkraise() will bring one to the front.
        for name, frame in self.frames.items():
            frame.grid(row=0, column=0, sticky="nsew")

    def _create_accounts_list_view(self, parent_frame):
        """Creates the Treeview widget for displaying account data."""
        
        # Define columns based on your SQL schema (only show relevant ones for a list)
        columns = ("#", "Name", "Type", "Institution", "Number", "OpeningDate")
        
        # Create the Treeview
        self.accounts_tree = ttk.Treeview(parent_frame, columns=columns, show='headings')
        
        # Configure Headings and Column Widths
        self.accounts_tree.heading("#", text="ID")
        self.accounts_tree.column("#", width=50, stretch=tk.NO, anchor='center')
        
        self.accounts_tree.heading("Name", text="Account Name")
        self.accounts_tree.column("Name", anchor='w')
        
        self.accounts_tree.heading("Type", text="Type")
        self.accounts_tree.column("Type", width=120, anchor='center')
        
        self.accounts_tree.heading("Institution", text="Institution")
        self.accounts_tree.column("Institution", width=150, anchor='w')
        
        self.accounts_tree.heading("Number", text="Account #")
        self.accounts_tree.column("Number", width=100, anchor='w')
        
        self.accounts_tree.heading("OpeningDate", text="Opened")
        self.accounts_tree.column("OpeningDate", width=100, anchor='center')

        # Add Scrollbar
        vsb = ttk.Scrollbar(parent_frame, orient="vertical", command=self.accounts_tree.yview)
        self.accounts_tree.configure(yscrollcommand=vsb.set)
        
        # Place Treeview and Scrollbar in the parent frame using Grid
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)
        
        self.accounts_tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        vsb.grid(row=0, column=1, sticky='ns', pady=10)            

    def _create_new_account_form(self, parent_frame):
        """
        Populates the New Account form frame with widgets based on the Accounts table schema.
        """
        
        # Ensure the form's content frame is expandable in column 1 for entries
        parent_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(parent_frame, text="Create New Account", 
                  font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(10, 25))

        row_index = 1
        
        # --- Core Details ---

        # 1. Account Name
        ttk.Label(parent_frame, text="Account Name (Internal):").grid(row=row_index, column=0, sticky="w", pady=5, padx=10)
        self.entry_account_name = ttk.Entry(parent_frame, width=40)
        self.entry_account_name.grid(row=row_index, column=1, sticky="ew", pady=5, padx=10)
        row_index += 1

        # 2. CRA Account Name (for compliance/tax forms)
        ttk.Label(parent_frame, text="Account Name (CRA):").grid(row=row_index, column=0, sticky="w", pady=5, padx=10)
        self.entry_account_name_cra = ttk.Entry(parent_frame, width=40)
        self.entry_account_name_cra.grid(row=row_index, column=1, sticky="ew", pady=5, padx=10)
        row_index += 1

        # 3. Account Type (Consider a Combobox later for predefined types)
        ttk.Label(parent_frame, text="Account Type:").grid(row=row_index, column=0, sticky="w", pady=5, padx=10)
        self.entry_account_type = ttk.Entry(parent_frame, width=40)
        self.entry_account_type.grid(row=row_index, column=1, sticky="ew", pady=5, padx=10)
        row_index += 1
        
        # Separator for clarity
        ttk.Separator(parent_frame, orient='horizontal').grid(row=row_index, column=0, columnspan=2, sticky='ew', pady=15)
        row_index += 1

        # --- Institution Details ---

        # 4. Institution Name
        ttk.Label(parent_frame, text="Institution:").grid(row=row_index, column=0, sticky="w", pady=5, padx=10)
        self.entry_institution = ttk.Entry(parent_frame, width=40)
        self.entry_institution.grid(row=row_index, column=1, sticky="ew", pady=5, padx=10)
        row_index += 1

        # 5. Account Number
        ttk.Label(parent_frame, text="Account Number:").grid(row=row_index, column=0, sticky="w", pady=5, padx=10)
        self.entry_account_number = ttk.Entry(parent_frame, width=40)
        self.entry_account_number.grid(row=row_index, column=1, sticky="ew", pady=5, padx=10)
        row_index += 1
        
        # Separator
        ttk.Separator(parent_frame, orient='horizontal').grid(row=row_index, column=0, columnspan=2, sticky='ew', pady=15)
        row_index += 1

        # --- Date Fields ---

        # 6. Opening Date (You might want a calendar picker for this later)
        ttk.Label(parent_frame, text="Opening Date (YYYY-MM-DD):").grid(row=row_index, column=0, sticky="w", pady=5, padx=10)
        self.entry_opening_date = ttk.Entry(parent_frame, width=40)
        self.entry_opening_date.grid(row=row_index, column=1, sticky="ew", pady=5, padx=10)
        row_index += 1
        
        # 7. Close Date (Optional)
        ttk.Label(parent_frame, text="Close Date (Optional):").grid(row=row_index, column=0, sticky="w", pady=5, padx=10)
        self.entry_close_date = ttk.Entry(parent_frame, width=40)
        self.entry_close_date.grid(row=row_index, column=1, sticky="ew", pady=5, padx=10)
        row_index += 1

        # --- Notes ---
        
        # 8. Notes (Use a Text widget for multi-line input)
        ttk.Label(parent_frame, text="Notes:").grid(row=row_index, column=0, sticky="nw", pady=5, padx=10)
        self.text_notes = tk.Text(parent_frame, width=40, height=4)
        self.text_notes.grid(row=row_index, column=1, sticky="ew", pady=5, padx=10)
        row_index += 1
        
        # --- Action Button ---

        ttk.Button(parent_frame, text="Save Account", command=self.save_account_data).grid(
            row=row_index, column=1, sticky="e", pady=(20, 10), padx=10)
        
    def clear_new_account_form(self):
        """Helper to clear all form fields."""
        self.entry_account_name.delete(0, tk.END)
        self.entry_account_name_cra.delete(0, tk.END)
        self.entry_account_type.delete(0, tk.END)
        self.entry_institution.delete(0, tk.END)
        self.entry_account_number.delete(0, tk.END)
        self.entry_opening_date.delete(0, tk.END)
        self.entry_close_date.delete(0, tk.END)
        self.text_notes.delete("1.0", tk.END) # Delete from start to end for Text widgets        

    def _create_transactions_list_view(self, parent_frame):
        """Creates the Treeview for Transactions with separate Deposit/Withdrawal columns."""
        
        columns = ("ID", "Account", "Date", "Deposit", "Withdrawal", "Notes")
        self.trans_tree = ttk.Treeview(parent_frame, columns=columns, show='headings')

        # Column configuration
        column_configs = {
            "ID": (50, 'center'),
            "Account": (150, 'w'),
            "Date": (100, 'center'),
            "Deposit": (100, 'e'),    # Align numbers to the right (East)
            "Withdrawal": (100, 'e'), # Align numbers to the right (East)
            "Notes": (200, 'w')
        }

        for col, (width, anchor) in column_configs.items():
            self.trans_tree.heading(col, text=col)
            self.trans_tree.column(col, width=width, anchor=anchor)

        # Scrollbar
        vsb = ttk.Scrollbar(parent_frame, orient="vertical", command=self.trans_tree.yview)
        self.trans_tree.configure(yscrollcommand=vsb.set)

        # Layout
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)
        self.trans_tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        vsb.grid(row=0, column=1, sticky='ns', pady=10)

    def _create_new_transaction_form(self, parent_frame):
        """Creates the form for entering new transactions."""
        parent_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(parent_frame, text="Add New Transaction", 
                font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 1. Account Dropdown
        ttk.Label(parent_frame, text="Select Account:").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_account = ttk.Combobox(parent_frame, state="readonly")
        self.combo_account.grid(row=1, column=1, sticky="ew", padx=10)

        # 2. Date
        ttk.Label(parent_frame, text="Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_trans_date = ttk.Entry(parent_frame)
        self.entry_trans_date.grid(row=2, column=1, sticky="ew", padx=10)

        # 3. Transaction Type (Radio Buttons)
        ttk.Label(parent_frame, text="Transaction Type:").grid(row=3, column=0, sticky="w", pady=5)
        self.trans_type_var = tk.StringVar(value="Deposit") # Default value
        
        radio_frame = tk.Frame(parent_frame, bg='white')
        radio_frame.grid(row=3, column=1, sticky="w", padx=10)
        
        tk.Radiobutton(radio_frame, text="Deposit", variable=self.trans_type_var, 
                    value="Deposit", bg='white').pack(side="left")
        tk.Radiobutton(radio_frame, text="Withdrawal", variable=self.trans_type_var, 
                    value="Withdrawal", bg='white').pack(side="left", padx=10)

        # 4. Amount
        ttk.Label(parent_frame, text="Amount:").grid(row=4, column=0, sticky="w", pady=5)
        self.entry_amount = ttk.Entry(parent_frame)
        self.entry_amount.grid(row=4, column=1, sticky="ew", padx=10)

        # 5. Notes
        ttk.Label(parent_frame, text="Notes:").grid(row=5, column=0, sticky="nw", pady=5)
        self.text_trans_notes = tk.Text(parent_frame, width=40, height=4)
        self.text_trans_notes.grid(row=5, column=1, sticky="ew", padx=10)

        # Save Button
        ttk.Button(parent_frame, text="Save Transaction", 
                command=self.save_transaction_data).grid(row=6, column=1, sticky="e", pady=20, padx=10)
        
    def show_new_transaction_view(self):
        """Refreshes account list and then shows the form."""
        if self.conn:
            self.refresh_account_dropdown()
        self.show_frame("NewTransactionForm")

    def refresh_account_dropdown(self):
        """Fetches account names and IDs to populate the Combobox."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, AccountName FROM Accounts ORDER BY AccountName")
            rows = cursor.fetchall()
            
            # Build the map: {"Checking": 1, "Savings": 2}
            self.account_map = {name: acc_id for acc_id, name in rows}
            
            # Update Combobox values
            self.combo_account['values'] = list(self.account_map.keys())
            
            if self.account_map:
                self.combo_account.current(0) # Select first item by default
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not load accounts: {e}")        

    def _create_room_years_list_view(self, parent_frame):
        """Creates the Treeview for Room by Years."""
        
        columns = ("Year", "NewRoom")
        self.room_years_tree = ttk.Treeview(parent_frame, columns=columns, show='headings')

        self.room_years_tree.heading("Year", text="Year")
        self.room_years_tree.column("Year", width=100, anchor='center')

        self.room_years_tree.heading("NewRoom", text="New Room")
        self.room_years_tree.column("NewRoom", width=100, anchor='center')

        # Scrollbar
        vsb = ttk.Scrollbar(parent_frame, orient="vertical", command=self.room_years_tree.yview)
        self.room_years_tree.configure(yscrollcommand=vsb.set)

        # Layout
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)
        self.room_years_tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        vsb.grid(row=0, column=1, sticky='ns', pady=10)

    def _create_new_room_year_form(self, parent_frame):
        """Creates the form to input New Room per Year data."""
        parent_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(parent_frame, text="Add New Room Per Year",
                font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 1. Year Entry (User only types YYYY)
        ttk.Label(parent_frame, text="Year (YYYY):").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_room_year = ttk.Entry(parent_frame)
        self.entry_room_year.grid(row=1, column=1, sticky="ew", padx=10)

        # 2. New Room Amount
        ttk.Label(parent_frame, text="New Room Amount:").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_room_amount = ttk.Entry(parent_frame)
        self.entry_room_amount.grid(row=2, column=1, sticky="ew", padx=10)

        # Save Button
        ttk.Button(parent_frame, text="Save Record",
                command=self.save_new_room_year_data).grid(row=3, column=1, sticky="e", pady=20, padx=10)

    def _create_default_view(self, parent_frame):
        """Creates the content for when no database is open."""
        ttk.Label(parent_frame, text="Please create a new database file or open an existing one.", 
                  font=('Arial', 16, 'bold'), background=CONTENT_COLOR, 
                  foreground='#444').pack(pady=100, padx=20)
        ttk.Label(parent_frame, text="Use File -> New or File -> Open in the menu bar.", 
                  font=('Arial', 12), background=CONTENT_COLOR).pack(pady=10)

    def show_frame(self, frame_name):
        """
        The critical function: Brings the requested frame to the top.
        """
        frame = self.frames.get(frame_name)
        if frame:
            frame.tkraise()
            print(f"Switched view to: {frame_name}")

    def set_ui_state(self, db_is_open):
        """
        Toggles the state of sidebar buttons and displays the appropriate content frame.
        :param db_is_open: Boolean, True if a DB connection is active.
        """
        # 1. Toggle Sidebar Buttons
        state = tk.NORMAL if db_is_open else tk.DISABLED
        for button in self.sidebar_buttons:
            button.config(state=state)
        
        # 2. Toggle Content View
        if db_is_open:
            # If DB is open, switch to a useful view (e.g., New Account form)
            self.show_frame("AccountsList")
            self.show_accounts_view()
        else:
            # If DB is closed, show the instructional message
            self.show_frame("DefaultView")

    # --- NEW: Database Management Functions ---

    def new_database(self):
        """
        Pops up the 'Save As' file dialog, creates a new database file,
        and initializes the schema using initdb.sql.
        """
        
        # 1. Determine the Default Path
        # os.getcwd() gets the current working directory (where the script is executed from)
        default_dir = os.getcwd()
        
        # 2. Open the File Dialog with the default path
        db_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
            title="Create New TFSAid File",
            initialdir=default_dir  # <-- This sets the starting folder
        )
        
        if not db_path:
            # User cancelled the dialog
            return

        try:
            # 3. CLOSE ANY EXISTING CONNECTION
            # The self.close_database() function handles checking if self.conn is set (open)
            # and closes it safely, resetting the UI state to 'closed'.
            self.close_database()

            # 3. Initialize the Database Schema
            self._initialize_database(db_path)

            # 4. Initialize the database schema and set self.conn
            self._initialize_database(db_path)            
            
            # 5. Success Feedback and UI State Update
            self.set_ui_state(True)

            self.current_db_path = db_path
            self.title(f"TFSAid App Layout - [{os.path.basename(db_path)}]")
            self.file_menu.entryconfig("Close", state=tk.NORMAL) 
            messagebox.showinfo("Success", f"New database created and initialized at:\n{db_path}")
            
        except FileNotFoundError:
            messagebox.showerror("Error", "initdb.sql script not found! Database schema not created.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred during DB creation: {e}")

    def _initialize_database(self, db_path):
        """
        Connects to the database and executes the schema creation script.
        """
        # Read the SQL script content
        with open("./src/sql/initdb.sql", 'r') as f:
            sql_script = f.read()

        # Connect to the database (creates the file if it doesn't exist)
        self.conn = sqlite3.connect(db_path)
        cursor = self.conn.cursor()
        
        # Execute the script (executes all commands in the file)
        cursor.executescript(sql_script)
        
        # Commit changes and close the connection
        self.conn.commit()
        # self.conn.close() keep db connection active

    # --- NEW FUNCTION: open_database(self) ---
    def open_database(self):
        """
        Pops up the 'Open File' dialog, connects to an existing SQLite file, 
        and updates the application state.
        """
        
        default_dir = os.getcwd()
        
        # 1. Open the File Dialog to select an existing file
        db_path = filedialog.askopenfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
            title="Open Existing TFSAid File",
            initialdir=default_dir
        )

        if not db_path:
            # User cancelled the dialog
            return

        try:
            # 2. Close any existing connection first (safety measure)
            self.close_database()

            # 3. Establish connection to the existing file
            self.conn = sqlite3.connect(db_path)
            
            # 4. Success Feedback and UI State Update
            self.set_ui_state(True)
            self.current_db_path = db_path
            self.title(f"TFSAid App Layout - [{os.path.basename(db_path)}]")
            self.file_menu.entryconfig("Close", state=tk.NORMAL)
            messagebox.showinfo("Success", f"Database successfully opened:\n{db_path}")

        except sqlite3.Error as e:
            # This handles errors like permission issues or file corruption
            messagebox.showerror("Database Error", f"Could not open database file: {e}")
            # Ensure the state is reset if connection fails
            self.conn = None
            self.set_ui_state(False)

    def close_database(self):
        """
        NEW FUNCTION: Closes the persistent database connection if it is open.
        Resets state to reflect no open file.
        """
        if self.conn:
            try:
                self.conn.close()
                self.conn = None
                self.current_db_path = None

                # Update UI State to reflect closed DB
                self.set_ui_state(False) 

                self.title("TFSAid App Layout")
                self.file_menu.entryconfig("Close", state=tk.DISABLED)
                print("Database connection successfully closed.")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Could not close connection: {e}")
        else:
            print("No active database connection to close.")

    def save_account_data(self):
        """
        Reads data from the form and inserts a new account record into the database.
        """
        if not self.conn:
            messagebox.showerror("Error", "No database file is currently open.")
            return

        # 1. Retrieve data from entry widgets
        account_data = (
            self.entry_account_name.get().strip(),
            self.entry_account_name_cra.get().strip(),
            self.entry_account_type.get().strip(),
            self.entry_institution.get().strip(),
            self.entry_account_number.get().strip(),
            self.entry_opening_date.get().strip(),
            self.entry_close_date.get().strip(),
            self.text_notes.get("1.0", tk.END).strip() # Use "1.0" to tk.END for Text widgets
        )

        # Basic Validation (Check required fields)
        if not account_data[0] or not account_data[1]:
            messagebox.showwarning("Input Error", "Account Name (Internal) and Account Name (CRA) are required.")
            return

        # 2. SQL Execution
        sql = """
        INSERT INTO Accounts 
        (AccountName, AccountNameCRA, AccountType, Institution, AccountNumber, OpeningDate, CloseDate, Notes) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, account_data)
            self.conn.commit()
            
            messagebox.showinfo("Success", f"Account '{account_data[0]}' saved successfully.")
            
            # Optional: Clear the form after successful submission
            self.clear_new_account_form()
            
        except sqlite3.IntegrityError as e:
            # Handles UNIQUE constraints (e.g., if AccountName already exists)
            messagebox.showerror("Database Error", f"Failed to save account (Integrity Error): {e}. Check for duplicate names.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save account: {e}")

    # --- Database Query and Treeview Population ---
    def load_accounts_list(self):
        """
        Fetches all accounts from the database and displays them in the Treeview.
        """
        if not self.conn:
            # Should not happen if set_ui_state is working, but safe check is good.
            return 
        
        # 1. Clear existing data in the Treeview
        for item in self.accounts_tree.get_children():
            self.accounts_tree.delete(item)
            
        # 2. SQL Query
        sql = """
        SELECT id, AccountName, AccountType, Institution, AccountNumber, OpeningDate 
        FROM Accounts 
        ORDER BY AccountName;
        """
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            
            # 3. Insert data into the Treeview
            for row in cursor.fetchall():
                # The values list corresponds to the columns defined in _create_accounts_list_view
                self.accounts_tree.insert('', tk.END, values=row)
                
            count = len(self.accounts_tree.get_children())
            print(f"Loaded {count} accounts into the view.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to retrieve accounts list: {e}")

    def save_transaction_data(self):
        """Validates and saves the transaction to the database."""
        if not self.conn:
            return

        # 1. Retrieve data
        selected_name = self.combo_account.get()
        trans_date = self.entry_trans_date.get().strip()
        trans_type = self.trans_type_var.get()
        amount_str = self.entry_amount.get().strip()
        notes = self.text_trans_notes.get("1.0", tk.END).strip()

        # 2. Basic Validation
        if not selected_name or not trans_date or not amount_str:
            messagebox.showwarning("Input Error", "Account, Date, and Amount are required.")
            return

        try:
            # Convert amount to float
            amount = float(amount_str)
            account_id = self.account_map[selected_name]

            # 3. SQL Insert
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO Transactions (Account_id, TransDate, TransType, Amount, Notes)
                VALUES (?, ?, ?, ?, ?)
            """, (account_id, trans_date, trans_type, amount, notes))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Transaction recorded successfully.")
            
            # 4. Reset Form
            self.entry_amount.delete(0, tk.END)
            self.text_trans_notes.delete("1.0", tk.END)
            
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for the Amount.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not save transaction: {e}")

    def load_transactions_list(self):
        """Fetches transactions, joins with accounts for the name, and splits amounts."""
        if not self.conn:
            return

        # Clear existing rows
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)

        # SQL with JOIN to get AccountName instead of ID
        sql = """
        SELECT T.id, A.AccountName, T.TransDate, T.TransType, T.Amount, T.Notes
        FROM Transactions T
        JOIN Accounts A ON T.Account_id = A.id
        ORDER BY T.TransDate DESC;
        """

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            
            for row in cursor.fetchall():
                t_id, name, date, t_type, amount, notes = row
                
                # Logic to separate Deposit and Withdrawal
                # Format the amount to 2 decimal places
                formatted_amount = f"{amount:.2f}"
                
                if t_type == 'Deposit':
                    deposit = formatted_amount
                    withdrawal = ""
                else:
                    deposit = ""
                    withdrawal = formatted_amount
                
                # Insert the processed row into the Treeview
                self.trans_tree.insert('', tk.END, values=(t_id, name, date, deposit, withdrawal, notes))

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load transactions: {e}")

    def save_new_room_year_data(self):
        """Converts year to first day of year and saves to NewRoomPerYear table."""
        if not self.conn:
            return

        year_input = self.entry_room_year.get().strip()
        amount_input = self.entry_room_amount.get().strip()

        # 1. Validation
        if not year_input or not amount_input:
            messagebox.showwarning("Input Error", "Both Year and Amount are required.")
            return

        if not (year_input.isdigit() and len(year_input) == 4):
            messagebox.showwarning("Input Error", "Please enter a valid 4-digit year (e.g., 2025).")
            return

        # 2. Convert Year to First Day of Year
        # Transformation: "2025" -> "2025-01-01"
        year_first_day = f"{year_input}-01-01"

        try:
            amount = float(amount_input)
            cursor = self.conn.cursor()

            # 3. Check for existing entry (YearFirstDay is UNIQUE)
            cursor.execute("SELECT id FROM NewRoomPerYear WHERE YearFirstDay = ?", (year_first_day,))
            if cursor.fetchone():
                messagebox.showwarning("Duplicate Error", f"A record for the year {year_input} already exists.")
                return

            # 4. Insert into Database
            cursor.execute("""
                INSERT INTO NewRoomPerYear (YearFirstDay, NewRoom)
                VALUES (?, ?)
            """, (year_first_day, amount))

            self.conn.commit()
            messagebox.showinfo("Success", f"Record for {year_input} saved successfully.")

            # Clear form
            self.entry_room_year.delete(0, tk.END)
            self.entry_room_amount.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for the Amount.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def load_room_year_list(self):
            """
            Fetches records from NewRoomPerYear and displays them in the Room Years Treeview.
            """
            if not self.conn:
                return

            # 1. Clear self.room_years_tree
            for item in self.room_years_tree.get_children():
                self.room_years_tree.delete(item)

            # 2. SQL Query
            sql = """
            SELECT YearFirstDay, NewRoom 
            FROM NewRoomPerYear 
            ORDER BY YearFirstDay;
            """

            try:
                cursor = self.conn.cursor()
                cursor.execute(sql)

                # 3. Insert into self.room_years_tree
                for row in cursor.fetchall():
                    full_date, amount = row

                    # OPTIONAL: Extract just the year for a cleaner UI
                    # "2025-01-01" -> "2025"
                    display_year = full_date.split('-')[0] if '-' in full_date else full_date

                    self.room_years_tree.insert('', tk.END, values=(display_year, amount))

                # 4. FIX: Check count of the correct tree
                count = len(self.room_years_tree.get_children())
                print(f"Loaded {count} years into the view.")

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to retrieve room by years list: {e}")

if __name__ == "__main__":
    root = TFSAid()
    root.mainloop()