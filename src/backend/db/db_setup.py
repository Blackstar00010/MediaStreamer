import sqlite3
import logging

DB_PATH = "media.db"


def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS music (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT UNIQUE NOT NULL,
        title TEXT,
        artist TEXT,
        album TEXT,
        genre TEXT,
        duration REAL,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    logging.info("Database and tables created successfully.")
