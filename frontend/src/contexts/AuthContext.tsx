import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';

import { getCurrentUser, loginRequest, registerRequest, type UserResponse } from '../api/auth';
import { getOnboardingStatus } from '../api/onboarding';
import { useAuthStore } from '../store/authStore';

interface AuthContextValue {
  isAuthenticated: boolean;
  isOnboarded: boolean | null;
  user: UserResponse | null;
  isLoading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, fullName: string) => Promise<boolean>;
  logout: () => void;
  setIsOnboarded: (val: boolean) => void;
  refreshOnboarding: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * Auth & Onboarding flow controller (roadmap task 22).
 *
 * Bridges the Zustand token store to React: tracks authentication,
 * tenant profile, and onboarding gate status.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const accessToken = useAuthStore((s) => s.accessToken);
  const setTokens = useAuthStore((s) => s.setTokens);
  const clearTokens = useAuthStore((s) => s.clearTokens);
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isOnboarded, setIsOnboarded] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!error) return;
    const timer = setTimeout(() => setError(null), 6000);
    return () => clearTimeout(timer);
  }, [error]);

  // Sync user profile & onboarding status whenever access token changes
  useEffect(() => {
    if (!accessToken) {
      setUser(null);
      setIsOnboarded(null);
      return;
    }
    let isMounted = true;
    getCurrentUser()
      .then((profile) => {
        if (isMounted) {
          setUser(profile);
          setIsOnboarded(profile.is_onboarded);
        }
      })
      .catch(() => {
        if (isMounted) {
          getOnboardingStatus()
            .then((st) => {
              if (isMounted) setIsOnboarded(st.is_onboarded);
            })
            .catch(() => {});
        }
      });
    return () => {
      isMounted = false;
    };
  }, [accessToken]);

  const value = useMemo<AuthContextValue>(
    () => ({
      isAuthenticated: Boolean(accessToken),
      isOnboarded,
      user,
      isLoading,
      error,
      setIsOnboarded,
      async refreshOnboarding() {
        try {
          const st = await getOnboardingStatus();
          setIsOnboarded(st.is_onboarded);
          return st.is_onboarded;
        } catch {
          return false;
        }
      },
      async login(username, password) {
        setIsLoading(true);
        setError(null);
        try {
          const tokens = await loginRequest(username, password);
          setTokens(tokens.access_token, tokens.refresh_token);
          try {
            const profile = await getCurrentUser();
            setUser(profile);
            setIsOnboarded(profile.is_onboarded);
          } catch {
            // fallback handled by token effect
          }
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
      async register(email, password, fullName) {
        setIsLoading(true);
        setError(null);
        try {
          await registerRequest({ email, password, full_name: fullName, role: 'analyst' });
          const tokens = await loginRequest(email, password);
          setTokens(tokens.access_token, tokens.refresh_token);
          try {
            const profile = await getCurrentUser();
            setUser(profile);
            setIsOnboarded(profile.is_onboarded);
          } catch {
            setIsOnboarded(false);
          }
          return true;
        } catch (err) {
          setError(
            axiosErrorMessage(err, 'Could not create account. Email may already exist.'),
          );
          return false;
        } finally {
          setIsLoading(false);
        }
      },
      logout() {
        clearTokens();
        setUser(null);
        setIsOnboarded(null);
      },
    }),
    [accessToken, isOnboarded, user, isLoading, error, setTokens, clearTokens],
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
