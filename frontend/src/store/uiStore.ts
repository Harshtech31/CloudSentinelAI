import { create } from 'zustand';

export interface FindingDrawerData {
  ruleId: string;
  title: string;
  severity: string;
  resourceId: string;
  description: string;
  remediation?: string;
  findingId?: string;
  cliCommand?: string;
  explanation?: string;
}

interface UIState {
  // Drawer
  isDrawerOpen: boolean;
  drawerData: FindingDrawerData | null;
  openDrawer: (data: FindingDrawerData) => void;
  closeDrawer: () => void;

  // Toast
  toastMessage: string | null;
  showToast: (message: string) => void;
  hideToast: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  isDrawerOpen: false,
  drawerData: null,
  openDrawer: (data) => set({ isDrawerOpen: true, drawerData: data }),
  closeDrawer: () => set({ isDrawerOpen: false }),

  toastMessage: null,
  showToast: (message) => {
    set({ toastMessage: message });
    setTimeout(() => {
      set((state) => (state.toastMessage === message ? { toastMessage: null } : {}));
    }, 3500);
  },
  hideToast: () => set({ toastMessage: null }),
}));
