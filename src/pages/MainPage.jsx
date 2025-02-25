import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./MainPage.css";

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
            <div style={styles.gridContainer} id="album-grid">
                {albums.map((album) => (
                    <div className="album-card" key={album.key} style={styles.card} onClick={() => navigate(`/album/${album.key}`)}>
                        <img
                            src={album.art || "/album_placeholder.png"}
                            alt={album.name || "Unclassified"}
                            style={styles.albumArt} />
                        <p>{album.name}</p>
                        <p>{album.artist}</p>
                    </div>
                ))}
            </div>
        </>
    );
}

const styles = {
    container: {
        textAlign: "center",
    },
    gridContainer: {
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
        gridAutoRows: "minmax(auto, max-content)", // Match row height to content
        gap: "15px",
        padding: "20px",
        // enable scrolling
        height: '80vh',
        overflowY: 'auto',
        alignItems: "stretch",  // asdfasdf
    },
    card: {
        backgroundColor: "#222",
        color: "#fff",
        padding: "10px",
        textAlign: "center",
        borderRadius: "8px",
        textDecoration: "none",
        // maxHeight: "200px",
        height: "fit-content",
        cursor: "pointer",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        transition: "transform 0.2s ease-in-out",
        "&:hover": {
            transform: "scale(1.05)",
        },
    },
    albumArt: {
        width: "100%",
        height: "auto",
        aspectRatio: "1 / 1", // Maintain square aspect ratio
        objectFit: "cover", // Ensures images scale properly
        borderRadius: "5px",
    },
};

export default MainPage;