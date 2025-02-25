import React from "react";
import { Link } from "react-router-dom";
import "./avisited.css";

const NotFoundPage = () => {
    return (
        <div style={styles.container}>
            <img src="/album_placeholder.png" alt="404" style={styles.image} />
            <h1>404 - Page Not Found</h1>
            <p>Oops! The page you are looking for does not exist.</p>
            {/* <button style={styles.homeLinkButton}>
                <Link to="/" style={styles.homeLink}>Go back to Home</Link>
            </button> */}
            <Link to="/" style={styles.homeLink}>
                <button style={styles.homeLinkButton}>Go back to Home</button>
            </Link>
            {/* <Link to="/" style={styles.homeLink}>Go back to Home</Link> */}
        </div >
    );
};

// Styles
const styles = {
    container: {
        textAlign: "center",
        padding: "50px",
        color: "#fff",
        // backgroundColor: "#222",
        height: "30vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        margin: "auto",
    },
    image: {
        width: "200px",
        height: "200px",
        margin: "auto",
    },
    homeLinkButton: {
        backgroundColor: "#646cff",
        color: "#fff",
        padding: "10px 20px",
        border: "none",
        borderRadius: "5px",
        cursor: "pointer",
        marginTop: "20px",
    },
    homeLink: {
        // color: "#646cff",
        textDecoration: "none",
        fontSize: "18px",
    },
};

export default NotFoundPage;