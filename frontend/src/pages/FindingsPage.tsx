/**
 * Security findings placeholder (roadmap task 21).
 *
 * Phase 2 replaces this with the findings table from the approved
 * mockup: severity chips, risk scores, status pills, filters.
 */
export default function FindingsPage() {
  return (
    <section className="page">
      <header className="page-head">
        <div>
          <h2>Security Findings</h2>
          <p>Misconfigurations ranked by contextual risk.</p>
        </div>
      </header>
      <div className="panel placeholder-note">
        <h3>Findings appear after a scan</h3>
        <p>The rule engine runs during the scan pipeline in Phase 2.</p>
      </div>
    </section>
  );
}
