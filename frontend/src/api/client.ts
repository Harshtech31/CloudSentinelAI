import axios from 'axios';

import { useAuthStore } from '../store/authStore';

/**
 * Shared HTTP client.
 *
 * Base URL defaults to the local FastAPI backend and is overridable via
 * VITE_API_BASE_URL (see .env.example). The interceptor attaches the
 * bearer token from the auth store when a session exists.
 */
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
