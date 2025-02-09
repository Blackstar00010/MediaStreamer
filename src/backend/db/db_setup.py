import sqlite3
import logging
from backend.config import DB_PATH, METADATA_KEYS, METADATA_KEY_TYPES


def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # TODO: add added_at
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS music (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE NOT NULL,
            {", ".join([f"{key} {METADATA_KEY_TYPES[key]}" for key in METADATA_KEYS])}
        )
        """
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    logging.info("Database and tables created successfully.")
