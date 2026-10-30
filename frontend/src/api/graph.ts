import { api } from './client';
import type { AttackChain, GraphTopology } from './types';

export async function getGraphData(scanId?: string): Promise<GraphTopology> {
  const { data } = await api.get<GraphTopology>('/graph', {
    params: scanId ? { scan_id: scanId } : undefined,
  });
  return data;
}

export async function getAttackChains(scanId?: string): Promise<{ attack_chains: AttackChain[] }> {
  const { data } = await api.get<{ attack_chains: AttackChain[] }>('/graph/attack-chains', {
    params: scanId ? { scan_id: scanId } : undefined,
  });
  return data;
}
