import os

# Define project root dynamically (useful if the project moves)
BE_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BE_PATH, ".."))
# PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# Define important paths
MEDIA_DIR = os.path.join(PROJECT_ROOT, "media")  # Media files directory
DB_PATH = os.path.join(PROJECT_ROOT, "media.db")  # SQLite database file

# Define supported audio file extensions
SUPPORTED_EXTS = [".mp3", ".wav", ".flac", ".m4a"]

# id and file_path not included
AUDIO_METADATA_KEY_TYPES = {
    "title": "TEXT",
    # "artist": "TEXT",
    # "album": "TEXT",
    "album_id": "INTEGER",
    # "genre": "TEXT",
    "genre_id": "INTEGER",
    "duration": "REAL",
    "tracknumber": "INTEGER",
    "date": "TEXT",
    # "organization": "TEXT",
    "organization_id": "INTEGER",
    "tracknumber": "INTEGER",
    "totaltracks": "INTEGER",
    "discnumber": "INTEGER",
    "totaldiscs": "INTEGER",
    "albumartist": "TEXT",
    "composer": "TEXT",
}

# keys that require special handling
# (e.g. splitting by comma for multiple values)
ID_KEYS = ["album", "genre", "organization"]
IDS_KEYS = ["artist"]

ALBUM_METADATA_KEY_TYPES = {
    "album_name": "TEXT",
    "album_path": "TEXT",
    "album_art": "TEXT",
    # "album_art_path": "TEXT",
}

if __name__ == "__main__":
    print("You are running config.py directly.")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Media directory: {MEDIA_DIR}")
    print(f"Database path: {DB_PATH}")
    print(f"Supported extensions: {SUPPORTED_EXTS}")
    print(f"Metadata keys: {AUDIO_METADATA_KEY_TYPES.keys()}")
