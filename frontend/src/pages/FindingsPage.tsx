import { useEffect, useMemo, useState } from 'react';
import { listFindings } from '../api/findings';
import type { Finding } from '../api/types';
import { useUIStore } from '../store/uiStore';

export const DEFAULT_FINDINGS: Finding[] = [
  {
    id: 'fnd-001',
    scan_id: 'scn-001',
    rule_id: 'AWS-CIS-3.1',
    title: 'CloudTrail Multi-Region Audit Capture Disabled',
    description: 'Ensure CloudTrail records API events across all AWS regions to prevent unmonitored adversary activity.',
    severity: 'CRITICAL',
    risk_score: 9.5,
    resource_type: 'AWS::CloudTrail::Trail',
    resource_arn: 'global-cloudtrail',
    region: 'ap-south-1',
    remediation_guidance: 'Ensure CloudTrail records API events across all AWS regions to prevent unmonitored adversary activity.',
    status: 'open',
  },
  {
    id: 'fnd-002',
    scan_id: 'scn-001',
    rule_id: 'AWS-IAM-002',
    title: "Overly Permissive '*:*' Statement Attached to IAM Role",
    description: 'Scope IAM statements using least-privilege Resource and Action elements.',
    severity: 'CRITICAL',
    risk_score: 9.2,
    resource_type: 'AWS::IAM::Role',
    resource_arn: 'ProdAppAdminRole',
    region: 'global',
    remediation_guidance: 'Scope IAM statements using least-privilege Resource and Action elements.',
    status: 'open',
  },
  {
    id: 'fnd-003',
    scan_id: 'scn-001',
    rule_id: 'AWS-NET-001',
    title: 'Security Group Ingress Permits 0.0.0.0/0 on Port 22',
    description: 'Restrict port 22 ingress to authorized bastion IPs instead of 0.0.0.0/0.',
    severity: 'HIGH',
    risk_score: 7.8,
    resource_type: 'AWS::EC2::SecurityGroup',
    resource_arn: 'sg-07f9c812b',
    region: 'ap-south-1',
    remediation_guidance: 'Restrict port 22 ingress to authorized bastion IPs instead of 0.0.0.0/0.',
    status: 'open',
  },
  {
    id: 'fnd-004',
    scan_id: 'scn-001',
    rule_id: 'AWS-S3-001',
    title: 'S3 Bucket Grants Anonymous Global Read Permission',
    description: 'Apply S3 Block Public Access to prevent anonymous object access.',
    severity: 'HIGH',
    risk_score: 7.5,
    resource_type: 'AWS::S3::Bucket',
    resource_arn: 'finance-data-bucket',
    region: 'ap-south-1',
    remediation_guidance: 'Apply S3 Block Public Access to prevent anonymous object access.',
    status: 'open',
  },
  {
    id: 'fnd-005',
    scan_id: 'scn-001',
    rule_id: 'AWS-CIS-3.5',
    title: 'AWS Config Recording Inactive in Active Region',
    description: 'Enable AWS Config recording for all resource types in ap-south-1.',
    severity: 'MEDIUM',
    risk_score: 5.5,
    resource_type: 'AWS::Config::ConfigurationRecorder',
    resource_arn: 'default-recorder',
    region: 'ap-south-1',
    remediation_guidance: 'Enable AWS Config recording for all resource types in ap-south-1.',
    status: 'open',
  },
  {
    id: 'fnd-006',
    scan_id: 'scn-001',
    rule_id: 'AWS-S3-002',
    title: 'S3 Bucket Lacks Object Versioning Protection',
    description: 'Enable bucket object versioning to protect against accidental overwrite or deletion.',
    severity: 'MEDIUM',
    risk_score: 5.0,
    resource_type: 'AWS::S3::Bucket',
    resource_arn: 'cloudsentinel-eval-s4-logs',
    region: 'ap-south-1',
    remediation_guidance: 'Enable bucket object versioning to protect against accidental overwrite or deletion.',
    status: 'open',
  },
  {
    id: 'fnd-007',
    scan_id: 'scn-001',
    rule_id: 'AWS-S3-003',
    title: 'Server Access Logging Not Configured for Storage Bucket',
    description: 'Enable S3 server access logging to track read/write operations.',
    severity: 'LOW',
    risk_score: 2.5,
    resource_type: 'AWS::S3::Bucket',
    resource_arn: 'cloudsentinel-eval-lab-s1',
    region: 'ap-south-1',
    remediation_guidance: 'Enable S3 server access logging to track read/write operations.',
    status: 'open',
  },
];

export default function FindingsPage() {
  const { openDrawer } = useUIStore();
  const [findingsList, setFindingsList] = useState<Finding[]>([]);
  const [filterSev, setFilterSev] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');

  useEffect(() => {
    listFindings({ page: 1, page_size: 50 })
      .then((data) => {
        if (data && Array.isArray(data.findings)) {
          setFindingsList(data.findings);
        }
      })
      .catch(() => {});
  }, []);

  const filteredFindings = useMemo(() => {
    return findingsList.filter((item) => {
      const matchSev = filterSev === 'ALL' || item.severity.toUpperCase() === filterSev;
      const term = searchTerm.toLowerCase();
      const matchSearch =
        !term ||
        item.title.toLowerCase().includes(term) ||
        item.rule_id.toLowerCase().includes(term) ||
        item.resource_arn.toLowerCase().includes(term);
      return matchSev && matchSearch;
    });
  }, [findingsList, filterSev, searchTerm]);

  const handleRowClick = (item: Finding) => {
    openDrawer({
      findingId: item.id,
      ruleId: item.rule_id,
      title: item.title,
      severity: item.severity,
      resourceId: item.resource_arn,
      description: item.description,
      remediation: item.remediation_guidance,
      explanation: item.ai_explanation || undefined,
    });
  };

  return (
    <div style={{ animation: 'tabFade 0.15s ease-out' }}>
      <div className="data-table-container">
        {/* Table Header Filter Bar */}
        <div className="table-header-bar">
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
            <span className="table-title">Misconfiguration Register</span>
            <div style={{ display: 'flex', gap: '4px', marginLeft: '12px' }}>
              <button
                type="button"
                className="btn"
                style={{
                  padding: '2px 7px',
                  fontSize: '11px',
                  borderColor: filterSev === 'ALL' ? 'var(--cyan-bright)' : undefined,
                  color: filterSev === 'ALL' ? 'var(--cyan-bright)' : undefined,
                }}
                onClick={() => setFilterSev('ALL')}
              >
                All
              </button>
              <button
                type="button"
                className="btn"
                style={{
                  padding: '2px 7px',
                  fontSize: '11px',
                  color: 'var(--sev-crit)',
                  borderColor: filterSev === 'CRITICAL' ? 'var(--sev-crit)' : undefined,
                }}
                onClick={() => setFilterSev('CRITICAL')}
              >
                Critical
              </button>
              <button
                type="button"
                className="btn"
                style={{
                  padding: '2px 7px',
                  fontSize: '11px',
                  color: 'var(--sev-high)',
                  borderColor: filterSev === 'HIGH' ? 'var(--sev-high)' : undefined,
                }}
                onClick={() => setFilterSev('HIGH')}
              >
                High
              </button>
              <button
                type="button"
                className="btn"
                style={{
                  padding: '2px 7px',
                  fontSize: '11px',
                  color: 'var(--sev-med)',
                  borderColor: filterSev === 'MEDIUM' ? 'var(--sev-med)' : undefined,
                }}
                onClick={() => setFilterSev('MEDIUM')}
              >
                Medium
              </button>
              <button
                type="button"
                className="btn"
                style={{
                  padding: '2px 7px',
                  fontSize: '11px',
                  color: 'var(--cyan-bright)',
                  borderColor: filterSev === 'LOW' ? 'var(--cyan-bright)' : undefined,
                }}
                onClick={() => setFilterSev('LOW')}
              >
                Low
              </button>
            </div>
          </div>

          <input
            type="text"
            className="field-input"
            placeholder="Search finding or ARN..."
            style={{ width: '220px', padding: '4px 8px', fontSize: '11.5px' }}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Data Table */}
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: '80px' }}>Severity</th>
              <th style={{ width: '120px' }}>Rule ID</th>
              <th>Finding Title</th>
              <th style={{ width: '240px' }}>Resource Target</th>
              <th style={{ width: '65px', textAlign: 'right' }}>Risk</th>
            </tr>
          </thead>
          <tbody>
            {filteredFindings.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', padding: '48px 16px', color: 'var(--text-tertiary)', fontSize: '12px' }}>
                  No security misconfigurations found. Go to{' '}
                  <a href="/onboarding" style={{ color: 'var(--cyan-bright)', textDecoration: 'underline' }}>
                    AWS &amp; AI Setup
                  </a>{' '}
                  or{' '}
                  <a href="/scan" style={{ color: 'var(--cyan-bright)', textDecoration: 'underline' }}>
                    Cloud Scanner
                  </a>{' '}
                  to run an audit against your real cloud environment.
                </td>
              </tr>
            ) : (
              filteredFindings.map((item) => {
                const sev = item.severity.toUpperCase();
              const sevClass =
                sev === 'CRITICAL' ? 'crit' : sev === 'HIGH' ? 'high' : sev === 'MEDIUM' ? 'med' : 'low';

              return (
                <tr key={item.id} onClick={() => handleRowClick(item)}>
                  <td>
                    <span className={`tag-sev ${sevClass}`}>{sev}</span>
                  </td>
                  <td>
                    <span className="code-id">{item.rule_id}</span>
                  </td>
                  <td style={{ color: '#FFF' }}>{item.title}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
                    {item.resource_arn}
                  </td>
                  <td
                    style={{
                      textAlign: 'right',
                      fontFamily: 'var(--font-mono)',
                      fontWeight: 600,
                      color:
                        sev === 'CRITICAL'
                          ? 'var(--sev-crit)'
                          : sev === 'HIGH'
                          ? 'var(--sev-high)'
                          : 'var(--sev-med)',
                    }}
                  >
                    {item.risk_score?.toFixed(1) ?? '7.5'}
                  </td>
                </tr>
              );
            }))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
