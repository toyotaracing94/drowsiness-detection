// Extract protocol and hostname/port
export const PROTOCOL = window.location.protocol;
export const HOST = window.location.hostname;
export const PORT = "8000";

// Combine dynamically
export const API_URL_LOCATION = `${PROTOCOL}//${HOST}:${PORT}`;

// Fallback for dev
export const API_URL_LOCATION_DEV = `http://localhost:8000`;
