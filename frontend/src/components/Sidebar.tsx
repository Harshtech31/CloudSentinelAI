import { NavLink } from 'react-router-dom';

import { useAuth } from '../contexts/AuthContext';

interface NavItem {
  to: string;
  label: string;
  icon: string;
  end?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { to: '/', label: 'Dashboard', icon: '▦', end: true },
  { to: '/scan', label: 'Cloud Scan', icon: '⟳' },
  { to: '/graph', label: 'Knowledge Graph', icon: '⊛' },
  { to: '/findings', label: 'Security Findings', icon: '⚑' },
  { to: '/reports', label: 'Reports', icon: '▤' },
];

/**
 * Console navigation (roadmap task 20).
 *
 * One item per stage of the analyst's loop: see posture, scan, explore
 * the graph, triage findings, export reports. Active item follows the
 * URL; NavLink end-prop keeps Dashboard from matching every route.
 */
export function Sidebar() {
  const { isAuthenticated } = useAuth();
  const initials = 'SA';

  return (
    <aside className="sidebar">
      <div className="side-brand">
        <span className="side-logo" aria-hidden="true">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6l8-4z" />
            <path d="M8.5 12l2.5 2.5L16 9" />
          </svg>
        </span>
        <div>
          <b>CloudSentinel AI</b>
          <small>Security console</small>
        </div>
      </div>

      <nav className="side-nav" aria-label="Primary">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) => (isActive ? 'side-link is-active' : 'side-link')}
          >
            <span className="side-ic" aria-hidden="true">
              {item.icon}
            </span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="side-user">
        <span className="side-avatar" aria-hidden="true">
          {initials}
        </span>
        <div>
          <b>SOC Analyst</b>
          <small>{isAuthenticated ? 'Signed in' : 'Session only'}</small>
        </div>
      </div>
    </aside>
  );
}
