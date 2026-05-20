from __future__ import annotations

from pathlib import Path
from typing import Any


def write_summary(report: dict[str, Any], path: str | Path = "results/summary.md") -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Retrieval Evaluation Summary",
        "",
        f"Queries: {report['summary']['queries']}",
        f"Passed: {report['summary']['passed']}",
        f"Failed: {report['summary']['failed']}",
        "",
        "## Failures",
    ]
    for failure in report["summary"].get("failure_reasons", []):
        lines.append(f"- {failure}")
    output.write_text("\n".join(lines) + "\n")
