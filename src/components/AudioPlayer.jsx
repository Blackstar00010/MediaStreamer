import React, { useState, useRef, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
// import { faPlay, faPause } from "@fortawesome/free-solid-svg-icons";
import { faBackward, faPlay, faPause, faForward } from "@fortawesome/free-solid-svg-icons";
import { width } from "@fortawesome/free-solid-svg-icons/fa0";

const AudioPlayer = ({ songID, setCurrentSongID, queue, setQueue, backQueue, setBackQueue }) => {
    const audioRef = useRef(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [progress, setProgress] = useState(0);
    const [volume, setVolume] = useState(1.0);

    const playNext = () => {
        setQueue(prevQueue => {
            console.log('prevQueue: ', prevQueue);
            if (prevQueue.length === 0) return []; // No songs left

            const nextTrack = prevQueue[0]; // Get first track in queue
            setBackQueue(prevBackQueue => [songID, ...prevBackQueue]); // Move current song to backQueue
            setCurrentSongID(nextTrack); // Set new song

            return prevQueue.slice(1); // Remove first song from queue
        });
    };
    // const playNext = () => {
    //     if (queue.length > 0) {
    //         const nextTrackID = queue[0];
    //         setCurrentSongID(nextTrackID);
    //         setQueue(queue.slice(1));
    //         setBackQueue([songID, ...backQueue]);
    //     }
    // };
    const playPrev = () => {
        // if progress less than 10 seconds, start over
        if (audioRef.current && audioRef.current.currentTime > 10) {
            audioRef.current.currentTime = 0;
            setProgress(0);
            return;
        }
        // if there are previous tracks, play the last one
        if (backQueue.length > 0) {
            const prevTrackID = backQueue[0];
            setBackQueue(backQueue.slice(1));
            setCurrentSongID(prevTrackID);
            setQueue([songID, ...queue]);
        }
    };

    useEffect(() => {
        // Update the audio source when the songID changes, and play the song
        if (audioRef.current && songID) {
            audioRef.current.src = `http://127.0.0.1:8000/stream/${songID}`;
            audioRef.current.play().catch(() => setIsPlaying(false));
            setIsPlaying(true);
            setProgress(0);
        }
    }, [songID]);

    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        const updateProgress = () => {
            setProgress((audio.currentTime / audio.duration) * 100 || 0);
        };
        const handleSongEnd = () => {
            // Play the next song in the queue
            if (queue.length > 0) {
                const nextTrack = queue[0];
                if (nextTrack) {
                    setCurrentSongID(nextTrack.id);
                    setQueue(queue.slice(1));
                }
            } else {
                setIsPlaying(false);
            }
            setBackQueue([songID, ...backQueue]);
            console.log('queue: ', queue);
        };

        audio.addEventListener("timeupdate", updateProgress);
        audio.addEventListener("ended", handleSongEnd);
        return () => {
            audio.removeEventListener("timeupdate", updateProgress);
            audio.removeEventListener("ended", handleSongEnd);
        }
    }, [songID, queue, backQueue]);

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
            <audio ref={audioRef} preload="metadata"></audio>

            <div className="buttons" style={styles.buttons}>
                <button onClick={playPrev} style={styles.button} disabled={backQueue.length === 0}>
                    <FontAwesomeIcon icon={faBackward} />
                </button>
                <button onClick={togglePlay} style={styles.button}>
                    <FontAwesomeIcon icon={isPlaying ? faPause : faPlay} />
                </button>
                <button onClick={playNext} style={styles.button} disabled={queue.length === 0}>
                    <FontAwesomeIcon icon={faForward} />
                </button>
            </div>

            <div className="sliders" style={styles.sliders}>
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
        </div>
    );
};

// Inline styles for simplicity (can use CSS or Tailwind later)
const styles = {
    playerContainer: {
        position: "fixed",
        bottom: 0,
        width: "100%",
        backgroundColor: "#333",
        color: "#fff",
        margin: "0",
        padding: "0",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "10px",
    },
    buttons: {
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "0",
        width: "fit-content",
        margin: "0",
    },
    button: {
        padding: "10px",
        backgroundColor: "#444",
        color: "white",
        // border: "none",
        cursor: "pointer",
        width: "60px",
        height: "60px",
    },
    sliders: {
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "10px",
        // width: calc(100 % - 120px)
        width: "calc((100% - 120px)*0.9)",
        margin: "0 calc((100% - 120px)*0.02)",
    },
    slider: {
        width: "80%",
        background: "transparent",
        height: "20px",
        flex: "1",
    },
    volumeSlider: {
        width: "20%",
        maxWidth: "100px",
    },
};

export default AudioPlayer;