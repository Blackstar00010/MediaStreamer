import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

function MainPage({ setCurrentSongID }) {
    const navigate = useNavigate();
    const [albums, setAlbums] = useState([]);

    useEffect(() => {
        fetch("http://127.0.0.1:8000/albums")
            .then((res) => res.json())
            .then((data) => setAlbums(data))
            .catch((error) => console.error("Error fetching albums:", error));
    }, []);

    return (
        <>
            <h1>All Albums</h1>
            <div style={styles.gridContainer}>
                {albums.map((album) => (
                    <Link to={`/album/${album.key}`} key={album.key}>
                        <div style={styles.card}>
                            <img
                                src={album.art || "/album_placeholder.png"}
                                alt={album.name || "Unclassified"}
                                style={styles.albumArt} />
                            <p>{album.name}</p>
                            <p>{album.artist}</p>
                        </div>
                    </Link>
                ))}

                {/* {songs.map((song) => (
                    <div key={song.id} style={styles.card}>
                        <img
                            src={song.album_art || null}
                            alt={song.title}
                            style={styles.albumArt} />
                        <p>{song.title}</p>
                        <p>{song.artist}</p>
                    </div>
                ))} */}
            </div>
        </>
    );
}

const styles = {
    container: {
        textAlign: "center",
    },
    inputContainer: {
        margin: "20px 0",
        display: "flex",
        justifyContent: "center",
        gap: "10px",
    },
    input: {
        padding: "10px",
        fontSize: "16px",
        width: "150px",
    },
    button: {
        padding: "10px",
        backgroundColor: "#444",
        color: "white",
        border: "none",
        cursor: "pointer",
        fontSize: "16px",
    },
    gridContainer: {
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))",
        gap: "15px",
        padding: "20px",
        // enable scrolling
        overflowY: 'auto',
        // set the height of the container
        height: '80vh',
    },
    card: {
        backgroundColor: "#222",
        color: "#fff",
        padding: "10px",
        textAlign: "center",
        borderRadius: "8px",
    },
    albumArt: {
        width: "100%",
        height: "auto",
        borderRadius: "5px",
    },
};

export default MainPage;