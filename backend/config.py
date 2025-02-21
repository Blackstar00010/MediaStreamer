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

# file_path not included
AUDIO_METADATA_KEY_TYPES = {
    "title": "TEXT",
    "artist": "TEXT",
    "artist_id": "INTEGER",  # TODO: artist might be a list
    "album": "TEXT",
    "album_id": "INTEGER",
    "genre": "TEXT",
    "genre_id": "INTEGER",  # TODO: genre might be a list
    "duration": "REAL",
    "tracknumber": "INTEGER",
    "date": "TEXT",
    "organization": "TEXT",
    "organization_id": "INTEGER",
    # "album_art": "TEXT",  # extracted each time a file is fetched
}

if __name__ == "__main__":
    print("You are running config.py directly.")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Media directory: {MEDIA_DIR}")
    print(f"Database path: {DB_PATH}")
    print(f"Supported extensions: {SUPPORTED_EXTS}")
    print(f"Metadata keys: {AUDIO_METADATA_KEY_TYPES.keys()}")
