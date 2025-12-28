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

    def get_accounts(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT AccountName, AccountNameCRA, AccountType, Institution, AccountNumber, OpeningDate FROM Accounts ORDER BY AccountName")
        return cursor.fetchall()

    def save_account(self, data):
        sql = """INSERT INTO Accounts 
                 (AccountName, AccountNameCRA, AccountType, Institution, AccountNumber, OpeningDate, CloseDate, Notes) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor = self.conn.cursor()
        cursor.execute(sql, data)
        self.conn.commit()

    def get_account_map(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, AccountName FROM Accounts ORDER BY AccountName")
        return {name: acc_id for acc_id, name in cursor.fetchall()}

    def save_transaction(self, account_id, date, t_type, amount, notes):
        cursor = self.conn.cursor()
        cursor.execute("""INSERT INTO Transactions (Account_id, TransDate, TransType, Amount, Notes)
                          VALUES (?, ?, ?, ?, ?)""", (account_id, date, t_type, amount, notes))
        self.conn.commit()

    def get_transactions(self):
        # Returns: AccountName, TransDate, TransType, Amount, Notes
        sql = """SELECT A.AccountName, T.TransDate, T.TransType, T.Amount, T.Notes
                FROM Transactions T JOIN Accounts A ON T.Account_id = A.id
                ORDER BY T.TransDate"""
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def save_room_year(self, date, amount):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO NewRoomPerYear (YearFirstDay, NewRoom) VALUES (?, ?)", (date, amount))
        self.conn.commit()

    def get_room_years(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT YearFirstDay, NewRoom FROM NewRoomPerYear ORDER BY YearFirstDay")
        return cursor.fetchall()