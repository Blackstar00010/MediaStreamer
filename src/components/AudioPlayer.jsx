import React, { useState, useRef, useEffect } from "react";

const AudioPlayer = ({ songUrl }) => {
    const audioRef = useRef(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [progress, setProgress] = useState(0);
    const [volume, setVolume] = useState(1.0);

    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        const updateProgress = () => {
            setProgress((audio.currentTime / audio.duration) * 100);
        };

        audio.addEventListener("timeupdate", updateProgress);
        return () => audio.removeEventListener("timeupdate", updateProgress);
    }, []);

    const togglePlay = () => {
        if (isPlaying) {
            audioRef.current.pause();
        } else {
            audioRef.current.play();
        }
        setIsPlaying(!isPlaying);
    };

    const handleSeek = (e) => {
        const newTime = (e.target.value / 100) * audioRef.current.duration;
        audioRef.current.currentTime = newTime;
        setProgress(e.target.value);
    };

    const handleVolumeChange = (e) => {
        const newVolume = e.target.value;
        setVolume(newVolume);
        audioRef.current.volume = newVolume;
    };

    return (
        <div style={styles.playerContainer}>
            <audio ref={audioRef} src={songUrl} preload="metadata"></audio>

            <button onClick={togglePlay} style={styles.button}>
                {isPlaying ? "⏸" : "▶️"}
            </button>
            {/* TODO: use font awesome
            npm install @fortawesome/react-fontawesome @fortawesome/free-solid-svg-icons
            then do
            import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
            import { faPlay, faPause } from "@fortawesome/free-solid-svg-icons";

            <button onClick={togglePlay} style={styles.button}>
                <FontAwesomeIcon icon={isPlaying ? faPause : faPlay} />
            </button>
            */}

            <input
                type="range"
                value={progress}
                onChange={handleSeek}
                style={styles.slider}
            />

            <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={volume}
                onChange={handleVolumeChange}
                style={styles.volumeSlider}
            />
        </div>
    );
};

// Inline styles for simplicity (can use CSS or Tailwind later)
const styles = {
    playerContainer: {
        // position: "fixed",
        bottom: 0,
        width: "100%",
        backgroundColor: "#222",
        color: "#fff",
        margin: "10px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "10px",
    },
    button: {
        padding: "10px",
        backgroundColor: "#444",
        color: "white",
        // border: "none",
        cursor: "pointer",
        width: "20%",
        maxWidth: "50px",
        height: "50px",
    },
    slider: {
        width: "80%",
        background: "transparent",
        height: "20px",
    },
    volumeSlider: {
        width: "20%",
        maxWidth: "100px",
    },
};

export default AudioPlayer;