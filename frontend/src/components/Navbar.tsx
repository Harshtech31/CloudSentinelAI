import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getOnboardingStatus, type OnboardingStatus } from '../api/onboarding';

const VIEW_TITLES: Record<string, string> = {
  '/': 'Overview & Posture',
  '/graph': 'Attack Path Knowledge Graph',
  '/findings': 'Security Findings & AI Intelligence',
  '/scan': 'Cloud Scanner Execution',
  '/compliance': 'CIS AWS Benchmark Compliance',
  '/reports': 'Assessment Export Reports',
  '/settings': 'Cloud & AI Settings',
};

export function Navbar() {
  const { logout, user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

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

  const currentTitle = VIEW_TITLES[location.pathname] || 'Overview & Posture';
  const accountLabel = status?.aws_account_id
    ? `AWS (${status.aws_account_id})`
    : 'AWS Environment';
  const aiProviderLabel = (status?.ai_provider || 'bedrock').toUpperCase();

  return (
    <header className="topbar">
      <div className="breadcrumb">
        <span>Target</span>
        <span className="breadcrumb-sep">/</span>
        <span>{accountLabel}</span>
        <span className="breadcrumb-sep">/</span>
        <span className="breadcrumb-current">{currentTitle}</span>
      </div>

      <div className="topbar-actions">
        {status?.aws_account_id ? (
          <div className="pill-telemetry cyan" title="Connected AWS Tenant Account">
            <span>AWS ACC:</span>
            <b>{status.aws_account_id}</b>
          </div>
        ) : (
          <div className="pill-telemetry" title="Default Audit Region">
            <span>REGION:</span>
            <b>{status?.aws_default_region || 'us-east-1'}</b>
          </div>
        )}

        <div className="pill-telemetry" title="Active AI Remediation Engine">
          <span>AI ENGINE:</span>
          <b>{aiProviderLabel}</b>
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
          title={`Signed in as ${user?.email || 'User'}`}
        >
          Sign out
        </button>
      </div>
    </header>
  );
}
