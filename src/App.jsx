import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import AudioPlayer from "./components/AudioPlayer";
import MainPage from "./pages/MainPage";
import AlbumPage from "./pages/AlbumPage";
import MediaPage from "./pages/MediaPage";
import SettingsPage from "./pages/SettingsPage";
import "./App.css";

const App = () => {
    return (
        <Router>
            <div className="App">
                <nav className="navbar">
                    <Link to="/">Home</Link>
                    <Link to="/settings">Settings</Link>
                    <Link to="/">Rate</Link>
                </nav>

                <h1>Media Streamer</h1>

                <Routes>
                    <Route path="/" element={<MainPage />} />
                    <Route path="/album/:id" element={<AlbumPage />} />
                    <Route path="/media/:id" element={<MediaPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                </Routes>

                {/* Fixed, full-width Audio Player */}
                <div className="player">
                    <AudioPlayer songUrl="http://127.0.0.1:8000/stream/1648" />
                </div>
            </div>
        </Router>
    );
};

export default App;