import { useState, type FormEvent } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const { login, register, isLoading, error } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('admin@cloudsentinel.ai');
  const [password, setPassword] = useState('Sentinel#2026');
  const [fullName, setFullName] = useState('CloudSentinel Analyst');

  const from = (() => {
    const params = new URLSearchParams(location.search);
    const raw = params.get('from');
    return raw && raw.startsWith('/') ? raw : '/';
  })();

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!username.trim() || !password) return;
    let ok = false;
    if (isRegister) {
      ok = await register(username.trim(), password, fullName.trim() || 'New Analyst');
    } else {
      ok = await login(username.trim(), password);
    }
    if (ok) navigate(from, { replace: true });
  }

  return (
    <main className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">
          <span className="auth-logo" aria-hidden="true">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M12 2L3 7v6c0 5.5 3.8 10.7 9 12 5.2-1.3 9-6.5 9-12V7l-9-5z" />
            </svg>
          </span>
          <div>
            <h1>CloudSentinel</h1>
            <p>Cloud Security Posture &amp; Attack Graph Console</p>
          </div>
        </div>

        {/* Tab Toggle: Sign In vs Create Account */}
        <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
          <button
            type="button"
            className="btn"
            style={{
              flex: 1,
              justifyContent: 'center',
              fontSize: '11px',
              padding: '6px',
              color: !isRegister ? 'var(--cyan-bright)' : 'var(--text-secondary)',
              borderColor: !isRegister ? 'var(--cyan-bright)' : 'var(--border-subtle)',
            }}
            onClick={() => setIsRegister(false)}
          >
            Sign In
          </button>
          <button
            type="button"
            className="btn"
            style={{
              flex: 1,
              justifyContent: 'center',
              fontSize: '11px',
              padding: '6px',
              color: isRegister ? 'var(--cyan-bright)' : 'var(--text-secondary)',
              borderColor: isRegister ? 'var(--cyan-bright)' : 'var(--border-subtle)',
            }}
            onClick={() => {
              setIsRegister(true);
              if (username === 'admin@cloudsentinel.ai') {
                setUsername('');
                setPassword('');
              }
            }}
          >
            Create Account
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {isRegister && (
            <>
              <label htmlFor="register-name">Full Name</label>
              <input
                id="register-name"
                type="text"
                autoComplete="name"
                placeholder="Jane Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />
            </>
          )}

          <label htmlFor="login-username">Email / Principal</label>
          <input
            id="login-username"
            type="text"
            autoComplete="username"
            placeholder="analyst@cloudsentinel.ai"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <label htmlFor="login-password">Password</label>
          <input
            id="login-password"
            type="password"
            autoComplete={isRegister ? 'new-password' : 'current-password'}
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

          <button type="submit" className="btn btn-cyan auth-submit" disabled={isLoading}>
            {isLoading
              ? isRegister
                ? 'Creating Account…'
                : 'Authenticating…'
              : isRegister
              ? 'Create New Account'
              : 'Sign in to Console'}
          </button>
        </form>

        <div className="auth-foot" style={{ fontSize: '10px', color: 'var(--text-tertiary)', marginTop: '16px', lineHeight: 1.4 }}>
          {isRegister ? (
            <span style={{ color: 'var(--cyan-dim)' }}>
              🔒 New accounts operate in isolated sandbox mode with zero access to your personal AWS account.
            </span>
          ) : (
            <span>
              Target: <code>cloudsentinel-eval &middot; 250675044619</code>
            </span>
          )}
        </div>
      </div>
    </main>
  );
}
