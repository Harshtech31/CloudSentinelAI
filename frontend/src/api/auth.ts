import { api } from './client';

/** Mirrors the backend TokenResponse schema (app/schemas/auth.py). */
export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

/** POST /auth/login — backend contract is { username, password }. */
export async function loginRequest(username: string, password: string): Promise<TokenPair> {
  const { data } = await api.post<TokenPair>('/auth/login', { username, password });
  return data;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
  role?: 'admin' | 'analyst' | 'viewer';
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_onboarded: boolean;
  created_at: string;
}

/** POST /auth/register — creates new user account. */
export async function registerRequest(payload: RegisterPayload): Promise<UserResponse> {
  const { data } = await api.post<UserResponse>('/auth/register', payload);
  return data;
}

/** GET /auth/me — gets current authenticated user profile. */
export async function getCurrentUser(): Promise<UserResponse> {
  const { data } = await api.get<UserResponse>('/auth/me');
  return data;
}

