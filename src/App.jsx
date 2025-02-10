import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import AudioPlayer from "./components/AudioPlayer";
import MainPage from "./pages/MainPage";
import AlbumPage from "./pages/AlbumPage";
import MediaPage from "./pages/MediaPage";
import SettingsPage from "./pages/SettingsPage";
import "./App.css";

const App = () => {
    const [currentSongID, setCurrentSongID] = useState(1648);
    return (
        <Router>
            <div className="App">
                <nav className="navbar">
                    <Link to="/">Home</Link>
                    <Link to="/settings">Settings</Link>
                    <Link to="/">Rate</Link>
                </nav>

                <Routes>
                    <Route path="/" element={<MainPage setCurrentSongID={setCurrentSongID} />} />
                    <Route path="/album/:id" element={<AlbumPage />} />
                    <Route path="/media/:id" element={<MediaPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                </Routes>

                {/* Fixed, full-width Audio Player */}
                {
                    currentSongID &&
                    <div className="player">
                        <AudioPlayer songID={currentSongID} />
                    </div>
                }
            </div>
        </Router>
    );
};

export default App;