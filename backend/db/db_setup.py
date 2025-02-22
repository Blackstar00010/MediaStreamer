import sqlite3
import logging
from backend.config import DB_PATH, AUDIO_METADATA_KEY_TYPES, ALBUM_METADATA_KEY_TYPES, ID_KEYS, IDS_KEYS


def create_table(cursor, table_name, columns, overwrite=True):
    """Create a table in the database with the given columns."""
    if overwrite:
        cursor.execute(
            f"""
            DROP TABLE IF EXISTS {table_name}
            """
        )
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {", ".join([f"{key} {value}" for key, value in columns.items()])}
        )
        """
    )
    

def create_link_table(cursor, table1, table2, col1, col2, overwrite=True):
    """Create a table in the database with the given columns + "_id"."""
    table_name = f"{table1}_{table2}"
    if overwrite:
        cursor.execute(
            f"""
            DROP TABLE IF EXISTS {table_name}
            """
        )
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} ({col1}_id INTEGER, {col2}_id INTEGER,
        FOREIGN KEY ({col1}_id) REFERENCES {table1}({col1}_id),
        FOREIGN KEY ({col2}_id) REFERENCES {table2}({col2}_id),
        PRIMARY KEY ({col1}_id, {col2}_id))
        """
    )


def create_tables():
    logging.info(f"Creating database and tables at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # TODO: add added_at
    music_key_types = AUDIO_METADATA_KEY_TYPES.copy()
    music_key_types["music_id"] = "INTEGER PRIMARY KEY AUTOINCREMENT"
    music_key_types["file_path"] = "TEXT UNIQUE NOT NULL"
    # [music_key_types.update({f"{key}_id": "INTEGER"}) for key in ID_KEYS] 
    for key in ID_KEYS:
        music_key_types[f"{key}_id"] = "INTEGER"
        # music_key_types.pop(key)
    # for key in IDS_KEYS:
    #     music_key_types.pop(key)
    create_table(cursor, "music", music_key_types)
    
    album_key_types = ALBUM_METADATA_KEY_TYPES.copy()
    album_key_types["album_id"] = "INTEGER PRIMARY KEY"
    create_table(cursor, "albums", album_key_types)
    
    artist_key_types = {"artist_id": "INTEGER PRIMARY KEY AUTOINCREMENT", "artist_name": "TEXT UNIQUE"}
    create_table(cursor, "artists", artist_key_types)
    
    genre_key_types = {"genre_id": "INTEGER PRIMARY KEY AUTOINCREMENT", "genre_name": "TEXT UNIQUE"}
    create_table(cursor, "genres", genre_key_types)
    
    organization_key_types = {"organization_id": "INTEGER PRIMARY KEY AUTOINCREMENT", "organization_name": "TEXT UNIQUE"}
    create_table(cursor, "organizations", organization_key_types)
    
    # tables to link artists-(music, albums)
    create_link_table(cursor, "artists", "music", "artist", "music")
    create_link_table(cursor, "artists", "albums", "artist", "album")
    
    for table in ID_KEYS + IDS_KEYS:
        cursor.execute(f"INSERT INTO {table}s ({table}_id, {table}_name) VALUES (0, NULL)")
    
    # insert column "album_art_path" into albums table
    # cursor.execute("ALTER TABLE albums ADD COLUMN album_art_path TEXT")
    
    conn.commit()
    conn.close()
    logging.info("Database and tables created successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_tables()
