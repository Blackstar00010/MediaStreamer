import { Link, useNavigate } from "react-router-dom";
// import { useState } from "react";

const Navbar = () => {
    const navigate = useNavigate();
    // const [loading, setLoading] = useState(false);

    const fetchRandomAlbum = async (event) => {
        event.preventDefault(); // Prevent default link behavior
        // setLoading(true);
        try {
            const response = await fetch("http://127.0.0.1:8000/random_album");
            if (!response.ok) throw new Error("Failed to fetch");
            const data = await response.json();
            navigate(`/album/${data.album_id}`); // Redirect
        } catch (error) {
            console.error("Error fetching random album:", error);
        }
        // setLoading(false);
    };

    return (
        <nav className="navbar">
            {/* <a href="#" onClick={fetchRandomMusic}>Random Music</a> */}
            <Link to="/">Home</Link>
            <a href="#" onClick={fetchRandomAlbum}>Random Album</a>
            <Link to="/compare">Compare</Link>
            {/* <Link to="/settings">Settings</Link> */}
        </nav>
    );
};

export default Navbar;



