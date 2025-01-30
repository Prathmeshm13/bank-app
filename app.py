# Develop a Bank CRUD application using python for backend and each activity should be saved in Database.
# Note :-  No need of UI
# -> Create account
# -> deposit
# -> withdraw
# -> view transactions
# -> balance

import sqlite3
import datetime

def create_account(conn, name, initial_deposit):
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO accounts (name, balance) VALUES (?, ?)", (name, initial_deposit))
        account_id = cursor.lastrowid
        conn.commit()
        log_transaction(conn, account_id, "deposit", initial_deposit, "Account Creation")
        print(f"Account created successfully. Account ID: {account_id}")
        return account_id
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None


def deposit(conn, account_id, amount):
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, account_id))
        conn.commit()
        log_transaction(conn, account_id, "deposit", amount)
        print(f"Deposit of {amount} successful.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


def withdraw(conn, account_id, amount):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
        balance = cursor.fetchone()[0]
        if balance >= amount:
            cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, account_id))
            conn.commit()
            log_transaction(conn, account_id, "withdrawal", amount)
            print(f"Withdrawal of {amount} successful.")
        else:
            print("Insufficient balance.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


def view_transactions(conn, account_id):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM transactions WHERE account_id = ?", (account_id,))
        transactions = cursor.fetchall()
        if transactions:
          print("Transactions:")
          for transaction in transactions:
              print(transaction)
        else:
            print("No transactions found for this account.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

def balance(conn, account_id):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
        balance = cursor.fetchone()[0]
        print(f"Current balance: {balance}")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


def log_transaction(conn, account_id, transaction_type, amount, description=""):
    cursor = conn.cursor()
    timestamp = datetime.datetime.now()
    try:
        cursor.execute("""
            INSERT INTO transactions (account_id, transaction_type, amount, timestamp, description)
            VALUES (?, ?, ?, ?, ?)""",
            (account_id, transaction_type, amount, timestamp, description))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error logging transaction: {e}")


def main():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            balance REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            description TEXT,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        )
    ''')
    conn.commit()


    account_id = create_account(conn, "Surya", 3000)

    if account_id:
        deposit(conn, account_id, 500)
        withdraw(conn, account_id, 200)
        view_transactions(conn, account_id)
        balance(conn, account_id)

    conn.close()

if __name__ == "__main__":
    main()