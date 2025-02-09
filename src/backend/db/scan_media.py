import os
import sqlite3
import logging
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wavpack import WavPack
from mutagen.mp4 import MP4
from backend.config import MEDIA_DIR, DB_PATH, METADATA_KEYS, SUPPORTED_EXTS


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
        ret = {
            key: audio.get(key, ["Unknown"])[0]
            for key in METADATA_KEYS
            if key != "duration"
        }
        ret["duration"] = audio.info.length if audio.info else 0
        ret["file_path"] = file_path
        return ret
    except Exception as e:
        logging.error(f"Failed to read metadata for {file_path}: {e}")
        return None


def scan_and_store() -> None:
    """Scan media folder and store metadata in SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    keys_with_path = ["file_path"] + METADATA_KEYS
    for root, _, files in os.walk(MEDIA_DIR):
        for file in files:
            if any(file.lower().endswith(ext) for ext in SUPPORTED_EXTS):
                file_path = os.path.join(root, file)
                metadata = extract_metadata(file_path)

                if metadata:
                    cmd = f"""
                        INSERT OR IGNORE INTO music ({", ".join(keys_with_path)})
                        VALUES ({", ".join(["?"] * len(keys_with_path))})
                    """
                    print(cmd)
                    cursor.execute(
                        cmd, tuple([metadata[key] for key in keys_with_path])
                    )

    conn.commit()
    conn.close()
    logging.info("Scanning and storing completed.")


if __name__ == "__main__":
    scan_and_store()
