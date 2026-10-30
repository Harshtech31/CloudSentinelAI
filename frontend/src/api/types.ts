/**
 * CloudSentinel AI — Frontend API & Domain Data Types
 */

export type SeverityLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

export interface Finding {
  id: string;
  scan_id: string;
  rule_id: string;
  title: string;
  description: string;
  severity: SeverityLevel;
  risk_score: number;
  resource_type: string;
  resource_arn: string;
  region: string;
  remediation_guidance: string;
  ai_explanation?: string | null;
  status: 'open' | 'resolved';
  created_at?: string;
}

export interface FindingStats {
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
  total: number;
}

export interface FindingExplainResult {
  finding_id: string;
  explanation: string;
  remediation_steps: string[];
  provider: string;
  model: string;
  tokens_used: number;
}

export interface DashboardSummary {
  security_score: number;
  scanned_resources: number;
  total_findings: number;
  critical_findings: number;
  attack_paths_identified: number;
}

export interface TopRisk {
  id: string;
  rule_id: string;
  title: string;
  severity: SeverityLevel;
  risk_score: number;
  resource_type: string;
  resource_id: string;
  region: string;
}

export interface ComplianceControl {
  control_id: string;
  description: string;
  status: 'PASS' | 'FAIL';
  remediation_hint: string;
}

export interface ComplianceReport {
  framework: string;
  total_controls: number;
  passed_controls: number;
  failed_controls: number;
  compliance_percentage?: number;
  compliance_score?: number;
  controls: ComplianceControl[];
}

export interface ScanStatusResponse {
  scan_id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  provider: string;
  account_id?: string;
  region?: string;
  resources_scanned?: number;
  findings_count?: number;
  attack_paths_count?: number;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

export interface CytoscapeNode {
  data: {
    id: string;
    label: string;
    type?: string;
    risk_score?: number;
    severity?: SeverityLevel;
    exposure?: string;
    is_crown_jewel?: boolean;
    [key: string]: unknown;
  };
}

export interface CytoscapeEdge {
  data: {
    id: string;
    source: string;
    target: string;
    label?: string;
    is_attack_path?: boolean;
    [key: string]: unknown;
  };
}

export interface GraphTopology {
  elements: {
    nodes: CytoscapeNode[];
    edges: CytoscapeEdge[];
  };
}

export interface AttackChain {
  chain_id: string;
  source: string;
  target: string;
  hops: string[];
  risk_score: number;
  description: string;
}

export interface ReportItem {
  id: string;
  scan_id: string;
  format: 'pdf' | 'html' | 'json' | 'csv';
  created_at: string;
}
