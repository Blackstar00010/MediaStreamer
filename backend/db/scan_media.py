import os
import sqlite3
import logging
import base64
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wavpack import WavPack
from mutagen.mp4 import MP4
import backend.config as config
from backend.db import utils


def ensure_default_entries(cursor: sqlite3.Cursor):
    """Ensure default entries of NULL for artist and album where we cannot fetch them. Also, adds default elo rating for albums."""
    cursor.execute("INSERT OR IGNORE INTO artists (artist_id, artist_name) VALUES (0, NULL)")
    cursor.execute("INSERT OR IGNORE INTO albums (album_id, album_name) VALUES (0, NULL)")
    cursor.execute("INSERT OR IGNORE INTO genres (genre_id, genre_name) VALUES (0, NULL)")
    cursor.execute("INSERT OR IGNORE INTO organizations (organization_id, organization_name) VALUES (0, NULL)")
    

def check_columns(cursor: sqlite3.Cursor, table: str, columns_and_types: dict) -> list:
    """Check if the columns exist in the table. If not, add them. Returns newly added columns."""
    logging.info(f"Checking columns for {table}...")

    # check if table exists
    cursor.execute(f"SELECT * FROM {table} LIMIT 1")
    if not cursor.description:
        logging.error(f"Table {table} does not exist.")
        return

    # check if columns exist
    cursor.execute(f"PRAGMA table_info({table})")
    existing_columns = [row[1] for row in cursor.fetchall()]
    ret = []
    # for column in columns:
    for column in columns_and_types.keys():
        if column in existing_columns:
            continue
        cursor.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} {columns_and_types[column]}"
        )
        logging.info(f"Added column {column} to {table}.")
        ret.append(column)

    logging.info(f"Checked columns for {table}.")
    return ret


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
            logging.error(
                f"Unsupported file format for {file_path}. Extension must be one of: .mp3, .flac, .wav, .m4a"
            )
            return None
    except FileNotFoundError as e:
        logging.error(f"File not found: {file_path}")
        return None
    except Exception as e:
        logging.error(f"Failed to read audio file {file_path}: {e}")
        return None
    if not audio:
        logging.error(f"Failed to read audio file {file_path}.")
        return None
    try:
        ret = {"duration": audio.info.length if audio.info else 0, "file_path": file_path}
        for key in config.AUDIO_METADATA_KEY_TYPES.keys():
            if key in ret.keys():
                continue
            ret[key.replace("_id", "")] = audio.get(key.replace("_id", ""), [None])[0]
        for key in config.IDS_KEYS:
            ret[key] = audio.get(key, [None])[0]
        return ret
    except Exception as e:
        logging.error(f"Failed to read metadata for {file_path}: {e}")
        return None


def get_or_create_id(cursor, table_wo_s, value):
    """Get ID from database, or insert new value if not found. Return ID and boolean indicating if new entry was created."""
    if value is None:
        cursor.execute(f"SELECT {table_wo_s}_id FROM {table_wo_s}s WHERE {table_wo_s}_name IS NULL")
    else:
        cursor.execute(f"SELECT {table_wo_s}_id FROM {table_wo_s}s WHERE {table_wo_s}_name = ?", (value,))
    row = cursor.fetchone()

    if row:  # already exists
        return row[0], False

    cursor.execute(f"INSERT INTO {table_wo_s}s ({table_wo_s}_name) VALUES (?)", (value,))
    return cursor.lastrowid, True


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
    """Extract album art from an audio file and return it as a base64 string. If not embedded, look for a separate album art file."""
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


def get_or_create_ids(cursor, table_wo_s, values):
    """Retrieve artist IDs from database, or insert new artists if not found."""
    ids = []

    # If artist is missing, return the default "Unknown Artist" (ID 0)
    if not values or values == ["Unknown"]:
        return [0]

    for value in values:
        cursor.execute(f"SELECT artist_id FROM {table_wo_s}s WHERE {table_wo_s}_name = ?", (value,))
        row = cursor.fetchone()

        if row:
            artist_id = row[0]  # Artist already exists
        else:
            cursor.execute(f"INSERT INTO {table_wo_s}s ({table_wo_s}_name) VALUES (?)", (value,))
            artist_id = cursor.lastrowid  # Get newly inserted artist ID

        ids.append(artist_id)

    return ids


def scan_basics(cursor: sqlite3.Cursor):
    """Scan media folder and store metadata in SQLite."""
    
    # keys for music table
    keys_musics = list(config.AUDIO_METADATA_KEY_TYPES.keys()) + ["file_path"]

    # Scan files
    for root, _, files in os.walk(config.MEDIA_DIR):
        files = [file for file in files 
                 if not file.startswith(".") 
                 and any(file.lower().endswith(ext) for ext in config.SUPPORTED_EXTS)]
        files.sort()
        for i, file in enumerate(files):
            file_path = os.path.join(root, file)
            logging.info(f"Scanning {file_path}...")
            
            metadata = extract_metadata(file_path)
            if not metadata:
                continue
            
            # Fill in missing metadata
            metadata['title'] = metadata.get('title', None) or os.path.splitext(file)[0]
            metadata['album'] = metadata.get('album', None) or os.path.basename(root)
            metadata['tracknumber'] = metadata.get('tracknumber', None) or i + 1
            metadata['totaltracks'] = metadata.get('totaltracks', None) or len(files)
            metadata['discnumber'] = metadata.get('discnumber', None) or 1
            metadata['totaldiscs'] = metadata.get('totaldiscs', None) or 1
            metadata['albumartist'] = metadata.get('albumartist', None) or metadata.get('artist', None)
            
            for key in config.ID_KEYS:
                result = get_or_create_id(cursor, key, metadata.get(key, None))
                metadata[f"{key}_id"] = result[0]
                if not result[1] or key != "album":
                    continue
                album_art = extract_album_art(file_path)
                if not album_art:
                    continue
                cursor.execute(
                    f"""
                    UPDATE albums
                    SET album_art = ?
                    WHERE album_id = ?
                    """,
                    (album_art, metadata["album_id"]),
                )
                    
            ids_stuff = {}
            for key in config.IDS_KEYS:
                values_to_seek = metadata.get(key, None)
                values_to_seek = values_to_seek.split(", ") if values_to_seek else []
                ids_stuff[key] = get_or_create_ids(cursor, key, values_to_seek)
            # e.g.) ids_stuff = {"artist": [1, 2, 3], ...}

            # Insert song into music table
            # TODO: only fill the empty fields in case we might use user input
            cmd = f"""
                INSERT OR REPLACE INTO music ({", ".join(keys_musics)})
                VALUES ({", ".join(["?"] * len(keys_musics))})
            """
            cursor.execute(
                cmd,
                [metadata.get(key, None) for key in keys_musics],
            )
            music_id = cursor.lastrowid

            for key in config.IDS_KEYS:
                for id_ in ids_stuff[key]:
                    cursor.execute(
                        f"INSERT OR REPLACE INTO {key}s_music ({key}_id, music_id) VALUES (?, ?)",
                        (id_, music_id),
                    )
            # TODO: insert into artists_albums using maximum overlap of artist_ids for each album_id
            
    logging.info("Scanning and storing completed.")


def get_artist_id_maps(cursor: sqlite3.Cursor, music_ids: list) -> dict:
    """Get artist IDs associated with a list of music IDs."""
    cursor.execute(
        f"""
        SELECT artist_id, music_id
        FROM artists_music
        WHERE music_id IN ({",".join(["?"] * len(music_ids))})
        """,
        music_ids,
    )
    artist_data = cursor.fetchall()
    artist_id_map = {music_id: [] for music_id in music_ids}
    for artist_id, music_id in artist_data:
        artist_id_map[music_id].append(artist_id)
    return artist_id_map


def link_albumartists(cursor: sqlite3.Cursor):
    """Link artists to albums. Use album artists if available, else use artists associated with tracks."""
    cursor.execute("SELECT DISTINCT album_id FROM albums")
    album_ids = [row[0] for row in cursor.fetchall() if row[0] != 0]
    
    for album_id in album_ids:
        cursor.execute(
            "SELECT music_id, albumartist FROM music WHERE album_id = ?",
            (album_id,),
        )
        all_rows = cursor.fetchall()
        if not all_rows:
            continue
        music_ids = [row[0] for row in all_rows]
        album_artists = [row[1].split(', ') for row in all_rows if row[1]]  # in case only certain tracks have album artists
        largest_subset = utils.find_largest_subset(album_artists)
        if largest_subset:  # if largest subset is not empty
            album_artist = ", ".join(largest_subset)
            # if all(item in largest_subset for item in album_artists[0]):
            #     # if the first row is the largest subset. we are doing this to conserve the order as much as possible
            #     album_artist = album_artists[0]
            # else:
            #     album_artist = ", ".join(largest_subset)
        else:  # if largest subset is not found, use artists associated with tracks
            artist_ids = get_artist_id_maps(cursor, music_ids)
            artist_ids = [artist_ids[music_id] for music_id in music_ids]  # list of list of ids
            largest_subset = utils.find_largest_subset(artist_ids)
            if largest_subset:
                album_artist = ", ".join(
                    [cursor.execute("SELECT artist_name FROM artists WHERE artist_id = ?", (artist_id,)).fetchone()[0] for artist_id in largest_subset]
                )
            else:
                album_artist = "Various Artists"
        album_artist_ids = get_or_create_ids(cursor, "artist", album_artist.split(", "))
        for artist_id in album_artist_ids:
            cursor.execute(
                "INSERT OR REPLACE INTO artists_albums (artist_id, album_id) VALUES (?, ?)",
                (artist_id, album_id),
            )
    logging.info("Linking artists to albums completed.")
        
    
def fill_album_ratings(cursor: sqlite3.Cursor):
    """Fill in album ratings based on track ratings."""
    # cursor.execute("UPDATE albums SET album_rating = 1000 WHERE album_id IS NULL")
    cursor.execute("UPDATE OR IGNORE albums SET album_rating = 1000 WHERE album_rating IS NULL")
    
    
def main():
    if not os.path.exists(config.MEDIA_DIR):
        logging.error(
            f"Media directory not found at {config.MEDIA_DIR}. Please check the configuration."
        )
        return
    if not os.path.exists(config.DB_PATH):
        logging.info("Database not found. Creating tables...")
        import db_setup
        db_setup.create_tables()

    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    # Ensure default entries of NULL for artist and album where we cannot fetch them
    cols_to_check = config.AUDIO_METADATA_KEY_TYPES.copy()
    cols_to_check["file_path"] = "TEXT"
    check_columns(cursor, "music", cols_to_check)
    check_columns(cursor, "artists", {"artist_name": "TEXT"})
    check_columns(cursor, "albums", config.ALBUM_METADATA_KEY_TYPES)
    ensure_default_entries(cursor)
    
    scan_basics(cursor)
    link_albumartists(cursor)
    fill_album_ratings(cursor)
    
    conn.commit()
    conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
    