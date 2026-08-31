import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

export default function App() {
  return (
    <Router>
      <div style={{ minHeight: '100vh', backgroundColor: '#0f172a', color: '#f8fafc', padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
        <header style={{ borderBottom: '1px solid #334155', paddingBottom: '1rem', marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 'bold', color: '#38bdf8' }}>🛡️ CloudSentinel AI</h1>
          <p style={{ color: '#94a3b8', marginTop: '0.25rem' }}>Automated Cloud Security Posture Management & Attack Path Analysis</p>
        </header>
        <main>
          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '0.5rem', padding: '1.5rem' }}>
            <h2 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>System Status: Online</h2>
            <p style={{ color: '#94a3b8' }}>Phase 1 Foundation Scaffolded & Ready.</p>
          </div>
        </main>
      </div>
    </Router>
  );
}
