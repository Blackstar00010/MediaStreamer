import os

# Define project root dynamically (useful if the project moves)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# Define important paths
MEDIA_DIR = os.path.join(PROJECT_ROOT, "media")  # Media files directory
DB_PATH = os.path.join(PROJECT_ROOT, "media.db")  # SQLite database file

# Define supported audio file extensions
SUPPORTED_EXTS = [".mp3", ".wav", ".flac", ".m4a"]

# Define metadata keys to extract
METADATA_KEYS = [
    "title",
    "artist",
    "album",
    "genre",
    "duration",
    "tracknumber",
    "date",
    "organization",
]
METADATA_KEY_TYPES = {
    "title": "TEXT",
    "artist": "TEXT",
    "album": "TEXT",
    "genre": "TEXT",
    "duration": "REAL",
    "tracknumber": "INTEGER",
    "date": "TEXT",
    "organization": "TEXT",
}

if __name__ == "__main__":
    print("You are running config.py directly.")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Media directory: {MEDIA_DIR}")
    print(f"Database path: {DB_PATH}")
    print(f"Supported extensions: {SUPPORTED_EXTS}")
    print(f"Metadata keys: {METADATA_KEYS}")
