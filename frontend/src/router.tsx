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
import SettingsPage from './pages/SettingsPage';
import { RequireAuth } from './routes/RequireAuth';
import { RequireOnboarded } from './routes/RequireOnboarded';

/**
 * Route map:
 * /login      — public; signed-in users bounce to /
 * /onboarding — standalone AWS & AI connection setup (gated, separate from dashboard)
 * /           — Overview & Posture dashboard (requires completed onboarding)
 * /scan       — Cloud Scanner Execution (requires completed onboarding)
 * /graph      — Attack Path Knowledge Graph (requires completed onboarding)
 * /findings   — Security Findings & AI Remediation (requires completed onboarding)
 * /compliance — CIS AWS Benchmark Compliance (requires completed onboarding)
 * /reports    — Assessment Reports Export (requires completed onboarding)
 * /settings   — Cloud & AI Settings editor inside dashboard (view & edit info, download IAM policy)
 */
export const router = createBrowserRouter([
  {
    element: <AuthLayout />,
    children: [{ path: '/login', element: <LoginPage /> }],
  },
  {
    element: <RequireAuth />,
    children: [
      // Standalone full-page onboarding setup (NOT in dashboard)
      { path: '/onboarding', element: <OnboardingPage /> },

      // Dashboard shell: strictly protected until AWS and AI setup is completed
      {
        element: <RequireOnboarded />,
        children: [
          {
            element: <MainLayout />,
            children: [
              { path: '/', element: <DashboardPage /> },
              { path: '/scan', element: <ScanPage /> },
              { path: '/graph', element: <GraphPage /> },
              { path: '/findings', element: <FindingsPage /> },
              { path: '/compliance', element: <CompliancePage /> },
              { path: '/reports', element: <ReportsPage /> },
              { path: '/settings', element: <SettingsPage /> },
            ],
          },
        ],
      },
    ],
  },
  { path: '*', element: <Navigate to="/" replace /> },
]);
