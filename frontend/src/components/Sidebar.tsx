import { NavLink } from 'react-router-dom';

export function Sidebar() {
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
            Overview
          </div>
        </NavLink>

        <NavLink
          to="/graph"
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          <div className="nav-item-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="18" cy="5" r="3" />
              <circle cx="6" cy="12" r="3" />
              <circle cx="18" cy="19" r="3" />
              <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
              <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
            </svg>
            Attack Graph
          </div>
          <span className="badge-count alert">1 Chain</span>
        </NavLink>

        <NavLink
          to="/findings"
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          <div className="nav-item-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            Findings
          </div>
          <span className="badge-count">14</span>
        </NavLink>

        <div className="nav-group-label" style={{ marginTop: '8px' }}>Operations</div>

        <NavLink
          to="/scan"
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          <div className="nav-item-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
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
          <span className="badge-count">85%</span>
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

        <div className="nav-group-label" style={{ marginTop: '8px' }}>Integrations</div>

        <NavLink
          to="/onboarding"
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          <div className="nav-item-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
            AWS &amp; AI Setup
          </div>
        </NavLink>
      </nav>

      {/* Target Account Badge */}
      <div className="sidebar-footer">
        <div className="account-badge">
          <div className="status-dot" />
          <div className="account-meta">
            <div className="account-name">cloudsentinel-eval</div>
            <div className="account-id">250675044619 · ap-south-1</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
