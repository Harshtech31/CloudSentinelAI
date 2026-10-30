import { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getOnboardingStatus, type OnboardingStatus } from '../api/onboarding';

export function Sidebar() {
  const { user } = useAuth();
  const [status, setStatus] = useState<OnboardingStatus | null>(null);

  useEffect(() => {
    let isMounted = true;
    getOnboardingStatus()
      .then((st) => {
        if (isMounted) setStatus(st);
      })
      .catch(() => {});
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="brand-header">
        <div className="brand-icon">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.8">
            <path d="M12 2L3 7v6c0 5.5 3.8 10.7 9 12 5.2-1.3 9-6.5 9-12V7l-9-5z" />
          </svg>
        </div>
        <div className="brand-title">
          CloudSentinel
          <span className="brand-version">v1.0</span>
        </div>
      </div>

      {/* Nav List */}
      <nav className="nav-list" aria-label="Main Navigation">
        <div className="nav-group-label">Analysis</div>

        <NavLink
          to="/"
          end
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          <div className="nav-item-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="3" width="7" height="9" rx="1" />
              <rect x="14" y="3" width="7" height="5" rx="1" />
              <rect x="14" y="12" width="7" height="9" rx="1" />
              <rect x="3" y="16" width="7" height="5" rx="1" />
            </svg>
            Dashboard
          </div>
        </NavLink>

        <NavLink
          to="/graph"
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          <div className="nav-item-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="6" cy="6" r="3" />
              <circle cx="18" cy="18" r="3" />
              <circle cx="18" cy="6" r="3" />
              <path d="M8.5 8.5l7 7M15.5 8.5l-7 7" />
            </svg>
            Attack Graph
          </div>
        </NavLink>

        <NavLink
          to="/findings"
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          <div className="nav-item-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
            Findings &amp; Remediation
          </div>
        </NavLink>

        <div className="nav-group-label">Operations</div>

        <NavLink
          to="/scan"
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          <div className="nav-item-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10" />
              <polygon points="10 8 16 12 10 16 10 8" />
            </svg>
            Cloud Scanner
          </div>
        </NavLink>

        <NavLink
          to="/compliance"
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          <div className="nav-item-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 11l3 3L22 4" />
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
            </svg>
            CIS Benchmarks
          </div>
        </NavLink>

        <NavLink
          to="/reports"
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          <div className="nav-item-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            Reports Export
          </div>
        </NavLink>

        <div className="nav-group-label" style={{ marginTop: '8px' }}>Settings</div>

        <NavLink
          to="/settings"
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          <div className="nav-item-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
            Cloud &amp; AI Setup
          </div>
        </NavLink>
      </nav>

      {/* Target Account Badge */}
      <div className="sidebar-footer">
        <div className="account-badge">
          <div className="status-dot" />
          <div className="account-meta">
            <div className="account-name">{user?.full_name || 'CloudSentinel Console'}</div>
            <div className="account-id">
              {status?.aws_account_id
                ? `${status.aws_account_id} · ${status.aws_default_region}`
                : user?.email || 'Protected Account'}
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
