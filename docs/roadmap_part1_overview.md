# CloudSentinel AI — Project Roadmap
## Part 1: Overview, Team Structure & Phase 1 (Base Setup)

---

## 👥 Team Structure (4 Members)

| Member | Role | Domain |
|--------|------|--------|
| **Harshith** (Lead) | Project Lead + Attack Engine | Graph, Attack Paths, CI/CD, Core |
| **Teammate 1** | Backend Core | FastAPI, Auth, Database, API |
| **Teammate 2** | Cloud Collectors | AWS SDK, Analyzers, Rules |
| **Teammate 3** | Risk Engine + AI + Frontend | Risk Scoring, LLM, React Dashboard |

> **Target:** 100+ commits per person across all phases.
> Each micro-task = 1 commit. Features are broken into the smallest meaningful units.

---

## 📅 Phase Overview (4 Phases)

| Phase | Name | Duration | Commits/Person |
|-------|------|----------|----------------|
| **Phase 1** | Base Setup & Infrastructure | 2 weeks | ~22 |
| **Phase 2** | Core Pipeline (Collectors → Graph) | 3 weeks | ~30 |
| **Phase 3** | Risk Engine + AI + Dashboard | 3 weeks | ~30 |
| **Phase 4** | Evaluation, Polish & Docs | 2 weeks | ~25 |

**Total: ~107 commits per person** ✅

---

## 🏗️ Phase 1 — Base Setup & Infrastructure (Week 1–2)

> Goal: Project skeleton running end-to-end with CI/CD, auth, and empty scaffolding wired up.

---

### 🔵 Harshith (Lead) — Repo, CI/CD & Project Config

| # | Task | Branch Name |
|---|------|-------------|
| 1 | Init git repo, add `.gitignore`, `LICENSE` | `chore/repo-init` |
| 2 | Create `docker-compose.yml` (postgres + backend + frontend) | `infra/docker-compose-base` |
| 3 | Write backend `Dockerfile` | `infra/backend-dockerfile` |
| 4 | Write frontend `Dockerfile` | `infra/frontend-dockerfile` |
| 5 | Set up GitHub Actions CI — lint check | `ci/lint-workflow` |
| 6 | Set up GitHub Actions CI — test runner | `ci/test-workflow` |
| 7 | Set up GitHub Actions CI — docker build check | `ci/docker-build-check` |
| 8 | Create `.env.example` with all required keys | `chore/env-example` |
| 9 | Write `pyproject.toml` with dev dependencies | `chore/pyproject-setup` |
| 10 | Write `backend/app/core/config.py` (Settings via pydantic) | `core/config-settings` |
| 11 | Write `backend/app/core/logging.py` | `core/logging-setup` |
| 12 | Write `backend/app/core/exceptions.py` | `core/custom-exceptions` |
| 13 | Write `backend/app/core/constants.py` | `core/constants` |
| 14 | Write `backend/app/core/security.py` (hashing utils) | `core/security-utils` |
| 15 | Write `backend/app/main.py` (FastAPI app init) | `core/fastapi-init` |
| 16 | Register all API routers in `main.py` | `core/router-registration` |
| 17 | Add CORS middleware config | `core/cors-middleware` |
| 18 | Write `backend/app/api/v1/health.py` endpoint | `api/health-endpoint` |
| 19 | Write root `README.md` with setup instructions | `docs/readme-base` |
| 20 | Scaffold `attack_engine/` stubs (attack_graph, attack_paths, scoring, lateral_movement, privilege_escalation) | `attack/engine-scaffold` |
| 21 | Scaffold `graph/` stubs (builder, models, traversals, networkx, neo4j) | `graph/scaffold` |
| 22 | Tag release `v0.1.0-base` | `release/v0.1.0` |

---

### 🟢 Teammate 1 — Database & Auth Foundation

| # | Task | Branch Name |
|---|------|-------------|
| 1 | Set up SQLAlchemy base in `database/base.py` | `db/sqlalchemy-base` |
| 2 | Write `database/session.py` (engine + session factory) | `db/session-factory` |
| 3 | Write `database/models/__init__.py` + User model | `db/user-model` |
| 4 | Write Scan model (id, user, status, created_at) | `db/scan-model` |
| 5 | Write Finding model (id, scan_id, severity, type) | `db/finding-model` |
| 6 | Write Report model | `db/report-model` |
| 7 | Write `database/migrations/__init__.py` + Alembic init | `db/alembic-init` |
| 8 | Create initial migration (users table) | `db/migration-users` |
| 9 | Create migration for scans + findings tables | `db/migration-scans-findings` |
| 10 | Write `database/seed.py` (seed test user) | `db/seed-data` |
| 11 | Write `auth/jwt.py` — token creation + verification | `auth/jwt-utils` |
| 12 | Write `auth/password.py` — bcrypt hash/verify | `auth/password-utils` |
| 13 | Write `auth/permissions.py` — RBAC roles enum | `auth/rbac-roles` |
| 14 | Write `auth/oauth.py` — Google OAuth stub | `auth/oauth-stub` |
| 15 | Write `api/v1/auth.py` — `/register` endpoint | `api/auth-register` |
| 16 | Write `api/v1/auth.py` — `/login` endpoint | `api/auth-login` |
| 17 | Write `api/v1/auth.py` — `/refresh` token endpoint | `api/auth-refresh` |
| 18 | Write `api/dependencies.py` — get_current_user dep | `api/auth-dependency` |
| 19 | Write unit test for JWT utils | `test/jwt-unit-test` |
| 20 | Write unit test for password hashing | `test/password-unit-test` |
| 21 | Write `api/v1/findings.py` stub endpoint | `api/findings-stub` |
| 22 | Write `api/v1/dashboard.py` stub endpoint | `api/dashboard-stub` |

---

### 🟡 Teammate 2 — Collectors & Analyzers Scaffolding

| # | Task | Branch Name |
|---|------|-------------|
| 1 | Write `collectors/base.py` — Abstract base collector | `collector/base-class` |
| 2 | Write `collectors/aws/__init__.py` + AWS session helper | `collector/aws-session` |
| 3 | Write `collectors/aws/iam.py` — list users stub | `collector/aws-iam-stub` |
| 4 | Write `collectors/aws/ec2.py` — list instances stub | `collector/aws-ec2-stub` |
| 5 | Write `collectors/aws/s3.py` — list buckets stub | `collector/aws-s3-stub` |
| 6 | Write `collectors/aws/vpc.py` — list VPCs stub | `collector/aws-vpc-stub` |
| 7 | Write `collectors/aws/security_groups.py` — stub | `collector/aws-sg-stub` |
| 8 | Write `collectors/aws/rds.py` — stub | `collector/aws-rds-stub` |
| 9 | Write `collectors/aws/cloudtrail.py` — stub | `collector/aws-cloudtrail-stub` |
| 10 | Write `collectors/aws/config.py` — AWS Config rules stub | `collector/aws-config-stub` |
| 11 | Write `collectors/gcp/__init__.py` — placeholder | `collector/gcp-placeholder` |
| 12 | Write `collectors/azure/__init__.py` — placeholder | `collector/azure-placeholder` |
| 13 | Write `analyzers/__init__.py` + base analyzer | `analyzer/base-class` |
| 14 | Write `analyzers/iam.py` — IAM rule stubs | `analyzer/iam-stub` |
| 15 | Write `analyzers/networking.py` — network rule stubs | `analyzer/networking-stub` |
| 16 | Write `analyzers/storage.py` — storage rule stubs | `analyzer/storage-stub` |
| 17 | Write `analyzers/encryption.py` — encryption stubs | `analyzer/encryption-stub` |
| 18 | Write `analyzers/compliance.py` — compliance stubs | `analyzer/compliance-stub` |
| 19 | Write `analyzers/misconfigurations.py` — main router | `analyzer/misconfig-router` |
| 20 | Write `api/v1/scan.py` — `/scan/start` stub endpoint | `api/scan-start-stub` |
| 21 | Write `schemas/__init__.py` + scan request/response schemas | `schemas/scan-schemas` |
| 22 | Write `tasks/__init__.py` + background task stub for scan | `tasks/scan-task-stub` |

---

### 🟠 Teammate 3 — Risk Engine, AI & Frontend Scaffolding

| # | Task | Branch Name |
|---|------|-------------|
| 1 | Write `risk_engine/__init__.py` + base classes | `risk/base-scaffold` |
| 2 | Write `risk_engine/weights.py` — scoring weight constants | `risk/weight-constants` |
| 3 | Write `risk_engine/context.py` — context data model | `risk/context-model` |
| 4 | Write `risk_engine/calculator.py` — base risk formula stub | `risk/calculator-stub` |
| 5 | Write `risk_engine/prioritizer.py` — stub sorter | `risk/prioritizer-stub` |
| 6 | Write `risk_engine/business_impact.py` — impact mapper stub | `risk/business-impact-stub` |
| 7 | Write `ai/__init__.py` + AI provider interface | `ai/provider-interface` |
| 8 | Write `ai/providers/openai.py` — OpenAI client stub | `ai/openai-stub` |
| 9 | Write `ai/providers/bedrock.py` + `ollama.py` stubs | `ai/bedrock-ollama-stub` |
| 10 | Write `ai/prompts.py` — prompt templates skeleton | `ai/prompt-templates` |
| 11 | Write `ai/parser.py` + `ai/explain.py` stubs | `ai/explain-parser-stub` |
| 12 | Write `ai/recommendations.py` stub | `ai/recommendations-stub` |
| 13 | Write `reports/__init__.py` + json/csv/html/pdf stubs | `reports/all-stubs` |
| 14 | Write `api/v1/reports.py` stub endpoint | `api/reports-stub` |
| 15 | Init React app with Vite + TypeScript | `frontend/vite-init` |
| 16 | Install deps: react-router, axios, zustand, recharts, cytoscape | `frontend/install-deps` |
| 17 | Set up global CSS + design tokens (dark theme, colors, fonts) | `frontend/design-tokens` |
| 18 | Set up React Router + all route paths | `frontend/router-setup` |
| 19 | Create `layouts/MainLayout.tsx` + `AuthLayout.tsx` | `frontend/layouts` |
| 20 | Create `components/Navbar.tsx` + `Sidebar.tsx` | `frontend/nav-components` |
| 21 | Create all page placeholders (Login, Dashboard, Scan, Graph, Findings, Reports) | `frontend/page-stubs` |
| 22 | Set up Zustand auth store + `AuthContext.tsx` + wire login form | `frontend/auth-wired` |

---

## ✅ Phase 1 Deliverable Checklist

- [ ] Repo live on GitHub with branch protection on `main`
- [ ] CI pipeline runs on every PR (lint + test + build)
- [ ] Docker Compose brings up postgres + backend + frontend
- [ ] `/health` API returns `{ status: "ok" }`
- [ ] `/auth/register` and `/auth/login` endpoints working
- [ ] Frontend shows Login page and routes correctly
- [ ] All module stubs in place (no crashes on import)
- [ ] Seed script creates a test user
- [ ] **~88 commits total** (22 × 4 members) across Phase 1 ✅

---

> 📌 **Next:** `roadmap_part2_core_pipeline.md` — Phase 2: Real collectors, graph construction, working scan pipeline.
