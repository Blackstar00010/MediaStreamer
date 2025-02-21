import React, { useState, useEffect } from "react";

function MainPage({ setCurrentSongID }) {
    const [songs, setSongs] = useState([]);
    const [inputId, setInputId] = useState(1);

    useEffect(() => {
        fetch("http://127.0.0.1:8000/songs")
            .then((res) => res.json())
            .then((data) => setSongs(data))
            .catch((error) => console.error("Error fetching songs:", error));
    }, []);

    const handlePlay = () => {
        if (!inputId) return;
        setCurrentSongID(inputId);
    };

    return (
        <>
            <h1>Music Library</h1>

            {/* Input Field & Button */}
            <div style={styles.inputContainer}>
                <input
                    type="number"
                    placeholder="Enter song ID; default is 1648"
                    value={inputId}
                    onChange={(e) => setInputId(e.target.value)}
                    style={styles.input} />
                <button onClick={handlePlay} style={styles.button}>Enter</button>
            </div>

            {/* Song List */}
            <div style={styles.gridContainer}>
                {songs.map((song) => (
                    <div key={song.id} style={styles.card}>
                        {/* TODO: add backend logic to send artworks */}
                        <img
                            src={song.album_art || null}
                            alt={song.title}
                            style={styles.albumArt} />
                        <p>{song.title}</p>
                        <p>{song.artist}</p>
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