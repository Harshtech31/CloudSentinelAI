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
