import sqlite3
import pytest
from bank import create_account, deposit, withdraw, view_transactions, balance


@pytest.fixture
def setup_db():
    """Creates an in-memory SQLite database for testing."""
    conn = sqlite3.connect(":memory:")  # Use in-memory DB for faster tests
    cursor = conn.cursor()
    
    # Create accounts table
    cursor.execute('''
        CREATE TABLE accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            balance REAL NOT NULL
        )
    ''')
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE transactions (
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
    yield conn  # Provide the connection to tests
    conn.close()  # Close DB after tests


def test_create_account(setup_db):
    """Test account creation."""
    conn = setup_db
    account_id = create_account(conn, "Test User", 1000)
    assert account_id is not None

    cursor = conn.cursor()
    cursor.execute("SELECT name, balance FROM accounts WHERE id = ?", (account_id,))
    result = cursor.fetchone()
    assert result == ("Test User", 1000)


def test_deposit(setup_db):
    """Test depositing money into an account."""
    conn = setup_db
    account_id = create_account(conn, "Test User", 1000)
    deposit(conn, account_id, 500)

    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
    balance = cursor.fetchone()[0]
    assert balance == 1500


def test_withdraw(setup_db):
    """Test withdrawing money from an account."""
    conn = setup_db
    account_id = create_account(conn, "Test User", 1000)
    withdraw(conn, account_id, 400)

    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
    balance = cursor.fetchone()[0]
    assert balance == 600  # 1000 - 400


def test_insufficient_funds(setup_db, capsys):
    """Test withdrawing money when balance is insufficient."""
    conn = setup_db
    account_id = create_account(conn, "Test User", 300)
    withdraw(conn, account_id, 500)

    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
    balance = cursor.fetchone()[0]
    assert balance == 300  # Balance should remain the same

    # Capture console output and check error message
    captured = capsys.readouterr()
    assert "Insufficient balance." in captured.out


def test_transactions_log(setup_db):
    """Test if transactions are logged correctly."""
    conn = setup_db
    account_id = create_account(conn, "Test User", 1000)
    deposit(conn, account_id, 200)
    withdraw(conn, account_id, 100)

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE account_id = ?", (account_id,))
    transactions_count = cursor.fetchone()[0]
    assert transactions_count == 3  # 1 deposit (initial) + 1 deposit + 1 withdrawal


def test_balance(setup_db, capsys):
    """Test checking account balance."""
    conn = setup_db
    account_id = create_account(conn, "Test User", 1500)
    
    balance(conn, account_id)  # Call balance function

    # Capture console output
    captured = capsys.readouterr()
    assert "Current balance: 1500" in captured.out
