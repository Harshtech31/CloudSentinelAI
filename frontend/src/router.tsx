import { createBrowserRouter, Navigate } from 'react-router-dom';

import { AuthLayout } from './layouts/AuthLayout';
import { MainLayout } from './layouts/MainLayout';
import DashboardPage from './pages/DashboardPage';
import FindingsPage from './pages/FindingsPage';
import GraphPage from './pages/GraphPage';
import LoginPage from './pages/LoginPage';
import ReportsPage from './pages/ReportsPage';
import ScanPage from './pages/ScanPage';
import { RequireAuth } from './routes/RequireAuth';

/**
 * Route map (roadmap task 18).
 *
 * /login — public; signed-in users bounce to /
 * /      — protected app shell; children are Phase 1 placeholders that
 *          become real views in Phases 2–3.
 */
export const router = createBrowserRouter([
  {
    element: <AuthLayout />,
    children: [{ path: '/login', element: <LoginPage /> }],
  },
  {
    element: <RequireAuth />,
    children: [
      {
        element: <MainLayout />,
        children: [
          { path: '/', element: <DashboardPage /> },
          { path: '/scan', element: <ScanPage /> },
          { path: '/graph', element: <GraphPage /> },
          { path: '/findings', element: <FindingsPage /> },
          { path: '/reports', element: <ReportsPage /> },
        ],
      },
    ],
  },
  { path: '*', element: <Navigate to="/" replace /> },
]);
