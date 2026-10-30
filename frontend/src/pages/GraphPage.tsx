import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUIStore } from '../store/uiStore';

interface AssetTelemetry {
  id: string;
  type: string;
  exposure: string;
  desc: string;
  severity: string;
  ruleId?: string;
  remediation?: string;
}

const DEFAULT_ASSETS: Record<string, AssetTelemetry> = {
  internet: {
    id: 'Public Internet (0.0.0.0/0)',
    type: 'External::Internet',
    exposure: 'PERIMETER_INGRESS',
    desc: 'Untrusted global internet gateway ingress point with unauthenticated network reachability.',
    severity: 'CRITICAL',
    ruleId: 'AWS-NET-001',
    remediation: 'Restrict public CIDR 0.0.0.0/0 ingress to known corporate VPN IPs.',
  },
  sg: {
    id: 'sg-07f9c812b',
    type: 'AWS::EC2::SecurityGroup',
    exposure: 'PORT_22_OPEN',
    desc: 'Ingress rule permits SSH tcp/22 ingress from global CIDR (0.0.0.0/0).',
    severity: 'HIGH',
    ruleId: 'AWS-NET-001',
    remediation: 'Revoke port 22 ingress rule from security group sg-07f9c812b.',
  },
  bastion: {
    id: 'i-0a8b79c3d4e',
    type: 'AWS::EC2::Instance',
    exposure: 'PUBLIC_IP_ATTACHED',
    desc: 'Public instance with attached IAM Instance Profile ProdAppAdminRole.',
    severity: 'CRITICAL',
    ruleId: 'AWS-IAM-002',
    remediation: 'Remove public IP assignment or enforce session manager (SSM) instead of SSH.',
  },
  role: {
    id: 'ProdAppAdminRole',
    type: 'AWS::IAM::Role',
    exposure: 'ADMIN_PRIVILEGE',
    desc: "Attached policy statement grants wildcard Action:* on Resource:*, allowing lateral pivot to data plane.",
    severity: 'CRITICAL',
    ruleId: 'AWS-IAM-002',
    remediation: 'Scope IAM statements using least-privilege Resource and Action elements.',
  },
  s3: {
    id: 'finance-data-bucket',
    type: 'AWS::S3::Bucket',
    exposure: 'CROWN_JEWEL_EXPOSURE',
    desc: 'Critical storage bucket storing financial audit logs and customer records.',
    severity: 'CRITICAL',
    ruleId: 'AWS-S3-001',
    remediation: 'Apply S3 Block Public Access to prevent anonymous object access.',
  },
  vpc: {
    id: 'vpc-091fca2',
    type: 'AWS::EC2::VPC',
    exposure: 'DEFAULT_VPC',
    desc: 'Default VPC utilized for testing workloads.',
    severity: 'MEDIUM',
    ruleId: 'AWS-VPC-001',
  },
  subnet: {
    id: 'subnet-private-1a',
    type: 'AWS::EC2::Subnet',
    exposure: 'ISOLATED_SUBNET',
    desc: 'Private subnet with local routing table only.',
    severity: 'LOW',
  },
  rds: {
    id: 'rds-database-prod',
    type: 'AWS::RDS::DBInstance',
    exposure: 'ENCRYPTED_DB',
    desc: 'PostgreSQL instance configured with AWS KMS storage encryption.',
    severity: 'LOW',
  },
  s3logs: {
    id: 'cloudsentinel-audit-s4',
    type: 'AWS::S3::Bucket',
    exposure: 'LOG_STORAGE',
    desc: 'Dedicated bucket receiving CloudTrail audit logs.',
    severity: 'LOW',
  },
};

export default function GraphPage() {
  const navigate = useNavigate();
  const { openDrawer } = useUIStore();

  const [selectedAsset, setSelectedAsset] = useState<AssetTelemetry>(DEFAULT_ASSETS.bastion);
  const [scale, setScale] = useState(1);

  const zoom = (factor: number) => {
    setScale((prev) => Math.max(0.6, Math.min(2.0, prev * factor)));
  };

  const reset = () => {
    setScale(1);
  };

  const sevLower = selectedAsset.severity.toLowerCase();
  const sevClass =
    sevLower === 'critical'
      ? 'crit'
      : sevLower === 'high'
      ? 'high'
      : sevLower === 'medium'
      ? 'med'
      : 'low';

  const handleInspectFinding = () => {
    if (selectedAsset.ruleId) {
      openDrawer({
        ruleId: selectedAsset.ruleId,
        title: `${selectedAsset.type} - ${selectedAsset.exposure}`,
        severity: selectedAsset.severity,
        resourceId: selectedAsset.id,
        description: selectedAsset.desc,
        remediation: selectedAsset.remediation,
      });
    } else {
      navigate('/findings');
    }
  };

  return (
    <div style={{ animation: 'tabFade 0.15s ease-out' }}>
      <div className="graph-viewport">
        {/* HUD Controls */}
        <div className="graph-hud-bar">
          <button type="button" className="hud-btn" title="Zoom In" onClick={() => zoom(1.2)}>
            +
          </button>
          <button type="button" className="hud-btn" title="Zoom Out" onClick={() => zoom(0.8)}>
            &minus;
          </button>
          <button type="button" className="hud-btn" title="Reset View" onClick={reset}>
            R
          </button>
        </div>

        {/* SVG Network Graph Canvas */}
        <div className="graph-svg-wrapper">
          <svg
            style={{
              width: '100%',
              height: '100%',
              transform: `scale(${scale})`,
              transformOrigin: 'center center',
              transition: 'transform 0.15s ease',
            }}
            viewBox="0 0 920 620"
          >
            <defs>
              <marker
                id="arrow-normal"
                viewBox="0 0 10 10"
                refX="24"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#242A37" />
              </marker>
              <marker
                id="arrow-exploit"
                viewBox="0 0 10 10"
                refX="24"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#FF3366" />
              </marker>
            </defs>

            {/* Normal Structural Infrastructure Edges */}
            <line x1="260" y1="180" x2="460" y2="180" className="edge-link" markerEnd="url(#arrow-normal)" />
            <line x1="460" y1="180" x2="660" y2="180" className="edge-link" markerEnd="url(#arrow-normal)" />
            <line x1="660" y1="180" x2="840" y2="180" className="edge-link" markerEnd="url(#arrow-normal)" />
            <line x1="460" y1="380" x2="840" y2="500" className="edge-link" markerEnd="url(#arrow-normal)" />

            {/* High-Voltage Attack Chain Edges */}
            <line x1="100" y1="380" x2="280" y2="380" className="edge-exploit" markerEnd="url(#arrow-exploit)" />
            <line x1="280" y1="380" x2="460" y2="380" className="edge-exploit" markerEnd="url(#arrow-exploit)" />
            <line x1="460" y1="380" x2="660" y2="380" className="edge-exploit" markerEnd="url(#arrow-exploit)" />
            <line x1="660" y1="380" x2="840" y2="380" className="edge-exploit" markerEnd="url(#arrow-exploit)" />

            {/* Node: Internet Entry */}
            <g
              className="graph-node"
              transform="translate(100, 380)"
              onClick={() => setSelectedAsset(DEFAULT_ASSETS.internet)}
            >
              <circle cx="0" cy="0" r="22" fill="#0E1015" stroke="#00F5D4" strokeWidth="1.8" />
              <text y="4" className="node-text">
                INTERNET
              </text>
              <text y="36" className="node-sub">
                0.0.0.0/0
              </text>
            </g>

            {/* Node: Security Group */}
            <g
              className="graph-node"
              transform="translate(280, 380)"
              onClick={() => setSelectedAsset(DEFAULT_ASSETS.sg)}
            >
              <circle cx="0" cy="0" r="22" fill="#0E1015" stroke="#FF8833" strokeWidth="1.8" />
              <text y="4" className="node-text">
                SG: SSH
              </text>
              <text y="36" className="node-sub">
                Port 22
              </text>
            </g>

            {/* Node: Compute */}
            <g
              className="graph-node"
              transform="translate(460, 380)"
              onClick={() => setSelectedAsset(DEFAULT_ASSETS.bastion)}
            >
              <circle cx="0" cy="0" r="24" fill="#0E1015" stroke="#FF3366" strokeWidth="2" />
              <text y="4" className="node-text">
                EC2 BASTION
              </text>
              <text y="38" className="node-sub">
                13.232.41.88
              </text>
            </g>

            {/* Node: IAM Role */}
            <g
              className="graph-node"
              transform="translate(660, 380)"
              onClick={() => setSelectedAsset(DEFAULT_ASSETS.role)}
            >
              <circle cx="0" cy="0" r="22" fill="#0E1015" stroke="#FFCC00" strokeWidth="1.8" />
              <text y="4" className="node-text">
                IAM ROLE
              </text>
              <text y="36" className="node-sub">
                AdminPrivs
              </text>
            </g>

            {/* Node: Target Crown Jewel S3 */}
            <g
              className="graph-node"
              transform="translate(840, 380)"
              onClick={() => setSelectedAsset(DEFAULT_ASSETS.s3)}
            >
              <circle cx="0" cy="0" r="26" fill="#1C0910" stroke="#FF3366" strokeWidth="2.5" />
              <text y="4" className="node-text">
                S3 TARGET
              </text>
              <text y="42" className="node-sub" style={{ fill: 'var(--sev-crit)' }}>
                Crown Jewel
              </text>
            </g>

            {/* Isolated VPC Infrastructure Nodes */}
            <g
              className="graph-node"
              transform="translate(260, 180)"
              onClick={() => setSelectedAsset(DEFAULT_ASSETS.vpc)}
            >
              <circle cx="0" cy="0" r="18" fill="#0E1015" stroke="#242A37" strokeWidth="1.5" />
              <text y="3" className="node-text">
                VPC
              </text>
              <text y="30" className="node-sub">
                172.31.0.0/16
              </text>
            </g>

            <g
              className="graph-node"
              transform="translate(460, 180)"
              onClick={() => setSelectedAsset(DEFAULT_ASSETS.subnet)}
            >
              <circle cx="0" cy="0" r="18" fill="#0E1015" stroke="#242A37" strokeWidth="1.5" />
              <text y="3" className="node-text">
                SUBNET
              </text>
              <text y="30" className="node-sub">
                ap-south-1a
              </text>
            </g>

            <g
              className="graph-node"
              transform="translate(660, 180)"
              onClick={() => setSelectedAsset(DEFAULT_ASSETS.rds)}
            >
              <circle cx="0" cy="0" r="20" fill="#0E1015" stroke="#00F5D4" strokeWidth="1.5" />
              <text y="3" className="node-text">
                RDS DB
              </text>
              <text y="34" className="node-sub">
                KMS Encrypted
              </text>
            </g>

            <g
              className="graph-node"
              transform="translate(840, 500)"
              onClick={() => setSelectedAsset(DEFAULT_ASSETS.s3logs)}
            >
              <circle cx="0" cy="0" r="18" fill="#0E1015" stroke="#242A37" strokeWidth="1.5" />
              <text y="3" className="node-text">
                S3 LOGS
              </text>
              <text y="30" className="node-sub">
                Private
              </text>
            </g>
          </svg>
        </div>

        {/* Asset Telemetry Aside Panel */}
        <aside className="graph-details-aside">
          <div className="aside-title">
            <span>Asset Telemetry</span>
            <span className={`tag-sev ${sevClass}`}>{selectedAsset.severity}</span>
          </div>

          <div className="prop-row">
            <span className="prop-label">Resource ID</span>
            <span className="prop-val">{selectedAsset.id}</span>
          </div>

          <div className="prop-row">
            <span className="prop-label">Entity Classification</span>
            <span className="prop-val">{selectedAsset.type}</span>
          </div>

          <div className="prop-row">
            <span className="prop-label">Condition &amp; Exposure</span>
            <span className="prop-val" style={{ color: 'var(--cyan-bright)' }}>
              {selectedAsset.exposure}
            </span>
          </div>

          <div className="prop-row">
            <span className="prop-label">Attack Path Graph Association</span>
            <span
              className="prop-val"
              style={{
                fontFamily: 'var(--font-sans)',
                color: 'var(--text-secondary)',
                fontSize: '11.5px',
              }}
            >
              {selectedAsset.desc}
            </span>
          </div>

          <div style={{ marginTop: 'auto' }}>
            <button
              type="button"
              className="btn btn-cyan"
              style={{ width: '100%', justifyContent: 'center' }}
              onClick={handleInspectFinding}
            >
              Inspect Rule Violations
            </button>
          </div>
        </aside>
      </div>
    </div>
  );
}
