const SCAN_STAGES = [
  'Asset discovery',
  'Knowledge graph',
  'Attack graph',
  'Risk assessment',
  'AI recommendations',
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
