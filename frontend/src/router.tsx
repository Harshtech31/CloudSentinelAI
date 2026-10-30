import { createBrowserRouter, Navigate } from 'react-router-dom';

import { AuthLayout } from './layouts/AuthLayout';
import { MainLayout } from './layouts/MainLayout';
import CompliancePage from './pages/CompliancePage';
import DashboardPage from './pages/DashboardPage';
import FindingsPage from './pages/FindingsPage';
import GraphPage from './pages/GraphPage';
import LoginPage from './pages/LoginPage';
import OnboardingPage from './pages/OnboardingPage';
import ReportsPage from './pages/ReportsPage';
import ScanPage from './pages/ScanPage';
import { RequireAuth } from './routes/RequireAuth';

/**
 * Route map:
 * /login      — public; signed-in users bounce to /
 * /onboarding — AWS IAM & AI connection onboarding
 * /           — Overview & Posture dashboard
 * /scan       — Cloud Scanner Execution
 * /graph      — Attack Path Knowledge Graph
 * /findings   — Security Findings & AI Remediation
 * /compliance — CIS AWS Benchmark Compliance
 * /reports    — Assessment Reports Export
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
          { path: '/onboarding', element: <OnboardingPage /> },
          { path: '/scan', element: <ScanPage /> },
          { path: '/graph', element: <GraphPage /> },
          { path: '/findings', element: <FindingsPage /> },
          { path: '/compliance', element: <CompliancePage /> },
          { path: '/reports', element: <ReportsPage /> },
        ],
      },
    ],
  },
  { path: '*', element: <Navigate to="/" replace /> },
]);
