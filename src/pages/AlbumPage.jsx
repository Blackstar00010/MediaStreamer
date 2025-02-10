import React from "react";
import { useParams } from "react-router-dom";

const AlbumPage = () => {
    const { id } = useParams();
    return (
        <div>
            <h1>Album {id}</h1>
            <p>Show tracks from album {id} here.</p>
        </div>
    );
};

export default AlbumPage;