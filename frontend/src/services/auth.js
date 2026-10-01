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
    return data;
}