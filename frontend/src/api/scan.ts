import { api } from './client';
import type { ScanStatusResponse } from './types';

export interface ScanStartRequest {
  provider: 'aws' | 'azure' | 'gcp';
  region?: string;
  account_id?: string;
}

export async function startScan(payload: ScanStartRequest = { provider: 'aws', region: 'ap-south-1' }): Promise<{ scan_id: string; message: string }> {
  const { data } = await api.post<{ scan_id: string; message: string }>('/scan/start', payload);
  return data;
}

export async function getScanStatus(scanId: string): Promise<ScanStatusResponse> {
  const { data } = await api.get<ScanStatusResponse>(`/scan/${scanId}/status`);
  return data;
}

export async function listScans(): Promise<{ scans: ScanStatusResponse[]; total: number }> {
  const { data } = await api.get<{ scans: ScanStatusResponse[]; total: number }>('/scans');
  return data;
}
