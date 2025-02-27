import sqlite3
import logging
import backend.config as config


def get_column_names(cursor: sqlite3.Cursor, table_name: str) -> list:
    """Get the column names of a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [column[1] for column in cursor.fetchall()]


def get_all_entries(cursor, table_name, column_names: list | str | None=None, distinct: bool=False) -> list:
    """Get data from a table. Returns a list of tuples."""
    cursor_is_local = not cursor
    if cursor_is_local:
        conn = sqlite3.connect(config.DB_PATH)
        cursor = conn.cursor()
    all_columns = get_column_names(cursor, table_name)
    if type(column_names) == str:
        column_names = [column_names]
    if not column_names:
        column_names = all_columns
    else:
        not_found = [column for column in column_names if column not in all_columns]
        if not_found:
            raise ValueError(f"Column(s) '{', '.join(not_found)}' not found in table '{table_name}'")
    cursor.execute(f"SELECT {', '.join(column_names)} FROM {table_name}")
    data = cursor.fetchall()
    if distinct:
        ret = []
        # for row in cursor.fetchall():
        for row in data:
            if row not in ret:
                ret.append(row)
        return ret
    if cursor_is_local:
        conn.close()
    return data
    # return cursor.fetchall()


def get_musicids_by_albumid(cursor=None, album_id: list | int | None=None):
    """
    Get music IDs by album ID and returns as {album_id: [music_id1, ...], ...}.
    Args:
        cursor: sqlite3.Cursor. Cursor object.
        album_id: list | int | None. Album IDs to get music IDs from.
        
    Returns:
        music_ids: dict. Keys are album IDs and values are lists of music IDs.
    """
    cursor_is_local = not cursor
    if cursor_is_local:
        conn = sqlite3.connect(config.DB_PATH)
        cursor = conn.cursor()
    if not album_id:
        # default album_id to all IDs in the table
        album_id = [item[0] for item in get_all_entries(cursor, "albums", "album_id")]
    else:
        # check if all IDs are in the table
        album_id = [album_id] if type(album_id) == int else album_id
        all_ids = [item[0] for item in get_all_entries(cursor, "albums", "album_id")]
        not_found = [id for id in album_id if id not in all_ids]
        if not_found:
            raise ValueError(f"ID(s) '{', '.join(not_found)}' not found in table 'albums'")
    cursor.execute(f"SELECT album_id, music_id FROM music WHERE album_id IN ({', '.join([str(id) for id in album_id])})")
    music_ids = {}
    for row in cursor.fetchall():
        if row[0] not in music_ids:
            music_ids[row[0]] = []
        music_ids[row[0]].append(row[1])
    if cursor_is_local:
        conn.close()
    return music_ids


def get_albums_by_albumid(cursor=None, album_ids: list | int | None=None, column_names: list | str | None=None) -> dict:
    """Get albums by ID."""
    cursor_is_local = not cursor
    if cursor_is_local:
        conn = sqlite3.connect(config.DB_PATH)
        cursor = conn.cursor()
    
    album_ids = [album_ids] if type(album_ids) == int else album_ids
    all_ids = [item[0] for item in get_all_entries(cursor, "albums", "album_id")]
    if not album_ids:
        album_ids = [album for album in all_ids]
    else:
        not_found = [str(album_id) for album_id in album_ids if album_id not in all_ids]
        if not_found:
            raise ValueError(f"Album ID(s) '{', '.join(not_found)}' not found in table 'albums'")
    column_names = [column_names] if type(column_names) == str else column_names
    all_columns = get_column_names(cursor, "albums")
    if not column_names:
        column_names = all_columns
    else:
        not_found = [column for column in column_names if column not in all_columns]
        if not_found:
            raise ValueError(f"Column(s) '{', '.join(not_found)}' not found in table 'albums'")
    
    cursor.execute(f"SELECT {', '.join(column_names)} FROM albums WHERE album_id IN ({', '.join('?' for _ in album_ids)})", album_ids)
    albums = cursor.fetchall()
    
    if cursor_is_local:
        conn.close()
    ret = { album_ids[i]: {column_names[j]: albums[i][j] for j in range(len(column_names))}
           for i in range(len(album_ids)) }
    return ret


def get_artists_by_albumid(cursor=None, album_ids: list | int | None=None, column_names: list | str | None=None) -> dict:
    """
    Get artists by album ID. Returns as {album_id: [{column_name1: value1, ...}, ...], ...}.
    Args:
        cursor: sqlite3.Cursor. Cursor object.
        album_ids: list | int | None. Album IDs to get artists from.
        column_names: list | str | None. Column names to get from the table 'artists'.
        
    Returns:
        artists: dict. Keys are album IDs and values are lists of dictionaries of column names and values.
    """
    cursor_is_local = not cursor
    if cursor_is_local:
        conn = sqlite3.connect(config.DB_PATH)
        cursor = conn.cursor()
    
    album_ids = [album_ids] if type(album_ids) == int else album_ids
    all_ids = [item[0] for item in get_all_entries(cursor, "albums", "album_id")]
    if not album_ids:
        album_ids = [album for album in all_ids]
    else:
        not_found = [album_id for album_id in album_ids if album_id not in all_ids]
        if not_found:
            raise ValueError(f"Album ID(s) '{', '.join(not_found)}' not found in table 'albums'")
    column_names = [column_names] if type(column_names) == str else column_names
    all_columns = get_column_names(cursor, "artists")
    if not column_names:
        column_names = all_columns
    else:
        not_found = [column for column in column_names if column not in all_columns]
        if not_found:
            raise ValueError(f"Column(s) '{', '.join(not_found)}' not found in table 'artists'")
    
    cursor.execute(f"SELECT album_id, artist_id FROM artists_albums WHERE album_id IN ({', '.join('?' for _ in album_ids)})", album_ids)
    artist_ids = {}
    for row in cursor.fetchall():
        if row[0] not in artist_ids:
            artist_ids[row[0]] = []
        artist_ids[row[0]].append(row[1])
        
    artists = {}
    for album_id in artist_ids.keys():
        artists[album_id] = []
        for artist_id in artist_ids[album_id]:
            cursor.execute(f"SELECT {', '.join(column_names)} FROM artists WHERE artist_id = ?", (artist_id,))
            row = cursor.fetchone()
            artists[album_id].append({column_names[j]: row[j] for j in range(len(column_names))})
            
    if cursor_is_local:
        conn.close()
    return artists
    


def get_data_by_musicid(cursor=None, music_ids: list | int | None = None, column_names: dict = None) -> dict:
    """
    Get data by ID.
    Args:
        cursor: sqlite3.Cursor. Cursor object.
        ids: list | int | None. Music IDs to get data from.
        column_names: dict. Column names to get data from, with table names as keys. e.g. {'music': ['music_id', 'title'], 'albums': ['album_id', 'title']}

    Returns:
        data: dict. Keys are music IDs and values are dictionaries of column names and values.
    """
    cursor_is_local = not cursor
    if cursor_is_local:
        conn = sqlite3.connect(config.DB_PATH)
        cursor = conn.cursor()
    if not music_ids:
        # default ids to all IDs in the table
        music_ids = [item[0] for item in get_all_entries(cursor, "music", "music_id")]
    else:
        # check if all IDs are in the table
        music_ids = [music_ids] if type(music_ids) == int else music_ids
        all_ids = [item[0] for item in get_all_entries(cursor, "music", "music_id")]
        not_found = [id for id in music_ids if id not in all_ids]
        if not_found:
            raise ValueError(f"ID(s) '{', '.join(not_found)}' not found in table 'music'")
    if not column_names:
        # default column names to all columns in all tables
        column_names = {id_type: get_column_names(cursor, id_type) for id_type in ['music', 'albums', 'artists']}
    else:
        # check if all columns are in
        for table in column_names.keys():
            all_columns = get_column_names(cursor, table)
            not_found = [column for column in column_names[table] if column not in all_columns]
            if not_found:
                raise ValueError(f"Column(s) '{', '.join(not_found)}' not found in table '{table}'")

    # get data
    data = {}
    for id in music_ids:
        data[id] = {}
        for table in column_names.keys():
            if table == 'music':
                cursor.execute(f"SELECT {', '.join(column_names[table])} FROM {table} WHERE music_id = ?", (id,))
                row = cursor.fetchone()
                for column in column_names[table]:
                    data[id][column] = row[column_names[table].index(column)]
            elif table == 'albums':
                cursor.execute(f"SELECT album_id FROM music WHERE music_id = ?", (id,))
                album_id = cursor.fetchone()[0]
                cursor.execute(f"SELECT {', '.join(column_names[table])} FROM {table} WHERE album_id = ?", (album_id,))
                row = cursor.fetchone()
                for column in column_names[table]:
                    data[id][column] = row[column_names[table].index(column)]
            elif table == 'artists':
                # because multiple artists can be associated with a music, each artist-related columns are lists
                cursor.execute(f"SELECT artist_id FROM artists_music WHERE music_id = ?", (id,))
                artist_ids = [item[0] for item in cursor.fetchall()]
                data[id]['artists'] = []
                for artist_id in artist_ids:
                    cursor.execute(f"SELECT {', '.join(column_names[table])} FROM {table} WHERE artist_id = ?", (artist_id,))
                    row = cursor.fetchone()
                    data[id]['artists'].append({column: row[column_names[table].index(column)] for column in column_names[table]})
            else:
                raise ValueError(f"Table '{table}' not found or implemented")
    if cursor_is_local:
        conn.close()
    return data
    


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    ids = [1, 2, 3]
    # musics = get_data_by_musicid(cursor, ids)
    musics = get_data_by_musicid(cursor, ids, 
                                 {'music': ['music_id', 'title', 'duration'], 
                                  'albums': ['album_id', 'album_name'], 
                                  'artists': ['artist_id', 'artist_name']})
    logging.info(musics[1])
    
    logging.info(get_musicids_by_albumid(cursor, [1, 2]))
    logging.info(get_albums_by_albumid(cursor, [1, 2], ['album_id', 'album_name']))

    conn.close()
    