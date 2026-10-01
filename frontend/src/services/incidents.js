import { apiRequest } from "./api";

export async function getIncidents() {
    return await apiRequest("/incidents", {
        method: "GET"
    });
}

export async function getIncidentById(id) {
    return await apiRequest(`/incidents/${id}`, {
        method: "GET"
    });
}

export async function createIncident(incidentData) {
    return await apiRequest("/incidents", {
        method: "POST",
        body: JSON.stringify(incidentData)
    });
}

export async function getCategories() {
    return await apiRequest("/incidents/categories", {
        method: "GET"
    });
}

export async function performIncidentAction(incidentId, action) {
    return await apiRequest(`/incidents/${incidentId}/action/${action}`, {
        method: "POST"
    });
}

export async function getDepartments() {
    return await apiRequest("/departments", {
        method: "GET"
    });
}

export async function getRoles() {
    return await apiRequest("/roles", {
        method: "GET"
    });
}
