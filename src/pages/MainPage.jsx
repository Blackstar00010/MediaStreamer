import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { fetchAllAlbums } from "../api/basic";
import "./MainPage.css";

function MainPage() {
    const navigate = useNavigate();
    const [albums, setAlbums] = useState([]);

    useEffect(() => {
        fetchAllAlbums()
            .then((data) => {
                console.log("Fetched albums:", data);
                setAlbums(data);
            })
            .catch((error) => console.error("Error fetching albums:", error));
    }, []);

    return (
        <>
            <h1>All Albums</h1>
            <div style={styles.gridContainer} id="album-grid">
                {albums.map((album) => (
                    <div className="album-card" key={album.album_id} style={styles.card} onClick={() => navigate(`/album/${album.album_id}`)}>
                        <img
                            src={album.album_art || "/album_placeholder.png"}
                            alt={album.album_name || "Unclassified"}
                            style={styles.albumArt} />
                        <p>{album.album_name}</p>
                        <p>
                            {album.artist && album.artist.map((artist) => artist.artist_name).join(", ")}
                        </p>
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