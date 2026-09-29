# 👤 Member 3 — Complete Work Plan (Consolidated)

> **Role:** Risk Engine, AI Explanations & Frontend Dashboard
> **Owns:** `backend/app/risk_engine/`, `backend/app/ai/`, `backend/app/reports/`, `frontend/`
> **Total tasks:** 107 across 4 phases (22 + 30 + 30 + 25)

---

## 📍 Where this plan lives in the repo

| Phase | Source file | Section |
|---|---|---|
| Phase 1 — Scaffolding | `docs/roadmap_part1_overview.md` | Line ~137 → "🟠 Teammate 3 — Risk Engine, AI & Frontend Scaffolding" |
| Phase 2 — Frontend Wiring & Risk Engine | `docs/roadmap_part2_core_pipeline.md` | "🟠 Teammate 3 — Frontend Wiring & Risk Engine Foundation" |
| Phase 3 — AI Integration & Dashboard | `docs/roadmap_part3_risk_ai_dashboard.md` | "🟠 Teammate 3 — AI Integration & Complete Dashboard" |
| Phase 4 — Frontend Polish, UX & E2E | `docs/roadmap_part4_evaluation_polish.md` | "🟠 Teammate 3 — Frontend Polish, UX & E2E Tests" |

---

## 📦 Files Member 3 owns (current status)

| File | Status |
|---|---|
| `backend/app/risk_engine/{__init__,weights,context,calculator,prioritizer,business_impact}.py` | ❌ All empty (0 bytes) |
| `backend/app/ai/{__init__,prompts,parser,explain,recommendations}.py` | ❌ All empty |
| `backend/app/ai/providers/{__init__,openai,bedrock,ollama}.py` | ❌ All empty |
| `backend/app/reports/{__init__,json,csv,html,pdf}.py` | ❌ All empty |
| `backend/app/api/v1/reports.py` | ⚠️ Stub exists (Lead's Phase 1) |
| `frontend/package.json` | ✅ Vite + TS + all deps installed (axios, zustand, recharts, cytoscape, react-router) |
| `frontend/src/index.css` | ⚠️ Minimal dark theme only — full design tokens missing |
| `frontend/src/App.tsx` | ⚠️ Static status page — no routes |
| `frontend/src/{pages,components,layouts,store,api,types,hooks,contexts}/` | ❌ Empty (.gitkeep only) |

---

## Phase 1 — Risk Engine, AI & Frontend Scaffolding (22 tasks)

> Goal: backend stubs import cleanly; React app routes with Login page + wired auth form.
> **Status: backend 0% (empty files) · frontend deps done, structure 0% · tasks 14-16 pre-done.**

### Risk engine stubs (backend)
- [ ] 1. `risk_engine/__init__.py` + base classes
- [ ] 2. `risk_engine/weights.py` — scoring weight constants
- [ ] 3. `risk_engine/context.py` — context data model
- [ ] 4. `risk_engine/calculator.py` — base risk formula stub
- [ ] 5. `risk_engine/prioritizer.py` — stub sorter
- [ ] 6. `risk_engine/business_impact.py` — impact mapper stub

### AI stubs (backend)
- [ ] 7. `ai/__init__.py` + AI provider interface
- [ ] 8. `ai/providers/openai.py` — OpenAI client stub
- [ ] 9. `ai/providers/bedrock.py` + `ollama.py` stubs
- [ ] 10. `ai/prompts.py` — prompt templates skeleton
- [ ] 11. `ai/parser.py` + `ai/explain.py` stubs
- [ ] 12. `ai/recommendations.py` stub

### Reports stubs (backend)
- [ ] 13. `reports/__init__.py` + json/csv/html/pdf stubs
- [x] 14. `api/v1/reports.py` stub endpoint *(pre-existing from Lead's Phase 1)*

### Frontend scaffolding
- [x] 15. Init React app with Vite + TypeScript *(pre-existing, commit `4753eb9`)*
- [x] 16. Install deps: react-router, axios, zustand, recharts, cytoscape *(pre-existing)*
- [ ] 17. Set up global CSS + design tokens (dark theme, colors, fonts) *(partial — minimal CSS exists)*
- [ ] 18. Set up React Router + all route paths
- [ ] 19. Create `layouts/MainLayout.tsx` + `AuthLayout.tsx`
- [ ] 20. Create `components/Navbar.tsx` + `Sidebar.tsx`
- [ ] 21. Create all page placeholders (Login, Dashboard, Scan, Graph, Findings, Reports)
- [ ] 22. Set up Zustand auth store + `AuthContext.tsx` + wire login form

---

## Phase 2 — Frontend Wiring & Risk Engine Foundation (30 tasks)

> Goal: frontend talks to the real API; risk scores attached to findings. **Status: 0%.**

### Types & API clients
- [ ] 1. `frontend/src/types/scan.ts` — Scan + Finding TypeScript types
- [ ] 2. `frontend/src/types/graph.ts` — Graph node/edge types
- [ ] 3. `frontend/src/api/scanApi.ts` — start, status, results, list
- [ ] 4. `frontend/src/api/findingsApi.ts` — list, detail, resolve
- [ ] 5. `frontend/src/api/graphApi.ts` — fetch graph data

### Scan & Findings UI
- [ ] 6. `ScanPage.tsx` — AWS credentials form + start scan button
- [ ] 7. Scan status polling (useEffect + interval)
- [ ] 8. Scan progress bar UI component
- [ ] 9. `FindingsPage.tsx` — findings table with severity badges
- [ ] 10. Severity filter on findings table
- [ ] 11. Pagination on findings table
- [ ] 12. `components/FindingCard.tsx` — single finding detail card

### Graph UI
- [ ] 13. `GraphPage.tsx` — Cytoscape.js canvas render
- [ ] 14. Node click handler — details in sidebar
- [ ] 15. Graph legend (IAM/EC2/S3 nodes, attack paths)

### Dashboard
- [ ] 16. `DashboardPage.tsx` — summary stat cards
- [ ] 17. Recharts bar chart — findings by severity
- [ ] 18. Recharts pie chart — findings by service

### State & UX
- [ ] 19. Zustand `scanStore.ts` — global scan state
- [ ] 20. Toast notifications on scan complete/error

### Risk engine (real)
- [ ] 21. `risk_engine/calculator.py` — real risk score formula
- [ ] 22. `risk_engine/context.py` — extract context from graph
- [ ] 23. `risk_engine/weights.py` — tuned weight values
- [ ] 24. `risk_engine/business_impact.py` — data sensitivity mapping
- [ ] 25. `risk_engine/prioritizer.py` — sort findings by risk score
- [ ] 26. Wire risk engine into scan pipeline (enrich findings)
- [ ] 27. Risk score display in `FindingCard.tsx` (0–10 badge)
- [ ] 28. Sort-by-risk-score in findings table
- [ ] 29. Unit test for risk calculator
- [ ] 30. Tag release `v0.2.0-frontend`

---

## Phase 3 — AI Integration & Complete Dashboard (30 tasks)

> Goal: LLM explanations for every finding, full dashboard, reports UI. **Status: 0%.**

### AI backend
- [ ] 1. `ai/providers/openai.py` — real OpenAI API call
- [ ] 2. `ai/providers/ollama.py` — real Ollama local call
- [ ] 3. `ai/prompts.py` — finding explanation prompt
- [ ] 4. `ai/prompts.py` — attack chain narration prompt
- [ ] 5. `ai/prompts.py` — remediation steps prompt
- [ ] 6. `ai/parser.py` — parse LLM JSON response reliably
- [ ] 7. `ai/explain.py` — explanation for a single finding
- [ ] 8. `ai/recommendations.py` — remediation steps (with code)
- [ ] 9. `ai/explain.py` — batch explain all findings in a scan
- [ ] 10. LLM provider selection via env var (openai / ollama / bedrock)
- [ ] 11. LLM response caching (by finding hash)
- [ ] 12. Wire AI explanation into scan pipeline (post-risk-scoring)
- [ ] 13. `ai_explanation` field on finding model + migration
- [ ] 14. Expose AI explanation in `GET /findings/{id}`

### Dashboard & frontend completion
- [ ] 15. `DashboardPage.tsx` — complete redesign with live data
- [ ] 16. Scan history list on dashboard (last 5 scans)
- [ ] 17. `FindingsPage.tsx` — expandable row with AI explanation
- [ ] 18. `GraphPage.tsx` — attack chain highlighting (red edges)
- [ ] 19. Graph controls: zoom, fit, reset layout
- [ ] 20. Node type filters in graph page
- [ ] 21. `ReportsPage.tsx` — generate + download report UI
- [ ] 22. Loading skeletons on all data pages
- [ ] 23. Empty state illustrations (no scans, no findings)
- [ ] 24. Dark/light theme toggle
- [ ] 25. `components/RiskScoreGauge.tsx` — animated gauge (0–10)
- [ ] 26. `components/AttackChainCard.tsx` — attack path summary card
- [ ] 27. Recharts line chart — risk score trend over scans
- [ ] 28. Responsive layout (mobile-friendly sidebar)
- [ ] 29. Unit test for AI prompt builder
- [ ] 30. Tag release `v0.3.0-ai-dashboard`

---

## Phase 4 — Frontend Polish, UX & E2E Tests (25 tasks)

> Goal: production-quality UI, accessibility, E2E coverage. **Status: 0%.**

- [ ] 1. UI audit — fix all broken/misaligned components
- [ ] 2. Keyboard navigation (Tab, Enter, Esc) across all pages
- [ ] 3. ARIA labels + roles for accessibility
- [ ] 4. Global error boundary
- [ ] 5. 404 Not Found page
- [ ] 6. Network error handling with retry button
- [ ] 7. `components/ConfirmModal.tsx` for destructive actions
- [ ] 8. `GraphPage.tsx` — minimap, pan/zoom shortcuts
- [ ] 9. Attack chain step-through animation
- [ ] 10. Finding detail drawer/modal with full AI explanation
- [ ] 11. Remediation code block rendering (syntax highlighted)
- [ ] 12. Copy-to-clipboard for remediation code
- [ ] 13. `ReportsPage.tsx` — download progress indicator
- [ ] 14. `pages/SettingsPage.tsx` — AWS credentials, LLM provider
- [ ] 15. Profile page (user info, scan stats)
- [ ] 16. Frontend search — findings by resource name/type
- [ ] 17. `components/Badge.tsx`, `Tooltip.tsx`, `Chip.tsx` reusable atoms
- [ ] 18. Dashboard stat card count-up animations
- [ ] 19. Set up Playwright for E2E testing
- [ ] 20. E2E test — login + start scan + view findings
- [ ] 21. E2E test — graph page loads + node click details
- [ ] 22. E2E test — download report as PDF
- [ ] 23. Bundle optimization (code splitting, lazy routes)
- [ ] 24. `docs/USER_GUIDE.md` — end-user guide with screenshots
- [ ] 25. Tag release `v1.0.0-frontend-polish`

---

## 🔗 Dependencies on other members

| Depends on | Why |
|---|---|
| **Member 1** (DB & Auth) | Login form needs real `/auth/login`; auth store needs JWT endpoints; findings UI needs DB-backed APIs |
| **Member 2** (Collectors) | Risk engine scores the findings analyzers produce; dashboard/charts need real finding data |
| **Lead** (Graph/Attack) | Graph page renders the Cytoscape serializer output; attack chain cards need chain data |

## 🚀 Suggested build order (when work starts)

1. Phase 1 backend stubs: risk_engine → ai → reports (mirror Member 2's approach: structured stubs, tested, one commit each)
2. Phase 1 frontend: design tokens → router + layouts → nav components → page placeholders → auth store + login form
3. Phase 2: TS types + API clients → risk engine real implementation → pages with live data
4. Phase 3: AI providers + prompts + caching → dashboard redesign → reports UI
5. Phase 4: a11y + polish → Playwright E2E → bundle optimization
