# CloudSentinel AI — Project Roadmap
## Part 4: Phase 4 — Evaluation, Polish & Documentation

> **Duration:** 2 Weeks | **Target:** ~25 commits per person (~100 total)
> **Goal:** Validate against thesis evaluation plan, fix all bugs, polish the UI, write all docs, and prep for demo/submission.

---

## 🔵 Harshith (Lead) — Evaluation Scenarios & Final Integration

| # | Task | Branch Name |
|---|------|-------------|
| 1 | Deploy controlled AWS test environment (LocalStack or real sandbox) | `eval/aws-test-env-setup` |
| 2 | Inject Scenario 1: Public S3 bucket with sensitive data | `eval/scenario1-public-s3` |
| 3 | Inject Scenario 2: Overly permissive IAM admin policy | `eval/scenario2-admin-iam` |
| 4 | Inject Scenario 3: SG with SSH/RDP open to 0.0.0.0/0 | `eval/scenario3-open-sg` |
| 5 | Inject Scenario 4: CloudTrail disabled | `eval/scenario4-cloudtrail-off` |
| 6 | Inject Scenario 5: Full multi-stage chain (EC2→IAM→Secrets→S3) | `eval/scenario5-full-chain` |
| 7 | Run CloudSentinel AI on all 5 scenarios — record results | `eval/results-cloudsentinel` |
| 8 | Run Prowler on same environment — record results for comparison | `eval/results-prowler` |
| 9 | Run ScoutSuite on same environment — record results | `eval/results-scoutsuite` |
| 10 | Build comparison table: detection rates, attack paths, false positives | `eval/comparison-table` |
| 11 | Write `docs/EVALUATION_RESULTS.md` with all experiment results | `docs/evaluation-results` |
| 12 | Fix any attack engine bugs found during evaluation | `fix/attack-engine-eval-bugs` |
| 13 | Optimize graph build performance (profile + fix bottlenecks) | `perf/graph-build-optimize` |
| 14 | Optimize attack path generation (prune low-probability paths) | `perf/attack-path-pruning` |
| 15 | Add `GET /api/v1/eval/scenarios` — endpoint to load demo scenarios | `api/demo-scenarios` |
| 16 | Write final `CONTRIBUTING.md` guide for the repo | `docs/contributing-md` |
| 17 | Write `docs/DEPLOYMENT.md` — production deployment guide | `docs/deployment-guide` |
| 18 | Add GitHub issue templates (bug report, feature request) | `chore/issue-templates` |
| 19 | Add GitHub PR template with checklist | `chore/pr-template` |
| 20 | Create project demo video script outline | `docs/demo-script` |
| 21 | Final end-to-end smoke test on fresh Docker Compose setup | `test/e2e-smoke-test` |
| 22 | Add `CHANGELOG.md` with Phase 1–4 history | `docs/changelog` |
| 23 | Pin all Python dependency versions in `requirements.txt` | `chore/pin-dependencies` |
| 24 | Tag release `v1.0.0-rc1` | `release/v1.0.0-rc1` |
| 25 | Tag final release `v1.0.0` | `release/v1.0.0` |

---

## 🟢 Teammate 1 — API Hardening, Testing & OpenAPI Docs

| # | Task | Branch Name |
|---|------|-------------|
| 1 | Write integration tests for full auth flow (register → login → protected endpoint) | `test/auth-flow-integration` |
| 2 | Write integration tests for full scan flow (start → poll → results) | `test/scan-flow-integration` |
| 3 | Write integration tests for report generation + download | `test/report-flow-integration` |
| 4 | Achieve 80%+ test coverage on all `api/v1/` files | `test/api-coverage-80` |
| 5 | Add pytest fixtures for mock AWS credentials + scan data | `test/pytest-fixtures` |
| 6 | Implement proper 401/403/404/422 error responses on all endpoints | `api/error-response-standards` |
| 7 | Add request body size limit (prevent large payload abuse) | `api/request-size-limit` |
| 8 | Add security headers middleware (X-Frame-Options, CSP, HSTS) | `api/security-headers` |
| 9 | Implement `/api/v1/health/deep` — check DB + AI provider connectivity | `api/health-deep-check` |
| 10 | Clean up OpenAPI tags + descriptions for all endpoints | `docs/openapi-cleanup` |
| 11 | Add OpenAPI examples for all request/response bodies | `docs/openapi-examples` |
| 12 | Add Swagger UI auth button (Bearer token support) | `docs/swagger-auth` |
| 13 | Write `docs/AUTH.md` — JWT + API key authentication guide | `docs/auth-guide-md` |
| 14 | Add `/api/v1/users/me/scans` — user-scoped scan history | `api/user-scans-endpoint` |
| 15 | Fix any failing unit tests from Phase 3 | `fix/phase3-unit-test-failures` |
| 16 | Add DB connection pooling config (pool_size, max_overflow) | `db/connection-pool-config` |
| 17 | Add async background task queue with status tracking (Celery stub) | `tasks/celery-stub` |
| 18 | Performance test — API response times under 100 concurrent requests | `test/api-load-test` |
| 19 | Add `/api/v1/version` endpoint returning app version | `api/version-endpoint` |
| 20 | Implement soft delete for scans (deleted_at field, not hard delete) | `db/soft-delete-scans` |
| 21 | Add `updated_at` timestamps to all models | `db/updated-at-timestamps` |
| 22 | Migrate secrets from `.env` to AWS Secrets Manager stub | `infra/secrets-manager-stub` |
| 23 | Write `docs/TESTING.md` — guide to running tests locally | `docs/testing-guide-md` |
| 24 | Final review of all DB migrations (clean + consistent) | `db/migration-final-review` |
| 25 | Tag release `v1.0.0-api-hardened` | `release/v1.0.0-api` |

---

## 🟡 Teammate 2 — Collector Testing, CI/CD & DevOps

| # | Task | Branch Name |
|---|------|-------------|
| 1 | Write boto3 mock fixtures using `moto` library | `test/moto-fixtures` |
| 2 | Write unit tests for IAM collector using moto | `test/iam-collector-unit` |
| 3 | Write unit tests for EC2 collector using moto | `test/ec2-collector-unit` |
| 4 | Write unit tests for S3 collector using moto | `test/s3-collector-unit` |
| 5 | Write unit tests for VPC + SG collector using moto | `test/vpc-sg-collector-unit` |
| 6 | Write unit tests for RDS + CloudTrail collector using moto | `test/rds-cloudtrail-unit` |
| 7 | Write unit tests for all analyzer rules (remaining coverage) | `test/analyzer-rules-coverage` |
| 8 | Achieve 80%+ test coverage on `collectors/` + `analyzers/` | `test/collector-analyzer-coverage-80` |
| 9 | Add CI step — run moto-based collector tests on every PR | `ci/collector-test-step` |
| 10 | Optimize IAM collector — batch API calls (reduce rate limiting) | `perf/iam-collector-batch` |
| 11 | Optimize S3 collector — parallel bucket metadata fetch | `perf/s3-collector-parallel` |
| 12 | Add retry logic with exponential backoff for all AWS API calls | `collector/retry-backoff` |
| 13 | Add `--dry-run` CLI flag to run without AWS credentials (uses mock data) | `cli/dry-run-flag` |
| 14 | Write `Makefile` with common commands (run, test, lint, migrate, seed) | `chore/makefile` |
| 15 | Create production-ready `docker-compose.prod.yml` | `infra/docker-compose-prod` |
| 16 | Add Docker health checks to all services | `infra/docker-healthchecks` |
| 17 | Set up GitHub Actions deployment workflow (CD to staging) | `ci/cd-deploy-staging` |
| 18 | Add Dependabot config for automated dependency updates | `chore/dependabot-config` |
| 19 | Add pre-commit hooks (ruff lint, black format, mypy type check) | `chore/pre-commit-hooks` |
| 20 | Fix all ruff lint warnings across the codebase | `fix/ruff-lint-cleanup` |
| 21 | Fix all mypy type errors across backend | `fix/mypy-type-errors` |
| 22 | Write `docs/COLLECTORS.md` — guide to adding new cloud collectors | `docs/collectors-guide-md` |
| 23 | Write `docs/RULES.md` — final documented rule list with IDs | `docs/rules-final-md` |
| 24 | Performance benchmark report — scan time for 50/100/200 resources | `docs/perf-benchmark-report` |
| 25 | Tag release `v1.0.0-devops` | `release/v1.0.0-devops` |

---

## 🟠 Teammate 3 — Frontend Polish, UX & E2E Tests

| # | Task | Branch Name |
|---|------|-------------|
| 1 | Complete UI audit — fix all broken/misaligned components | `frontend/ui-audit-fixes` |
| 2 | Add keyboard navigation support (Tab, Enter, Esc) across all pages | `frontend/keyboard-nav` |
| 3 | Add ARIA labels + roles for accessibility (a11y) | `frontend/a11y-aria-labels` |
| 4 | Implement global error boundary (catch React render errors) | `frontend/error-boundary` |
| 5 | Add 404 Not Found page | `frontend/404-page` |
| 6 | Add network error handling (show retry button on API failure) | `frontend/network-error-handling` |
| 7 | Implement `components/ConfirmModal.tsx` (for destructive actions) | `frontend/confirm-modal` |
| 8 | Polish `GraphPage.tsx` — add minimap, pan/zoom keyboard shortcuts | `frontend/graph-minimap` |
| 9 | Add attack chain step-through animation in graph | `frontend/graph-chain-animation` |
| 10 | Implement finding detail drawer/modal with full AI explanation | `frontend/finding-detail-modal` |
| 11 | Add remediation code block rendering (syntax highlighted) | `frontend/remediation-code-block` |
| 12 | Implement copy-to-clipboard for remediation code | `frontend/copy-to-clipboard` |
| 13 | Polish `ReportsPage.tsx` — download progress indicator | `frontend/report-download-progress` |
| 14 | Implement `pages/SettingsPage.tsx` — update AWS credentials, LLM provider | `frontend/settings-page` |
| 15 | Add profile page (show user info, scan stats) | `frontend/profile-page` |
| 16 | Implement frontend search — search findings by resource name/type | `frontend/findings-search` |
| 17 | Add `components/Badge.tsx`, `Tooltip.tsx`, `Chip.tsx` reusable atoms | `frontend/ui-atoms` |
| 18 | Animate dashboard stat cards on load (count-up animation) | `frontend/stat-card-animation` |
| 19 | Set up Playwright for E2E testing | `test/playwright-setup` |
| 20 | Write E2E test — login + start scan + view findings | `test/e2e-scan-flow` |
| 21 | Write E2E test — graph page loads + node click shows details | `test/e2e-graph-flow` |
| 22 | Write E2E test — download report as PDF | `test/e2e-report-download` |
| 23 | Optimize frontend bundle size (code splitting, lazy routes) | `frontend/bundle-optimize` |
| 24 | Write `docs/USER_GUIDE.md` — end-user guide with screenshots | `docs/user-guide-md` |
| 25 | Tag release `v1.0.0-frontend-polish` | `release/v1.0.0-frontend` |

---

## ✅ Phase 4 Deliverable Checklist

- [ ] All 5 thesis evaluation scenarios run + results documented
- [ ] Comparative analysis vs Prowler + ScoutSuite complete
- [ ] 80%+ test coverage on backend (collectors, analyzers, API)
- [ ] E2E tests passing for core user flows
- [ ] Zero ruff/mypy errors in CI
- [ ] All docs written: API.md, RULES.md, ARCHITECTURE.md, DEPLOYMENT.md, USER_GUIDE.md
- [ ] Production Docker Compose tested on fresh machine
- [ ] `v1.0.0` tagged and released on GitHub
- [ ] **~100 commits total** (25 × 4 members) ✅

---

## 📊 Full Project Commit Summary

| Phase | Duration | Commits/Person | Total Commits |
|-------|----------|----------------|---------------|
| Phase 1 — Base Setup | 2 weeks | 22 | 88 |
| Phase 2 — Core Pipeline | 3 weeks | 30 | 120 |
| Phase 3 — Risk / AI / Dashboard | 3 weeks | 30 | 120 |
| Phase 4 — Evaluation & Polish | 2 weeks | 25 | 100 |
| **TOTAL** | **10 weeks** | **107** | **428** |

> ✅ Every team member hits **107 commits** across the full project lifecycle.

---

## 🏁 Final Project Milestones

```
Week 1–2   → Phase 1 complete: skeleton + auth + stubs running in Docker
Week 3–5   → Phase 2 complete: real scan pipeline + graph + frontend wired
Week 6–8   → Phase 3 complete: AI explanations + full dashboard + reports
Week 9–10  → Phase 4 complete: evaluated + polished + documented + v1.0.0
```
