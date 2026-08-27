# CloudSentinel AI — Project Roadmap
## Part 2: Phase 2 — Core Pipeline (Collectors → Graph)

> **Duration:** 3 Weeks | **Target:** ~30 commits per person (~120 total)
> **Goal:** Make the end-to-end scan pipeline work — real AWS data in, real findings + graph out.

---

## 🔵 Harshith (Lead) — Graph Builder & Attack Engine

| # | Task | Branch Name |
|---|------|-------------|
| 1 | Implement `graph/models.py` — Node + Edge dataclasses | `graph/node-edge-models` |
| 2 | Implement `graph/builder.py` — add_node / add_edge logic | `graph/builder-core` |
| 3 | Build IAM relationship edges (User → Role → Policy) | `graph/iam-edges` |
| 4 | Build network relationship edges (SG → EC2 → VPC) | `graph/network-edges` |
| 5 | Build data access edges (EC2 → S3, EC2 → RDS) | `graph/data-access-edges` |
| 6 | Implement `graph/networkx.py` — in-memory NetworkX graph | `graph/networkx-impl` |
| 7 | Implement `graph/traversals.py` — BFS/DFS traversal helpers | `graph/traversals` |
| 8 | Implement `graph/neo4j.py` — Neo4j client stub (future) | `graph/neo4j-stub` |
| 9 | Implement `attack_engine/attack_graph.py` — build attack graph from knowledge graph | `attack/graph-builder` |
| 10 | Implement `attack_engine/attack_paths.py` — BFS path finder from entry nodes | `attack/path-finder` |
| 11 | Implement `attack_engine/lateral_movement.py` — detect EC2 → EC2 lateral moves | `attack/lateral-movement` |
| 12 | Implement `attack_engine/privilege_escalation.py` — detect IAM priv-esc paths | `attack/priv-esc` |
| 13 | Implement `attack_engine/scoring.py` — path severity score | `attack/path-scoring` |
| 14 | Write `api/v1/graph.py` — GET `/graph` endpoint (returns graph JSON) | `api/graph-endpoint` |
| 15 | Write graph serializer — convert NetworkX graph to Cytoscape.js format | `graph/cytoscape-serializer` |
| 16 | Write integration test — graph builder with mock AWS data | `test/graph-integration` |
| 17 | Write unit test — attack path detection | `test/attack-path-unit` |
| 18 | Write unit test — lateral movement detection | `test/lateral-movement-unit` |
| 19 | Write unit test — privilege escalation detection | `test/priv-esc-unit` |
| 20 | Wire attack engine into scan pipeline (attack paths stored to DB) | `attack/pipeline-wire` |
| 21 | Add graph stats endpoint — node count, edge count, attack path count | `api/graph-stats` |
| 22 | Write `infrastructure/` Docker setup for optional Neo4j service | `infra/neo4j-service` |
| 23 | Performance test — graph build time for 100 resources | `test/graph-perf` |
| 24 | Update `README.md` with graph architecture notes | `docs/graph-readme` |
| 25 | Fix bugs from Phase 1 integration (CI red fixes) | `fix/phase1-ci-bugs` |
| 26 | Add graph endpoint to Swagger docs | `docs/graph-swagger` |
| 27 | Write `graph/builder.py` — merge graphs from multiple collectors | `graph/multi-collector-merge` |
| 28 | Handle missing/null AWS fields gracefully in graph builder | `graph/null-safety` |
| 29 | Add logging to all attack engine steps | `attack/logging` |
| 30 | Tag release `v0.2.0-graph` | `release/v0.2.0` |

---

## 🟢 Teammate 1 — Scan Pipeline & API

| # | Task | Branch Name |
|---|------|-------------|
| 1 | Implement `database/repositories/scan_repo.py` — CRUD for scans | `db/scan-repository` |
| 2 | Implement `database/repositories/finding_repo.py` — CRUD for findings | `db/finding-repository` |
| 3 | Implement `database/repositories/report_repo.py` — CRUD for reports | `db/report-repository` |
| 4 | Implement `tasks/scan_task.py` — background scan orchestrator | `tasks/scan-orchestrator` |
| 5 | Wire collector → analyzer → graph → findings in `scan_task.py` | `tasks/pipeline-wire` |
| 6 | Implement `api/v1/scan.py` — POST `/scan/start` (create scan + trigger task) | `api/scan-start` |
| 7 | Implement `api/v1/scan.py` — GET `/scan/{id}/status` (poll scan status) | `api/scan-status` |
| 8 | Implement `api/v1/scan.py` — GET `/scan/{id}/results` (get findings) | `api/scan-results` |
| 9 | Implement `api/v1/scan.py` — GET `/scans` (list all scans for user) | `api/scan-list` |
| 10 | Implement `api/v1/findings.py` — GET `/findings` with pagination | `api/findings-paginated` |
| 11 | Implement `api/v1/findings.py` — GET `/findings/{id}` single finding | `api/finding-detail` |
| 12 | Implement `api/v1/findings.py` — PATCH `/findings/{id}` (mark resolved) | `api/finding-resolve` |
| 13 | Implement `api/v1/findings.py` — GET `/findings/stats` (severity counts) | `api/findings-stats` |
| 14 | Implement `api/v1/dashboard.py` — GET `/dashboard/summary` | `api/dashboard-summary` |
| 15 | Add Pydantic response schemas for scan + finding endpoints | `schemas/scan-response-schemas` |
| 16 | Add scan status enum (pending, running, completed, failed) | `schemas/scan-status-enum` |
| 17 | Add severity enum (critical, high, medium, low, info) | `schemas/severity-enum` |
| 18 | Implement rate limiting on `/scan/start` (max 1 concurrent scan/user) | `api/scan-rate-limit` |
| 19 | Add scan cancellation endpoint — DELETE `/scan/{id}` | `api/scan-cancel` |
| 20 | Write unit test for scan repository | `test/scan-repo-unit` |
| 21 | Write unit test for finding repository | `test/finding-repo-unit` |
| 22 | Write integration test for full scan flow (mock collectors) | `test/scan-integration` |
| 23 | Add DB migration for scan status + timestamps | `db/migration-scan-status` |
| 24 | Add error handling — catch AWS credential errors in scan | `api/aws-cred-error-handling` |
| 25 | Add scan duration tracking (start_time, end_time) | `db/scan-duration-fields` |
| 26 | Update OpenAPI docs for all scan endpoints | `docs/scan-swagger` |
| 27 | Write `api/v1/auth.py` — GET `/me` profile endpoint | `api/auth-me` |
| 28 | Add audit log model + migration | `db/audit-log-model` |
| 29 | Write audit log entries on scan create/complete | `db/audit-log-entries` |
| 30 | Tag release `v0.2.0-api` | `release/v0.2.0-api` |

---

## 🟡 Teammate 2 — Real Collectors & Analyzers

| # | Task | Branch Name |
|---|------|-------------|
| 1 | Implement `collectors/aws/iam.py` — list users, roles, policies (boto3) | `collector/aws-iam-real` |
| 2 | Implement `collectors/aws/iam.py` — collect attached + inline policies | `collector/aws-iam-policies` |
| 3 | Implement `collectors/aws/iam.py` — collect MFA status per user | `collector/aws-iam-mfa` |
| 4 | Implement `collectors/aws/ec2.py` — list instances with metadata | `collector/aws-ec2-real` |
| 5 | Implement `collectors/aws/ec2.py` — collect instance IAM profiles | `collector/aws-ec2-iam-profiles` |
| 6 | Implement `collectors/aws/s3.py` — list buckets + ACL + public access block | `collector/aws-s3-real` |
| 7 | Implement `collectors/aws/s3.py` — collect bucket encryption settings | `collector/aws-s3-encryption` |
| 8 | Implement `collectors/aws/s3.py` — collect bucket logging status | `collector/aws-s3-logging` |
| 9 | Implement `collectors/aws/vpc.py` — list VPCs + subnets + route tables | `collector/aws-vpc-real` |
| 10 | Implement `collectors/aws/security_groups.py` — list SGs + rules | `collector/aws-sg-real` |
| 11 | Implement `collectors/aws/rds.py` — list instances + encryption status | `collector/aws-rds-real` |
| 12 | Implement `collectors/aws/cloudtrail.py` — check trail status + logging | `collector/aws-cloudtrail-real` |
| 13 | Implement `collectors/aws/config.py` — AWS Config recorder status | `collector/aws-config-real` |
| 14 | Add multi-region support to all collectors | `collector/multi-region` |
| 15 | Implement `analyzers/iam.py` — rule: root account MFA disabled | `analyzer/iam-root-mfa` |
| 16 | Implement `analyzers/iam.py` — rule: admin wildcard policy | `analyzer/iam-admin-wildcard` |
| 17 | Implement `analyzers/iam.py` — rule: unused IAM credentials (90 days) | `analyzer/iam-unused-creds` |
| 18 | Implement `analyzers/networking.py` — rule: SG allows 0.0.0.0/0 on SSH/RDP | `analyzer/networking-open-ssh-rdp` |
| 19 | Implement `analyzers/networking.py` — rule: SG allows all traffic | `analyzer/networking-all-traffic` |
| 20 | Implement `analyzers/storage.py` — rule: public S3 bucket | `analyzer/storage-public-s3` |
| 21 | Implement `analyzers/storage.py` — rule: S3 bucket without versioning | `analyzer/storage-s3-versioning` |
| 22 | Implement `analyzers/encryption.py` — rule: unencrypted RDS | `analyzer/encryption-rds` |
| 23 | Implement `analyzers/encryption.py` — rule: unencrypted S3 bucket | `analyzer/encryption-s3` |
| 24 | Implement `analyzers/compliance.py` — CIS AWS Benchmark v1.5 rules (20 rules) | `analyzer/cis-benchmark` |
| 25 | Implement `analyzers/misconfigurations.py` — orchestrate all analyzers | `analyzer/orchestrator` |
| 26 | Add finding model fields: rule_id, resource_arn, region, remediation_url | `schemas/finding-enriched` |
| 27 | Write unit tests for IAM analyzer rules | `test/iam-analyzer-unit` |
| 28 | Write unit tests for networking analyzer rules | `test/networking-analyzer-unit` |
| 29 | Write unit tests for storage analyzer rules | `test/storage-analyzer-unit` |
| 30 | Tag release `v0.2.0-collectors` | `release/v0.2.0-collectors` |

---

## 🟠 Teammate 3 — Frontend Wiring & Risk Engine Foundation

| # | Task | Branch Name |
|---|------|-------------|
| 1 | Write `frontend/src/types/scan.ts` — Scan + Finding TypeScript types | `frontend/scan-types` |
| 2 | Write `frontend/src/types/graph.ts` — Graph node/edge types | `frontend/graph-types` |
| 3 | Write `frontend/src/api/scanApi.ts` — start, status, results, list | `frontend/scan-api-service` |
| 4 | Write `frontend/src/api/findingsApi.ts` — list, detail, resolve | `frontend/findings-api-service` |
| 5 | Write `frontend/src/api/graphApi.ts` — fetch graph data | `frontend/graph-api-service` |
| 6 | Implement `ScanPage.tsx` — AWS credentials form + start scan button | `frontend/scan-form` |
| 7 | Implement scan status polling (useEffect + interval) | `frontend/scan-polling` |
| 8 | Implement scan progress bar UI component | `frontend/scan-progress-bar` |
| 9 | Implement `FindingsPage.tsx` — findings table with severity badges | `frontend/findings-table` |
| 10 | Add severity filter to findings table (critical/high/medium/low) | `frontend/findings-filter` |
| 11 | Add pagination to findings table | `frontend/findings-pagination` |
| 12 | Create `components/FindingCard.tsx` — single finding detail card | `frontend/finding-card` |
| 13 | Implement `GraphPage.tsx` — Cytoscape.js canvas render | `frontend/graph-canvas` |
| 14 | Add node click handler — show node details in sidebar | `frontend/graph-node-click` |
| 15 | Add graph legend (IAM nodes, EC2 nodes, S3 nodes, attack paths) | `frontend/graph-legend` |
| 16 | Implement `DashboardPage.tsx` — summary stats cards (total findings, critical count) | `frontend/dashboard-stats` |
| 17 | Add recharts bar chart — findings by severity | `frontend/dashboard-severity-chart` |
| 18 | Add recharts pie chart — findings by service (IAM, EC2, S3) | `frontend/dashboard-service-chart` |
| 19 | Set up Zustand `scanStore.ts` — store scan state globally | `frontend/scan-store` |
| 20 | Add toast notifications on scan complete/error | `frontend/toast-notifications` |
| 21 | Implement `risk_engine/calculator.py` — real risk score formula | `risk/calculator-real` |
| 22 | Implement `risk_engine/context.py` — extract context from graph | `risk/context-extraction` |
| 23 | Implement `risk_engine/weights.py` — tuned weight values | `risk/weights-tuned` |
| 24 | Implement `risk_engine/business_impact.py` — data sensitivity mapping | `risk/business-impact-real` |
| 25 | Implement `risk_engine/prioritizer.py` — sort findings by risk score | `risk/prioritizer-real` |
| 26 | Wire risk engine into scan pipeline (enrich findings with scores) | `risk/pipeline-wire` |
| 27 | Add risk score display to `FindingCard.tsx` (0–10 badge) | `frontend/risk-score-badge` |
| 28 | Add sort-by-risk-score to findings table | `frontend/findings-sort-risk` |
| 29 | Write unit test for risk calculator | `test/risk-calculator-unit` |
| 30 | Tag release `v0.2.0-frontend` | `release/v0.2.0-frontend` |

---

## ✅ Phase 2 Deliverable Checklist

- [ ] Real AWS data collected via boto3 (IAM, EC2, S3, VPC, SG, RDS, CloudTrail)
- [ ] Knowledge graph built from collected data
- [ ] Attack paths detected and stored
- [ ] `/scan/start` → background job → `/scan/{id}/results` working end-to-end
- [ ] Findings displayed in frontend with severity filter
- [ ] Graph visualization rendered in Cytoscape.js
- [ ] Dashboard shows summary stats + charts
- [ ] Risk scores calculated and attached to findings
- [ ] **~120 commits total** (30 × 4 members) ✅

---

> 📌 **Next:** `roadmap_part3_risk_ai_dashboard.md` — Phase 3: Full AI integration, complete dashboard, polished attack path visualization.
