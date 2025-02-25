import React, { useState, useEffect } from "react";
import "./ComparePage.css";

const ComparePage = () => {
    const [albums, setAlbums] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchAlbums();
    }, []);

    const fetchAlbums = async () => {
        setLoading(true);
        try {
            const response = await fetch("http://127.0.0.1:8000/compare_albums");
            const data = await response.json();
            setAlbums(data.albums);
        } catch (error) {
            console.error("Error fetching albums:", error);
        }
        setLoading(false);
    };

    const chooseAlbum = async (winnerId, loserId) => {
        try {
            const response = await fetch("http://127.0.0.1:8000/update_rating", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ winner_id: winnerId, loser_id: loserId }), // Ensure correct JSON keys
            });
            console.log(response);

            if (!response.ok) {
                throw new Error("Failed to update rating");
            }

            fetchAlbums(); // Load new albums after voting
        } catch (error) {
            console.error("Error updating rating:", error);
        }
    };

    if (loading || albums.length < 2) {
        return <h2>Loading albums...</h2>;
    }

    return (
        <div id="compare-container">
            {albums.map((album, index) => (
                <div key={album.id} className="album-card" onClick={() => chooseAlbum(album.id, albums[1 - index].id)}>
                    <img src={album.art || "/album_placeholder.png"} alt={album.name} className="album-art" />
                    <h3>{album.name}</h3>
                    {/* <p>{album.artist}</p> */}
                    <p>Rating Score: {album.rating}</p>
                </div>
            ))}
        </div>
    );
};

export default ComparePage;