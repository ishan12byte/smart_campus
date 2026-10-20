const API_BASE_URL = "http://localhost:8000";

export async function apiRequest(endpoint, options = {}) {

    const token = localStorage.getItem("token");

    const headers = {
        ...options.headers
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: headers
    });

    if (response.ok) {
        const data = await response.json();
        return data;
    }

    const errorData = await response.json();

    throw new Error(
        errorData.detail || `Request failed with status ${response.status}`
    );
}