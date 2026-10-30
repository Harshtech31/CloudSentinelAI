import { api } from './client';

export interface ReportGenerationRequest {
  format: 'pdf' | 'html' | 'json' | 'csv';
  scan_id?: string;
}

export interface ReportResponse {
  id: string;
  scan_id: string;
  format: 'pdf' | 'html' | 'json' | 'csv';
  download_url: string;
  file_size_bytes: number;
  created_at: string;
}

export async function generateReport(payload: ReportGenerationRequest): Promise<ReportResponse> {
  const { data } = await api.post<ReportResponse>('/reports/generate', payload);
  return data;
}

export async function downloadReportFile(reportId: string, filename: string): Promise<void> {
  const response = await api.get(`/reports/${reportId}/download`, {
    responseType: 'blob',
  });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
