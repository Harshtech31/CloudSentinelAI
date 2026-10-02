import { AwsServiceIcon } from '../components/AwsServiceIcon';

const SCAN_STAGES = [
  'Asset discovery',
  'Knowledge graph',
  'Attack graph',
  'Risk assessment',
  'AI recommendations',
];

const SCANNED_SERVICES: Array<{ key: string; label: string }> = [
  { key: 'iam', label: 'IAM' },
  { key: 'ec2', label: 'EC2' },
  { key: 's3', label: 'S3' },
  { key: 'vpc', label: 'VPC' },
  { key: 'security-group', label: 'Security Group' },
  { key: 'rds', label: 'RDS' },
  { key: 'cloudtrail', label: 'CloudTrail' },
  { key: 'config', label: 'Config' },
];

/**
 * Scan control placeholder (roadmap task 21).
 *
 * Phase 2 wires the Start button to POST /scan/start and these stages
 * to the live scan timeline from the approved mockup.
 */
export default function ScanPage() {
  return (
    <section className="page">
      <header className="page-head">
        <div>
          <h2>Cloud Scan</h2>
          <p>Collect resources and analyze posture across regions.</p>
        </div>
        <button type="button" className="btn btn-primary" disabled>
          Start scan — coming in Phase 2
        </button>
      </header>

      <div className="panel">
        <h3>Services covered</h3>
        <div className="icon-strip">
          {SCANNED_SERVICES.map(({ key, label }) => (
            <span key={key} className="icon-chip" title={`AWS ${label}`}>
              <AwsServiceIcon service={key} size={22} />
              <small>{label}</small>
            </span>
          ))}
        </div>
      </div>

      <div className="panel">
        <h3>Scan stages</h3>
        <ol className="stage-list">
          {SCAN_STAGES.map((stage) => (
            <li key={stage}>{stage}</li>
          ))}
        </ol>
      </div>
    </section>
  );
}
