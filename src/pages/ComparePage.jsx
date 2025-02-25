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
            console.log(data);
            setAlbums(data.albums);
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