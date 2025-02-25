import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { fetchAllAlbums } from "../api/basic";
import "./MainPage.css";

function MainPage() {
    const navigate = useNavigate();
    const [albums, setAlbums] = useState([]);

    useEffect(() => {
        fetchAllAlbums()
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
        alignItems: "stretch",
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
    },
    albumArt: {
        width: "100%",
        height: "auto",
        aspectRatio: "1 / 1", // square aspect ratio
        objectFit: "cover", // ensures images scale properly
        borderRadius: "5px",
    },
};

export default MainPage;