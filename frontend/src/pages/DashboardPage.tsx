import { Link } from 'react-router-dom';

const PLACEHOLDER_METRICS = [
  { label: 'Cloud Assets', value: '—', note: 'First scan pending' },
  { label: 'Misconfigurations', value: '—', note: 'First scan pending' },
  { label: 'Critical Findings', value: '—', note: 'First scan pending' },
  { label: 'Attack Paths', value: '—', note: 'First scan pending' },
];

/**
 * Operations dashboard placeholder (roadmap task 21).
 *
 * Phase 2 wires this to live scan data and rebuilds it to the approved
 * mockup (severity donut, attack-graph preview, findings table). For
 * now it states exactly what is missing and where to start.
 */
export default function DashboardPage() {
  return (
    <section className="page">
      <header className="page-head">
        <div>
          <h2>Operations</h2>
          <p>Security posture across your cloud accounts.</p>
        </div>
        <Link to="/scan" className="btn btn-primary">
          Run first scan
        </Link>
      </header>

      <div className="placeholder-grid">
        {PLACEHOLDER_METRICS.map((metric) => (
          <div key={metric.label} className="panel metric-card">
            <small>{metric.label}</small>
            <b>{metric.value}</b>
            <span>{metric.note}</span>
          </div>
        ))}
      </div>

      <div className="panel placeholder-note">
        <h3>No scan data yet</h3>
        <p>
          The dashboard fills in after the first scan completes. The pipeline
          (collectors → analyzers → graph → findings) is being built in Phase 2.
        </p>
      </div>
    </section>
  );
}
