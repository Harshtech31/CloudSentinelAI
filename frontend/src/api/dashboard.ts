import { api } from './client';
import type { DashboardSummary, TopRisk } from './types';

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const { data } = await api.get<DashboardSummary>('/dashboard/summary');
  return data;
}

export async function getTopRisks(): Promise<{ top_risks: TopRisk[] }> {
  const { data } = await api.get<{ top_risks: TopRisk[] }>('/dashboard/top-risks');
  return data;
}
