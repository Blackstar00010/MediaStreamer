import React, { useState, useEffect } from "react";
import { fetchComparisonAlbums, updateEloRating } from "../api/basic";
import "./ComparePage.css";

const ComparePage = () => {
    const [albums, setAlbums] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchAlbums();
    }, []);

    // for now db is small but in future we might use pagination
    const fetchAlbums = async () => {
        setLoading(true);
        try {
            const data = await fetchComparisonAlbums();
            // console.log(data);
            setAlbums(data);
        } catch (error) {
            console.error("Error fetching albums:", error);
        }
        setLoading(false);
    };

    const chooseAlbum = async (winnerId, loserId) => {
        try {
            await updateEloRating(winnerId, loserId);
            // Load new albums after voting
            fetchAlbums();
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
                <div key={album.album_id} className="album-card" onClick={() => chooseAlbum(album.album_id, albums[1 - index].album_id)}>
                    <img src={album.album_art || "/album_placeholder.png"} alt={album.album_name} className="album-art" />
                    <h3>{album.album_name}</h3>
                    <p>
                        {
                            album.album_artists && album.album_artists.join(", ")
                        }
                    </p>
                    <p>Rating Score: {album.album_rating}</p>
                </div>
            ))}
        </div>
    );
};

export default ComparePage;