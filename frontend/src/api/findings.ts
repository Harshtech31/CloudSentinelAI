import { api } from './client';
import type { ComplianceReport, Finding, FindingExplainResult, FindingStats } from './types';

export interface FindingsQueryParams {
  severity?: string;
  rule_id?: string;
  resource_id?: string;
  scan_id?: string;
  page?: number;
  page_size?: number;
}

export async function listFindings(params?: FindingsQueryParams): Promise<{ findings: Finding[]; total: number }> {
  const { data } = await api.get<{ findings: Finding[]; total: number }>('/findings', { params });
  return data;
}

export async function getFindingStats(scanId?: string): Promise<FindingStats> {
  const { data } = await api.get<FindingStats>('/findings/stats/summary', {
    params: scanId ? { scan_id: scanId } : undefined,
  });
  return data;
}

export async function getComplianceReport(scanId?: string): Promise<ComplianceReport> {
  const { data } = await api.get<ComplianceReport>('/findings/compliance-report', {
    params: scanId ? { scan_id: scanId } : undefined,
  });
  return data;
}

export async function explainFinding(findingId: string): Promise<FindingExplainResult> {
  const { data } = await api.post<FindingExplainResult>(`/findings/${findingId}/explain`);
  return data;
}

export async function updateFindingStatus(findingId: string, status: 'open' | 'resolved'): Promise<Finding> {
  const { data } = await api.patch<Finding>(`/findings/${findingId}`, { status });
  return data;
}
