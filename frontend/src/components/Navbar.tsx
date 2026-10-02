import { Link } from 'react-router-dom';

import { CloudProviderIcon } from './CloudProviderIcon';
import { useAuth } from '../contexts/AuthContext';

/**
 * Top navigation bar (roadmap task 20).
 *
 * Carries the session facts an analyst checks first — environment and
 * scan state — plus the primary action and sign-out.
 */
export function Navbar() {
  const { logout } = useAuth();

  return (
    <header className="topbar">
      <div className="topbar-title">
        <span className="topbar-status" aria-hidden="true">
          ●
        </span>
        <div>
          <small>Environment</small>
          <b className="topbar-env">
            Production · <CloudProviderIcon provider="aws" size={15} title="AWS" />
          </b>
        </div>
      </div>
      <div className="topbar-actions">
        <Link to="/scan" className="btn btn-primary">
          New Scan
        </Link>
        <button type="button" className="btn" onClick={logout}>
          Sign out
        </button>
      </div>
    </header>
  );
}
