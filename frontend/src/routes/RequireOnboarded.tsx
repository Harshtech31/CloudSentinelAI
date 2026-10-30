import { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';

import { useAuth } from '../contexts/AuthContext';
import { getOnboardingStatus } from '../api/onboarding';

/**
 * Route guard that blocks access to the dashboard shell until
 * the user has completed their AWS credentials and AI configuration.
 */
export function RequireOnboarded() {
  const { isOnboarded, setIsOnboarded, logout } = useAuth();
  const [checking, setChecking] = useState(isOnboarded === null);

  useEffect(() => {
    let mounted = true;
    if (isOnboarded === null) {
      getOnboardingStatus()
        .then((status) => {
          if (mounted) {
            setIsOnboarded(status.is_onboarded);
            setChecking(false);
          }
        })
        .catch((err) => {
          if (mounted) {
            if (err.response?.status === 401) {
              logout();
            } else {
              setIsOnboarded(false);
            }
            setChecking(false);
          }
        });
    } else {
      setChecking(false);
    }
    return () => {
      mounted = false;
    };
  }, [isOnboarded, setIsOnboarded, logout]);

  if (checking) {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#0B0F19',
          color: 'var(--text-secondary)',
          gap: '16px',
        }}
      >
        <div
          style={{
            width: '36px',
            height: '36px',
            border: '3px solid rgba(0, 229, 255, 0.2)',
            borderTopColor: 'var(--cyan-bright)',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite',
          }}
        />
        <span style={{ fontSize: '13px', letterSpacing: '0.04em' }}>
          Verifying Cloud Sentinel Security Posture…
        </span>
      </div>
    );
  }

  // Intercept and redirect to standalone setup if not onboarded
  if (!isOnboarded) {
    return <Navigate to="/onboarding" replace />;
  }

  return <Outlet />;
}
