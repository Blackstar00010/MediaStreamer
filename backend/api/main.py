from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, Response
import sqlite3
import os
import mimetypes
from backend.config import DB_PATH

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Music Streaming API!"}


@app.get("/songs")
def get_songs():
    """Fetch all songs from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, artist, album FROM music")
    songs = cursor.fetchall()
    conn.close()

    return [
        {"id": song[0], "title": song[1], "artist": song[2], "album": song[3]}
        for song in songs
    ]


@app.get("/songs/{song_id}")
def get_song(song_id: int):
    """Fetch metadata for a specific song by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM music WHERE id = ?", (song_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Song not found")

    # Get column names dynamically
    columns = [desc[0] for desc in cursor.description]

    # Convert row data into a dictionary
    song_data = dict(zip(columns, row))

    return song_data


def get_song_path(song_id: int) -> str:
    """Fetch the file path of a song by ID from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM music WHERE id = ?", (song_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None
    return row[0]  # Extract file path from the result


@app.get("/stream/{song_id}")
def stream_song(song_id: int, request: Request):
    """Stream an audio file by song ID."""
    file_path = get_song_path(song_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Song not found")
    file_size = os.path.getsize(file_path)  # TODO: add file size to db

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


@app.get("/album/{album_id}")
def get_album(album_id: str):
    """Fetch all tracks in a specific album."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, album, title, artist FROM music WHERE album_id = ?", (album_id,))
    tracks = cursor.fetchall()
    conn.close()

    if not tracks:
        raise HTTPException(status_code=404, detail="Album not found")

    return {
        "album_id": album_id,
        "album_name": tracks[1],
        "tracks": [{"id": track[0], "title": track[2], "artist": track[3]} for track in tracks],
    }
