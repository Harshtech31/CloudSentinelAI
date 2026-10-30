import { Outlet } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { SlideDrawer } from '../components/SlideDrawer';
import { Toast } from '../components/Toast';

export function MainLayout() {
  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-area">
        <Navbar />
        <main className="content-body">
          <Outlet />
        </main>
      </div>
      <SlideDrawer />
      <Toast />
    </div>
  );
}
