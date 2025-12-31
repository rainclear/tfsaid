# dbm/database_manager.py
import sqlite3
import os

class DatabaseManager:
    def __init__(self):
        self.conn = None

    def connect(self, db_path):
        if self.conn:
            self.close()
        self.conn = sqlite3.connect(db_path)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def initialize_schema(self, db_path, schema_path):
        with open(schema_path, 'r') as f:
            sql_script = f.read()
        self.connect(db_path)
        self.conn.executescript(sql_script)
        self.conn.commit()

    def save_account(self, data):
        sql = """INSERT INTO Accounts 
                 (AccountName, AccountNameCRA, AccountType, Institution, AccountNumber, OpeningDate, CloseDate, Notes) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor = self.conn.cursor()
        cursor.execute(sql, data)
        self.conn.commit()

    def update_account(self, account_id, data):
        """Updates an existing account record."""
        sql = """UPDATE Accounts
                SET AccountName=?, AccountNameCRA=?, AccountType=?,
                    Institution=?, AccountNumber=?, OpeningDate=?,
                    CloseDate=?, Notes=?
                WHERE id = ?"""
        cursor = self.conn.cursor()
        # Combine the form data and the ID into one tuple
        cursor.execute(sql, data + (account_id,))
        self.conn.commit()

    def get_account_map(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, AccountName FROM Accounts ORDER BY AccountName")
        return {name: acc_id for acc_id, name in cursor.fetchall()}

    def get_accounts(self):
        """Modified to include the 'id' as the first element."""
        cursor = self.conn.cursor()
        # We fetch 'id' but we will hide it in the UI
        sql = """SELECT id, AccountName, AccountNameCRA, AccountType,
                        Institution, AccountNumber, OpeningDate
                 FROM Accounts ORDER BY AccountName"""
        cursor.execute(sql)
        return cursor.fetchall()

    def get_account_by_id(self, account_id):
        """Fetches a single account record by its ID for the edit form."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Accounts WHERE id = ?", (account_id,))
        return cursor.fetchone()

    def delete_account(self, account_id):
        """Deletes an account and all its associated transactions."""
        cursor = self.conn.cursor()
        try:
            # Delete linked transactions first (Foreign Key safety)
            cursor.execute("DELETE FROM Transactions WHERE Account_id = ?", (account_id,))

            # Delete the account itself
            cursor.execute("DELETE FROM Accounts WHERE id = ?", (account_id,))

            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e

    def save_transaction(self, account_id, date, t_type, amount, notes):
        cursor = self.conn.cursor()
        cursor.execute("""INSERT INTO Transactions (Account_id, TransDate, TransType, Amount, Notes)
                          VALUES (?, ?, ?, ?, ?)""", (account_id, date, t_type, amount, notes))
        self.conn.commit()

    def delete_transaction(self, trans_id):
        """Deletes a specific transaction record."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Transactions WHERE id = ?", (trans_id,))
        self.conn.commit()

    def get_transactions(self):
        """Fetches transactions with ID for UI management."""
        sql = """SELECT T.id, A.AccountName, T.TransDate, T.TransType, T.Amount, T.Notes
                FROM Transactions T JOIN Accounts A ON T.Account_id = A.id
                ORDER BY T.TransDate"""
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def get_transaction_by_id(self, trans_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Transactions WHERE id = ?", (trans_id,))
        return cursor.fetchone()

    def update_transaction(self, trans_id, account_id, date, t_type, amount, notes):
        cursor = self.conn.cursor()
        sql = """UPDATE Transactions
                 SET Account_id=?, TransDate=?, TransType=?, Amount=?, Notes=?
                 WHERE id = ?"""
        cursor.execute(sql, (account_id, date, t_type, amount, notes, trans_id))
        self.conn.commit()

    def save_room_year(self, date, amount):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO NewRoomPerYear (YearFirstDay, NewRoom) VALUES (?, ?)", (date, amount))
        self.conn.commit()

    def get_room_years(self):
        """Fetches all room per year entries sorted by year."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, YearFirstDay, NewRoom FROM NewRoomPerYear ORDER BY YearFirstDay DESC")
        return cursor.fetchall()

    def delete_room_year(self, room_id):
        """Deletes a specific year room entry."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM NewRoomPerYear WHERE id = ?", (room_id,))
        self.conn.commit()

    def get_cra_report_data(self):
        """Fetches transactions ordered for the CRA report."""
        sql = """SELECT A.AccountNameCRA, T.TransDate, T.TransType, T.Amount, T.Notes
                FROM Transactions T
                JOIN Accounts A ON T.Account_id = A.id
                ORDER BY A.AccountNameCRA ASC, T.TransDate ASC"""
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
