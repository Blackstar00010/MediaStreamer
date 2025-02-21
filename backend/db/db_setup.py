import sqlite3
import logging
from backend.config import DB_PATH, AUDIO_METADATA_KEY_TYPES, ALBUM_METADATA_KEY_TYPES


def create_tables():
    logging.info(f"Creating database and tables at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # TODO: add added_at
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS music (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE NOT NULL,
            {", ".join([f"{key} {AUDIO_METADATA_KEY_TYPES[key]}" for key in AUDIO_METADATA_KEY_TYPES.keys()])}
        )
        """
    )
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS album (
            album_id INTEGER PRIMARY KEY,
            {", ".join([f"{key} {ALBUM_METADATA_KEY_TYPES[key]}" for key in ALBUM_METADATA_KEY_TYPES.keys()])}
        )
        """
    )
    conn.commit()
    conn.close()
    logging.info("Database and tables created successfully.")


if __name__ == "__main__":
    create_tables()
    logging.info("Database and tables created successfully.")
