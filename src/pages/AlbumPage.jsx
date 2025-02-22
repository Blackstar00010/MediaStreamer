import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

const AlbumPage = ({ setCurrentSongID, queue, setQueue, backQueue, setBackQueue }) => {
    const { albumID } = useParams();  // retrieve the albumID from the URL. e.g. .../album/1 -> albumID = 1
    const [albumName, setAlbumName] = useState("");
    const [artistName, setArtistName] = useState("");
    const [albumArt, setAlbumArt] = useState("");
    const [tracks, setTracks] = useState([]);
    const navigate = useNavigate(); // Redirect to 404 if album not found

    useEffect(() => {
        fetch(`http://127.0.0.1:8000/album/${albumID}`)
            .then((res) => {
                // only route if the response is 404
                if (res.status === 404) {
                    navigate("/404");
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
                    setArtistName(data.album_artists);
                    setAlbumArt(data.album_art);
                    setTracks(data.tracks);
                }
            })
            .catch(() => navigate("/404"));
    }, [albumID, navigate]);

    const PlaySong = (track) => {
        setCurrentSongID(track.id);
        setQueue(tracks.slice(track.track_number).map((track) => track.id));
        var newBackQueue = tracks.slice(0, track.track_number - 1).map((track) => track.id);
        newBackQueue.reverse();
        setBackQueue(newBackQueue);
        console.log('queue: ', tracks.slice(track.track_number).map((track) => track.id));
        console.log('backQueue: ', newBackQueue);
    };

    // sort by track number
    tracks.sort((a, b) => a.track_number - b.track_number);

    // Add responsive styles
    useEffect(() => {
        const styleTag = document.createElement("style");
        styleTag.innerHTML = responsiveStyles;
        document.head.appendChild(styleTag);
        return () => {
            document.head.removeChild(styleTag);
        };
    }, []);

    return (
        <div style={styles.albumContents} className="albumContents">
            <div className="album-info-container" style={styles.albumInfoContainer}>
                {/* Display album art (if available) */}
                {albumArt ? (
                    <img src={albumArt} alt="Album Cover" style={styles.albumArt} />
                ) : (
                    <img src="/icon1415.png" alt="Default Album Cover" style={styles.albumArt} />
                )}
                <h1 style={{ marginLeft: "0" }}>{albumName}</h1>
                <h2 style={{ marginLeft: "0" }}>{artistName}</h2>

            </div>
            <ul style={styles.tracklist} className="tracklist">
                {tracks.map((track) => (
                    <li key={track.track_number} style={styles.trackItem}>
                        <button onClick={() => PlaySong(track)} style={styles.trackButton}>
                            <div style={{ marginRight: "10px", display: "inline-block", width: "30px" }}>
                                {track.track_number}
                            </div>
                            <div style={{ textAlign: "left", display: "inline-block" }}>
                                <div>{track.title}</div>
                                {track.artist !== artistName && track.artist !== undefined &&
                                    // if the artist is different from the album artist, display the rest of the artist name
                                    // replace all but last, replace last
                                    <div>{track.artist.replace(artistName + ", ", "").replace(", " + artistName, "")}</div>
                                }
                            </div>
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

// Styles
const styles = {
    container: {
        textAlign: "left",
        padding: "20px",
        width: "80%",
        margin: "auto",
    },
    albumContents: {
        display: "flex",
        flexDirection: "row", // Default: side-by-side layout
        justifyContent: "center",
        alignItems: "flex-start",
        flexWrap: "wrap", // Allow wrapping when the screen is too narrow
    },
    albumInfoContainer: {
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-start",
        margin: "20px",
        textAlign: "left",
        flex: "1 1 300px", // Grow/shrink, but won't go below 300px
    },
    albumArt: {
        maxWidth: "500px",
        maxHeight: "500px",
        width: "100%", // Ensures it scales down
        height: "auto",
        minWidth: "200px", // Prevents shrinking below 200px
        borderRadius: "8px",
    },
    tracklist: {
        listStyleType: "none",
        padding: 0,
        paddingRight: "20px",  // for scroll bar
        margin: "30px",
        overflowY: "auto",
        height: "80vh",
        textAlign: "left",
        flex: "2 1 500px", // Allows shrinking, moves below if needed
    },
    trackItem: {
        margin: "30px 0",
    },
    trackButton: {
        background: "none",
        border: "none",
        color: "#fff",
        fontSize: "16px",
        cursor: "pointer",
        display: "flex",
        flexDirection: "row",
        justifyContent: "space-between",
        alignItems: "center",
        width: "100%",
    },
};

// Responsive styles
const responsiveStyles = `
@media (max-width: 800px) {
    .albumContents {
        flex-direction: column !important; /* Move tracklist below album info */
        height: auto !important; /* Allow scrolling */
        overflow-y: visible !important; /* Allow tracklist to grow */
        align-items: center !important;
    }
    .albumInfoContainer {
        text-align: center !important;
    }
    .albumArt {
        max-width: 200px !important; /* Shrink album art further */
    }
    .tracklist {
        width: 100% !important; /* Make tracklist take full width */
        height: auto !important;
        overflow-y: visible !important; /* Allow tracklist to grow */
    }
}
`;

export default AlbumPage;