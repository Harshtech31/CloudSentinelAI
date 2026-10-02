/**
 * Knowledge graph placeholder (roadmap task 21).
 *
 * Phase 2 mounts the Cytoscape canvas here, styled per the approved
 * mockup's graph view (Fig A.2): category colors, risk-scored nodes,
 * stats rail.
 */
export default function GraphPage() {
  return (
    <section className="page">
      <header className="page-head">
        <div>
          <h2>Knowledge Graph</h2>
          <p>Assets and their relationships, risk-scored.</p>
        </div>
      </header>
      <div className="panel placeholder-note">
        <h3>Graph canvas arrives with the first scan</h3>
        <p>Nodes and edges are built from collected resources during Phase 2.</p>
      </div>
    </section>
  );
}
