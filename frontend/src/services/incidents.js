import { apiRequest } from "./api";

export async function createIncident(incidentData) {
    const data = await apiRequest("/incidents", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(incidentData)
    });

    return data;
}