import { create } from 'zustand';

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  setTokens: (accessToken: string, refreshToken: string) => void;
  clearTokens: () => void;
}

const STORAGE_KEY = 'cloudsentinel.auth';

function load(): Pick<AuthState, 'accessToken' | 'refreshToken'> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { accessToken: null, refreshToken: null };
    const parsed = JSON.parse(raw) as { accessToken?: string | null; refreshToken?: string | null };
    return { accessToken: parsed.accessToken ?? null, refreshToken: parsed.refreshToken ?? null };
  } catch {
    return { accessToken: null, refreshToken: null };
  }
}

/**
 * Session-scoped token store (roadmap task 22).
 *
 * Zustand keeps tokens outside the React tree so the axios interceptor
 * can read them synchronously; localStorage keeps the session across
 * page reloads. Tokens leave this store only via the API layer.
 */
export const useAuthStore = create<AuthState>((set) => ({
  ...load(),
  setTokens: (accessToken, refreshToken) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ accessToken, refreshToken }));
    } catch {
      /* storage unavailable: session lives in memory only */
    }
    set({ accessToken, refreshToken });
  },
  clearTokens: () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
    set({ accessToken: null, refreshToken: null });
  },
}));
