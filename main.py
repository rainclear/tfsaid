# main.py
import tkinter as tk
from tkinter import filedialog, messagebox
from dbm.database_manager import DatabaseManager
from ui.main_window import MainWindowLayout
from ui.menu_bar import AppMenuBar
from ui.frames import AccountsListFrame, TransactionsListFrame, NewTransactionFrame #, NewRoomYearForm # etc.

class TFSAid(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TFSAid - Help Tracking TFSA Room")
        self.geometry("1500x750")
        self.minsize(1500, 750)
        # self.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=1)

        # 1. Initialize Logic
        self.db = DatabaseManager()

        # 2. Setup Menu Bar
        self.menubar = AppMenuBar(self)
        self.config(menu=self.menubar)

        # 3. Setup Layout
        self.layout = MainWindowLayout(self, self)

        # 4. Initialize Frames
        self.frames = {}
        # Add all your frame classes to this tuple
#        for F in (AccountsListFrame, NewTransactionFrame, NewRoomYearForm):
        for F in (AccountsListFrame, TransactionsListFrame,  NewTransactionFrame):
            page_name = F.__name__
            frame = F(parent=self.layout.content_area, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Start with a default view or a "Home" frame
        self.show_frame("AccountsListFrame")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if hasattr(frame, "refresh"):
            frame.refresh()
        frame.tkraise()

    # --- Database Control Methods (Triggered by Menu) ---

    def new_database(self):
        db_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite DB", "*.db")])
        if db_path:
            self.db.connect(db_path)
            messagebox.showinfo("Success", f"Created new database: {db_path}")

    def open_database(self):
        db_path = filedialog.askopenfilename(filetypes=[("SQLite DB", "*.db")])
        if db_path:
            self.db.connect(db_path)
            self.show_frame("AccountsListFrame") # Refresh view on open

    def initialize_database(self):
        if not self.db.conn:
            messagebox.showwarning("Warning", "Open or create a database first!")
            return
        
        schema_path = filedialog.askopenfilename(filetypes=[("SQL scripts", "*.sql")])
        if schema_path:
            try:
                self.db.initialize_schema(self.db.conn_path, schema_path) # Need to track path in DB manager
                messagebox.showinfo("Success", "Database initialized successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to initialize: {e}")

    def close_database(self):
        self.db.close()
        messagebox.showinfo("Database", "Database closed.")

if __name__ == "__main__":
    app = TFSAid()
    app.mainloop()