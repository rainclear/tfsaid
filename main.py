# main.py
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from dbm.database_manager import DatabaseManager
from ui.main_window import MainWindowLayout
from ui.menu_bar import AppMenuBar

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
        # a. Register the Frames
        from ui.frames import WelcomeFrame, AccountsListFrame, TransactionsListFrame, NewAccountFrame, NewTransactionFrame # etc.
        self.frames = {}
        frame_list = (WelcomeFrame, AccountsListFrame, TransactionsListFrame, NewAccountFrame, NewTransactionFrame)
        # Add all your frame classes to this tuple
        for F in frame_list:
            page_name = F.__name__
            frame = F(parent=self.layout.content_area, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Initial State: Disable buttons until a file is opened
        self.update_ui_state()

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if hasattr(frame, "refresh"):
            frame.refresh()
        frame.tkraise()

    def update_ui_state(self):
        """Logic to switch views based on connection status."""
        is_connected = self.db.conn is not None
        self.layout.set_navigation_state(enabled=is_connected)

        if not is_connected:
            # Show welcome screen if no DB is open
            self.show_frame("WelcomeFrame")
        else:
            # If we just opened a DB, go to the default list view
            self.show_frame("AccountsListFrame")

    # --- Database Control Methods (Triggered by Menu) ---
    def new_database(self):
        """Creates a new database and automatically runs the schema script."""
        db_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite DB", "*.db")],
            title="Create New TFSAid Database"
        )

        if db_path:
            # 1. Locate the schema file (assuming it's in /sql/initdb.sql relative to main.py)
            # Using __file__ ensures it works even if you run the app from a different folder
            base_dir = os.path.dirname(__file__)
            schema_path = os.path.join(base_dir, 'sql', 'initdb.sql')

            try:
                # 2. Use the Model to create the file AND run the SQL script
                self.db.initialize_schema(db_path, schema_path)

                # 3. Store the path so we can check it later if needed
                self.db.current_path = db_path

                # 4. Update UI
                self.update_ui_state()
                self.show_frame("AccountsListFrame")
                messagebox.showinfo("Success", f"New database created and initialized:\n{db_path}")

            except FileNotFoundError:
                messagebox.showerror("Error", f"Could not find schema file at:\n{schema_path}")
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to initialize: {e}")

    def open_database(self):
        """Opens an existing database file."""
        db_path = filedialog.askopenfilename(filetypes=[("SQLite DB", "*.db")])
        if db_path:
            # Avoid re-opening the same file
            if hasattr(self.db, 'current_path') and self.db.current_path == db_path:
                return

            try:
                self.db.connect(db_path)
                self.db.current_path = db_path # Keep track of path
                self.update_ui_state()
                self.show_frame("AccountsListFrame")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open database: {e}")

    def close_database(self):
        """Manually triggered from the Menu."""
        self.db.close()
        self.update_ui_state() # This will now trigger the WelcomeFrame
        messagebox.showinfo("Database", "Database closed successfully.")

    def handle_save_account(self, data_tuple):
        """Mediator: Saves account data and refreshes UI."""
        if not self.db.conn:
            messagebox.showerror("Error", "No database connected.")
            return

        try:
            # 1. Tell the Model (database_manager) to save
            self.db.save_account(data_tuple)

            # 2. Success feedback
            messagebox.showinfo("Success", "Account saved successfully.")

            # 3. Clear the form in the View
            self.frames["NewAccountFrame"].clear_form()

            # 4. Redirect user to the list of accounts
            self.show_frame("AccountsListFrame")

        except Exception as e:
            messagebox.showerror("Database Error", f"Could not save account: {e}")

    def prepare_edit_account(self, account_id):
        """Fetches data and opens the form in Edit Mode."""
        # 1. Fetch the specific record from the DB
        # (You'll need a simple 'get_account_by_id' method in your DatabaseManager)
        account_data = self.db.get_account_by_id(account_id)

        if account_data:
            # 2. Tell the frame to load the data
            form_frame = self.frames["NewAccountFrame"]
            form_frame.load_account_data(account_id, account_data)

            # 3. Switch to the form view
            self.show_frame("NewAccountFrame")

    def handle_update_account(self, account_id, data):
        """Calls the model to update the record."""
        try:
            self.db.update_account(account_id, data)
            messagebox.showinfo("Success", "Account updated successfully.")

            # Reset the form state for next use
            self.frames["NewAccountFrame"].edit_id = None
            self.frames["NewAccountFrame"].save_btn.config(text="Save Account")

            self.show_frame("AccountsListFrame")
        except Exception as e:
            messagebox.showerror("Error", f"Update failed: {e}")


    def confirm_delete_account(self, account_id, account_name):
        """Shows a warning and deletes the account if confirmed."""
        msg = (f"Are you sure you want to delete '{account_name}'?\n\n"
               "WARNING: This will also delete ALL transactions associated with this account. "
               "This action cannot be undone.")

        if messagebox.askyesno("Confirm Delete", msg, icon='warning'):
            try:
                self.db.delete_account(account_id)
                messagebox.showinfo("Deleted", f"Account '{account_name}' has been removed.")

                # Refresh the view to show the updated list
                self.frames["AccountsListFrame"].refresh()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete account: {e}")

if __name__ == "__main__":
    app = TFSAid()
    app.mainloop()