# MediaStreamer

My media(audio for now) streaming service. Used to replace existing services on my homelab such as Plex/Jellyfin/Emby, but more suited to my own needs. For example, random album feature, album rating feature(similar to piku.co.kr), etc.

## Folder Structure

```plaintext
proj/
│── media.db                  # SQLite database file
│── requirements.txt          # Python dependencies
│── README.md                 # Project documentation
|── .venv/                    # Virtual environment (Python)
│── .git/                     # Git directory
│── media/                    # Media folder (stores audio files)
│── src/                      # Source code directory
│   ├── backend/                  # Backend (mostly python ig)
│   │   ├── config.py                 # Configurations
│   │   ├── db/                       # Database-related scripts
│   │   │   ├── db_setup.py               # Database setup script
│   │   │   ├── scan_media.py             # Script to scan media folder
│   │   │   ├── utils.py                  # Utility functions
│   │   ├── api/                      # FastAPI
│   │   │   ├── main.py                   # Main backend API entry point
│   ├── frontend/                 # Frontend (React)
│   │   ├── public/                   # Static assets (favicons, default images, etc.)
│   │   ├── src/                      # React source code
│   │   │   ├── components/               # UI components (players, navbars, etc.)
│   │   │   ├── pages/                    # Page components (home, album, album comparison, etc.)
│   │   │   ├── App.jsx                   # Main React component
│   │   │   ├── index.jsx                 # React entry point
│   │   ├── package.json              # Frontend dependencies
│   │   ├── vite.config.js            # Vite config
```

## Dones and To Dos

- Dones
  - Basic media player
  - Main page that shows all albums
  - Album page that shows all songs in an album + Random album page
  - Album comparison page that shows all songs in two albums
- TODOs
  - Dockerise for easy deployment
  - Settings page
  - Loading screen
  - Search & sort
    - Search bar
    - Sort by album name, artist name, etc.
  - Playlists
  - Allow users to edit metadata such as artists, etc.
  - All musics page
  - Video integration
  - Image integration?
  - Users

## How to run

For backend,

```shell
uvicorn backend.api.main:app --reload
```

For frontend, while the backend is running,

```shell
npm run dev
```
