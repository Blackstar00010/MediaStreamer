from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import mimetypes
import random
from backend.config import DB_PATH
from backend.db import queries
# from backend.db.scan_media import get_artist_id_maps
import logging

app = FastAPI()

# enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Music Streaming API!"}

@app.get("/songs")
def get_songs():
    """Fetch all songs from the database."""
    data = queries.get_musics_by_musicid(
        cursor=None, music_ids=None, 
        column_names=["music_id", "title", "artist", "album"])
    return data


@app.get("/songs/{song_id}")
def get_song(song_id: int):
    """Fetch metadata for a specific song by ID."""
    data = queries.get_data_by_musicid(
        cursor=None, music_ids=[song_id], 
        column_names={"music": ["music_id", "title", "file_path"], "artists": ["artist_name"], "albums": ["album_name"]})
    if not data:
        raise HTTPException(status_code=404, detail="Song not found")
    return data[song_id]


def get_song_path(song_id: int) -> str:
    """Fetch the file path of a song by ID from the database."""
    data = queries.get_data_by_musicid(
        cursor=None, music_ids=[song_id], 
        column_names={"music": ["file_path"]}
    )
    # print(data)
    if not data:
        raise HTTPException(status_code=404, detail="Song not found")
    return data[song_id]["file_path"]


@app.get("/stream/{song_id}")
def stream_song(song_id: int, request: Request):
    """Stream an audio file by song ID."""
    file_path = get_song_path(song_id)
    file_size = os.path.getsize(file_path)  # TODO: add file size to db?

    # NOTE: without html5 audio player, the browser will download the file if the mime type is not audio/mpeg
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"  # Fallback if unknown

    range_header = request.headers.get("range")
    if range_header:
        print(range_header)
        # Parse the "Range" header (Example: "bytes=1000-")
        range_value = range_header.replace("bytes=", "").strip()
        start, end = range_value.split(
            "-") if "-" in range_value else (None, None)

        # If not specified, start = 0 and end = full file
        start = int(start) if start else 0
        end = int(end) if end else file_size - 1

        # Ensure valid range
        if start >= file_size:
            raise HTTPException(
                status_code=416, detail="Requested Range Not Satisfiable"
            )

        chunk_size = end - start + 1

        def file_iterator():
            with open(file_path, "rb") as f:
                f.seek(start)  # Move to requested position
                while chunk := f.read(min(1024 * 64, chunk_size)):  # Read in chunks
                    yield chunk

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(chunk_size),
            "Content-Type": mime_type,
        }

        return StreamingResponse(file_iterator(), status_code=206, headers=headers)

    # If no Range header, serve the full file
    headers = {
        "Content-Length": str(file_size),
        "Content-Type": mime_type,
        "Accept-Ranges": "bytes",
    }
    try:
        def full_file_iterator():
            with open(file_path, "rb") as f:
                while chunk := f.read(1024 * 64):  # Read in 64 KB chunks
                    yield chunk

        return StreamingResponse(
            full_file_iterator(),
            media_type=mime_type,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error streaming file: {str(e)}")


@app.get("/albums")
def get_albums():
    """Fetch all albums from the database, sorted by rating."""
    album_data = queries.get_albums_by_albumid(
        cursor=None, album_ids=None, 
        column_names=["album_id", "album_name", "album_art", "album_rating"])
    # because album-artist link is many-to-many, we need to fetch artist data separately
    artists = queries.get_artists_by_albumid(
        cursor=None, album_ids=None, 
        column_names=["artist_name"])
    # merge artist data into album data
    for album_id in album_data.keys():
        album_data[album_id]["artist"] = artists.get(album_id, None)
    # sort by rating, by default
    album_data = list(album_data.values())
    album_data.sort(key=lambda x: x["album_rating"], reverse=True)
    return album_data


@app.get("/album/{album_id}")
def get_album(album_id: int):
    """Fetch all tracks in a specific album, including artists."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch album name and album art
    try:
        data = queries.get_albums_by_albumid(cursor, [album_id], ["album_name", "album_art"])
    except ValueError as e:
        if e.args[0].startswith("Album ID(s) "):
            raise HTTPException(status_code=404, detail="Album not found")
        else:
            raise e
    album_name = data[album_id]["album_name"]
    album_art = data[album_id]["album_art"]
    
    artists = queries.get_artists_by_albumid(cursor, [album_id], ["artist_name"])
    album_artists = [artist["artist_name"] for artist in artists.get(album_id, [])]
    if album_artists:
        album_artists.sort()
        album_artists = ', '.join(album_artists)

    # Fetch tracks in the album (including music IDs)
    music_ids = queries.get_musicids_by_albumid(cursor, album_id)[album_id]
    music_data = list(queries.get_data_by_musicid(cursor, music_ids, {"music": ["music_id", "tracknumber", "title", "file_path"], "artists": ["artist_name"]}).values())
    print(music_data[0])
    ret = {
        "album_id": album_id,
        "album_name": album_name,
        "album_art": album_art,
        "album_artists": album_artists,
        "tracks": music_data
    }
    return ret
    # cursor.execute("SELECT music_id, tracknumber, title, file_path FROM music WHERE album_id = ?", (album_id,))
    # tracks = cursor.fetchall()

    # # Fetch artist IDs associated with these tracks
    # music_ids = [track[0] for track in tracks]
    # track_artist_map = get_artist_id_maps(cursor, music_ids)
    # artists = {}
    # for music_id, artist_ids in track_artist_map.items():
    #     cursor.execute(f"SELECT artist_name FROM artists WHERE artist_id IN ({','.join('?' * len(artist_ids))})", artist_ids)
    #     artist_names = [row[0] for row in cursor.fetchall()]
    #     artists[music_id] = ', '.join(artist_names) if artist_names else None

    # # Fetch album artists
    # cursor.execute("SELECT artist_id from artists_albums WHERE album_id = ?", (album_id,))
    # artist_ids = [row[0] for row in cursor.fetchall()]
    # cursor.execute(f"SELECT artist_name FROM artists WHERE artist_id IN ({','.join('?' * len(artist_ids))})", artist_ids)
    # album_artists = [row[0] for row in cursor.fetchall()]
    # album_artists.sort()
    # album_artists = ', '.join(album_artists)

    # conn.close()
    
    # # Process the response
    # ret = {
    #     "album_id": album_id,
    #     "album_name": album_name,
    #     "album_art": album_art,
    #     "album_artists": album_artists,
    #     "tracks": [
    #         {
    #             "id": track[0],
    #             "track_number": track[1],
    #             "title": track[2],
    #             "artist": artists.get(track[0], None),
    #         }
    #         for track in tracks
    #     ]
    # }

    # # print(ret)
    # return ret


@app.get("/random_album")
def get_random_album():
    """Fetch a random album ID from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT album_id FROM albums WHERE album_name IS NOT NULL")
    album_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not album_ids:
        raise HTTPException(status_code=404, detail="No albums found")

    random_album_id = random.choice(album_ids)
    print(random_album_id)
    return {"album_id": random_album_id}


def get_album_name(album_id):
    """Fetch the name of an album by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT album_name FROM albums WHERE album_id = ?", (album_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def get_elo_rating(album_id):
    """Fetch the Elo rating of an album."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT album_rating FROM albums WHERE album_id = ?", (album_id,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        logging.info(f"No rating found for album ID {album_id}")
    return result[0] if result else 1000

@app.get("/compare_albums")
def compare_albums():
    """Fetch two random albums for comparison."""
    album_ids = queries.get_all_entries(None, "albums", ["album_id"])
    if len(album_ids) < 2:
        raise HTTPException(status_code=404, detail="Not enough albums to compare.")
    random.shuffle(album_ids)
    album_ids = [item[0] for item in album_ids[:2]]
    data = queries.get_albums_by_albumid(
        cursor=None, album_ids=album_ids,
        column_names=["album_id", "album_name", "album_art", "album_rating"])
    ret = [data[album_ids[0]], data[album_ids[1]]]
    
    artists = queries.get_artists_by_albumid(
        cursor=None, album_ids=album_ids, 
        column_names=["artist_name"])
    for i in range(2):
        ret[i]["album_artists"] = [item['artist_name'] for item in artists.get(album_ids[i], [])]
    return ret


@app.post("/update_rating")
async def update_rating(request: Request):
    """Update the Elo ratings of two albums after a comparison."""
    data = await request.json()  # Manually parse JSON
    print("Received data:", data)  # Debugging log

    winner_id = data.get("winner_id")
    loser_id = data.get("loser_id")

    if not isinstance(winner_id, int) or not isinstance(loser_id, int):
        raise HTTPException(status_code=400, detail="Invalid input data")

    # Fetch current ratings
    winner_elo = get_elo_rating(winner_id)
    loser_elo = get_elo_rating(loser_id)

    K = 32  # Elo rating adjustment factor

    # Expected scores
    expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    expected_loser = 1 - expected_winner

    # Update ratings
    new_winner_elo = round(winner_elo + K * (1 - expected_winner))
    new_loser_elo = round(loser_elo + K * (0 - expected_loser))

    # Update database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE albums SET album_rating = ? WHERE album_id = ?", (new_winner_elo, winner_id))
    cursor.execute("UPDATE albums SET album_rating = ? WHERE album_id = ?", (new_loser_elo, loser_id))
    conn.commit()
    conn.close()

    return {"message": "Elo ratings updated", "winner_new_elo": new_winner_elo, "loser_new_elo": new_loser_elo}

