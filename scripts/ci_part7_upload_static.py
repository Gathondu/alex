#!/usr/bin/env python3
"""
Upload Next.js static export (frontend/out) to S3 and invalidate CloudFront.

Mirrors scripts/deploy.py upload_frontend(); driven by environment variables for CI.

Required:
  PART7_S3_BUCKET          S3 bucket name (terraform output s3_bucket_name)
  PART7_CLOUDFRONT_ID       CloudFront distribution ID

Optional:
  FRONTEND_OUT_DIR         Path to static export (default: repo/frontend/out)
"""

import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print(f"Running: {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=cwd)
    if r.returncode != 0:
        sys.exit(r.returncode)


def main() -> None:
    bucket = os.environ.get("PART7_S3_BUCKET", "").strip()
    dist_id = os.environ.get("PART7_CLOUDFRONT_ID", "").strip()
    if not bucket or not dist_id:
        print("PART7_S3_BUCKET and PART7_CLOUDFRONT_ID must be set.", file=sys.stderr)
        sys.exit(1)

    repo_root = Path(__file__).resolve().parent.parent
    out_dir = Path(os.environ.get("FRONTEND_OUT_DIR", str(repo_root / "frontend" / "out")))

    if not out_dir.is_dir():
        print(f"Frontend build not found: {out_dir}", file=sys.stderr)
        sys.exit(1)

    # Clear bucket, then upload with types (matches deploy.py)
    run(["aws", "s3", "rm", f"s3://{bucket}/", "--recursive"])

    base = str(out_dir) + "/"
    s3_base = f"s3://{bucket}/"

    run(
        [
            "aws", "s3", "cp", base, s3_base,
            "--recursive", "--exclude", "*", "--include", "*.html",
            "--content-type", "text/html",
            "--cache-control", "max-age=0,no-cache,no-store,must-revalidate",
        ]
    )
    run(
        [
            "aws", "s3", "cp", base, s3_base,
            "--recursive", "--exclude", "*", "--include", "*.css",
            "--content-type", "text/css",
            "--cache-control", "max-age=31536000,public",
        ]
    )
    run(
        [
            "aws", "s3", "cp", base, s3_base,
            "--recursive", "--exclude", "*", "--include", "*.js",
            "--content-type", "application/javascript",
            "--cache-control", "max-age=31536000,public",
        ]
    )
    run(
        [
            "aws", "s3", "cp", base, s3_base,
            "--recursive", "--exclude", "*", "--include", "*.json",
            "--content-type", "application/json",
            "--cache-control", "max-age=31536000,public",
        ]
    )

    for ext, ctype in [
        ("*.png", "image/png"),
        ("*.jpg", "image/jpeg"),
        ("*.jpeg", "image/jpeg"),
        ("*.gif", "image/gif"),
        ("*.svg", "image/svg+xml"),
        ("*.ico", "image/x-icon"),
    ]:
        run(
            [
                "aws", "s3", "cp", base, s3_base,
                "--recursive", "--exclude", "*", "--include", ext,
                "--content-type", ctype,
                "--cache-control", "max-age=31536000,public",
            ]
        )

    run(["aws", "s3", "sync", base, s3_base, "--cache-control", "max-age=31536000,public"])

    run(
        [
            "aws", "cloudfront", "create-invalidation",
            "--distribution-id", dist_id,
            "--paths", "/*",
        ]
    )
    print("Upload and CloudFront invalidation complete.")


if __name__ == "__main__":
    main()
