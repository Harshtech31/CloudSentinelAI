import { Navigate, Outlet, useLocation } from 'react-router-dom';

import { useAuth } from '../contexts/AuthContext';

/**
 * Route guard for the app shell (roadmap task 22).
 *
 * Unauthenticated visits redirect to /login, preserving the intended
 * destination so login can send the user back after signing in.
 */
export function RequireAuth() {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    const from = encodeURIComponent(location.pathname + location.search);
    return <Navigate to={`/login?from=${from}`} replace />;
  }
  return <Outlet />;
}
