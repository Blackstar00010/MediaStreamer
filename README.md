# MediaStreamer

My media(audio for now) streaming service. Used to replace existing services such as Plex/Jellyfin/Emby, but more suited to my own needs.

## Folder Structure

```plaintext
proj/
│── media.db                  # SQLite database file
│── .env                      # Environment variables
│── requirements.txt          # Python dependencies
│── docker-compose.yml        # Docker setup (if using Docker)
│── README.md                 # Project documentation
|── .venv/                    # Virtual environment (Python)
│── .git/                     # Git directory
│── media/                    # Media folder (stores audio files)
│── src/                      # Source code directory
│   ├── backend/                  # Backend (mostly python ig)
│   │   ├── db/                       # Database-related scripts
│   │   │   ├── schema.py                 # Database schema setup
│   │   │   ├── scan_media.py             # Script to scan media folder
│   │   ├── api/                      # FastAPI or Flask API
│   │   │   ├── main.py                   # Main backend API entry point
│   │   │   ├── routes.py                 # API routes
│   │   │   ├── models.py                 # Database models (if using SQLAlchemy)
│   │   │   ├── utils.py                  # Utility functions
│   │   ├── services/                 # Business logic (metadata extraction, streaming)
│   │   │   ├── metadata.py               # Extract metadata from audio files
│   │   │   ├── streamer.py               # Handle audio streaming
│   ├── frontend/                 # Frontend (React, probably)
│   │   ├── public/                   # Static assets (favicons, index.html, etc.)
│   │   ├── src/                      # React source code
│   │   │   ├── components/               # UI components (buttons, players, etc.)
│   │   │   ├── pages/                    # Page components (Home, Library, etc.)
│   │   │   ├── api/                      # API calls to backend
│   │   │   ├── App.js                    # Main React component
│   │   │   ├── index.js                  # React entry point
│   │   ├── package.json              # Frontend dependencies
│   │   ├── vite.config.js            # Vite (or webpack) config
```

## Roadmap
- Phase 1: Basic File Management & Scanning
    1. Structure the whole project
    2. Set the Target Directory
       - Make a folder named "media" to store all the media files.
       - Optional: allow dynamic changes to this directory; configuration file or some UI.
    3. Scan the Directory for Music Files
        - Store metadata (filename, path, artist, album, duration, etc.) in db (sqlite) using python mutagen
        - Periodically scan for new, deleted, or modified files.
- Phase 2: Backend
    4.	Set Up a Web Server
        - Choose backend: FastAPI, Express, or Django
        - Implement REST APIs for listing, searching, and playing.
    5.	Implement Audio Streaming
        - Use HTTP range requests to allow seeking within songs.
        - Stream audio using FFmpeg if transcoding is needed.
- Phase 3: Frontend UI & Player
- Phase 4: Extra Features