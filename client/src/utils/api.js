/**
 * API Client — Centralized HTTP client for backend communication.
 * Automatically attaches JWT token to every request.
 */

import axios from "axios";
import { getToken, removeToken } from "./storage";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 — redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken();
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
