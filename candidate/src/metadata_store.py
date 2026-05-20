from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import psycopg

from .config import get_settings


def connect_with_retry(retries: int = 30) -> psycopg.Connection:
    settings = get_settings()
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            return psycopg.connect(settings.postgres_dsn)
        except Exception as exc:  # pragma: no cover - exercised by integration retry path
            last_error = exc
            time.sleep(1)
    raise RuntimeError(f"postgres did not become ready: {last_error}")


def migrate() -> None:
    with connect_with_retry() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tenants (
                  id TEXT PRIMARY KEY,
                  name TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS users (
                  id TEXT PRIMARY KEY,
                  tenant_id TEXT NOT NULL REFERENCES tenants(id),
                  email TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS user_groups (
                  user_id TEXT NOT NULL REFERENCES users(id),
                  group_name TEXT NOT NULL,
                  PRIMARY KEY (user_id, group_name)
                );
                CREATE TABLE IF NOT EXISTS document_metadata (
                  doc_id TEXT PRIMARY KEY,
                  tenant_id TEXT NOT NULL REFERENCES tenants(id),
                  title TEXT NOT NULL,
                  effective_date TEXT,
                  acl_groups TEXT NOT NULL,
                  object_key TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS eval_runs (
                  id BIGSERIAL PRIMARY KEY,
                  run_name TEXT NOT NULL,
                  metrics_json JSONB NOT NULL,
                  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
                """
            )
        conn.commit()


def seed_tenants(path: str | Path = "fixtures/public/tenants.json") -> None:
    data = json.loads(Path(path).read_text())
    with connect_with_retry() as conn:
        with conn.cursor() as cur:
            for tenant in data["tenants"]:
                cur.execute(
                    "INSERT INTO tenants (id, name) VALUES (%s, %s) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name",
                    (tenant["id"], tenant["name"]),
                )
            for user in data["users"]:
                cur.execute(
                    """
                    INSERT INTO users (id, tenant_id, email)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET tenant_id = EXCLUDED.tenant_id, email = EXCLUDED.email
                    """,
                    (user["id"], user["tenant_id"], user["email"]),
                )
                for group in user["groups"]:
                    cur.execute(
                        "INSERT INTO user_groups (user_id, group_name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        (user["id"], group),
                    )
        conn.commit()


def upsert_document_metadata(document: dict[str, Any]) -> None:
    with connect_with_retry() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO document_metadata (doc_id, tenant_id, title, effective_date, acl_groups, object_key)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (doc_id) DO UPDATE SET
                  tenant_id = EXCLUDED.tenant_id,
                  title = EXCLUDED.title,
                  effective_date = EXCLUDED.effective_date,
                  acl_groups = EXCLUDED.acl_groups,
                  object_key = EXCLUDED.object_key
                """,
                (
                    document["doc_id"],
                    document["tenant_id"],
                    document["title"],
                    document.get("effective_date"),
                    ",".join(document.get("acl_groups", [])),
                    document["object_key"],
                ),
            )
        conn.commit()


def get_user_context(user_id: str) -> dict[str, Any]:
    with connect_with_retry() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, tenant_id, email FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            if row is None:
                raise KeyError(f"unknown user_id: {user_id}")
            cur.execute("SELECT group_name FROM user_groups WHERE user_id = %s ORDER BY group_name", (user_id,))
            groups = [group_row[0] for group_row in cur.fetchall()]
    return {"user_id": row[0], "tenant_id": row[1], "email": row[2], "groups": groups}


def record_eval_run(run_name: str, metrics: dict[str, Any]) -> None:
    with connect_with_retry() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO eval_runs (run_name, metrics_json) VALUES (%s, %s)",
                (run_name, json.dumps(metrics)),
            )
        conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["migrate", "seed-tenants"])
    parser.add_argument("--tenants", default="fixtures/public/tenants.json")
    args = parser.parse_args()

    if args.command == "migrate":
        migrate()
    elif args.command == "seed-tenants":
        migrate()
        seed_tenants(args.tenants)


if __name__ == "__main__":
    main()
