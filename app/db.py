import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "expenses.db"


def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            note TEXT
        )
    """)
    return conn


def add_expense(date_str, category, amount, note):
    conn = get_connection()
    conn.execute(
        "INSERT INTO expenses (date, category, amount, note) VALUES (?, ?, ?, ?)",
        (date_str, category, amount, note),
    )
    conn.commit()
    conn.close()


def get_expenses(month=None, category=None):
    conn = get_connection()
    query = "SELECT id, date, category, amount, note FROM expenses WHERE 1=1"
    params = []
    if month:
        query += " AND date LIKE ?"
        params.append(f"{month}%")
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY date DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def delete_expense(expense_id):
    conn = get_connection()
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


def get_total(month=None):
    conn = get_connection()
    query = "SELECT SUM(amount) FROM expenses WHERE 1=1"
    params = []
    if month:
        query += " AND date LIKE ?"
        params.append(f"{month}%")
    total = conn.execute(query, params).fetchone()[0]
    conn.close()
    return total or 0.0


def get_category_totals(month=None):
    conn = get_connection()
    query = "SELECT category, SUM(amount) FROM expenses WHERE 1=1"
    params = []
    if month:
        query += " AND date LIKE ?"
        params.append(f"{month}%")
    query += " GROUP BY category ORDER BY SUM(amount) DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows