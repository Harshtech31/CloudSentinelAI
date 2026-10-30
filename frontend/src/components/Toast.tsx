import { useUIStore } from '../store/uiStore';

export function Toast() {
  const { toastMessage } = useUIStore();

  if (!toastMessage) return null;

  return (
    <div className="app-toast" role="status" aria-live="polite">
      <span>{toastMessage}</span>
    </div>
  );
}
