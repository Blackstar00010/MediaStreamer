import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

const AlbumPage = ({ setCurrentSongID }) => {
    const { albumID } = useParams();
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
                    setArtistName(data.album_artists);
                    setAlbumArt(data.album_art);
                    setTracks(data.tracks);
                }
            })
        // .catch(() => navigate("/404"));
    }, [albumID, navigate]);

    console.log(tracks);

    // sort by track number
    tracks.sort((a, b) => a.track_number - b.track_number);

    return (
        <div style={styles.container}>
            <div style={styles.albumContents}>
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
                <ul style={styles.tracklist}>
                    {tracks.map((track) => (
                        <li key={track.track_number} style={styles.trackItem}>
                            <button onClick={() => setCurrentSongID(track.id)} style={styles.trackButton}>
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
        </div>
    );
};

// Styles
const styles = {
    container: {
        textAlign: "center",
        padding: "20px",
        maxWidth: "80%",
        margin: 'auto',
    },
    albumContents: {
        // display items inside it side by side
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
    },
    albumInfoContainer: {
        // don't vertically center align; stick the image at the top
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'flex-start',
        // alignItems: 'center',
        margin: '20px',
        // text align to left
        textAlign: 'left',
    },
    albumArt: {
        width: "500px",
        height: "500px",
        borderRadius: "8px",
    },
    tracklist: {
        listStyleType: "none",
        padding: 0,
        margin: "30px",
        // enable scrolling
        overflowY: 'auto',
        // set the height of the container
        height: '80vh',
        // left aligh
        textAlign: 'left',

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
        textAlign: "left",
        // side by side, left align
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
};

export default AlbumPage;