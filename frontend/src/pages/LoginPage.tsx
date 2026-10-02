import { useState, type FormEvent } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import { useAuth } from '../contexts/AuthContext';

/**
 * Sign-in page (roadmap tasks 21/22).
 *
 * Single job: get the analyst into the console. The form calls the real
 * POST /auth/login flow via AuthContext; the backend stub accepts any
 * credentials until Member 1's database track lands.
 */
export default function LoginPage() {
  const { login, isLoading, error } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const from = (() => {
    const params = new URLSearchParams(location.search);
    const raw = params.get('from');
    return raw && raw.startsWith('/') ? raw : '/';
  })();

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!username.trim() || !password) return;
    const ok = await login(username.trim(), password);
    if (ok) navigate(from, { replace: true });
  }

  return (
    <main className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">
          <span className="auth-logo" aria-hidden="true">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6l8-4z" />
              <path d="M8.5 12l2.5 2.5L16 9" />
            </svg>
          </span>
          <div>
            <h1>CloudSentinel AI</h1>
            <p>Enterprise cloud security platform</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <label htmlFor="login-username">Email</label>
          <input
            id="login-username"
            type="email"
            autoComplete="username"
            placeholder="analyst@company.com"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <label htmlFor="login-password">Password</label>
          <input
            id="login-password"
            type="password"
            autoComplete="current-password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && (
            <p className="auth-error" role="alert">
              {error}
            </p>
          )}

          <button type="submit" className="btn btn-primary auth-submit" disabled={isLoading}>
            {isLoading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p className="auth-foot">Research prototype · Department of Computer Science</p>
      </div>
    </main>
  );
}
