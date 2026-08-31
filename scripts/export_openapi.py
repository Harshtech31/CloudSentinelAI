#!/usr/bin/env python3
"""
Utility script to extract and export FastAPI OpenAPI schema to JSON.
"""

import json
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.main import app


def export_openapi_schema(output_path: Path) -> None:
    """Generate OpenAPI schema dictionary from FastAPI app and save to file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    openapi_schema = app.openapi()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)

    print(f"✅ Successfully exported OpenAPI schema to: {output_path}")
    print(f"📊 Total endpoints documented: {len(openapi_schema.get('paths', {}))}")


if __name__ == "__main__":
    target = Path(__file__).resolve().parent.parent / "docs" / "api" / "openapi.json"
    export_openapi_schema(target)
