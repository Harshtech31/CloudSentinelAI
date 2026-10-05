"""Live HTTP walkthrough of the complete Member 1 Phase 2 pipeline.

Boots the real FastAPI app (uvicorn in a daemon thread) against a fresh
migrated demo.db, then exercises the full journey over real HTTP:

    register -> login -> auth guard -> start scan -> poll -> results ->
    scan list -> findings -> stats -> dashboard -> audit trail

Runs the genuine production chain: real DB rows, real JWT, real
orchestrator with registered collectors (stubs return empty results, so
the scan completes honestly with zero resources until Member 2's boto3
collectors land).

Usage:
    cd backend && .venv/bin/python scripts/demo_phase2_scan_flow.py
"""

import atexit
import logging
import os
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BACKEND_DIR / "demo.db"
BASE = "http://127.0.0.1:8123/api/v1"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

if DB_PATH.exists():
    DB_PATH.unlink()

os.environ["DATABASE_SYNC_URL"] = f"sqlite:///{DB_PATH}"

import httpx  # noqa: E402
import uvicorn  # noqa: E402


def migrate() -> None:
    result = subprocess.run(
        [".venv/bin/python", "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        print(result.stdout, result.stderr)
        raise SystemExit("alembic upgrade failed")


def boot_server() -> tuple[uvicorn.Server, threading.Thread]:
    from app.main import app  # imported AFTER env var is set

    config = uvicorn.Config(app, host="127.0.0.1", port=8123, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.time() + 15
    while not server.started and time.time() < deadline:
        time.sleep(0.1)
    if not server.started:
        raise SystemExit("server failed to start")
    return server, thread


def shutdown(server: uvicorn.Server, thread: threading.Thread) -> None:
    server.should_exit = True
    thread.join(timeout=10)
    time.sleep(0.2)
    if DB_PATH.exists():
        DB_PATH.unlink()


def step(title: str) -> None:
    print(f"\n{'=' * 62}\n  {title}\n{'=' * 62}")


def main() -> int:
    # Pipeline progress lines are the story; HTTP internals are noise.
    for noisy in ("httpx", "httpcore", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    logging.getLogger("cloudsentinel").setLevel(logging.INFO)

    migrate()
    server, thread = boot_server()
    atexit.register(shutdown, server, thread)
    client = httpx.Client(base_url=BASE, timeout=15)

    step("1. Health — backend alive against migrated demo.db")
    r = client.get("/health")
    print(f"   GET /health -> {r.status_code} {r.json()}")

    step("2. Register an analyst over real HTTP")
    r = client.post(
        "/auth/register",
        json={
            "email": "demo@cloudsentinel.ai",
            "password": "DemoPassword123!",
            "full_name": "Phase 2 Demo Analyst",
        },
    )
    print(f"   POST /auth/register -> {r.status_code}")
    body = r.json()
    print(f"   user: {body.get('email')} role={body.get('role')}")

    step("3. Login — JWT issued from the database")
    r = client.post(
        "/auth/login",
        json={"username": "demo@cloudsentinel.ai", "password": "DemoPassword123!"},
    )
    token = r.json()["access_token"]
    print(f"   POST /auth/login -> {r.status_code}")
    print(f"   access_token: {token[:40]}...")

    step("4. Auth guard — dashboard without a token is rejected")
    r = client.get("/dashboard/summary")
    print(f"   GET /dashboard/summary (no token) -> {r.status_code} (expect 401)")

    headers = {"Authorization": f"Bearer {token}"}

    step("5. Start a scan — background pipeline begins")
    r = client.post("/scan/start", json={}, headers=headers)
    print(f"   POST /scan/start -> {r.status_code}")
    scan = r.json()
    scan_id = scan["scan_id"]
    print(f"   scan {scan_id} status={scan['status']} provider={scan.get('target_cloud')}")

    step("6. Poll status until the orchestrator finishes")
    deadline = time.time() + 30
    status_value = ""
    while time.time() < deadline:
        r = client.get(f"/scan/{scan_id}/status", headers=headers)
        status_value = r.json()["status"]
        if status_value in ("completed", "failed", "cancelled"):
            break
        time.sleep(0.5)
    print(f"   GET /scan/{scan_id}/status -> {r.status_code} status={status_value}")

    step("7. Scan results — real rows, real aggregates")
    r = client.get(f"/scan/{scan_id}/results", headers=headers)
    body = r.json()
    row, summary = body["scan"], body["summary"]
    print(f"   GET /scan/{scan_id}/results -> {r.status_code}")
    print(
        f"   scan: status={row['status']} regions={row.get('regions')} "
        f"services={len(row.get('services') or [])} "
        f"duration={row.get('duration_seconds')}s"
    )
    print(
        f"   summary: total_findings={summary['total_findings']} "
        f"critical={summary['critical_findings']} high={summary['high_findings']} "
        f"attack_paths={summary['attack_paths_count']}"
    )

    step("8. Scan list — the user's scan history")
    r = client.get("/scan", headers=headers)
    body = r.json()
    print(f"   GET /scan -> {r.status_code} ({body.get('total')} scan(s))")
    for item in body.get("scans", []):
        print(
            f"   - {item['scan_id'][:12]}... {item['status']} "
            f"{item.get('target_cloud')} progress={item.get('progress_percentage')}%"
        )

    step("9. Findings + stats (empty until real collectors land)")
    r = client.get("/findings", headers=headers)
    print(f"   GET /findings -> {r.status_code} total={r.json().get('total')}")
    r = client.get("/findings/stats/summary", headers=headers)
    stats = r.json()
    print(
        f"   GET /findings/stats/summary -> {r.status_code} "
        f"critical={stats.get('critical')} high={stats.get('high')} "
        f"total={stats.get('total')}"
    )

    step("10. Error handling — unknown finding returns a clean 404")
    r = client.get("/findings/fnd_does_not_exist", headers=headers)
    print(f"   GET /findings/fnd_does_not_exist -> {r.status_code} {r.json()}")

    step("11. Executive dashboard summary")
    r = client.get("/dashboard/summary", headers=headers)
    body = r.json()
    print(f"   GET /dashboard/summary -> {r.status_code}")
    print(
        f"   security_score={body.get('security_score')} "
        f"scanned_resources={body.get('scanned_resources')} "
        f"total_findings={body.get('total_findings')}"
    )
    print(f"   attack_paths_identified={body.get('attack_paths_identified')}")

    step("12. Audit trail — written in the same transactions as the scan")
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT action, entity_type, detail, created_at FROM audit_logs ORDER BY created_at ASC"
    ).fetchall()
    conn.close()
    for action, entity_type, detail, created_at in rows:
        print(f"   [{created_at}] {action} on {entity_type}  {detail or ''}")
    if not rows:
        print("   (no audit rows found)")

    step("DEMO COMPLETE — all steps ran against the real app over HTTP")
    return 0


if __name__ == "__main__":
    sys.exit(main())
