import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';

import { loginRequest } from '../api/auth';
import { useAuthStore } from '../store/authStore';

interface AuthContextValue {
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * Auth flow controller (roadmap task 22).
 *
 * Bridges the Zustand token store to React: components read
 * `isAuthenticated`, the login form calls `login()`, the axios
 * interceptor reads the store directly. `logout()` revokes the session
 * everywhere at once (store + localStorage).
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const accessToken = useAuthStore((s) => s.accessToken);
  const setTokens = useAuthStore((s) => s.setTokens);
  const clearTokens = useAuthStore((s) => s.clearTokens);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!error) return;
    const timer = setTimeout(() => setError(null), 6000);
    return () => clearTimeout(timer);
  }, [error]);

  const value = useMemo<AuthContextValue>(
    () => ({
      isAuthenticated: Boolean(accessToken),
      isLoading,
      error,
      async login(username, password) {
        setIsLoading(true);
        setError(null);
        try {
          const tokens = await loginRequest(username, password);
          setTokens(tokens.access_token, tokens.refresh_token);
          return true;
        } catch (err) {
          setError(
            axiosErrorMessage(err, 'Could not sign in. Check your credentials and try again.'),
          );
          return false;
        } finally {
          setIsLoading(false);
        }
      },
      logout() {
        clearTokens();
      },
    }),
    [accessToken, isLoading, error, setTokens, clearTokens],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

function axiosErrorMessage(err: unknown, fallback: string): string {
  if (typeof err === 'object' && err !== null && 'response' in err) {
    const response = (err as { response?: { status?: number } }).response;
    if (response?.status === 401) return 'Wrong email or password.';
  }
  if (typeof err === 'object' && err !== null && 'code' in err) {
    const code = (err as { code?: string }).code;
    if (code === 'ERR_NETWORK') return 'Backend unreachable. Is it running on port 8000?';
  }
  return fallback;
}
