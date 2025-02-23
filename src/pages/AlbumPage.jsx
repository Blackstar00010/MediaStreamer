import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import './AlbumPage.css';

const AlbumPage = ({ setCurrentSongID, setQueue, setBackQueue }) => {
    // retrieve the albumID from the URL. e.g. .../album/1 -> albumID = 1
    const { albumID } = useParams();
    // information to display
    const [albumName, setAlbumName] = useState("");
    const [artistName, setArtistName] = useState("");
    const [albumArt, setAlbumArt] = useState("");
    const [tracks, setTracks] = useState([]);
    // album info and track list are vertically stacked on narrow screens
    const [isVertical, setIsVertical] = useState(window.innerWidth <= 1020);
    const albumContentsRef = useRef(null);
    // Redirect to 404 if album not found
    const navigate = useNavigate();

    // when the album contents change, check if the tracklist is wrapped i.e. vertical
    useEffect(() => {
        const observer = new ResizeObserver(() => {
            if (albumContentsRef.current) {
                console.log(albumContentsRef.current.scrollHeight, albumContentsRef.current.clientHeight);
                const isWrapped = albumContentsRef.current.scrollHeight > albumContentsRef.current.clientHeight * 1.1;
                // console.log(isWrapped);
                setIsVertical(isWrapped);
            }
        });

        if (albumContentsRef.current) {
            observer.observe(albumContentsRef.current);
        }

        return () => {
            if (albumContentsRef.current) {
                observer.unobserve(albumContentsRef.current);
            }
        };
    }, []);

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

    return (
        <div id="album-contents" style={styles.albumContents} className={isVertical ? "vertical" : "horizontal"} ref={albumContentsRef}>
            <div id="album-info-container" style={styles.albumInfoContainer}>
                {/* Display album art (if available) */}
                {albumArt ? (
                    <img src={albumArt} alt="Album Cover" id="album-art" style={styles.albumArt} className={isVertical ? "vertical" : "horizontal"} />
                ) : (
                    <img src="/icon1415.png" alt="Default Album Cover" id="album-art" style={styles.albumArt} className={isVertical ? "vertical" : "horizontal"} />
                )}
                <h1 style={{ marginLeft: "0" }}>{albumName}</h1>
                <h2 style={{ marginLeft: "0" }}>{artistName}</h2>

            </div>
            <div id="tracklist-container" style={styles.tracklistContainer} className={isVertical ? "vertical" : "horizontal"}>
                <ul id="tracklist" style={styles.tracklist}>
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
        </div>
    );
};

// Styles
const styles = {
    albumContents: {
        textAlign: "left",
        width: "80%",
        maxHeight: "90vh",
        margin: "auto",
        display: "flex",
        flexDirection: "row", // Default: side-by-side layout
        justifyContent: "center",
        alignItems: "flex-start",
        flexWrap: "wrap", // Allow wrapping when the screen is too narrow
        padding: "30px",
    },
    albumInfoContainer: {
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-start",
        margin: "20px",
        textAlign: "center",
        flex: "1 1 300px", // Grow/shrink, but won't go below 300px
    },
    albumArt: {
        maxWidth: "500px",
        maxHeight: "500px",
        width: "100%", // Ensures it scales down
        height: "auto",
        minWidth: "200px", // Prevents shrinking below 200px
        borderRadius: "8px",
        margin: "auto",
    },
    tracklistContainer: {
        flex: "2 1 500px",
        overflowY: "auto", // Enable scrolling for tracklist (side-by-side)
        // height: "90vh",
        // width: "100%",
        width: "fit-content",
        paddingRight: "15px",
        padding: 0,
        paddingRight: "20px",  // for scroll bar
        overflowY: "auto",
        textAlign: "left",
        flex: "2 1 500px", // Allows shrinking, moves below if needed
    },
    tracklist: {
        listStyleType: "none",
        padding: 0,
    },
    trackItem: {
        margin: "30px 0",
        textAlign: "left",
    },
    trackButton: {
        background: "none",
        border: "none",
        color: "#fff",
        fontSize: "16px",
        cursor: "pointer",
        display: "flex",
        flexDirection: "row",
        alignItems: "left",
        width: "100%",
    },
    // albumContents: {
    //     display: "flex",
    //     flexDirection: "row", // Default: Side-by-side
    //     justifyContent: "center",
    //     alignItems: "flex-start",
    //     flexWrap: "wrap", // Allows tracklist to move below album art
    //     height: "100vh", // Full viewport height
    //     overflow: "hidden", // Prevents double scrolling in side-by-side mode
    // },
    // albumInfoContainer: {
    //     display: "flex",
    //     flexDirection: "column",
    //     justifyContent: "flex-start",
    //     margin: "20px",
    //     textAlign: "left",
    //     flex: "1 1 300px", // Allows shrinking, min width 300px
    // },
    // albumArt: {
    //     maxWidth: "500px",
    //     maxHeight: "500px",
    //     width: "100%",
    //     height: "auto",
    //     minWidth: "200px",
    //     borderRadius: "8px",
    // },
    // tracklistContainer: {
    //     flex: "2 1 500px",
    //     overflowY: "auto", // Enable scrolling for tracklist (side-by-side)
    //     height: "80vh",
    //     paddingRight: "15px",
    // },
};

export default AlbumPage;