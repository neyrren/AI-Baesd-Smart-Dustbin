import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.abspath("classifications.db")


def get_connection():
    """Open and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the classifications table if it does not exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS classifications (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                result     TEXT    NOT NULL,
                confidence TEXT    NOT NULL,
                timestamp  TEXT    NOT NULL
            )
        """)
        conn.commit()
    print(f"Database ready: {DB_PATH}")


def save_classification(result: str, confidence: str) -> None:
    """Insert a new classification record."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO classifications (result, confidence, timestamp) VALUES (?, ?, ?)",
            (result, confidence, timestamp)
        )
        conn.commit()


def get_recent(limit: int = 10) -> list:
    """Return the most recent classifications."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM classifications ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(row) for row in rows]


def get_counts() -> dict:
    """Return total, organic, and inorganic counts."""
    with get_connection() as conn:
        total     = conn.execute("SELECT COUNT(*) FROM classifications").fetchone()[0]
        organic   = conn.execute("SELECT COUNT(*) FROM classifications WHERE result = 'organic'").fetchone()[0]
        inorganic = conn.execute("SELECT COUNT(*) FROM classifications WHERE result = 'inorganic'").fetchone()[0]
    return {"total": total, "organic": organic, "inorganic": inorganic}


def delete_all() -> None:
    """Delete all classification records from the database."""
    with get_connection() as conn:
        conn.execute("DELETE FROM classifications")
        conn.commit()
    print("All classification records deleted")


def delete_by_id(record_id: int) -> bool:
    """Delete a single record by ID."""
    with get_connection() as conn:
        conn.execute("DELETE FROM classifications WHERE id = ?", (record_id,))
        conn.commit()
    return True