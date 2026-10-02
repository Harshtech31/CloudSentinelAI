import { Outlet } from 'react-router-dom';

import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';

/**
 * App shell (roadmap task 19): sidebar, top bar, routed content.
 * Page content renders through the Outlet.
 */
export function MainLayout() {
  return (
    <div className="shell">
      <Sidebar />
      <div className="shell-main">
        <Navbar />
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
