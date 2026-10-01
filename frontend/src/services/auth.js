import { apiRequest, setAuthToken, clearAuthToken } from "./api";

export async function login(email, password) {
    const data = await apiRequest("/auth/login", {
        method: "POST",
        body: JSON.stringify({
            email: email,
            password: password
        })
    });

    if (data && data.access_token) {
        setAuthToken(data.access_token);
        const user = await getCurrentUser();
        localStorage.setItem("smart_campus_user", JSON.stringify(user));
        return { token: data.access_token, user };
    }

    return data;
}

export async function register(userData) {
    return await apiRequest("/auth/register", {
        method: "POST",
        body: JSON.stringify(userData)
    });
}

export async function getCurrentUser() {
    return await apiRequest("/auth/me", {
        method: "GET"
    });
}

export function getStoredUser() {
    try {
        const item = localStorage.getItem("smart_campus_user");
        return item ? JSON.parse(item) : null;
    } catch {
        return null;
    }
}

export function logout() {
    clearAuthToken();
}