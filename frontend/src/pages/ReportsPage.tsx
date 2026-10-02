const FORMATS = ['PDF', 'CSV', 'JSON'] as const;

/**
 * Reports placeholder (roadmap task 21).
 *
 * Phase 3 wires the export buttons to GET /reports in each format and
 * restyles per the mockup's report view (Fig A.4).
 */
export default function ReportsPage() {
  return (
    <section className="page">
      <header className="page-head">
        <div>
          <h2>Reports</h2>
          <p>Export posture and findings for audits.</p>
        </div>
      </header>
      <div className="panel placeholder-note">
        <h3>Export opens up in Phase 3</h3>
        <p>Report generation lands with the reports service: {FORMATS.join(', ')}.</p>
      </div>
    </section>
  );
}
