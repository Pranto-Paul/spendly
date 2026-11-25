import sqlite3
from datetime import date, timedelta
from pathlib import Path
from werkzeug.security import generate_password_hash

DB_PATH = Path(__file__).resolve().parent.parent / "spendly.db"

CATEGORIES = (
    "Food",
    "Transport",
    "Bills",
    "Health",
    "Entertainment",
    "Shopping",
    "Other",
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                email         TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                created_at    TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                amount      REAL    NOT NULL,
                category    TEXT    NOT NULL,
                date        TEXT    NOT NULL,
                description TEXT,
                created_at  TEXT    DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)
        conn.commit()
    finally:
        conn.close()


def seed_db():
    conn = get_db()
    try:
        existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if existing > 0:
            return

        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
        )
        user_id = cur.lastrowid

        today = date.today()
        first_of_month = today.replace(day=1)
        # Generate offsets spread across the current month, clamped to not exceed today
        max_offset = (today - first_of_month).days
        offsets = [0, 2, 4, 6, 9, 11, 13, 15]
        safe_offsets = [min(o, max_offset) for o in offsets]

        expenses = [
            (12.50, "Food", "Lunch at cafe"),
            (45.00, "Transport", "Monthly metro card"),
            (89.99, "Bills", "Electricity bill"),
            (25.00, "Health", "Pharmacy"),
            (15.75, "Entertainment", "Movie ticket"),
            (60.00, "Shopping", "New shoes"),
            (10.00, "Other", "Misc. expense"),
            (32.40, "Food", "Groceries"),
        ]

        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            [
                (
                    user_id,
                    amount,
                    category,
                    (first_of_month + timedelta(days=offset)).isoformat(),
                    description,
                )
                for (amount, category, description), offset in zip(expenses, safe_offsets)
            ],
        )
        conn.commit()
    finally:
        conn.close()