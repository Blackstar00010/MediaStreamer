import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import AudioPlayer from "./components/AudioPlayer";
import MainPage from "./pages/MainPage";
import AlbumPage from "./pages/AlbumPage";
// import MediaPage from "./pages/MediaPage";
// import SettingsPage from "./pages/SettingsPage";
import NotFoundPage from "./pages/NotFoundPage";
import "./App.css";

const App = () => {
    const [currentSongID, setCurrentSongID] = useState(null);

    // queues are arrays of song IDs
    const [queue, setQueue] = useState([]);
    const [backQueue, setBackQueue] = useState([]);  // store the previous songs, in reverse order. i.e. the last song played is the first in the backQueue

    return (
        <Router>
            <div className="App">
                <nav className="navbar">
                    <Link to="/">Home</Link>
                    {/* below are not implemented yet */}
                    {/* <Link to="/settings">Settings</Link> */}
                    {/* <Link to="/">Rate</Link> */}
                </nav>

                <Routes>
                    <Route path="/" element={<MainPage setCurrentSongID={setCurrentSongID} />} />
                    <Route path="/album/:albumID" element={<AlbumPage setCurrentSongID={setCurrentSongID} setQueue={setQueue} setBackQueue={setBackQueue} />} />
                    {/* <Route path="/media/:id" element={<MediaPage />} />
                    <Route path="/settings" element={<SettingsPage />} /> */}
                    <Route path="*" element={<NotFoundPage />} />
                </Routes>

                {
                    currentSongID &&
                    <AudioPlayer
                        songID={currentSongID}
                        setCurrentSongID={setCurrentSongID}
                        queue={queue}
                        setQueue={setQueue}
                        backQueue={backQueue}
                        setBackQueue={setBackQueue}
                    />
                }
            </div>
        </Router>
    );
};

export default App;