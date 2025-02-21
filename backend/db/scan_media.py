import os
import sqlite3
import logging
import base64
from mutagen.id3 import ID3
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wavpack import WavPack
from mutagen.mp4 import MP4
from backend.config import MEDIA_DIR, DB_PATH, AUDIO_METADATA_KEY_TYPES, SUPPORTED_EXTS


def find_separate_albumart(directory: str) -> str:
    """
    Checks if there is a separate album art file in the directory.
    Args:
        directory (str): The directory to check. Most preferably the directory of the audio file.
    Returns:
        str: The path to the album art file if found, else None.
    """
    candidates = [directory + "/" + item for item in os.listdir(directory)]
    image_exts = [".jpg", ".jpeg", ".png"]
    candidates = [item for item in candidates if any(
        item.lower().endswith(ext) for ext in image_exts)]
    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) == 0:
        # try subdirectories recursively
        for subdir in os.listdir(directory):
            subdir_path = directory + "/" + subdir
            if os.path.isdir(subdir_path):
                candidates += find_separate_albumart(subdir_path)
        if len(candidates) == 1:
            return candidates
        return None
    else:  # len(candidates) > 1:
        logging.error(
            f"Multiple album art files found for {directory}: {candidates}")
        return None


def extract_album_art(file_path: str) -> str:
    """Extract album art from an audio file and return it as a base64 string."""
    try:
        if file_path.lower().endswith(".mp3"):
            audio = MP3(file_path, ID3=ID3)
            if "APIC:" in audio.tags:
                album_art = audio.tags["APIC:"].data
            else:
                separate_albumart = find_separate_albumart(os.path.dirname(file_path))
                if separate_albumart:
                    with open(separate_albumart, "rb") as f:
                        album_art = f.read()
                else:
                    return None
        
        elif file_path.lower().endswith(".flac"):
            audio = FLAC(file_path)
            if audio.pictures:
                album_art = audio.pictures[0].data
            else:
                separate_albumart = find_separate_albumart(os.path.dirname(file_path))
                if separate_albumart:
                    with open(separate_albumart, "rb") as f:
                        album_art = f.read()
                else:
                    return None
        
        elif file_path.lower().endswith(".m4a"):
            audio = MP4(file_path)
            if "covr" in audio and len(audio["covr"]) > 0:
                album_art = audio["covr"][0]
            else:
                separate_albumart = find_separate_albumart(os.path.dirname(file_path))
                if separate_albumart:
                    with open(separate_albumart, "rb") as f:
                        album_art = f.read()
                else:
                    return None
        
        else:
            logging.error(
                f"Unsupported file format for {file_path}. Extension must be one of: .mp3, .flac, .m4a"
            )
            return None  # Unsupported file format
        
        return f"data:image/jpeg;base64,{base64.b64encode(album_art).decode('utf-8')}"
    
    except Exception as e:
        print(f"Failed to extract album art from {file_path}: {e}")
        return None


def extract_metadata(file_path: str) -> dict:
    """Extract metadata from an audio file."""
    try:
        if file_path.lower().endswith(".mp3"):
            audio = MP3(file_path, ID3=ID3)
        elif file_path.lower().endswith(".flac"):
            audio = FLAC(file_path)
        elif file_path.lower().endswith(".wav"):
            audio = WavPack(file_path)
        elif file_path.lower().endswith(".m4a"):
            audio = MP4(file_path)
        else:
            logging.error(
                f"Unsupported file format for {file_path}. Extension must be one of: .mp3, .flac, .wav, .m4a"
            )
            return None
        ret = {
            key: audio.get(key, ["Unknown"])[0]
            for key in AUDIO_METADATA_KEY_TYPES.keys()
            if key not in ["duration", "file_path"]
            or key.endswith("_id")  # ids are assigned in another function
        }
        ret["duration"] = audio.info.length if audio.info else 0
        ret["file_path"] = file_path
        return ret
    except Exception as e:
        logging.error(f"Failed to read metadata for {file_path}: {e}")
        return None


def scan_basics(cursor: sqlite3.Cursor) -> None:
    """Scan media folder and store metadata except ids in the cursor. conn.commit() should be called after this function to save changes."""
    logging.info("Scanning basic information...")
    keys_with_path = ["file_path"] + list(AUDIO_METADATA_KEY_TYPES.keys())

    for root, _, files in os.walk(MEDIA_DIR):
        for file in files:
            if not any(file.lower().endswith(ext) for ext in SUPPORTED_EXTS):
                continue

            file_path = os.path.join(root, file)
            metadata = extract_metadata(file_path)
            if not metadata:
                continue

            cmd = f"""
                INSERT OR IGNORE INTO music ({", ".join(keys_with_path)})
                VALUES ({", ".join(["?"] * len(keys_with_path))})
            """
            cursor.execute(
                cmd, tuple([metadata[key] for key in keys_with_path])
            )
    logging.info("Scanned basic information.")


def find_duplicates(target_list: list) -> list:
    """Find duplicates in a list."""
    seen = set()
    duplicates = set()
    for item in target_list:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)


def set_ids(cursor: sqlite3.Cursor) -> None:
    """Scan media folder and store metadata ids in the cursor. conn.commit() should be called after this function to save changes."""
    logging.info("Scanning ids...")
    id_maps = {key.replace("_id", ""): {}
               for key in AUDIO_METADATA_KEY_TYPES.keys() if key.endswith("_id")}

    # replace "Unknown" with NULL
    for key in id_maps.keys():
        cursor.execute(
            f"UPDATE music SET {key}_id = NULL WHERE {key}_id = 'Unknown'")

    for key in id_maps.keys():
        # find distinct key-(key+"_id") pairs by:
        cursor.execute(
            f"SELECT DISTINCT {key}, {key}_id FROM music WHERE {key} IS NOT NULL OR {key}_id IS NOT NULL")

        # first, check if key-(key+"_id") pairs are one-to-one
        all_rows = cursor.fetchall()
        all_rows_except_none = [row for row in all_rows if None not in row]
        all_are_none = len(all_rows_except_none) == 0
        if not all_are_none:
            keys, key_ids = zip(*all_rows_except_none)
        is_one_to_one = True
        if (not all_are_none) and (len(keys) != len(set(keys))):
            logging.error(
                f"Multiple {key}_id values found for the same {key}: {find_duplicates(keys)}"
            )
            is_one_to_one = False
        elif (not all_are_none) and (len(key_ids) != len(set(key_ids))):
            logging.error(
                f"Multiple {key} values found for the same {key}_id: {find_duplicates(key_ids)}"
            )
            is_one_to_one = False

        if not is_one_to_one:
            response = "a"
            while response.lower() not in ["y", "n"]:
                response = input("\tDo you wish to reset the ids? (Y/n): ")
            if response.lower() == "n":
                logging.info(f"Skipping {key} ids.")
                continue
            all_rows = []
            cursor.execute(f"UPDATE music SET {key}_id = NULL")
            logging.info(f"Reset {key} ids.")

        # then update the id_maps
        for row in all_rows:
            key_val, key_id_val = row
            if key_id_val is None:
                continue
            elif key_val not in id_maps[key]:
                id_maps[key][key_val] = key_id_val
                logging.info(
                    f"Found {key} id {key_id_val} for {key} {key_val}")
            else:
                cursor.execute(
                    f"UPDATE music SET {key}_id = ? WHERE {key} = ?", (id_maps[key][key_val], key_val))
                logging.info(
                    f"Updated {key} id {id_maps[key][key_val]} for {key} {key_val}")

        # then fill the missing ids in the table and update the id_maps
        cursor.execute(
            f"SELECT id, {key} FROM music WHERE {key}_id IS NULL OR {key}_id = 'Unknown'")
        for row in cursor.fetchall():
            key_val, key_id_val = row
            if key_id_val not in id_maps[key]:
                # id_maps[key][key_id_val] = len(id_maps[key]) + 1
                id_maps[key][key_id_val] = max(
                    id_maps[key].values(), default=0) + 1
                logging.info(
                    f"Assigned {key} id {id_maps[key][key_id_val]} to {key} {key_id_val}")
            cursor.execute(f"UPDATE music SET {key}_id = ? WHERE id = ?",
                           (id_maps[key][key_id_val], key_val))

    logging.info("Scanned ids.")


def check_columns(cursor: sqlite3.Cursor, table: str, columns: list):
    """Check if the columns exist in the table. If not, add them."""
    logging.info(f"Checking columns for {table}...")

    # check if table exists
    cursor.execute(f"SELECT * FROM {table} LIMIT 1")
    if not cursor.description:
        logging.error(f"Table {table} does not exist.")
        return

    # check if columns exist
    cursor.execute(f"PRAGMA table_info({table})")
    existing_columns = [row[1] for row in cursor.fetchall()]
    for column in columns:
        if column in existing_columns:
            continue
        cursor.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} {AUDIO_METADATA_KEY_TYPES[column]}")
        logging.info(f"Added column {column} to {table}.")

    logging.info(f"Checked columns for {table}.")
    return


def main():
    if not os.path.exists(MEDIA_DIR):
        logging.error(
            f"Media directory not found at {MEDIA_DIR}. Please check the configuration."
        )
        return
    if not os.path.exists(DB_PATH):
        logging.info("Database not found. Creating tables...")
        import db_setup
        db_setup.create_tables()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    check_columns(cursor, "music", AUDIO_METADATA_KEY_TYPES.keys())
    scan_basics(cursor)
    set_ids(cursor)
    
    conn.commit()
    conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
