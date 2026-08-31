# 🛡️ CloudSentinel AI

[![CI - Lint](https://github.com/Harshtech31/CloudSentinelAI/actions/workflows/lint.yml/badge.svg)](https://github.com/Harshtech31/CloudSentinelAI/actions/workflows/lint.yml)
[![CI - Test](https://github.com/Harshtech31/CloudSentinelAI/actions/workflows/test.yml/badge.svg)](https://github.com/Harshtech31/CloudSentinelAI/actions/workflows/test.yml)
[![Docker Build](https://github.com/Harshtech31/CloudSentinelAI/actions/workflows/docker-build.yml/badge.svg)](https://github.com/Harshtech31/CloudSentinelAI/actions/workflows/docker-build.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)

**CloudSentinel AI** is an advanced Cloud Security Posture Management (CSPM) and Automated Attack Path Analysis platform. It combines automated multi-cloud configuration collectors, graph-based attack path modeling (NetworkX/Neo4j), contextual risk calculation, and Large Language Model (LLM) powered remediation guidance into a single unified dashboard.

---

## 🏛️ System Architecture

```mermaid
graph TD
    A[Cloud Infrastructure AWS/GCP/Azure] -->|Boto3 / APIs| B[Multi-Cloud Collectors]
    B --> C[Security Analyzers & Rule Engine]
    C -->|Findings| D[Security Knowledge Graph Builder]
    D -->|Nodes & Edges| E[Attack Path Engine]
    E -->|Exploitable Chains| F[Contextual Risk Engine]
    F -->|Prioritized Risks| G[AI Explanation & Remediation]
    G --> H[FastAPI Backend & REST APIs]
    H --> I[Interactive React Dashboard & Cytoscape Viz]
```

---

## 👥 Team & Roles

| Member | Role | Key Domains |
|---|---|---|
| **Harshith** (Project Lead) | Lead Architect & Attack Engine | Graph Builder, Attack Engine, Infrastructure, CI/CD |
| **Teammate 1** | Backend Core | FastAPI, Database, Migrations, Authentication, API |
| **Teammate 2** | Cloud Collectors | AWS SDKs, Security Analyzers, CIS Benchmark Rules |
| **Teammate 3** | Risk Engine, AI & Frontend | Risk Scoring, LLM Explanations, React Dashboard |

---

## 🚀 Quick Start with Docker Compose

Ensure [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/) are installed.

```bash
# 1. Clone repository
git clone https://github.com/Harshtech31/CloudSentinelAI.git
cd CloudSentinelAI

# 2. Copy environment template
cp .env.example .env

# 3. Start all services (PostgreSQL, Backend API, Frontend)
docker compose up --build -d

# 4. Check container health
docker compose ps
```

- 🌐 **Frontend Dashboard**: [http://localhost:5173](http://localhost:5173)
- 🔌 **Backend API**: [http://localhost:8000](http://localhost:8000)
- 📖 **Swagger OpenAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- ❤️ **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 💻 Local Development Setup

### Backend (Python 3.11+)

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend server with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (Node 20+)

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

---

## 🧪 Running Tests & Quality Checks

```bash
# Run pytest test suite
cd backend
pytest -v

# Run linting with Ruff
ruff check .
ruff format --check .
```

---

## 📁 Repository Structure

```
.
├── .github/workflows/       # GitHub Actions CI/CD workflows
├── backend/
│   ├── app/
│   │   ├── ai/              # LLM providers & explanation generators
│   │   ├── analyzers/       # Misconfiguration & CIS compliance rules
│   │   ├── api/v1/          # FastAPI REST endpoints
│   │   ├── attack_engine/   # Attack graph & multi-hop path finder
│   │   ├── auth/            # JWT, password hashing & RBAC
│   │   ├── collectors/      # Multi-cloud collectors (AWS/GCP/Azure)
│   │   ├── core/            # Config, logging, exceptions, security
│   │   ├── database/        # SQLAlchemy base, models, migrations
│   │   ├── graph/           # Knowledge graph builder & NetworkX traversals
│   │   ├── reports/         # JSON/CSV/HTML/PDF report generators
│   │   └── risk_engine/     # Contextual risk calculators
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/
│   ├── src/                 # React 18 + Vite + TypeScript application
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── LICENSE
└── README.md
```

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
