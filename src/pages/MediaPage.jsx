import React from "react";
import { useParams } from "react-router-dom";

const MediaPage = () => {
    const { id } = useParams();
    return (
        <div>
            <h1>Media {id}</h1>
            <p>Show details for media {id} here.</p>
        </div>
    );
};

export default MediaPage;