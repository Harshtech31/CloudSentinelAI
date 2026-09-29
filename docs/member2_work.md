# 👤 Member 2 — Complete Work Plan (Consolidated)

> **Role:** Cloud Collectors & Rule Engine
> **Owns:** `backend/app/collectors/`, `backend/app/analyzers/`, CIS compliance rules, collector testing & DevOps
> **Total tasks:** 107 across 4 phases (22 + 30 + 30 + 25)

---

## 📍 Where this plan lives in the repo

| Phase | Source file | Section |
|---|---|---|
| Phase 1 — Scaffolding | `docs/roadmap_part1_overview.md` | Line 97 → "🟡 Teammate 2 — Collectors & Analyzers Scaffolding" |
| Phase 2 — Real Collectors & Analyzers | `docs/roadmap_part2_core_pipeline.md` | Line 83 → "🟡 Teammate 2 — Real Collectors & Analyzers" |
| Phase 3 — Rule Engine & Compliance | `docs/roadmap_part3_risk_ai_dashboard.md` | Line 83 → "🟡 Teammate 2 — Rule Engine Completion & Compliance" |
| Phase 4 — Testing, CI/CD & DevOps | `docs/roadmap_part4_evaluation_polish.md` | Line 73 → "🟡 Teammate 2 — Collector Testing, CI/CD & DevOps" |

---

## 📦 Files Member 2 owns (current status)

| File | Status |
|---|---|
| `backend/app/collectors/base.py` | ✅ Done (Phase 1) |
| `backend/app/collectors/aws/{iam,ec2,s3,vpc,security_groups,rds,cloudtrail,config}.py` | ✅ Stubs done (Phase 1) |
| `backend/app/collectors/{gcp,azure}/__init__.py` | ✅ Placeholders done (Phase 1) |
| `backend/app/analyzers/{iam,networking,storage,encryption,compliance,misconfigurations}.py` | ✅ Stubs done (Phase 1) |
| `backend/app/schemas/scan.py` | ✅ Exists (Phase 1, shared) |
| `backend/app/api/v1/scan.py` | ⚠️ Stub (shared with Member 1) |
| `backend/app/tasks/` | ✅ Stub done (Phase 1, shared with Member 1) |

---

## Phase 1 — Collectors & Analyzers Scaffolding (22 tasks)

> Goal: file skeleton + stubs so nothing crashes on import. **Status: ✅ Complete — all 22 tasks done, each tested (ruff + behavioral checks) and committed individually.**

- [x] 1. `collectors/base.py` — abstract base collector class
- [x] 2. `collectors/aws/__init__.py` + AWS session helper (boto3)
- [x] 3. `collectors/aws/iam.py` — list users stub
- [x] 4. `collectors/aws/ec2.py` — list instances stub
- [x] 5. `collectors/aws/s3.py` — list buckets stub
- [x] 6. `collectors/aws/vpc.py` — list VPCs stub
- [x] 7. `collectors/aws/security_groups.py` — stub
- [x] 8. `collectors/aws/rds.py` — stub
- [x] 9. `collectors/aws/cloudtrail.py` — stub
- [x] 10. `collectors/aws/config.py` — AWS Config rules stub
- [x] 11. `collectors/gcp/__init__.py` — placeholder
- [x] 12. `collectors/azure/__init__.py` — placeholder
- [x] 13. `analyzers/__init__.py` + base analyzer class
- [x] 14. `analyzers/iam.py` — IAM rule stubs
- [x] 15. `analyzers/networking.py` — network rule stubs
- [x] 16. `analyzers/storage.py` — storage rule stubs
- [x] 17. `analyzers/encryption.py` — encryption stubs
- [x] 18. `analyzers/compliance.py` — compliance stubs
- [x] 19. `analyzers/misconfigurations.py` — main rule router
- [x] 20. `api/v1/scan.py` — `/scan/start` stub endpoint *(pre-existing from Lead's Phase 1)*
- [x] 21. `schemas/__init__.py` + scan request/response schemas *(pre-existing from Lead's Phase 1)*
- [x] 22. `tasks/__init__.py` + background scan task stub

---

## Phase 2 — Real Collectors & Analyzers (30 tasks)

> Goal: real AWS data in via boto3, real findings out. **Status: 0% — the core of Member 2's work.**

### Collectors (boto3)
- [ ] 1. `aws/iam.py` — list users, roles, policies
- [ ] 2. `aws/iam.py` — collect attached + inline policies
- [ ] 3. `aws/iam.py` — collect MFA status per user
- [ ] 4. `aws/ec2.py` — list instances with metadata
- [ ] 5. `aws/ec2.py` — collect instance IAM profiles
- [ ] 6. `aws/s3.py` — buckets + ACL + public access block
- [ ] 7. `aws/s3.py` — bucket encryption settings
- [ ] 8. `aws/s3.py` — bucket logging status
- [ ] 9. `aws/vpc.py` — VPCs + subnets + route tables
- [ ] 10. `aws/security_groups.py` — SGs + rules
- [ ] 11. `aws/rds.py` — instances + encryption status
- [ ] 12. `aws/cloudtrail.py` — trail status + logging
- [ ] 13. `aws/config.py` — Config recorder status
- [ ] 14. Multi-region support for all collectors

### Analyzer rules (first batch)
- [ ] 15. IAM: root account MFA disabled
- [ ] 16. IAM: admin wildcard policy (`Action: "*"`)
- [ ] 17. IAM: unused credentials > 90 days
- [ ] 18. Networking: SG allows 0.0.0.0/0 on SSH/RDP
- [ ] 19. Networking: SG allows all traffic
- [ ] 20. Storage: public S3 bucket
- [ ] 21. Storage: S3 bucket without versioning
- [ ] 22. Encryption: unencrypted RDS
- [ ] 23. Encryption: unencrypted S3 bucket
- [ ] 24. Compliance: CIS AWS Benchmark v1.5 rules (20 rules)
- [ ] 25. `misconfigurations.py` — orchestrate all analyzers

### Enrichment & tests
- [ ] 26. Finding fields: rule_id, resource_arn, region, remediation_url
- [ ] 27. Unit tests — IAM analyzer rules
- [ ] 28. Unit tests — networking analyzer rules
- [ ] 29. Unit tests — storage analyzer rules
- [ ] 30. Tag release `v0.2.0-collectors`

---

## Phase 3 — Rule Engine Completion & Compliance (30 tasks)

> Goal: full CIS suite, NIST mappings, compliance score. **Status: 0%.**

### Rule suite
- [ ] 1. 20 CIS AWS Benchmark v1.5 IAM rules
- [ ] 2. CIS networking rules (SG, NACLs, VPC flow logs)
- [ ] 3. CIS storage rules (S3 public access, logging, versioning)
- [ ] 4. CIS logging rules (CloudTrail, Config recorder)
- [ ] 5. CIS monitoring rules (CloudWatch alarms)
- [ ] 6. AWS Well-Architected security pillar rules
- [ ] 7. NIST SP 800-53 control mappings for findings
- [ ] 8. Compliance framework field on each finding (CIS/NIST/AWS-WAF)
- [ ] 9. Overall compliance score (%) in `compliance.py`
- [ ] 10. `GET /findings/compliance-report` endpoint

### Additional rules
- [ ] 11. IAM: password policy too weak
- [ ] 12. IAM: access key rotation > 90 days
- [ ] 13. IAM: user with both console + API access
- [ ] 14. Networking: VPC flow logs disabled
- [ ] 15. Networking: default VPC in use
- [ ] 16. Storage: S3 object-level logging off
- [ ] 17. Encryption: EC2 root volume unencrypted
- [ ] 18. Encryption: RDS backups unencrypted

### Metadata, config & tests
- [ ] 19. Tag each finding with rule_id
- [ ] 20. False positive suppression (allowlist by resource ARN)
- [ ] 21. Rule severity override config (per-org customization)
- [ ] 22. Rule documentation metadata (description, remediation URL)
- [ ] 23. Unit tests — CIS IAM rules (all 20)
- [ ] 24. Unit tests — CIS networking rules
- [ ] 25. Unit tests — compliance scoring
- [ ] 26. Multi-account scanning stub (assume_role)
- [ ] 27. Dry-run mode — collect + analyze without saving to DB
- [ ] 28. Resource count summary in scan results
- [ ] 29. `docs/RULES.md` — document all security rules
- [ ] 30. Tag release `v0.3.0-rules`

---

## Phase 4 — Collector Testing, CI/CD & DevOps (25 tasks)

> Goal: 80%+ coverage, hardened collectors, DevOps polish. **Status: 0%.**

### Testing (moto)
- [ ] 1. boto3 mock fixtures using `moto`
- [ ] 2. Unit tests — IAM collector (moto)
- [ ] 3. Unit tests — EC2 collector (moto)
- [ ] 4. Unit tests — S3 collector (moto)
- [ ] 5. Unit tests — VPC + SG collector (moto)
- [ ] 6. Unit tests — RDS + CloudTrail collector (moto)
- [ ] 7. Unit tests — all remaining analyzer rules
- [ ] 8. 80%+ coverage on `collectors/` + `analyzers/`
- [ ] 9. CI step — moto tests on every PR

### Performance & resilience
- [ ] 10. IAM collector — batch API calls (rate limiting)
- [ ] 11. S3 collector — parallel bucket metadata fetch
- [ ] 12. Retry + exponential backoff on all AWS API calls
- [ ] 13. `--dry-run` CLI flag (mock data, no credentials)

### DevOps
- [ ] 14. `Makefile` (run, test, lint, migrate, seed)
- [ ] 15. Production `docker-compose.prod.yml`
- [ ] 16. Docker health checks on all services
- [ ] 17. GitHub Actions CD workflow (staging deploy)
- [ ] 18. Dependabot config
- [ ] 19. Pre-commit hooks (ruff, black, mypy)
- [ ] 20. Fix all ruff warnings
- [ ] 21. Fix all mypy type errors
- [ ] 22. `docs/COLLECTORS.md` — guide to adding new collectors
- [ ] 23. `docs/RULES.md` — final rule list with IDs
- [ ] 24. Perf benchmark report — scan time for 50/100/200 resources
- [ ] 25. Tag release `v1.0.0-devops`

---

## 🔗 Dependencies on other members

| Depends on | Why |
|---|---|
| **Member 1** (DB & Auth) | Findings must be persisted via `Finding` model + repositories; scan task writes results to DB |
| **Lead (Harshith)** | Graph engine consumes collector output (nodes/edges from collected resources) |
| **Member 3** | Risk engine + AI consume the findings Member 2's analyzers produce |

## 🚀 Suggested build order (when work starts)

1. `collectors/base.py` + `analyzers/` base classes + raw finding schema (foundation)
2. IAM collector + IAM analyzer rules (first real end-to-end slice)
3. EC2/S3/VPC/SG/RDS/CloudTrail/Config collectors (moto tests as you go)
4. Networking/storage/encryption rules + `misconfigurations.py` orchestrator
5. CIS v1.5 suite + compliance score + `docs/RULES.md`
6. Phase 4 hardening: moto coverage → 80%, retry/backoff, batching
