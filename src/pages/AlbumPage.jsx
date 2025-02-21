import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

const AlbumPage = ({ setCurrentSongID }) => {
    const { albumID } = useParams();
    const [albumName, setAlbumName] = useState("");
    const [albumArt, setAlbumArt] = useState("");
    const [tracks, setTracks] = useState([]);
    const navigate = useNavigate(); // Redirect to 404 if album not found

    useEffect(() => {
        fetch(`http://127.0.0.1:8000/album/${albumID}`)
            .then((res) => {
                // only route if the response is 404
                if (res.status === 404) {
                    // navigate("/404");
                    return null;
                } else if (!res.ok) {
                    throw new Error('Network response was not ok');
                }
                return res.json();
            })
            .then((data) => {
                // console.log(data);
                if (data) {
                    setAlbumName(data.album_name);
                    setAlbumArt(data.album_art);
                    setTracks(data.tracks);
                }
            })
        // .catch(() => navigate("/404"));
    }, [albumID, navigate]);
    // console.log(albumArt);

    return (
        <div style={styles.container}>
            <h1>{albumName}</h1>
            <div style={styles.albumContents}>
                <div className="album-art-container" style={styles.albumArtContainer}>
                    {/* Display album art (if available) */}
                    {albumArt ? (
                        <img src={albumArt} alt="Album Cover" style={styles.albumArt} />
                    ) : (
                        <img src="/icon1415.png" alt="Default Album Cover" style={styles.albumArt} />
                    )}
                </div>
                <ul style={styles.tracklist}>
                    {tracks.map((track) => (
                        <li key={track.id} style={styles.trackItem}>
                            <button onClick={() => setCurrentSongID(track.id)} style={styles.trackButton}>
                                {track.title} - {track.artist}
                            </button>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

// Styles
const styles = {
    container: {
        textAlign: "center",
        padding: "20px",
        margin: 'auto',
    },
    albumContents: {
        // display items inside it side by side
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
    },
    albumArtContainer: {
        // don't vertically center align; stick the image at the top
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'flex-start',
        alignItems: 'center',
        margin: '20px',

    },
    albumArt: {
        width: "500px",
        height: "500px",
        borderRadius: "8px",
    },
    tracklist: {
        listStyleType: "none",
        padding: 0,
        // enable scrolling
        overflowY: 'auto',
        // set the height of the container
        height: '80vh',
        // left aligh
        textAlign: 'left',

    },
    trackItem: {
        margin: "10px 0",
    },
    trackButton: {
        background: "none",
        border: "none",
        color: "#fff",
        fontSize: "16px",
        cursor: "pointer",
        textAlign: "left",
    },
};

export default AlbumPage;