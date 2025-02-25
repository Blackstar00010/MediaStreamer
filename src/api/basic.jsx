const API_URL = "http://127.0.0.1:8000";

// Fetch one album by album_id
export const fetchAlbum = async (albumId) => {
    const response = await fetch(`${API_URL}/album/${albumId}`);
    if (!response.ok) throw new Error("Failed to fetch album");
    return response.json();
}

export const fetchRandomAlbumID = async () => {
    const response = await fetch(`${API_URL}/random_album`);
    if (!response.ok) throw new Error("Failed to fetch random album");
    const data = await response.json();
    return data.album_id;
}

// Fetch all albums
export const fetchAllAlbums = async () => {
    const response = await fetch(`${API_URL}/albums`);
    if (!response.ok) throw new Error("Failed to fetch albums");
    return response.json();
};

// Fetch two random albums for comparison
// export const fetchComparisonAlbums = async () => {
//     fetchAllAlbums().then((data) => {
//         const album1 = data[Math.floor(Math.random() * data.length)];
//         const album2 = data[Math.floor(Math.random() * data.length)];
//         return [album1, album2];
//     });
// }
export const fetchComparisonAlbums = async () => {
    const response = await fetch(`${API_URL}/compare_albums`);
    if (!response.ok) throw new Error("Failed to fetch comparison albums");
    return response.json();
};

// Update Elo rating after user selects an album
export const updateEloRating = async (winnerId, loserId) => {
    const payload = JSON.stringify({ winner_id: Number(winnerId), loser_id: Number(loserId) });
    const response = await fetch(`${API_URL}/update_rating`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: payload,
    });

    if (!response.ok) {
        const errorData = await response.json();
        console.error("Server responded with:", errorData);
        throw new Error("Failed to update rating");
    }
};