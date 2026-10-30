import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const VIEW_TITLES: Record<string, string> = {
  '/': 'Overview & Posture',
  '/graph': 'Attack Path Knowledge Graph',
  '/findings': 'Security Findings & AI Intelligence',
  '/scan': 'Cloud Scanner Execution',
  '/compliance': 'CIS AWS Benchmark Compliance',
  '/reports': 'Assessment Export Reports',
};

export function Navbar() {
  const { logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const currentTitle = VIEW_TITLES[location.pathname] || 'Overview & Posture';

  return (
    <header className="topbar">
      <div className="breadcrumb">
        <span>Target</span>
        <span className="breadcrumb-sep">/</span>
        <span>AWS Production Sandbox</span>
        <span className="breadcrumb-sep">/</span>
        <span className="breadcrumb-current">{currentTitle}</span>
      </div>

      <div className="topbar-actions">
        <div className="pill-telemetry">
          <span>BEDROCK:</span>
          <b>claude-haiku-4.5</b>
        </div>
        <div className="pill-telemetry cyan">
          <span>AUDIT:</span>
          <b>PASSED 198/198</b>
        </div>
        <button
          type="button"
          className="btn btn-cyan"
          onClick={() => navigate('/scan')}
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="5 3 19 12 5 21 5 3" />
          </svg>
          Run Scan
        </button>
        <button
          type="button"
          className="btn"
          style={{ fontSize: '11px', padding: '4px 8px' }}
          onClick={logout}
          title="Sign out of console"
        >
          Sign out
        </button>
      </div>
    </header>
  );
}
