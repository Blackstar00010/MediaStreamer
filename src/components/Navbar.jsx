import { Link, useNavigate } from "react-router-dom";
import { fetchRandomAlbumID } from "../api/basic";
// import { useState } from "react";

const Navbar = () => {
    const navigate = useNavigate();
    // const [loading, setLoading] = useState(false);

    const handleRandomAlbumClick = async (event) => {
        event.preventDefault(); // Prevent default link behavior
        // setLoading(true);
        try {
            const randAlbumID = await fetchRandomAlbumID();
            navigate(`/album/${randAlbumID}`); // Redirect
        } catch (error) {
            console.error("Error fetching random album:", error);
        }
        // setLoading(false);
    };

    return (
        <nav className="navbar">
            {/* <a href="#" onClick={fetchRandomMusic}>Random Music</a> */}
            <Link to="/">Home</Link>
            <a href="#" onClick={handleRandomAlbumClick}>Random Album</a>
            <Link to="/compare">Compare</Link>
            {/* <Link to="/settings">Settings</Link> */}
        </nav>
    );
};

export default Navbar;



