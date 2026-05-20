from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError

from .config import get_settings


def client_with_retry(retries: int = 30):
    settings = get_settings()
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            client = boto3.client(
                "s3",
                endpoint_url=settings.minio_endpoint,
                aws_access_key_id=settings.minio_access_key,
                aws_secret_access_key=settings.minio_secret_key,
                region_name="us-east-1",
            )
            client.list_buckets()
            return client
        except (ClientError, EndpointConnectionError) as exc:  # pragma: no cover - integration retry path
            last_error = exc
            time.sleep(1)
    raise RuntimeError(f"minio did not become ready: {last_error}")


def ensure_bucket(client) -> None:
    bucket = get_settings().minio_bucket
    try:
        client.head_bucket(Bucket=bucket)
    except ClientError:
        client.create_bucket(Bucket=bucket)


def seed_documents(fixture: str | Path = "fixtures/public/documents.jsonl") -> None:
    client = client_with_retry()
    ensure_bucket(client)
    bucket = get_settings().minio_bucket
    for line in Path(fixture).read_text().splitlines():
        if not line.strip():
            continue
        document = json.loads(line)
        client.put_object(
            Bucket=bucket,
            Key=document["object_key"],
            Body=document["body"].encode("utf-8"),
            ContentType="text/plain",
            Metadata={
                "tenant_id": document["tenant_id"],
                "doc_id": document["doc_id"],
            },
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["seed"])
    parser.add_argument("--fixture", default="fixtures/public/documents.jsonl")
    args = parser.parse_args()
    if args.command == "seed":
        seed_documents(args.fixture)


if __name__ == "__main__":
    main()
