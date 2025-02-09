import os
import sqlite3
import logging
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wavpack import WavPack
from mutagen.mp4 import MP4

MEDIA_DIR = "media"
DB_PATH = "media.db"


def extract_metadata(file_path: str) -> dict:
    """Extract metadata from an audio file."""
    try:
        if file_path.lower().endswith(".mp3"):
            audio = MP3(file_path, ID3=EasyID3)
        elif file_path.lower().endswith(".flac"):
            audio = FLAC(file_path)
        elif file_path.lower().endswith(".wav"):
            audio = WavPack(file_path)
        elif file_path.lower().endswith(".m4a"):
            audio = MP4(file_path)
        else:
            raise ValueError(
                f"Unsupported file format for {file_path}. Extension must be one of: .mp3, .flac, .wav, .m4a"
            )
        return {
            "title": audio.get("title", ["Unknown"])[0],
            "artist": audio.get("artist", ["Unknown"])[0],
            "album": audio.get("album", ["Unknown"])[0],
            "genre": audio.get("genre", ["Unknown"])[0],
            "duration": audio.info.length if audio.info else 0,
        }
    except Exception as e:
        logging.error(f"Failed to read metadata for {file_path}: {e}")
        return None


def scan_and_store() -> None:
    """Scan media folder and store metadata in SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    target_exts = [".mp3", ".wav", ".flac", ".m4a"]

    for root, _, files in os.walk(MEDIA_DIR):
        for file in files:
            if any(file.lower().endswith(ext) for ext in target_exts):
                file_path = os.path.join(root, file)
                metadata = extract_metadata(file_path)

                if metadata:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO music (file_path, title, artist, album, genre, duration)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (
                            file_path,
                            metadata["title"],
                            metadata["artist"],
                            metadata["album"],
                            metadata["genre"],
                            metadata["duration"],
                        ),
                    )

    conn.commit()
    conn.close()
    logging.info("Scanning and storing completed.")


if __name__ == "__main__":
    scan_and_store()
