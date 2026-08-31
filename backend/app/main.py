"""
CloudSentinel AI Backend Application Entrypoint & OpenAPI Configuration.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.core.config import settings
from app.core.constants import APP_NAME, APP_VERSION
from app.core.exceptions import setup_exception_handlers
from app.core.logging import logger, setup_logging

# OpenAPI Metadata & Tags Definition
OPENAPI_TAGS = [
    {
        "name": "Health",
        "description": "Liveness and readiness probes for monitoring backend sub-engines and database connectivity.",
    },
    {
        "name": "Authentication",
        "description": "User account registration, JWT token generation, verification, and role-based access control (RBAC).",
    },
    {
        "name": "Scans",
        "description": "Multi-cloud infrastructure collection, scan orchestration, status polling, and scan history.",
    },
    {
        "name": "Findings",
        "description": "Security misconfiguration findings, CIS AWS Benchmark violations, severity metrics, and remediation.",
    },
    {
        "name": "Graph",
        "description": "Multi-cloud security knowledge graph, NetworkX traversals, and Cytoscape.js visual graph topologies.",
    },
    {
        "name": "Dashboard",
        "description": "Executive security posture metrics, compliance scores, and risk distributions.",
    },
    {
        "name": "Reports",
        "description": "Export comprehensive security assessment reports in PDF, HTML, JSON, and CSV formats.",
    },
]

OPENAPI_DESCRIPTION = """
## 🛡️ CloudSentinel AI API Overview

CloudSentinel AI is an automated **Cloud Security Posture Management (CSPM)** and **Graph-Based Attack Path Analysis** platform.

### 🌟 Core Capabilities
- **Multi-Cloud Collection**: Automated configuration gathering across IAM, EC2, S3, VPC, RDS, and CloudTrail.
- **Rule Engine & Compliance**: Policy evaluation against CIS AWS Benchmark v1.5 and Well-Architected Framework.
- **Graph Attack Path Analysis**: Knowledge graph modeling and multi-hop attack trajectory discovery (Internet → Compute → Role → Sensitive Data).
- **Contextual Risk Engine**: Dynamic risk scoring based on asset criticality, network exposure, and blast radius.
- **AI-Powered Explanations**: Contextual root cause explanation and remediation code generation.

### 🔑 Authentication
Protected endpoints require a **Bearer JWT access token** passed in the `Authorization` header:
```http
Authorization: Bearer <your_access_token>
```
"""


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan event handler for startup and shutdown procedures."""
    setup_logging()
    logger.info(f"Starting {APP_NAME} v{APP_VERSION} in [{settings.ENVIRONMENT}] mode...")
    yield
    logger.info(f"Shutting down {APP_NAME}...")


def create_application() -> FastAPI:
    """FastAPI Application factory with rich OpenAPI documentation."""
    app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        summary="Automated Cloud Security Posture Management & Attack Graph Analysis",
        description=OPENAPI_DESCRIPTION,
        openapi_tags=OPENAPI_TAGS,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        contact={
            "name": "CloudSentinel AI Engineering Team",
            "url": "https://github.com/Harshtech31/CloudSentinelAI",
            "email": "lead@cloudsentinel.ai",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
        swagger_ui_parameters={
            "defaultModelsExpandDepth": 1,
            "docExpansion": "list",
            "persistAuthorization": True,
            "filter": True,
        },
        lifespan=lifespan,
    )

    # Configure CORS Middleware
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Configure global exception handlers
    setup_exception_handlers(app)

    # Register API v1 Routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/", tags=["Health"])
    async def root():
        """Root service discovery endpoint."""
        return JSONResponse(
            content={
                "name": APP_NAME,
                "version": APP_VERSION,
                "status": "online",
                "docs": "/docs",
                "docs_url": "/docs",
                "redoc_url": "/redoc",
                "openapi_json": f"{settings.API_V1_STR}/openapi.json",
                "health_url": f"{settings.API_V1_STR}/health",
            }
        )

    return app


app = create_application()
