from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import sqlite3
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
def stream_song(song_id: int):
    """Stream an audio file by song ID."""
    file_path = get_song_path(song_id)

    if not file_path:
        raise HTTPException(status_code=404, detail="Song not found")

    # NOTE: without html5 audio player, the browser will download the file if the mime type is not audio/mpeg
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"  # Fallback if unknown

    print(mime_type)

    try:

        def file_iterator():
            with open(file_path, "rb") as f:
                while chunk := f.read(1024 * 64):  # Read in 64 KB chunks
                    yield chunk

        return StreamingResponse(
            file_iterator(),
            media_type=mime_type,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error streaming file: {str(e)}")
