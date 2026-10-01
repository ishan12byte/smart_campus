const API_BASE_URL = "http://localhost:8000";

export function getAuthToken() {
    return localStorage.getItem("smart_campus_token");
}

export function setAuthToken(token) {
    if (token) {
        localStorage.setItem("smart_campus_token", token);
    } else {
        localStorage.removeItem("smart_campus_token");
    }
}

export function clearAuthToken() {
    localStorage.removeItem("smart_campus_token");
    localStorage.removeItem("smart_campus_user");
}

export async function apiRequest(endpoint, options = {}) {
    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };

    const token = getAuthToken();
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const config = {
        ...options,
        headers
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    if (response.ok) {
        const data = await response.json();
        return data;
    } else {
        let errorMessage = `Request failed with status ${response.status}`;
        try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorMessage;
        } catch {
            // response was not JSON
        }
        throw new Error(errorMessage);
    }
}