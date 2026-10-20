
import { apiRequest } from "./api";

export async function login(email, password) {
    const data = await apiRequest("/auth/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email,
            password: password
        })
    });

    if (!data.access_token) {
        throw new Error("Login response did not contain an access token.");
    }

    // Save the token so apiRequest can use it on later requests.
    localStorage.setItem("token", data.access_token);

    try {
        // Fetch the profile using the saved token.
        const user = await apiRequest("/auth/me");

        return user;
    } catch (error) {
        // Remove the token if profile retrieval fails.
        localStorage.removeItem("token");
        throw error;
    }
}
