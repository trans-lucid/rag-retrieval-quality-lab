#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


PUBLIC_DOCS = [
    {
        "doc_id": "alpha-password-legacy",
        "tenant_id": "tenant_alpha",
        "title": "Password reset keywords legacy notice",
        "body": "Legacy password reset instructions say users should request a manual reset ticket and wait for overnight support review.",
        "effective_date": "2024-01-10",
        "acl_groups": ["support_basic", "support_admin"],
        "object_key": "tenant_alpha/password/legacy.txt",
    },
    {
        "doc_id": "alpha-password-current",
        "tenant_id": "tenant_alpha",
        "title": "Current account access recovery",
        "body": "Current guidance sends users through Account Settings, Security, Recover Access, and a verified email link.",
        "effective_date": "2026-04-15",
        "acl_groups": ["support_basic", "support_admin"],
        "object_key": "tenant_alpha/password/current.txt",
    },
    {
        "doc_id": "beta-password-private",
        "tenant_id": "tenant_beta",
        "title": "Password reset premium playbook",
        "body": "Tenant beta private support reset steps.",
        "effective_date": "2026-05-01",
        "acl_groups": ["support_basic", "support_admin"],
        "object_key": "tenant_beta/password/private.txt",
    },
]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["public", "hidden"], default="public")
    parser.add_argument("--seed", type=int, default=20260520)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    random.seed(args.seed)
    rows = list(PUBLIC_DOCS)
    if args.scenario == "hidden":
        rows.append(
            {
                "doc_id": "delta-workspace-current",
                "tenant_id": "tenant_delta",
                "title": "Workspace recovery",
                "body": "Members regain workspace access through identity verification and an email confirmation link.",
                "effective_date": "2026-05-09",
                "acl_groups": ["support_basic"],
                "object_key": "tenant_delta/workspace/current.txt",
            }
        )
    random.shuffle(rows)
    write_jsonl(Path(args.out), rows)


if __name__ == "__main__":
    main()
