# CloudSentinel AI — Project Roadmap
## Part 3: Phase 3 — Risk Engine, AI & Full Dashboard

> **Duration:** 3 Weeks | **Target:** ~30 commits per person (~120 total)
> **Goal:** Complete AI-powered explanations, full dashboard with attack graph viz, and report generation.

---

## 🔵 Harshith (Lead) — Attack Engine Completion & Graph API

| # | Task | Branch Name |
|---|------|-------------|
| 1 | Implement multi-hop attack chains (depth > 3 paths) | `attack/multi-hop-chains` |
| 2 | Implement Internet → EC2 → IAM → Secrets → S3 full chain scenario | `attack/ssrf-chain-scenario` |
| 3 | Implement attack chain deduplication (avoid duplicate paths) | `attack/chain-deduplication` |
| 4 | Add CVSS-inspired scoring to attack paths (AV, AC, PR, UI) | `attack/cvss-scoring` |
| 5 | Add attack chain ranking by total risk score | `attack/chain-ranking` |
| 6 | Implement `graph/traversals.py` — shortest path between any two nodes | `graph/shortest-path` |
| 7 | Implement `graph/traversals.py` — find all paths from internet-facing entry nodes | `graph/entry-node-paths` |
| 8 | Expose attack chains via `api/v1/graph.py` — GET `/graph/attack-chains` | `api/attack-chains-endpoint` |
| 9 | Add attack chain highlight data to Cytoscape format (highlight edges red) | `graph/attack-highlight-serializer` |
| 10 | Implement `graph/builder.py` — internet-facing node tagging | `graph/internet-facing-tag` |
| 11 | Add graph filtering API — filter by resource type (IAM/EC2/S3) | `api/graph-filter` |
| 12 | Write performance test — attack path generation on 500 node graph | `test/attack-perf-500-nodes` |
| 13 | Write integration test — full scan to attack chain end-to-end | `test/e2e-attack-chain` |
| 14 | Add attack path count to dashboard summary API | `api/dashboard-attack-count` |
| 15 | Implement scenario: public EC2 + admin IAM role = critical chain | `attack/scenario-ec2-admin` |
| 16 | Implement scenario: public S3 + no encryption = high finding | `attack/scenario-s3-public` |
| 17 | Implement scenario: CloudTrail disabled + any public resource = blind-spot chain | `attack/scenario-cloudtrail-blind` |
| 18 | Add attack chain to report data model | `schemas/attack-chain-report-schema` |
| 19 | Write `docs/ARCHITECTURE.md` explaining graph + attack engine design | `docs/architecture-md` |
| 20 | Refactor attack engine — extract chain_builder as separate class | `attack/refactor-chain-builder` |
| 21 | Add attack engine config (max_depth, max_paths) to settings | `core/attack-engine-config` |
| 22 | Write unit tests for CVSS scoring | `test/cvss-scoring-unit` |
| 23 | Write unit tests for attack chain deduplication | `test/chain-dedup-unit` |
| 24 | Fix attack engine performance regression from Phase 2 | `fix/attack-perf-regression` |
| 25 | Add attack chain severity classification (critical/high/medium) | `attack/chain-severity-class` |
| 26 | Expose attack chain count per scan in scan results response | `api/scan-results-attack-count` |
| 27 | Write `docs/ATTACK_SCENARIOS.md` with all 5 evaluation scenarios | `docs/attack-scenarios-md` |
| 28 | Add Prometheus metrics endpoint `/metrics` (request count, scan time) | `infra/prometheus-metrics` |
| 29 | Update `docker-compose.yml` with optional Grafana + Prometheus | `infra/grafana-optional` |
| 30 | Tag release `v0.3.0-attack-engine` | `release/v0.3.0` |

---

## 🟢 Teammate 1 — Report Generation & API Hardening

| # | Task | Branch Name |
|---|------|-------------|
| 1 | Implement `reports/json.py` — full JSON report with findings + attack chains | `reports/json-real` |
| 2 | Implement `reports/csv.py` — CSV export of findings (pandas) | `reports/csv-real` |
| 3 | Implement `reports/html.py` — HTML report with Jinja2 template | `reports/html-real` |
| 4 | Create `reports/templates/report.html.j2` — styled HTML template | `reports/html-template` |
| 5 | Implement `reports/pdf.py` — PDF from HTML using weasyprint | `reports/pdf-real` |
| 6 | Implement `api/v1/reports.py` — POST `/reports/generate` (trigger generation) | `api/reports-generate` |
| 7 | Implement `api/v1/reports.py` — GET `/reports/{id}/download` (file download) | `api/reports-download` |
| 8 | Implement `api/v1/reports.py` — GET `/reports` (list reports for user) | `api/reports-list` |
| 9 | Add report format selection (json/csv/html/pdf) to generate endpoint | `api/reports-format-select` |
| 10 | Store generated report file path in DB + serve via API | `db/report-file-path` |
| 11 | Implement `api/v1/dashboard.py` — GET `/dashboard/trends` (findings over time) | `api/dashboard-trends` |
| 12 | Implement `api/v1/dashboard.py` — GET `/dashboard/top-risks` (top 10 critical findings) | `api/dashboard-top-risks` |
| 13 | Add request logging middleware (log all API calls to audit table) | `api/request-logging-middleware` |
| 14 | Implement API key authentication (alternative to JWT for CLI use) | `auth/api-key-auth` |
| 15 | Add input validation — reject invalid AWS region strings | `api/input-validation-region` |
| 16 | Add input validation — sanitize all string fields | `api/input-validation-sanitize` |
| 17 | Implement global exception handler with structured error responses | `api/global-exception-handler` |
| 18 | Add response compression middleware (gzip) | `api/gzip-middleware` |
| 19 | Add ETag caching for GET `/graph` and GET `/findings` responses | `api/etag-caching` |
| 20 | Write unit tests for JSON report generator | `test/json-report-unit` |
| 21 | Write unit tests for HTML report generator | `test/html-report-unit` |
| 22 | Write unit tests for PDF report generator | `test/pdf-report-unit` |
| 23 | Write integration test for report download flow | `test/report-download-integration` |
| 24 | Add `GET /scan/{id}/summary` — compact summary for dashboard card | `api/scan-summary` |
| 25 | Add scan history endpoint with date range filter | `api/scan-history-filter` |
| 26 | Implement user settings endpoint (GET/PATCH `/users/me/settings`) | `api/user-settings` |
| 27 | Add DB index on findings table (scan_id, severity, created_at) | `db/findings-index` |
| 28 | Write `docs/API.md` — full API endpoint reference | `docs/api-reference-md` |
| 29 | Add health check to return DB connection status | `api/health-db-check` |
| 30 | Tag release `v0.3.0-reports` | `release/v0.3.0-reports` |

---

## 🟡 Teammate 2 — Rule Engine Completion & Compliance

| # | Task | Branch Name |
|---|------|-------------|
| 1 | Implement 20 CIS AWS Benchmark v1.5 IAM rules | `analyzer/cis-iam-rules` |
| 2 | Implement CIS networking rules (SG, NACLs, VPC flow logs) | `analyzer/cis-network-rules` |
| 3 | Implement CIS storage rules (S3 public access, logging, versioning) | `analyzer/cis-storage-rules` |
| 4 | Implement CIS logging rules (CloudTrail, Config recorder) | `analyzer/cis-logging-rules` |
| 5 | Implement CIS monitoring rules (CloudWatch alarms) | `analyzer/cis-monitoring-rules` |
| 6 | Implement AWS Well-Architected Framework security pillar rules | `analyzer/well-arch-rules` |
| 7 | Implement NIST SP 800-53 control mappings for findings | `analyzer/nist-mappings` |
| 8 | Add compliance framework field to each finding (CIS/NIST/AWS-WAF) | `schemas/finding-compliance-field` |
| 9 | Implement `analyzers/compliance.py` — overall compliance score (%) | `analyzer/compliance-score` |
| 10 | Implement `api/v1/findings.py` — GET `/findings/compliance-report` | `api/compliance-report` |
| 11 | Implement `analyzers/iam.py` — rule: password policy too weak | `analyzer/iam-password-policy` |
| 12 | Implement `analyzers/iam.py` — rule: access key rotation > 90 days | `analyzer/iam-key-rotation` |
| 13 | Implement `analyzers/iam.py` — rule: IAM user with both console + API access | `analyzer/iam-dual-access` |
| 14 | Implement `analyzers/networking.py` — rule: VPC flow logs disabled | `analyzer/networking-flow-logs` |
| 15 | Implement `analyzers/networking.py` — rule: default VPC in use | `analyzer/networking-default-vpc` |
| 16 | Implement `analyzers/storage.py` — rule: S3 object-level logging off | `analyzer/storage-object-logging` |
| 17 | Implement `analyzers/encryption.py` — rule: EC2 root volume unencrypted | `analyzer/encryption-ec2-volume` |
| 18 | Implement `analyzers/encryption.py` — rule: RDS backups unencrypted | `analyzer/encryption-rds-backup` |
| 19 | Implement `analyzers/misconfigurations.py` — tag each finding with rule_id | `analyzer/finding-rule-id` |
| 20 | Add false positive suppression — allowlist by resource ARN | `analyzer/false-positive-suppress` |
| 21 | Implement rule severity override config (per-org customization) | `analyzer/severity-override` |
| 22 | Add rule documentation metadata (description, remediation URL) | `analyzer/rule-metadata` |
| 23 | Write unit tests for CIS IAM rules (all 20) | `test/cis-iam-rules-unit` |
| 24 | Write unit tests for CIS networking rules | `test/cis-network-rules-unit` |
| 25 | Write unit tests for compliance scoring | `test/compliance-score-unit` |
| 26 | Add multi-account scanning support stub (assume_role) | `collector/multi-account-stub` |
| 27 | Implement dry-run mode — collect + analyze without saving to DB | `collector/dry-run-mode` |
| 28 | Add resource count summary to scan results (total resources per service) | `schemas/resource-count-summary` |
| 29 | Write `docs/RULES.md` — document all implemented security rules | `docs/rules-reference-md` |
| 30 | Tag release `v0.3.0-rules` | `release/v0.3.0-rules` |

---

## 🟠 Teammate 3 — AI Integration & Complete Dashboard

| # | Task | Branch Name |
|---|------|-------------|
| 1 | Implement `ai/providers/openai.py` — real OpenAI API call | `ai/openai-real` |
| 2 | Implement `ai/providers/ollama.py` — real Ollama local call | `ai/ollama-real` |
| 3 | Implement `ai/prompts.py` — finding explanation prompt template | `ai/prompt-finding-explain` |
| 4 | Implement `ai/prompts.py` — attack chain narration prompt | `ai/prompt-attack-narration` |
| 5 | Implement `ai/prompts.py` — remediation steps prompt | `ai/prompt-remediation` |
| 6 | Implement `ai/parser.py` — parse LLM JSON response reliably | `ai/parser-real` |
| 7 | Implement `ai/explain.py` — generate explanation for a single finding | `ai/explain-real` |
| 8 | Implement `ai/recommendations.py` — generate remediation steps (with code) | `ai/recommendations-real` |
| 9 | Implement `ai/explain.py` — batch explain all findings in a scan | `ai/batch-explain` |
| 10 | Add LLM provider selection via env var (openai / ollama / bedrock) | `ai/provider-selection` |
| 11 | Add LLM response caching (cache explanation by finding hash) | `ai/response-cache` |
| 12 | Wire AI explanation into scan pipeline (post-risk-scoring step) | `ai/pipeline-wire` |
| 13 | Add `ai_explanation` field to finding model + migration | `db/finding-ai-explanation` |
| 14 | Expose AI explanation in `GET /findings/{id}` response | `api/finding-with-ai` |
| 15 | Implement `DashboardPage.tsx` — complete redesign with live data | `frontend/dashboard-live` |
| 16 | Add scan history list to dashboard (last 5 scans) | `frontend/dashboard-scan-history` |
| 17 | Implement `FindingsPage.tsx` — expandable row with AI explanation | `frontend/findings-ai-expand` |
| 18 | Implement `GraphPage.tsx` — attack chain highlighting (red edges) | `frontend/graph-attack-highlight` |
| 19 | Add graph controls: zoom in/out, fit to screen, reset layout | `frontend/graph-controls` |
| 20 | Add node type filters in graph page (show/hide IAM, EC2, S3) | `frontend/graph-node-filters` |
| 21 | Implement `ReportsPage.tsx` — generate + download report UI | `frontend/reports-page-real` |
| 22 | Add loading skeletons to all data pages | `frontend/loading-skeletons` |
| 23 | Add empty state illustrations (no scans yet, no findings) | `frontend/empty-states` |
| 24 | Implement dark/light theme toggle | `frontend/theme-toggle` |
| 25 | Add `components/RiskScoreGauge.tsx` — animated gauge (0–10) | `frontend/risk-gauge` |
| 26 | Implement `components/AttackChainCard.tsx` — attack path summary card | `frontend/attack-chain-card` |
| 27 | Add recharts line chart — risk score trend over scans | `frontend/risk-trend-chart` |
| 28 | Implement responsive layout (mobile-friendly sidebar) | `frontend/responsive-layout` |
| 29 | Write unit tests for AI prompt builder | `test/ai-prompt-unit` |
| 30 | Tag release `v0.3.0-ai-dashboard` | `release/v0.3.0-ai` |

---

## ✅ Phase 3 Deliverable Checklist

- [ ] LLM generates explanation + remediation for every finding
- [ ] AI explanations stored in DB + shown in UI
- [ ] All 20+ CIS AWS Benchmark rules implemented
- [ ] Compliance score shown per scan
- [ ] Attack chains highlighted in graph visualization
- [ ] Reports downloadable as JSON / CSV / HTML / PDF
- [ ] Dashboard is fully live with real data and charts
- [ ] Dark/light theme toggle working
- [ ] **~120 commits total** (30 × 4 members) ✅

---

> 📌 **Next:** `roadmap_part4_evaluation_polish.md` — Phase 4: Testing, evaluation against baselines, final polish and docs.
