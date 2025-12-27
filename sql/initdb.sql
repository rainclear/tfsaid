DROP TABLE IF EXISTS NewRoomPerYear;
DROP TABLE IF EXISTS Accounts;
DROP TABLE IF EXISTS Transactions;

CREATE TABLE NewRoomPerYear (
  id integer PRIMARY KEY,
  YearFirstDay date UNIQUE NOT NULL,
  NewRoom decimal(20, 2) NOT NULL DEFAULT 0
);

CREATE TABLE Accounts (
  id integer PRIMARY KEY,
  AccountName varchar(256) UNIQUE NOT NULL,
  AccountNameCRA varchar(256) UNIQUE NOT NULL,
  AccountType varchar(256),
  Institution varchar(256),
  AccountNumber varchar(256),
  OpeningDate date,
  CloseDate date,
  Notes varchar(512)
);

CREATE TABLE Transactions (
  id integer PRIMARY KEY,
  Account_id integer NOT NULL,
  TransDate date NOT NULL,
  TransType varchar(32) CHECK( TransType IN ('Deposit', 'Withdrawal') ) NOT NULL DEFAULT 'Deposit',
  Amount decimal(20, 2) NOT NULL DEFAULT 0,
  Notes varchar(512),
  FOREIGN KEY (Account_id) REFERENCES Accounts(id)
);

CREATE INDEX ACCTNAME ON Accounts (AccountName);

CREATE INDEX ACCTNAMECRA ON Accounts (AccountNameCRA);

CREATE INDEX ACCT ON Transactions (Account_id);

CREATE INDEX TRANSTYPE ON Transactions (TransType);